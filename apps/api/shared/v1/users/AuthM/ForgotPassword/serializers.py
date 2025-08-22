from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from apps.users.models import User
from apps.users.services.validators import validate_international_phonenumber
from apps.users.services.utils import OTPUtils
from apps.users.services.choices import SendOTPType


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
        validators=[validate_international_phonenumber]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        help_text="New password (minimum 8 characters)"
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

    def validate(self, data):
        # Check if passwords match
        password = data.get('password')
        password2 = data.get('password2')

        if password != password2:
            raise serializers.ValidationError(
                _("Passwords do not match.")
            )

        # Validate password strength
        try:
            validate_password(password)
        except Exception as e:
            raise serializers.ValidationError(str(e))

        # Get session and phone number
        session = data.pop('session', None)
        phone_number = data.get('phone_number')

        # Verify OTP verification using existing OTP system
        verified_cache_key = OTPUtils.generate_cache_key(SendOTPType.FORGOT_PASSWORD, phone_number)
        verification_data = cache.get(verified_cache_key)

        if not verification_data:
            raise serializers.ValidationError(
                _("Phone number is not verified. Please verify the phone number first using the OTP verification endpoint.")
            )

        if isinstance(verification_data, dict):
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

    def save(self):
        phone_number = self.validated_data.get('phone_number')
        password = self.validated_data.get('password')

        # Get the user
        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                _("User not found with this phone number.")
            )

        # Update password
        user.password = make_password(password)
        user.save()

        # Clean up verification cache
        verified_cache_key = OTPUtils.generate_cache_key(SendOTPType.FORGOT_PASSWORD, phone_number)
        cache.delete(verified_cache_key)

        otp_sent_key = OTPUtils.generate_cache_key(f"{SendOTPType.FORGOT_PASSWORD}_sent", phone_number)
        cache.delete(otp_sent_key)

        return user
