from rest_framework import serializers

from apps.common.models import Facility
from apps.venues.models import Venue, Company, VenueImage, VenueWorkingHour, VenueSocialMedia, VenueCategory

class VenueDetailCompanySerializer(serializers.ModelSerializer):
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


class VenueDetailImageSerializer(serializers.ModelSerializer):
    image_small = serializers.SerializerMethodField()
    
    class Meta:
        model = VenueImage
        fields = (
            'image_small',
        )

    def get_image_small(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.thumbnail['200x200'].url)
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation['image_small']


class VenueDetailFacilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Facility
        fields = (
            'title',
            )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation['title']

class VenueDetailWorkingHourSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueWorkingHour
        fields = (
            'weekday',
            'opening_time',
            'closing_time',
        )

class VenueDetailSocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueSocialMedia    
        fields = (
            'id',
            'social_type',
            'link',
        )

class VenueDetailVenueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueCategory
        fields = (
            'id',
            'title',
            'category_type'
        )


class VenueDetailSerializer(serializers.ModelSerializer):
    company = VenueDetailCompanySerializer()
    background_image_large = serializers.SerializerMethodField()
    images = VenueDetailImageSerializer(many=True)
    facilities = VenueDetailFacilitySerializer(many=True)
    social_links = VenueDetailSocialMediaSerializer(many=True)
    reviews_count = serializers.IntegerField(read_only=True)
    working_hours = VenueDetailWorkingHourSerializer(many=True)
    is_favourite = serializers.SerializerMethodField()
    categories = VenueDetailVenueCategorySerializer(many=True)
    
    class Meta:
        model = Venue
        fields = (
            'id',
            'name',
            'company',
            'background_image_large',
            'description',
            'location',
            'longitude',
            'latitude',
            'rating',
            'reviews_count',
            'facilities',
            'categories',
            'working_hours',
            'images',
            'social_links',
            'is_favourite',
        )

    def get_background_image_large(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'background_image') and obj.background_image.image:
            return request.build_absolute_uri(obj.background_image.image.thumbnail['500x500'].url)
        return None
        
    def get_is_favourite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_venue_favourites.filter(user=request.user).exists()
        return False
        
        
    