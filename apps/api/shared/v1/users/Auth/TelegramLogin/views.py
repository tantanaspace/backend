from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.api.shared.v1.users.Auth.TelegramLogin.serializers import TelegramLoginSerializer
from apps.users.authentications import TelegramWebAppAuthentication
from apps.users.permissions import IsHostUser

class TelegramLoginAPIView(GenericAPIView):
    """
    Authentication through Telegram WebApp.
    Requires header: Authorization: Telegram <initData>
    """

    authentication_classes = [TelegramWebAppAuthentication]
    permission_classes = [IsHostUser]
    serializer_class = TelegramLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer({**request.user.tokens, 'user': request.user})
        return Response(serializer.data, status=status.HTTP_200_OK)


__all__ = [
    'TelegramLoginAPIView',
]