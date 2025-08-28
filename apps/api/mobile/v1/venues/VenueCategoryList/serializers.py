from rest_framework import serializers

from apps.venues.models import VenueCategory


class VenueCategoryListSerializer(serializers.ModelSerializer):
    icon_small = serializers.SerializerMethodField()
    
    class Meta:
        model = VenueCategory
        fields = (
            'id',
            'title',
            'icon_small',
        )
        
    def get_icon_small(self, obj):
        request = self.context.get('request')
        if obj.icon:
            return request.build_absolute_uri(obj.icon.thumbnail['200x200'].url)
        return None