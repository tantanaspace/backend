from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.api.shared.v1.users.Auth.RequestOTP.serializers import (
    RequestOTPSerializer,
    UserAction,
)
from apps.common.services.eskiz import eskiz_interface, send_sms
from utils.generators import CacheType, CodeType, generate_cache_key, generate_code


class RequestOTPAPIView(GenericAPIView):
    serializer_class = RequestOTPSerializer
    SESSION_EXPIRATION_TIME = 2

    cache_type_map = {
        UserAction.REGISTRATION: CacheType.REGISTRATION_SEND_OTP,
        UserAction.FORGOT_PASSWORD: CacheType.FORGOT_PASSWORD_SEND_OTP,
        UserAction.CHANGE_PHONE_NUMBER: CacheType.CHANGE_PHONE_NUMBER_SEND_OTP,
    }

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data["phone_number"]
        action = serializer.validated_data["action"]
        user_exists = (
            get_user_model().objects.filter(phone_number=phone_number).exists()
        )

        if (
            action == UserAction.REGISTRATION and user_exists
        ) or action == UserAction.LOGIN:
            response_data = {
                "phone_number": str(phone_number),
                "action": UserAction.LOGIN,
                "session": None,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        if action == UserAction.FORGOT_PASSWORD and not user_exists:
            response_data = {
                "phone_number": str(phone_number),
                "action": UserAction.REGISTRATION,
                "session": None,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        if action == UserAction.CHANGE_PHONE_NUMBER and user_exists:
            response_data = {
                "phone_number": str(phone_number),
                "action": UserAction.LOGIN,
                "session": None,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        existing_cache_key = generate_cache_key(
            self.cache_type_map[action], str(phone_number)
        )
        existing_cache_data = cache.keys(f"{existing_cache_key}*")

        if existing_cache_data:
            raise ValidationError(
                {"phone_number": "You can request only once 2 minute."}, code="cooldown"
            )

        code = generate_code(length=4, code_type=CodeType.NUMERIC)
        session = generate_code(length=32, code_type=CodeType.ALPHANUMERIC)

        cache_key = generate_cache_key(
            self.cache_type_map[action], str(phone_number), session
        )
        cache.set(cache_key, code, timeout=self.SESSION_EXPIRATION_TIME * 60)

        is_sent = send_sms(phone_number, eskiz_interface.confirmation_sms_message(code))
        if not is_sent:
            cache.delete(cache_key)
            raise ValidationError(
                {"phone_number": "Failed to send SMS. Please try again."},
                code="sms_failed",
            )

        response_data = {
            "phone_number": str(phone_number),
            "action": action,
            "session": session,
        }

        return Response(response_data, status=status.HTTP_200_OK)


__all__ = ["RequestOTPAPIView"]
