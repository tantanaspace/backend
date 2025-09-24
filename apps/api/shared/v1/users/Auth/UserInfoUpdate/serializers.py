from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "full_name",
            "date_of_birth",
            "gender",
            "avatar",
            "is_notification_enabled",
            "language",
        )
