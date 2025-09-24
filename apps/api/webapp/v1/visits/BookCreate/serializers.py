from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.visits.models import Visit


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = (
            "id",
            "booked_date",
            "booked_time",
            "user_full_name",
            "user_phone_number",
            "number_of_guests",
            "zone",
            "table_number",
            "status",
        )
        read_only_fields = (
            "id",
            "status",
        )

    def create(self, validated_data):
        try:
            user = get_user_model().objects.get(
                phone_number=validated_data["user_phone_number"]
            )
        except get_user_model().DoesNotExist:
            user = None

        validated_data["user"] = user
        return super().create(validated_data)
