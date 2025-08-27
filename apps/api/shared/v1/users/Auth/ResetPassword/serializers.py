from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    session = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=255, required=True, validators=[validate_password])