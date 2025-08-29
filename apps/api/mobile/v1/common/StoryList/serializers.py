from rest_framework import serializers
from apps.common.models import Story


class StoryListSerializer(serializers.ModelSerializer):
    background_image_small = serializers.SerializerMethodField()
    
    class Meta:
        model = Story
        fields = (
            'id',
            'background_image_small',
        )
        
    def get_background_image_small(self, obj):
        request = self.context.get('request')
        if obj.background_image:
            return request.build_absolute_uri(obj.background_image.image.thumbnail['100x100'].url)
        return None
        