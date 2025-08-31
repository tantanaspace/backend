from rest_framework import serializers
from apps.common.models import StoryItem
from apps.venues.models import Venue, Company, VenueCategory

class StoryDetailVenueCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueCategory
        fields = (
            'id',
            'title',
            'category_type'
        )

class StoryDetailCompanySerializer(serializers.ModelSerializer):
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

class StoryDetailVenueSerializer(serializers.ModelSerializer):
    company = StoryDetailCompanySerializer()
    categories = StoryDetailVenueCategorySerializer(many=True)

    class Meta:
        model = Venue
        fields = (
            'id',
            'name',
            'rating',
            'company',
            'categories'
        )

class StoryDetailSerializer(serializers.ModelSerializer):
    venue = StoryDetailVenueSerializer()
    
    class Meta:
        model = StoryItem
        fields = (
            'id',
            'media',
            'venue',
            'description',
            'link',
        )