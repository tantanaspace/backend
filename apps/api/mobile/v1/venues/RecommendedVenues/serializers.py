from rest_framework import serializers

from apps.venues.models import Venue, VenueCategory


class RecommendedVenuesVenueSerializer(serializers.ModelSerializer):
    background_image_large = serializers.SerializerMethodField()
    is_favourite = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = (
            "id",
            "name",
            "background_image_large",
            "location",
            "is_favourite",
        )

    def get_background_image_large(self, obj):
        request = self.context.get("request")
        if obj.background_image:
            return request.build_absolute_uri(
                obj.background_image.image.thumbnail["500x500"].url
            )
        return None

    def get_is_favourite(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.user_venue_favourites.filter(user=request.user).exists()
        return False


class RecommendedVenuesSerializer(serializers.ModelSerializer):
    venues = RecommendedVenuesVenueSerializer(source="recommended_venues", many=True)

    class Meta:
        model = VenueCategory
        fields = ("id", "title", "venues")
