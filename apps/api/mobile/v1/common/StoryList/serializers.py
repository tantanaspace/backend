from rest_framework import serializers

from apps.common.models import StoryGroup


class StoryListSerializer(serializers.ModelSerializer):
    background_image_small = serializers.SerializerMethodField()

    class Meta:
        model = StoryGroup
        fields = (
            "id",
            "title",
            "background_image_small",
        )

    def get_background_image_small(self, obj):
        request = self.context.get("request")
        if obj.background_image:
            return request.build_absolute_uri(
                obj.background_image.thumbnail["100x100"].url
            )
        return None
