from rest_framework import serializers

from apps.common.models import Facility, Tag
from apps.venues.models import Venue, Company, VenueImage, VenueWorkingHour, VenueSocialMedia

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
            'id',
            'image_small',
        )

    def get_image_small(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.thumbnail['200x200'].url)
        return None


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
            'id',
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


class VenueDetailSerializer(serializers.ModelSerializer):
    company = VenueDetailCompanySerializer()
    background_image_large = serializers.SerializerMethodField()
    images = VenueDetailImageSerializer(many=True)
    facilities = VenueDetailFacilitySerializer(many=True)
    social_links = VenueDetailSocialMediaSerializer(many=True)
    reviews_count = serializers.IntegerField(read_only=True)
    working_hours = VenueDetailWorkingHourSerializer(many=True)
    
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
            'working_hours',
            'images',
            'social_links',
        )

    def get_background_image_large(self, obj):
        request = self.context.get('request')
        if hasattr(obj, 'background_image') and obj.background_image.image:
            return request.build_absolute_uri(obj.background_image.image.thumbnail['500x500'].url)
        return None
        
        
    