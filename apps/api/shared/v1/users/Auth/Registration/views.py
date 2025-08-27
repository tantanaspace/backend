from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from apps.api.shared.v1.users.Auth.Registration.serializers import RegistrationSerializer
from utils.generators import generate_cache_key, CacheType


class RegistrationAPIView(GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        phone_number = serializer.validated_data["phone_number"]
        session = serializer.validated_data["session"]
        full_name = serializer.validated_data["full_name"]
        date_of_birth = serializer.validated_data["date_of_birth"]
        password = serializer.validated_data["password"]

        cache_key = generate_cache_key(CacheType.CONFIRMED_REGISTRATION_SEND_OTP, str(phone_number), session)
        if not cache.get(cache_key):
            raise serializers.ValidationError("Invalid registration session or expired.")

        cache.delete(cache_key)

        user = get_user_model().objects.create(
            phone_number=phone_number,
            full_name=full_name,
            date_of_birth=date_of_birth,
            role=get_user_model().Role.USER,
            is_notification_enabled=True,
        )

        user.set_password(password)
        user.save()

        return Response({"success": True}, status=status.HTTP_201_CREATED)

__all__ = [
    'RegistrationAPIView'
]