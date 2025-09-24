from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated

from apps.api.shared.v1.users.Auth.UserInfoUpdate.serializers import (
    UserInfoUpdateSerializer,
)


class UserInfoUpdateAPIView(GenericAPIView, UpdateModelMixin):
    serializer_class = UserInfoUpdateSerializer
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,)

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


__all__ = ["UserInfoUpdateAPIView"]
