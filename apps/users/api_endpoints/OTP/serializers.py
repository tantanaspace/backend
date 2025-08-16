from rest_framework import serializers

from apps.users.services.choices import SendOTPType
from apps.users.services.utils import OTPUtils, SendSMSService
from apps.users.services.validators import validate_international_phonenumber
from django.core.cache import cache


class CheckOTPSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=SendOTPType.choices, required=True)
    phone_number = serializers.CharField(max_length=15, required=True, validators=[validate_international_phonenumber])
    session = serializers.CharField(max_length=255, required=True)
    otp_code = serializers.CharField(max_length=6, required=True)

    def create(self, validated_data):
        phone_number = validated_data["phone_number"]
        otp_type = validated_data["type"]
        session = validated_data["session"]
        otp_code = validated_data["otp_code"]

        session_cache_key = OTPUtils.generate_cache_key(otp_type, phone_number, session)
        cached_otp = cache.get(session_cache_key)

        if not cached_otp:
            raise serializers.ValidationError("OTP code has expired or is invalid.")
        if cached_otp != otp_code:
            raise serializers.ValidationError("Invalid OTP code.")

        cache.delete(session_cache_key)

        verified_key = OTPUtils.generate_cache_key(otp_type, phone_number)
        verification_data = {
            "verified": True,
            "session": session,
            "verified_at": "now"
        }
        cache.set(verified_key, verification_data, timeout=3600)

        return validated_data


class SendSMSSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=SendOTPType.choices, required=True)
    phone_number = serializers.CharField(max_length=15, required=True, validators=[validate_international_phonenumber])
    session = serializers.CharField(max_length=255, read_only=True)

    def create(self, validated_data):
        request = self.context.get('request')
        phone_number = validated_data["phone_number"]
        otp_type = validated_data["type"]

        data = {}
        service = SendSMSService(phone_number, otp_type, **data)
        validated_data["session"] = service.send_sms()
        return validated_data
