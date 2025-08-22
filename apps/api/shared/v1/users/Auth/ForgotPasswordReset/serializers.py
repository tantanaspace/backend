import base64
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from rest_framework import serializers


class ForgotPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    session = serializers.CharField()
    password = serializers.CharField(min_length=8)

    def validate_password(self, value):
        """
        Checks that the password meets standard security requirements.
        """
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return value

    def validate_session(self, value):
        try:
            value = base64.b64decode(value).decode()
        except Exception:
            raise serializers.ValidationError({'session': _('Invalid session')}, code='invalid')
        return value