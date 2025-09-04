from rest_framework import serializers

from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

class RegistrationSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    session = serializers.CharField(max_length=255, required=True)
    full_name = serializers.CharField(max_length=255, required=True)
    date_of_birth = serializers.DateField(required=True)
    password = serializers.CharField(max_length=255, required=True, validators=[validate_password])


class RegistrationUserInfoSerializer(serializers.ModelSerializer):
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