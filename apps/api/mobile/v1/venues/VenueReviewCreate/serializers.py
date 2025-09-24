from rest_framework import serializers

from apps.venues.models import VenueReview


class VenueReviewCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(), write_only=True
    )

    class Meta:
        model = VenueReview
        fields = (
            "user",
            "venue",
            "description",
            "rating",
        )

    def create(self, validated_data):
        validated_data["full_name"] = self.context["request"].user.full_name
        return super().create(validated_data)
