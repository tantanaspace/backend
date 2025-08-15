from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from apps.users.models import User
from apps.users.services.validators import validate_international_phonenumber
from apps.users.services.utils import OTPUtils
from apps.users.services.choices import SendOTPType


class UserRegistrationSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        validators=[validate_international_phonenumber],
        write_only=True,
        help_text="Phone number that was verified with OTP"
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text="Password (minimum 8 characters)"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        help_text="Password confirmation"
    )
    session = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Session from OTP verification"
    )

    class Meta:
        model = User
        fields = (
            "phone_number",
            "password",
            "password2",
            "full_name",
            "date_of_birth",
            "gender",
            "language",
            "session"
        )

    def validate(self, data):
        # Check if passwords match
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError(
                _("Passwords do not match.")
            )

        # Hash the password
        data['password'] = make_password(password)

        # Remove password2 from data
        data.pop('password2', None)

        # Get session and phone number
        session = data.pop('session', None)
        phone_number = data.get('phone_number')

        # Verify OTP verification
        verified_cache_key = OTPUtils.generate_cache_key(SendOTPType.AUTH, phone_number)
        verification_data = cache.get(verified_cache_key)

        if not verification_data:
            raise serializers.ValidationError(
                _("Phone number is not verified. Please verify the phone number you want to register with.")
            )

        if isinstance(verification_data, bool):
            verification_data = {
                "verified": True,
                "session": session,
                "verified_at": "now"
            }
            cache.set(verified_cache_key, verification_data, timeout=60 * 60)
        elif isinstance(verification_data, dict):
            stored_session = verification_data.get('session')

            if stored_session != session:
                raise serializers.ValidationError(
                    _("Invalid session for this phone number. The session must match the one used to verify this specific phone number.")
                )
        else:
            cache.delete(verified_cache_key)
            raise serializers.ValidationError(
                _("Invalid verification data format. Please verify your phone number again.")
            )

        return data

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')

        # Create the user
        user = User.objects.create(**validated_data)

        # Clean up verification cache
        verified_cache_key = OTPUtils.generate_cache_key(SendOTPType.AUTH, phone_number)
        cache.delete(verified_cache_key)

        otp_sent_key = OTPUtils.generate_cache_key(f"{SendOTPType.AUTH}_sent", phone_number)
        cache.delete(otp_sent_key)

        return user

    def to_representation(self, instance):
        """Return user data with tokens after registration"""
        data = super().to_representation(instance)

        # Add tokens
        tokens = instance.tokens
        data['tokens'] = tokens

        # Remove sensitive fields
        data.pop('password', None)
        data.pop('password2', None)
        data.pop('session', None)

        return data
