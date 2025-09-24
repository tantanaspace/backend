from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.api.shared.v1.users.Auth.UserInfo.serializers import UserInfoSerializer


class UserInfoAPIView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving authenticated user information.
    Returns user's personal information.
    """

    serializer_class = UserInfoSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


__all__ = ["UserInfoAPIView"]
