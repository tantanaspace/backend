from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.api.shared.v1.users.Auth.Login.serializers import LoginSerializer


class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            phone_number=serializer.validated_data["phone_number"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            raise AuthenticationFailed(_("Invalid phone number or password."))

        serializer = self.get_serializer({**user.tokens, "user": user})
        return Response(serializer.data, status=status.HTTP_200_OK)


__all__ = ["LoginAPIView"]

print("User can now choose language")