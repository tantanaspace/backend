from django.contrib.auth import get_user_model
from rest_framework import serializers



class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "phone_number",
            "full_name",
            "date_of_birth",
            "role",
            "gender",
            "language",
            "avatar",
            "date_joined",
            "is_notification_enabled",
        )
        read_only_fields = fields 