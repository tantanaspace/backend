from django.core.cache import cache

from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from utils.generators import generate_cache_key, CacheType
from apps.api.shared.v1.users.Auth.ChangePhoneNumber.serializers import ChangePhoneNumberSerializer

class ChangePhoneNumberAPIView(GenericAPIView):
    serializer_class = ChangePhoneNumberSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data["phone_number"]
        session = serializer.validated_data["session"]
        
        cache_key = generate_cache_key(CacheType.CONFIRMED_CHANGE_PHONE_NUMBER_SEND_OTP, str(phone_number), session)
        if not cache.get(cache_key):
            raise ValidationError("Invalid change phone number session or expired.")

        cache.delete(cache_key)
        
        user = request.user
        user.phone_number = phone_number
        user.save(update_fields=["phone_number"])
        
        return Response({"success": True}, status=status.HTTP_200_OK) 

__all__ = [
    'ChangePhoneNumberAPIView'
]