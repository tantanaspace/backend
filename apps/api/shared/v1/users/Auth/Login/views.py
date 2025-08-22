from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import AuthenticationFailed

from apps.api.shared.v1.users.Auth.Login.serializers import LoginSerializer


class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )

        if user is None:
            raise AuthenticationFailed(_('Invalid email or password.'))

        return Response({
            "access_token": user.tokens["access_token"],
            "refresh_token": user.tokens["refresh_token"],
            "user": {
                "email": user.email,
                "phone_number": str(user.phone_number),
                "role": user.role,
                "language": user.language
            }
        }, status=status.HTTP_200_OK)


__all__ = [
    'LoginAPIView'
]
