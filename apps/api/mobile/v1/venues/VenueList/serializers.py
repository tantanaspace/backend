from rest_framework import serializers

from apps.venues.models import Venue, Company

class MapVenueListCompanySerializer(serializers.ModelSerializer):
    logo_small = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            'id',
            'name',
            'logo_small',
        )
        
    def get_logo_small(self, obj):
        request = self.context.get('request')
        if obj.logo:
            return request.build_absolute_uri(obj.logo.thumbnail['100x100'].url)
        return None


class MapVenueListSerializer(serializers.ModelSerializer):
    company = MapVenueListCompanySerializer()
    
    class Meta:
        model = Venue
        fields = (
            'id',
            'name',
            'company',
            'longitude',
            'latitude',
            'rating',
        )

# ------------------------------------------------ #


class VenueListCompanySerializer(serializers.ModelSerializer):
    logo_small = serializers.SerializerMethodField()
    
    class Meta:
        model = Company
        fields = (
            'id',
            'name',
            'logo_small',
        )
    
    def get_logo_small(self, obj):
        request = self.context.get('request')
        if obj.logo:
            return request.build_absolute_uri(obj.logo.thumbnail['100x100'].url)
        return None
    

class VenueListSerializer(serializers.ModelSerializer):
    company = VenueListCompanySerializer()
    background_image_medium = serializers.SerializerMethodField()
    
    class Meta:
        model = Venue
        fields = (
            'id',
            'name',
            'company',
            'background_image_medium',
            'location',
            'rating',
        )
        
    def get_background_image_medium(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'background_image') and obj.background_image.image:
            return request.build_absolute_uri(obj.background_image.image.thumbnail['300x300'].url)
        return None
    

__all__ = [
    'MapVenueListSerializer',
    'VenueListSerializer',
]