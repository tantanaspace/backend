from rest_framework import serializers

from apps.venues.models import VenueCategory


class VenueCategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueCategory
        fields = (
            "id",
            "title",
            "category_type",
        )
