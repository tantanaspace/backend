from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.mobile.v1.common.UserSearchHistoryList.serializers import (
    UserSearchHistoryListSerializer,
)
from apps.common.models import UserSearchHistory


class UserSearchHistoryListAPIView(ListAPIView):
    serializer_class = UserSearchHistoryListSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return UserSearchHistory.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )

    def delete(self, request, *args, **kwargs):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


__all__ = [
    "UserSearchHistoryListAPIView",
]
