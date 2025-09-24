from rest_framework import serializers

from apps.venues.models import VenueReview


class VenueReviewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueReview
        fields = (
            "id",
            "full_name",
            "description",
            "rating",
            "created_at",
        )
