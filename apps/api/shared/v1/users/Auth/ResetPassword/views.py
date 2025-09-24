from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.api.shared.v1.users.Auth.ResetPassword.serializers import (
    ResetPasswordSerializer,
)
from utils.generators import CacheType, generate_cache_key


class ResetPasswordAPIView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        session = serializer.validated_data["session"]
        password = serializer.validated_data["password"]

        cache_key = generate_cache_key(
            CacheType.CONFIRMED_FORGOT_PASSWORD_SEND_OTP, str(phone_number), session
        )
        if not cache.get(cache_key):
            raise serializers.ValidationError(
                "Invalid reset password session or expired."
            )

        cache.delete(cache_key)

        user = get_user_model().objects.get(phone_number=phone_number)
        user.set_password(password)
        user.save()

        return Response({"success": True}, status=status.HTTP_200_OK)


__all__ = ["ResetPasswordAPIView"]
