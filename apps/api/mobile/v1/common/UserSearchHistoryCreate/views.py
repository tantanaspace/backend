from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.api.mobile.v1.common.UserSearchHistoryCreate.serializers import UserSearchHistoryCreateSerializer

class UserSearchHistoryCreateAPIView(CreateAPIView):
    serializer_class = UserSearchHistoryCreateSerializer
    permission_classes = (IsAuthenticated,)

__all__ = [
    'UserSearchHistoryCreateAPIView',
]