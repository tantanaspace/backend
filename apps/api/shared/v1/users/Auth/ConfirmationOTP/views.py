from django.core.cache import cache

from rest_framework.generics import GenericAPIView
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status


from apps.api.shared.v1.users.Auth.ConfirmationOTP.serializers import ConfirmationOTPSerializer, UserAction
from utils.generators import generate_cache_key, CacheType, generate_code, CodeType



class ConfirmationOTPAPIView(GenericAPIView):
    serializer_class = ConfirmationOTPSerializer
    cache_type_map = {
        UserAction.REGISTRATION: CacheType.REGISTRATION_SEND_OTP,
        UserAction.FORGOT_PASSWORD: CacheType.FORGOT_PASSWORD_SEND_OTP,
        UserAction.CHANGE_PHONE_NUMBER: CacheType.CHANGE_PHONE_NUMBER_SEND_OTP,
    }
    cache_type_map_confirmed = {
        UserAction.REGISTRATION: CacheType.CONFIRMED_REGISTRATION_SEND_OTP,
        UserAction.FORGOT_PASSWORD: CacheType.CONFIRMED_FORGOT_PASSWORD_SEND_OTP,
        UserAction.CHANGE_PHONE_NUMBER: CacheType.CONFIRMED_CHANGE_PHONE_NUMBER_SEND_OTP,
    }
    SESSION_EXPIRATION_TIME = 2

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        session = serializer.validated_data["session"]
        otp_code = serializer.validated_data["otp_code"]
        action = serializer.validated_data["action"]

        cache_key = generate_cache_key(self.cache_type_map[action], str(phone_number), session)
        cached_otp = cache.get(cache_key)

        if not cached_otp or cached_otp != otp_code:
            raise serializers.ValidationError("OTP code has expired or is invalid.")

        cache.delete(cache_key)

        session_confirmed = generate_code(length=32, code_type=CodeType.ALPHANUMERIC)

        cache_key_confirmed = generate_cache_key(self.cache_type_map_confirmed[action], str(phone_number), session_confirmed)
        cache.set(cache_key_confirmed, True, timeout=self.SESSION_EXPIRATION_TIME * 60)


        response_data = {
            "phone_number": str(phone_number),
            "action": action,
            "session": session_confirmed,
        }

        return Response(response_data, status=status.HTTP_200_OK)

__all__ = [
    'ConfirmationOTPAPIView'
]