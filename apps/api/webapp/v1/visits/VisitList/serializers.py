from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.venues.models import VenueZone
from apps.visits.models import Visit


class VisitListZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueZone
        fields = (
            "id",
            "name",
        )


class VisitListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "full_name", "avatar")


class VisitListSerializer(serializers.ModelSerializer):
    user = VisitListUserSerializer(read_only=True)
    zone = VisitListZoneSerializer(read_only=True)

    class Meta:
        model = Visit
        fields = (
            "id",
            "user",
            "zone",
            "booked_date",
            "booked_time",
            "number_of_guests",
            "status",
        )
