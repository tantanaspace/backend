import base64

from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny

from apps.api.shared.v1.users.Auth.ForgotPasswordReset.serializers import ForgotPasswordResetSerializer
from utils.generators import *


class ForgotPasswordResetAPIView(GenericAPIView):
    serializer_class = ForgotPasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        session = serializer.validated_data['session']
        password = serializer.validated_data['password']

        # Find the cache key for this specific email and session
        cache_key = generate_cache_key(CacheType.FORGOT_PASSWORD, email, session)
        cache_data = cache.get(cache_key)
        
        if not cache_data:
            raise ValidationError(_("Session expired. Please send a new email."), code='session_expired')

        try:
            user = get_user_model().objects.get(pk=cache_data)
        except get_user_model().DoesNotExist:
            raise ValidationError(_("User not found or role mismatch."), code='user_not_found')

        # Clear cache
        cache.delete(cache_key)

        # Update password
        user.set_password(password)
        user.save(update_fields=['password'])

        return Response({
            'reset': True,
            'role': user.role
        })


__all__ = [
    'ForgotPasswordResetAPIView'
]
