import logging
import time as time_module
from datetime import time
from typing import Dict, List, Optional

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.timezone import now
from django.utils.text import slugify

from core.celery import app
from apps.venues.models import (
    Company, VenueCategory, Venue, VenueWorkingHour, 
    VenueImage, VenueSocialMedia, VenueReview
)
from apps.common.models import Facility

logger = logging.getLogger(__name__)


class GooglePlacesClient:
    """Google Places API v1 client for venue data collection"""
    
    BASE_URL = "https://places.googleapis.com/v1"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "*"
        }
    
    def search_restaurants_in_tashkent(self) -> List[Dict]:
        """Search for restaurants in Tashkent using multiple strategies"""
        all_results = []
        seen_ids = set()
        
        # Strategy 1: Nearby search from Tashkent center
        tashkent_coords = (41.2995, 69.2401)
        nearby_results = self._nearby_search(tashkent_coords[0], tashkent_coords[1])
        
        for result in nearby_results:
            place_id = result.get("id")
            if place_id and place_id not in seen_ids:
                seen_ids.add(place_id)
                all_results.append(result)
        
        # Strategy 2: Text search with different queries
        search_queries = [
            "restaurants in Tashkent center",
            "cafes in Tashkent old city", 
            "restaurants near Tashkent airport",
            "food in Tashkent suburbs",
            "restaurants in Tashkent mall",
            "cafes in Tashkent plaza",
            "restaurants in Tashkent new city",
            "cafes in Tashkent downtown",
            "bakeries in Tashkent",
            "bars in Tashkent",
            "coffee shops in Tashkent",
            "fast food in Tashkent",
            "ice cream shops in Tashkent",
            "dessert shops in Tashkent",
            "juice shops in Tashkent",
            "food courts in Tashkent",
            "chinese restaurants in Tashkent",
            "japanese restaurants in Tashkent",
            "korean restaurants in Tashkent",
            "indian restaurants in Tashkent",
            "italian restaurants in Tashkent",
            "french restaurants in Tashkent",
            "mediterranean restaurants in Tashkent",
            "barbecue restaurants in Tashkent",
            "fine dining in Tashkent",
            "buffet restaurants in Tashkent",
            "breakfast restaurants in Tashkent",
            "brunch restaurants in Tashkent",
            "deli shops in Tashkent",
            "confectionery shops in Tashkent",
            "chocolate shops in Tashkent",
            "donut shops in Tashkent",
            "cat cafes in Tashkent",
            "dog cafes in Tashkent"
        ]
        
        for query in search_queries:
            try:
                text_results = self._text_search(query)
                for result in text_results:
                    place_id = result.get("id")
                    if place_id and place_id not in seen_ids:
                        seen_ids.add(place_id)
                        all_results.append(result)
                
                time_module.sleep(1.0)  # Rate limiting
            except Exception as e:
                logger.warning(f"Failed to search with query '{query}': {e}")
                continue
        
        # Strategy 3: Search in different areas
        area_searches = [
            ("Chilanzar", 41.2995, 69.2401),
            ("Yunusabad", 41.3111, 69.2797),
            ("Mirabad", 41.2573, 69.2812),
            ("Sergeli", 41.2995, 69.2401)
        ]
        
        for area_name, area_lat, area_lng in area_searches:
            try:
                area_results = self._area_search(area_name, area_lat, area_lng)
                for result in area_results:
                    place_id = result.get("id")
                    if place_id and place_id not in seen_ids:
                        seen_ids.add(place_id)
                        all_results.append(result)
                
                time_module.sleep(1.0)  # Rate limiting between areas
            except Exception as e:
                logger.warning(f"Failed to search area {area_name}: {e}")
                continue
        
        # Strategy 4: Search by specific food types for comprehensive coverage
        food_type_queries = [
            'acai_shop', 'afghani_restaurant', 'african_restaurant', 'american_restaurant',
            'asian_restaurant', 'bagel_shop', 'bakery', 'bar', 'bar_and_grill',
            'barbecue_restaurant', 'brazilian_restaurant', 'breakfast_restaurant',
            'brunch_restaurant', 'buffet_restaurant', 'cafe', 'cafeteria',
            'candy_store', 'cat_cafe', 'chinese_restaurant', 'chocolate_factory',
            'chocolate_shop', 'coffee_shop', 'confectionery', 'deli',
            'dessert_restaurant', 'dessert_shop', 'diner', 'dog_cafe',
            'donut_shop', 'fast_food_restaurant', 'fine_dining_restaurant',
            'food_court', 'french_restaurant', 'greek_restaurant', 'hamburger_restaurant',
            'ice_cream_shop', 'indian_restaurant', 'indonesian_restaurant',
            'italian_restaurant', 'japanese_restaurant', 'juice_shop',
            'korean_restaurant', 'lebanese_restaurant', 'meal_delivery',
            'meal_takeaway', 'mediterranean_restaurant'
        ]
        
        for food_type in food_type_queries:
            try:
                type_results = self._search_by_type(food_type, tashkent_coords)
                for result in type_results:
                    place_id = result.get("id")
                    if place_id and place_id not in seen_ids:
                        seen_ids.add(place_id)
                        all_results.append(result)
                
                time_module.sleep(1.0)  # Rate limiting between types
            except Exception as e:
                logger.warning(f"Failed to search food type {food_type}: {e}")
                continue
        
        # Log search summary
        self._log_search_summary(all_results, seen_ids)
        
        return all_results
    
    def _nearby_search(self, lat: float, lng: float) -> List[Dict]:
        """Search for places near coordinates"""
        results = []
        place_types = [
            'acai_shop', 'afghani_restaurant', 'african_restaurant', 'american_restaurant',
            'asian_restaurant', 'bagel_shop', 'bakery', 'bar', 'bar_and_grill',
            'barbecue_restaurant', 'brazilian_restaurant', 'breakfast_restaurant',
            'brunch_restaurant', 'buffet_restaurant', 'cafe', 'cafeteria',
            'candy_store', 'cat_cafe', 'chinese_restaurant', 'chocolate_factory',
            'chocolate_shop', 'coffee_shop', 'confectionery', 'deli',
            'dessert_restaurant', 'dessert_shop', 'diner', 'dog_cafe',
            'donut_shop', 'fast_food_restaurant', 'fine_dining_restaurant',
            'food_court', 'french_restaurant', 'greek_restaurant', 'hamburger_restaurant',
            'ice_cream_shop', 'indian_restaurant', 'indonesian_restaurant',
            'italian_restaurant', 'japanese_restaurant', 'juice_shop',
            'korean_restaurant', 'lebanese_restaurant', 'meal_delivery',
            'meal_takeaway', 'mediterranean_restaurant'
        ]
        
        for place_type in place_types:
            url = f"{self.BASE_URL}/places:searchNearby"
            payload = {
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": lat, "longitude": lng},
                        "radius": 50000.0
                    }
                },
                "includedTypes": [place_type],
                "maxResultCount": 20,  # API limit
                "languageCode": "en"
            }
            
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if "places" in data:
                    results.extend(data["places"])
                    logger.info(f"Found {len(data['places'])} {place_type} places")
                
                time_module.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.warning(f"Failed to search {place_type}: {e}")
                continue
        
        logger.info(f"Nearby search completed: found {len(results)} total places")
        return results
    
    def _text_search(self, query: str) -> List[Dict]:
        """Text search for places"""
        url = f"{self.BASE_URL}/places:searchText"
        payload = {
            "textQuery": query,
            "maxResultCount": 20,  # API limit
            "languageCode": "en",
            "locationBias": {
                "circle": {
                    "center": {"latitude": 41.2995, "longitude": 69.2401},
                    "radius": 50000.0
                }
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "places" in data:
                logger.info(f"Found {len(data['places'])} places for query '{query}'")
                return data["places"]
        except Exception as e:
            logger.warning(f"Text search failed for query '{query}': {e}")
        
        return []
    
    def _area_search(self, area_name: str, lat: float, lng: float) -> List[Dict]:
        """Search for places in specific areas"""
        results = []
        place_types = [
            'restaurant', 'cafe', 'bar', 'bakery', 'coffee_shop', 'fast_food_restaurant',
            'ice_cream_shop', 'dessert_shop', 'juice_shop', 'food_court'
        ]
        
        for place_type in place_types:
            url = f"{self.BASE_URL}/places:searchNearby"
            payload = {
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": lat, "longitude": lng},
                        "radius": 15000.0  # Smaller radius for area-specific search
                    }
                },
                "includedTypes": [place_type],
                "maxResultCount": 20,  # API limit
                "languageCode": "en"
            }
            
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if "places" in data:
                    results.extend(data["places"])
                    logger.info(f"Found {len(data['places'])} {place_type} places in {area_name}")
                
                time_module.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.warning(f"Failed to search {place_type} in {area_name}: {e}")
                continue
        
        logger.info(f"Area search completed for {area_name}: found {len(results)} total places")
        return results
    
    def _search_by_type(self, food_type: str, center_coords: tuple) -> List[Dict]:
        """Search for places of specific food type across Tashkent"""
        results = []
        
        # Search in multiple areas to cover the city
        search_areas = [
            (center_coords[0], center_coords[1], 50000),  # Center
            (41.3111, 69.2797, 30000),  # Old city
            (41.2573, 69.2812, 30000),  # Airport area
            (41.2995, 69.2401, 30000)   # New city
        ]
        
        for lat, lng, radius in search_areas:
            url = f"{self.BASE_URL}/places:searchNearby"
            payload = {
                "locationRestriction": {
                    "circle": {
                        "center": {"latitude": lat, "longitude": lng},
                        "radius": float(radius)
                    }
                },
                "includedTypes": [food_type],
                "maxResultCount": 20,  # API limit
                "languageCode": "en"
            }
            
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                if "places" in data:
                    results.extend(data["places"])
                    logger.info(f"Found {len(data['places'])} {food_type} places in area ({lat}, {lng})")
                
                time_module.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.warning(f"Failed to search {food_type} in area ({lat}, {lng}): {e}")
                continue
        
        logger.info(f"Type search completed for {food_type}: found {len(results)} total places")
        return results
    
    def _log_search_summary(self, all_results: List[Dict], seen_ids: set):
        """Log summary of search results"""
        total_found = len(all_results)
        unique_found = len(seen_ids)
        
        logger.info("=" * 60)
        logger.info("SEARCH SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total places found: {total_found}")
        logger.info(f"Unique places: {unique_found}")
        logger.info(f"Duplicate places filtered: {total_found - unique_found}")
        logger.info("=" * 60)
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get detailed information for a place"""
        url = f"{self.BASE_URL}/places/{place_id}"
        
        # Request essential fields for venue data
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "id,photos,displayName,businessStatus,primaryType,primaryTypeDisplayName,rating,regularOpeningHours,websiteUri,userRatingCount,priceLevel,delivery,outdoorSeating,liveMusic,goodForChildren,goodForGroups,goodForWatchingSports,servesBeer,servesWine,servesBreakfast,servesLunch,servesDinner,servesCoffee,servesDessert,servesCocktails,reservable,editorialSummary,reviews,formattedAddress,location,types"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            # Log response for debugging
            if response.status_code != 200:
                logger.warning(f"API response for {place_id}: {response.status_code} - {response.text}")
            
            response.raise_for_status()
            data = response.json()
            
            # Validate that we got the expected data structure
            if not isinstance(data, dict):
                logger.warning(f"Unexpected response format for {place_id}: {type(data)}")
                return None
                
            return data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.warning(f"Invalid request for {place_id}: {e.response.text}")
            elif e.response.status_code == 404:
                logger.warning(f"Place not found: {place_id}")
            else:
                logger.warning(f"HTTP error for {place_id}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Failed to get details for {place_id}: {e}")
            return None
    
    def get_place_photo(self, photo_name: str, max_width: int = 800) -> Optional[ContentFile]:
        """Get photo from Google Places API"""
        url = f"{self.BASE_URL}/places/{photo_name}/media"
        params = {
            "maxWidthPx": max_width,
            "key": self.api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            filename = f"google_photo_{photo_name.split('/')[-1]}.jpg"
            return ContentFile(response.content, name=filename)
            
        except Exception as e:
            logger.warning(f"Failed to download photo: {e}")
            return None


class VenueDataProcessor:
    """Process and save venue data to database"""
    
    def __init__(self):
        self.default_company = None
        self._ensure_default_company()
    
    def _ensure_default_company(self):
        """Ensure default company exists"""
        self.default_company, _ = Company.objects.get_or_create(
            external_id="google_places_import",
            defaults={"name": "Google Places Import"}
        )
    
    def process_venue(self, place_data: Dict) -> Optional[Venue]:
        """Process a single venue from Google Places API data"""
        try:
            # Extract basic data
            name = place_data.get("displayName", {}).get("text", "Unnamed")[:200]
            address = place_data.get("formattedAddress", "")[:200]
            rating = place_data.get("rating", 0.0)
            place_types = place_data.get("types", [])
            website = place_data.get("websiteUri", "")
            
            # Extract coordinates
            location = place_data.get("location", {})
            lat = location.get("latitude")
            lng = location.get("longitude")
            
            # Extract business features
            business_features = self._extract_business_features(place_data)
            
            # Determine company
            try:
                company = self._determine_company(place_data)
                if company:
                    logger.info(f"Determined company '{company.name}' for venue {name}")
                else:
                    logger.warning(f"No company determined for venue {name}")
            except Exception as e:
                logger.error(f"Failed to determine company for venue {name}: {e}")
                company = self.default_company
            
            # Create or update venue
            venue, created = Venue.objects.update_or_create(
                parsing_id=place_data.get("id"),
                defaults={
                    "company": company,
                    "name": name,
                    "description": self._create_description(place_data),
                    "location": address,
                    "rating": rating,
                    "latitude": lat,
                    "longitude": lng
                }
            )
            
            # Process categories
            self._process_categories(venue, place_data)
            
            # Process working hours
            self._process_working_hours(venue, place_data.get("regularOpeningHours", {}))
            
            # Process photos
            self._process_photos(venue, place_data.get("photos", []))
            
            # Process social media
            if website:
                self._process_social_media(venue, website)
            
            # Process reviews
            self._process_reviews(venue, place_data.get("reviews", []))
            
            # Process facilities
            self._process_facilities(venue, business_features)
            
            return venue
            
        except Exception as e:
            logger.error(f"Failed to process venue: {e}")
            return None
    
    def _extract_business_features(self, place_data: Dict) -> Dict:
        """Extract business features from API data"""
        features = {}
        
        # Food service features - use safe get with fallback
        features["serves_breakfast"] = self._safe_get_bool(place_data, "servesBreakfast")
        features["serves_lunch"] = self._safe_get_bool(place_data, "servesLunch")
        features["serves_dinner"] = self._safe_get_bool(place_data, "servesDinner")
        features["serves_coffee"] = self._safe_get_bool(place_data, "servesCoffee")
        features["serves_dessert"] = self._safe_get_bool(place_data, "servesDessert")
        features["serves_cocktails"] = self._safe_get_bool(place_data, "servesCocktails")
        features["serves_beer"] = self._safe_get_bool(place_data, "servesBeer")
        features["serves_wine"] = self._safe_get_bool(place_data, "servesWine")
        
        # Atmosphere features - use safe get with fallback
        features["outdoor_seating"] = self._safe_get_bool(place_data, "outdoorSeating")
        features["live_music"] = self._safe_get_bool(place_data, "liveMusic")
        features["good_for_children"] = self._safe_get_bool(place_data, "goodForChildren")
        features["good_for_groups"] = self._safe_get_bool(place_data, "goodForGroups")
        features["good_for_watching_sports"] = self._safe_get_bool(place_data, "goodForWatchingSports")
        
        # Service features - use safe get with fallback
        features["delivery"] = self._safe_get_bool(place_data, "delivery")
        features["reservable"] = self._safe_get_bool(place_data, "reservable")
        
        return features
    
    def _safe_get_bool(self, data: Dict, key: str) -> bool:
        """Safely get boolean value from API response"""
        try:
            value = data.get(key)
            if value is None:
                return False
            return bool(value)
        except (TypeError, ValueError):
            return False
    
    def _create_description(self, place_data: Dict) -> str:
        """Create venue description from multiple data sources"""
        description_parts = []
        
        # Basic info
        if place_data.get("formattedAddress"):
            description_parts.append(f"Address: {place_data['formattedAddress']}")
        
        # Business features
        features = self._extract_business_features(place_data)
        feature_descriptions = []
        
        if features.get("serves_breakfast"):
            feature_descriptions.append("Breakfast")
        if features.get("serves_lunch"):
            feature_descriptions.append("Lunch")
        if features.get("serves_dinner"):
            feature_descriptions.append("Dinner")
        if features.get("outdoor_seating"):
            feature_descriptions.append("Outdoor seating")
        if features.get("live_music"):
            feature_descriptions.append("Live music")
        if features.get("good_for_children"):
            feature_descriptions.append("Family friendly")
        if features.get("delivery"):
            feature_descriptions.append("Delivery available")
        if features.get("reservable"):
            feature_descriptions.append("Reservations accepted")
        
        if feature_descriptions:
            description_parts.append(f"Features: {', '.join(feature_descriptions)}")
        
        # Price level
        price_level = place_data.get("priceLevel", "")
        if price_level and price_level != "PRICE_LEVEL_UNSPECIFIED":
            price_mapping = {
                "INEXPENSIVE": "Budget-friendly",
                "MODERATE": "Moderate pricing",
                "EXPENSIVE": "Premium pricing",
                "VERY_EXPENSIVE": "Luxury pricing"
            }
            price_desc = price_mapping.get(price_level, price_level)
            description_parts.append(f"Price: {price_desc}")
        
        # Editorial summary
        editorial_summary = place_data.get("editorialSummary", {}).get("text", "")
        if editorial_summary:
            description_parts.append(f"About: {editorial_summary}")
        
        return " | ".join(description_parts)[:500]
    
    def _determine_company(self, place_data: Dict) -> Company:
        """Determine if venue belongs to a chain or use default company"""
        name = place_data.get("displayName", {}).get("text", "")
        
        # Check for chain indicators
        types = place_data.get("types", [])
        chain_indicators = ['restaurant_chain', 'fast_food_chain', 'coffee_shop_chain']
        
        if any(indicator in types for indicator in chain_indicators):
            words = name.split()
            if words:
                brand_name = words[0][:100]
                company, _ = Company.objects.get_or_create(
                    name=brand_name,
                    defaults={
                        "external_id": f"chain_{brand_name.lower().replace(' ', '_')}",
                        "parsing_id": f"brand_{brand_name.lower().replace(' ', '_')}"
                    }
                )
                return company
        
        # Check for location-based chains
        location_indicators = ['center', 'airport', 'mall', 'plaza', 'station', 'terminal']
        name_lower = name.lower()
        
        if any(indicator in name_lower for indicator in location_indicators):
            words = name.split()
            if words:
                brand_name = words[0][:100]
                company, _ = Company.objects.get_or_create(
                    name=brand_name,
                    defaults={
                        "external_id": f"chain_{brand_name.lower().replace(' ', '_')}",
                        "parsing_id": f"brand_{brand_name.lower().replace(' ', '_')}"
                    }
                )
                return company
        
        # Check for common restaurant chains by name patterns
        common_chains = ['mcdonalds', 'kfc', 'burger king', 'pizza hut', 'dominos', 'starbucks', 'coffee', 'cafe']
        name_lower = name.lower()
        
        for chain in common_chains:
            if chain in name_lower:
                if chain in ['coffee', 'cafe']:
                    # Extract potential brand name for coffee/cafe
                    words = name.split()
                    if len(words) >= 2:
                        brand_name = ' '.join(words[:2])
                    else:
                        brand_name = name
                else:
                    brand_name = chain.replace(' ', '').title()
                
                company, _ = Company.objects.get_or_create(
                    name=brand_name,
                    defaults={
                        "external_id": f"chain_{brand_name.lower().replace(' ', '_')}",
                        "parsing_id": f"brand_{brand_name.lower().replace(' ', '_')}"
                    }
                )
                return company
        
        # If no specific chain found, try to create company from first word
        words = name.split()
        if words and len(words[0]) > 2:  # Avoid very short names
            brand_name = words[0][:100]
            company, _ = Company.objects.get_or_create(
                name=brand_name,
                defaults={
                    "external_id": f"chain_{brand_name.lower().replace(' ', '_')}",
                    "parsing_id": f"brand_{brand_name.lower().replace(' ', '_')}"
                }
            )
            return company
        
        return self.default_company
    
    def _process_categories(self, venue: Venue, place_data: Dict):
        """Process venue categories"""
        categories = []
        
        try:
            # Primary type
            primary_type = place_data.get("primaryType")
            if primary_type:
                category_title = slugify(primary_type).replace("-", " ").title()
                parsing_id = f"google_primary_{primary_type}"
                
                category, _ = VenueCategory.objects.get_or_create(
                    parsing_id=parsing_id,
                    defaults={
                        "title": category_title,
                        "is_active": True,
                        "order": 0
                    }
                )
                categories.append(category)
                logger.debug(f"Added primary category: {category_title}")
            
            # Primary type display name
            primary_type_display = place_data.get("primaryTypeDisplayName")
            if primary_type_display:
                category_title = slugify(primary_type_display).replace("-", " ").title()
                parsing_id = f"google_primary_display_{primary_type_display}"
                
                category, _ = VenueCategory.objects.get_or_create(
                    parsing_id=parsing_id,
                    defaults={
                        "title": category_title,
                        "is_active": True,
                        "order": 1
                    }
                )
                categories.append(category)
                logger.debug(f"Added display category: {category_title}")
            
            # Types from the types array
            types = place_data.get("types", [])
            for i, type_name in enumerate(types):
                if type_name != primary_type:  # Avoid duplicate with primary type
                    category_title = slugify(type_name).replace("-", " ").title()
                    parsing_id = f"google_type_{type_name}"
                    
                    category, _ = VenueCategory.objects.get_or_create(
                        parsing_id=parsing_id,
                        defaults={
                            "title": category_title,
                            "is_active": True,
                            "order": i + 2
                        }
                    )
                    categories.append(category)
                    logger.debug(f"Added type category: {category_title}")
            
            if categories:
                venue.category.set(categories)
                logger.info(f"Set {len(categories)} categories for venue {venue.name}")
            else:
                logger.warning(f"No categories found for venue {venue.name}")
                
        except Exception as e:
            logger.error(f"Failed to process categories for venue {venue.name}: {e}")
            # Try to set at least one default category
            try:
                default_category, _ = VenueCategory.objects.get_or_create(
                    parsing_id="google_default_restaurant",
                    defaults={
                        "title": "Restaurant",
                        "is_active": True,
                        "order": 0
                    }
                )
                venue.category.set([default_category])
                logger.info(f"Set default category for venue {venue.name}")
            except Exception as default_e:
                logger.error(f"Failed to set default category for venue {venue.name}: {default_e}")
    
    def _process_working_hours(self, venue: Venue, opening_hours: Dict):
        """Process venue working hours"""
        if not opening_hours:
            logger.warning(f"No opening hours data for venue {venue.name}")
            return
            
        periods = opening_hours.get("periods", [])
        if not periods:
            logger.warning(f"No periods data in opening hours for venue {venue.name}")
            return
        
        processed_periods = 0
        for period in periods:
            open_data = period.get("open", {})
            close_data = period.get("close", {})
            
            open_day = open_data.get("day")
            if open_day is None:
                logger.warning(f"Missing open day data in period: {period}")
                continue
            
            # Convert Google day format to internal format
            day_mapping = {0: 'sun', 1: 'mon', 2: 'tue', 3: 'wed', 4: 'thu', 5: 'fri', 6: 'sat'}
            weekday = day_mapping.get(open_day, 'mon')
            
            # Parse times
            open_time = self._parse_time(open_data.get("time"))
            close_time = self._parse_time(close_data.get("time"))
            
            if open_time and close_time:
                try:
                    VenueWorkingHour.objects.update_or_create(
                        venue=venue,
                        weekday=weekday,
                        defaults={
                            "opening_time": open_time,
                            "closing_time": close_time
                        }
                    )
                    processed_periods += 1
                except Exception as e:
                    logger.warning(f"Failed to create working hours for {venue.name} on {weekday}: {e}")
            else:
                logger.warning(f"Invalid time data for {venue.name} on {weekday}: open={open_data.get('time')}, close={close_data.get('time')}")
        
        if processed_periods > 0:
            logger.info(f"Processed {processed_periods} working hour periods for venue {venue.name}")
        else:
            logger.warning(f"No working hours processed for venue {venue.name}")
    
    def _parse_time(self, time_str: str) -> Optional[time]:
        """Parse Google time format (HHMM) to time object"""
        if not time_str or len(time_str) < 3:
            return None
        
        try:
            hour = int(time_str[:2])
            minute = int(time_str[2:4]) if len(time_str) >= 4 else 0
            return time(hour=hour, minute=minute)
        except (ValueError, TypeError):
            return None
    
    def _process_photos(self, venue: Venue, photos: List[Dict]):
        """Process venue photos"""
        if not photos:
            logger.warning(f"No photos data for venue {venue.name}")
            return
            
        processed_photos = 0
        for i, photo in enumerate(photos[:5]):  # Max 5 photos
            try:
                photo_name = photo.get("name")
                if not photo_name:
                    logger.debug(f"Photo {i} missing name for venue {venue.name}")
                    continue
                
                # Extract photo ID from the full path
                if '/' in photo_name:
                    photo_id = photo_name.split('/')[-1]
                else:
                    photo_id = photo_name
                
                # Download photo
                photo_content = self._download_photo(photo_id)
                if not photo_content:
                    logger.warning(f"Failed to download photo {photo_id} for venue {venue.name}")
                    continue
                
                # Create image record
                parsing_id = f"google_photo_{venue.parsing_id}_{photo_id}"
                
                image_obj, _ = VenueImage.objects.get_or_create(
                    venue=venue,
                    parsing_id=parsing_id,
                    defaults={
                        "order": i + 1,
                        "is_main": (i == 0)
                    }
                )
                
                # Save image file
                image_obj.image.save(photo_content.name, photo_content, save=True)
                processed_photos += 1
                
                # Set as background image if it's the first photo
                if i == 0 and not venue.background_image:
                    venue.background_image = image_obj
                    venue.save(update_fields=["background_image"])
                    logger.info(f"Set background image for venue {venue.name}")
                    
            except Exception as e:
                logger.error(f"Failed to process photo {i} for venue {venue.name}: {e}")
                continue
        
        if processed_photos > 0:
            logger.info(f"Processed {processed_photos} photos for venue {venue.name}")
        else:
            logger.warning(f"No photos processed for venue {venue.name}")
    
    def _download_photo(self, photo_name: str) -> Optional[ContentFile]:
        """Download photo using Google Places API"""
        try:
            # photo_name format: places/ChIJ.../photos/ATKogp...
            # We need to extract the photo ID correctly
            if '/' in photo_name:
                photo_id = photo_name.split('/')[-1]
            else:
                photo_id = photo_name
                
            # The correct URL format for Google Places API v1 photos
            # Try different URL formats as the API might require different approaches
            urls_to_try = [
                f"{self.BASE_URL}/places/{photo_id}/media",
                f"{self.BASE_URL}/places/{photo_id}/photos",
                f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={photo_id}&key={self.api_key}"
            ]
            
            for url in urls_to_try:
                try:
                    if "maps.googleapis.com" in url:
                        # Legacy API format
                        response = requests.get(url, timeout=30)
                    else:
                        # New API format
                        params = {
                            "maxWidthPx": 800,
                            "key": self.api_key
                        }
                        response = requests.get(url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        break
                except Exception:
                    continue
            else:
                logger.warning(f"All photo URL formats failed for {photo_id}")
                return None
            
            # Log response for debugging
            if response.status_code != 200:
                logger.warning(f"Photo download failed for {photo_id}: {response.status_code} - {response.text}")
                return None
                
            response.raise_for_status()
            
            filename = f"google_photo_{photo_id}.jpg"
            return ContentFile(response.content, name=filename)
            
        except Exception as e:
            logger.warning(f"Failed to download photo {photo_name}: {e}")
            return None
    
    def _process_social_media(self, venue: Venue, website: str):
        """Process venue social media/website"""
        VenueSocialMedia.objects.get_or_create(
            venue=venue,
            social_type='other',
            defaults={
                "link": website,
                "is_active": True
            }
        )
    
    def _process_reviews(self, venue: Venue, reviews: List[Dict]):
        """Process venue reviews"""
        for review_data in reviews:
            author_name = review_data.get("authorAttribution", {}).get("displayName", "Anonymous")[:100]
            review_text = review_data.get("text", {}).get("text", "")[:1000]
            review_rating = review_data.get("rating", 0)
            review_time = review_data.get("relativePublishTimeDescription", "")
            
            parsing_id = f"google_review_{venue.parsing_id}_{author_name}_{hash(review_time)}"
            
            VenueReview.objects.get_or_create(
                parsing_id=parsing_id,
                defaults={
                    "full_name": author_name,
                    "description": review_text,
                    "rating": review_rating,
                    "is_approved": True
                }
            )
    
    def _process_facilities(self, venue: Venue, business_features: Dict):
        """Process business features as facilities and attach to venue"""
        facilities = []
        
        # Map business features to facility names
        feature_mapping = {
            "serves_breakfast": "Breakfast",
            "serves_lunch": "Lunch", 
            "serves_dinner": "Dinner",
            "serves_coffee": "Coffee",
            "serves_dessert": "Dessert",
            "serves_cocktails": "Cocktails",
            "serves_beer": "Beer",
            "serves_wine": "Wine",
            "outdoor_seating": "Outdoor Seating",
            "live_music": "Live Music",
            "good_for_children": "Family Friendly",
            "good_for_groups": "Group Dining",
            "good_for_watching_sports": "Sports Viewing",
            "delivery": "Delivery",
            "reservable": "Reservations"
        }
        
        # Create or get facilities based on business features
        for feature_key, facility_name in feature_mapping.items():
            if business_features.get(feature_key, False):
                facility, _ = Facility.objects.get_or_create(
                    title=facility_name,
                    defaults={}
                )
                facilities.append(facility)
                
        # Attach facilities to venue
        if facilities:
            venue.facilities.add(*facilities)
            logger.info(f"Attached {len(facilities)} facilities to venue {venue.name}")


@app.task(bind=True, max_retries=3)
def sync_venues_from_google(self):
    """
    Synchronize venues from Google Places API v1 in Tashkent
    
    This task collects comprehensive restaurant data from Google Places API
    and saves it to the database with enhanced features and capabilities.
    """
    # Configuration
    api_key = getattr(settings, "VENUE_SYNC", {}).get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise RuntimeError("VENUE_SYNC.GOOGLE_PLACES_API_KEY is not configured")
    
    logger.info("Starting venue synchronization from Google Places API v1")
    
    try:
        # Initialize components
        client = GooglePlacesClient(api_key)
        processor = VenueDataProcessor()
        
        # Search for restaurants in Tashkent
        logger.info("Searching for restaurants in Tashkent...")
        search_results = client.search_restaurants_in_tashkent()
        logger.info(f"Found {len(search_results)} places to process")
        
        # Process each place
        processed_count = 0
        for i, place_item in enumerate(search_results, 1):
            try:
                # Get detailed information
                place_details = client.get_place_details(place_item.get("id"))
                if not place_details:
                    continue
                
                # Process venue data
                venue = processor.process_venue(place_details)
                if venue:
                    processed_count += 1
                
                logger.info(f"Processed {i}/{len(search_results)}: {venue.name if venue else 'Failed'}")
                
                # Rate limiting
                time_module.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Failed to process place {i}: {e}")
                continue
        
        logger.info(f"Venue synchronization completed successfully. Processed {processed_count} venues at {now()}")
        
    except Exception as e:
        logger.error(f"Venue synchronization failed: {e}")
        raise
