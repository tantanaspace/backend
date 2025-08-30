import uuid
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
    
    def __init__(self):
        self.api_key = getattr(settings, "VENUE_SYNC", {}).get("GOOGLE_PLACES_API_KEY")
        self.headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id"
        }

        if not self.api_key:
            raise RuntimeError("VENUE_SYNC.GOOGLE_PLACES_API_KEY is not configured")
    
    def search_restaurants_in_tashkent(self) -> List[Dict]:
        """Search for restaurants in Tashkent using multiple strategies"""
        all_results = []
        seen_ids = set()
        
        # Strategy 1: Nearby search from Tashkent center
        nearby_results = self._nearby_search()
        
        for result in nearby_results:
            place_id = result.get("id")
            if place_id:
                seen_ids.add(place_id)
                all_results.append(result)
        
        # Strategy 2: Text search with different queries
        text_results = self._text_search()
        
        for result in text_results:
            place_id = result.get("id")
            if place_id:
                seen_ids.add(place_id)
                all_results.append(result)
        
        
        # Log search summary
        self._log_search_summary(all_results, seen_ids)
        
        return all_results
    
    
    def _nearby_search(self) -> List[Dict]:
        """Search for places near coordinates"""
        results = []
        tashkent_grid_coordinates = {
            "northwest": (41.3700, 69.1700),
            "north":     (41.3700, 69.2400),
            "northeast": (41.3700, 69.3200),
            
            "west":      (41.3000, 69.1700),
            "center":    (41.3000, 69.2400),
            "east":      (41.3000, 69.3200),
            
            "southwest": (41.2300, 69.1700),
            "south":     (41.2300, 69.2400),
            "southeast": (41.2300, 69.3200),
        }
        place_types = [
            'acai_shop', 'afghani_restaurant', 'african_restaurant', 'american_restaurant', 'asian_restaurant',
            'bagel_shop', 'bakery', 'bar', 'bar_and_grill', 'barbecue_restaurant', 'brazilian_restaurant', 'breakfast_restaurant',
            'bakery', 'bar', 'bar_and_grill', 'barbecue_restaurant', 'brazilian_restaurant', 'breakfast_restaurant', 'brunch_restaurant',
            'buffet_restaurant', 'cafe', 'cafeteria', 'candy_store', 'cat_cafe', 'chinese_restaurant', 'chocolate_factory', 'chocolate_shop', 
            'coffee_shop', 'confectionery', 'deli', 'dessert_restaurant', 'dessert_shop', 'diner', 'dog_cafe', 'donut_shop',
            'fast_food_restaurant', 'fine_dining_restaurant', 'food_court', 'french_restaurant', 'greek_restaurant', 'hamburger_restaurant', 
            'ice_cream_shop', 'indian_restaurant', 'indonesian_restaurant', 'italian_restaurant', 'japanese_restaurant', 'juice_shop',
            'korean_restaurant', 'lebanese_restaurant', 'meal_delivery', 'meal_takeaway', 'mediterranean_restaurant', 'mexican_restaurant',
            'middle_eastern_restaurant', 'pizza_restaurant', 'pub', 'ramen_restaurant', 'restaurant', 'sandwich_shop', 'seafood_restaurant',
            'spanish_restaurant', 'steak_house', 'sushi_restaurant', 'tea_house', 'thai_restaurant', 'turkish_restaurant', 'vegan_restaurant',
            'vegetarian_restaurant', 'vietnamese_restaurant', 'wine_bar',
        ]
        place_types = ['cafe']
        
        for coordinate in tashkent_grid_coordinates:
            for place_type in place_types:
                url = f"{self.BASE_URL}/places:searchNearby"
                payload = {
                    "locationRestriction": {
                        "circle": {
                            "center": {"latitude": tashkent_grid_coordinates[coordinate][0], "longitude": tashkent_grid_coordinates[coordinate][1]},
                            "radius": 7000.0
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
    
    def _text_search(self) -> List[Dict]:
        """Text search for places"""
        results = []
        search_queries = [
            # General
            "restaurants in Tashkent", "cafes in Tashkent", "bars in Tashkent", "coffee shops in Tashkent",
            "fast food in Tashkent", "street food in Tashkent", "food courts in Tashkent",
            "bakeries in Tashkent", "confectionery shops in Tashkent", "dessert shops in Tashkent",
            "ice cream shops in Tashkent", "juice shops in Tashkent", "tea houses in Tashkent",

            # National cuisines
            "uzbek restaurants in Tashkent", "turkish restaurants in Tashkent", "korean restaurants in Tashkent",
            "japanese restaurants in Tashkent", "chinese restaurants in Tashkent", "italian restaurants in Tashkent",
            "indian restaurants in Tashkent", "french restaurants in Tashkent", "american restaurants in Tashkent",
            "mediterranean restaurants in Tashkent", "middle eastern restaurants in Tashkent",
            "barbecue restaurants in Tashkent", "steak houses in Tashkent", "sushi restaurants in Tashkent",
            "vegan restaurants in Tashkent", "vegetarian restaurants in Tashkent",

            # Districts
            "restaurants in Chilonzor Tashkent", "cafes in Chilonzor Tashkent",
            "restaurants in Yunusobod Tashkent", "cafes in Yunusobod Tashkent",
            "restaurants in Mirzo Ulugbek Tashkent", "cafes in Mirzo Ulugbek Tashkent",
            "restaurants in Shaykhantahur Tashkent", "cafes in Shaykhantahur Tashkent",
            "restaurants in Yakkasaroy Tashkent", "cafes in Yakkasaroy Tashkent",
            "restaurants in Sergeli Tashkent", "cafes in Sergeli Tashkent",
            "restaurants in Bektemir Tashkent", "cafes in Bektemir Tashkent",
            "restaurants in Olmazor Tashkent", "cafes in Olmazor Tashkent",

            # Popular places
            "restaurants near Tashkent airport", "cafes near Tashkent airport",
            "restaurants near Tashkent railway station", "cafes near Tashkent railway station",
            "restaurants near Magic City Tashkent", "cafes near Magic City Tashkent",
            "restaurants near Samarkand Darvoza mall Tashkent", "cafes near Samarkand Darvoza mall Tashkent",
            "restaurants near Next mall Tashkent", "cafes near Next mall Tashkent",
            "restaurants near Compass mall Tashkent", "cafes near Compass mall Tashkent",
            "restaurants near Tashkent City Park", "cafes near Tashkent City Park",
            "restaurants near Chorsu Bazaar Tashkent", "cafes near Chorsu Bazaar Tashkent",
            "restaurants near Amir Temur Square Tashkent", "cafes near Amir Temur Square Tashkent"
        ]

        for search_query in search_queries:
            url = f"{self.BASE_URL}/places:searchText"
            payload = {
                "textQuery": search_query,
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
                    results.extend(data["places"])
                    logger.info(f"Found {len(data['places'])} places for query '{search_query}'")
                
                time_module.sleep(0.5)  # Rate limiting
            except Exception as e:
                logger.warning(f"Text search failed for query '{search_query}': {e}")
                continue
            
        logger.info(f"Text search completed: found {len(results)} total places")
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
            "X-Goog-FieldMask": "id,displayName,formattedAddress,rating,websiteUri,location,servesBreakfast,servesLunch,servesDinner,servesCoffee,servesDessert,servesCocktails,servesBeer,servesWine,outdoorSeating,liveMusic,goodForChildren,goodForGroups,goodForWatchingSports,delivery,reservable,primaryType,types,primaryTypeDisplayName,regularOpeningHours,editorialSummary,reviews,photos"
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
        url = f"{self.BASE_URL}/{photo_name}/media"
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

google_places_client = GooglePlacesClient()

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
            name = place_data.get("displayName", {}).get("text", "Unnamed")[:250]
            address = place_data.get("formattedAddress", "Unknown address")[:250]
            rating = place_data.get("rating", 0.0)
            website = place_data.get("websiteUri", "")
            
            # Extract coordinates
            location = place_data.get("location", {})
            lat = location.get("latitude", 0.0)
            lng = location.get("longitude", 0.0)
                        
            # Create or update venue
            venue, _ = Venue.objects.update_or_create(
                parsing_id=place_data.get("id"),
                defaults={
                    "company": self.default_company,
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

            # Process facilities
            self._process_facilities(venue, place_data)
            
            # Process working hours
            self._process_working_hours(venue, place_data.get("regularOpeningHours", {}))
            
            # Process social media
            if website:
                self._process_social_media(venue, website)

            # Process photos
            self._process_photos(venue, place_data.get("photos", []))
            
            # Process reviews
            self._process_reviews(venue, place_data.get("reviews", []))
            
            return venue
            
        except Exception as e:
            logger.error(f"Failed to process venue: {e}")
            return None
    
    
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
                
        # Editorial summary
        editorial_summary = place_data.get("editorialSummary", {}).get("text", "")
        if editorial_summary:
            description_parts.append(f"About: {editorial_summary}")
        
        return " | ".join(description_parts)[:500]
    
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
                category_title = slugify(primary_type).replace("-", " ").replace("_", " ").title()
                parsing_id = f"google_category_{primary_type.strip().lower()}"
                
                category, _ = VenueCategory.objects.get_or_create(
                    parsing_id=parsing_id,
                    defaults={
                        "title": category_title
                    }
                )
                categories.append(category)
                logger.debug(f"Added primary category: {category_title}")
            
            # Primary type display name
            primary_type_display = place_data.get("primaryTypeDisplayName", {}).get("text")
            if primary_type_display:
                category_title = slugify(primary_type_display).replace("-", " ").replace("_", " ").title()
                parsing_id = f"google_category_{primary_type_display.strip().lower()}"
                
                category, _ = VenueCategory.objects.get_or_create(
                    parsing_id=parsing_id,
                    defaults={
                        "title": category_title
                    }
                )
                categories.append(category)
                logger.debug(f"Added display category: {category_title}")
            
            # Types from the types array
            types = place_data.get("types", [])
            for type_name in types:
            
                category_title = slugify(type_name).replace("-", " ").replace("_", " ").title()
                parsing_id = f"google_category_{type_name.strip().lower()}"
                
                category, _ = VenueCategory.objects.get_or_create(
                    parsing_id=parsing_id,
                    defaults={
                        "title": category_title
                    }
                )
                categories.append(category)
                logger.debug(f"Added type category: {category_title}")
            
            if categories:
                venue.categories.set(categories)
                logger.info(f"Set {len(categories)} categories for venue {venue.name}")
            else:
                logger.warning(f"No categories found for venue {venue.name}")
                
        except Exception as e:
            logger.error(f"Failed to process categories for venue {venue.name}: {e}")
            # Try to set at least one default category
            
    def _process_working_hours(self, venue: Venue, opening_hours: Dict):
        """Process venue working hours"""
        if not opening_hours:
            logger.warning(f"No opening hours data for venue {venue.name}")
            return
            
        periods = opening_hours.get("periods", [])
        if not periods:
            logger.warning(f"No periods data in opening hours for venue {venue.name}")
            return
        
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
            
            # Parse times using new API format
            open_time = self._parse_time(open_data)
            close_time = self._parse_time(close_data)
            
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
                except Exception as e:
                    logger.warning(f"Failed to create working hours for {venue.name} on {weekday}: {e}")
        
    def _parse_time(self, time_data: Dict) -> Optional[time]:
        """Parse Google Places API v1 time format with separate hour and minute fields"""
        if not time_data:
            return None
        
        try:
            hour = time_data.get("hour", 0)
            minute = time_data.get("minute", 0)
            
            # Validate hour and minute ranges
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                logger.warning(f"Invalid time values: hour={hour}, minute={minute}")
                return None
                
            return time(hour=hour, minute=minute)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse time data {time_data}: {e}")
            return None
    
    def _process_photos(self, venue: Venue, photos: List[Dict]):
        """Process venue photos"""
        if not photos:
            logger.warning(f"No photos data for venue {venue.name}")
            return
            
        for i, photo in enumerate(photos[:5]):  # Max 5 photos
            try:
                photo_name = photo.get("name")
                if not photo_name:
                    logger.debug(f"Photo {i} missing name for venue {venue.name}")
                    continue
                
                
                # Download photo
                photo_content = google_places_client.get_place_photo(photo_name)
                if not photo_content:
                    logger.warning(f"Failed to download photo {photo_name} for venue {venue.name}")
                    continue
                
                photo_id = photo_name.split('/')[-1]
                
                # Create image record
                parsing_id = f"google_photo_{venue.pk}_{photo_id}"
                
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
                
                # Set as background image if it's the first photo
                if not hasattr(venue, "background_image") or not venue.background_image:
                    venue.background_image = image_obj
                    venue.save(update_fields=["background_image"])
                    logger.info(f"Set background image for venue {venue.name}")
                    
            except Exception as e:
                logger.error(f"Failed to process photo {i} for venue {venue.name}: {e}")
                continue
    
    def _process_social_media(self, venue: Venue, website: str):
        """Process venue social media/website"""
        VenueSocialMedia.objects.get_or_create(
            venue=venue,
            social_type='other',
            defaults={
                "title": venue.name,
                "link": website,
            }
        )
    
    def _process_reviews(self, venue: Venue, reviews: List[Dict]):
        """Process venue reviews"""
        for review_data in reviews:
            review_id = review_data.get("name", f"/{uuid.uuid4()}").split("/")[-1]
            author_name = review_data.get("authorAttribution", {}).get("displayName", "Anonymous")[:100]
            review_text = review_data.get("text", {}).get("text", "")[:1000]
            review_rating = review_data.get("rating", 0)
            
            
            parsing_id = f"google_review_{venue.pk}_{review_id}"
            
            VenueReview.objects.get_or_create(
                venue=venue,
                parsing_id=parsing_id,
                defaults={
                    "full_name": author_name,
                    "description": review_text,
                    "rating": review_rating,
                    "is_approved": True
                }
            )
    
    def _process_facilities(self, venue: Venue, place_data: Dict):
        """Process business features as facilities and attach to venue"""
        # Extract business features
        business_features = self._extract_business_features(place_data)

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
            facility, _ = Facility.objects.get_or_create(
                title=facility_name,
                defaults={}
            )
            if business_features.get(feature_key, False):
                facilities.append(facility)
                
        # Attach facilities to venue
        if facilities:
            venue.facilities.add(*facilities)
            logger.info(f"Attached {len(facilities)} facilities to venue {venue.name}")

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


venue_data_processor = VenueDataProcessor()


@app.task(bind=True, max_retries=3)
def sync_venues_from_google(self):
    """
    Synchronize venues from Google Places API v1 in Tashkent
    
    This task collects comprehensive restaurant data from Google Places API
    and saves it to the database with enhanced features and capabilities.
    """    
    try:
        # Search for restaurants in Tashkent
        logger.info("Searching for restaurants in Tashkent...")
        search_results = google_places_client.search_restaurants_in_tashkent()
        logger.info(f"Found {len(search_results)} places to process")
        
        # Process each place
        processed_count = 0
        for i, place_item in enumerate(search_results, 1):
            try:
                # Get detailed information
                place_details = google_places_client.get_place_details(place_item.get("id"))
                if not place_details:
                    continue
                
                # Process venue data
                venue = venue_data_processor.process_venue(place_details)
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
