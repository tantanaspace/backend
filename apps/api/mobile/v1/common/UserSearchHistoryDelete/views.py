from rest_framework.generics import DestroyAPIView
from rest_framework.permissions import IsAuthenticated

from apps.common.models import UserSearchHistory

class UserSearchHistoryDeleteAPIView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return UserSearchHistory.objects.filter(user=self.request.user)


__all__ = [
    'UserSearchHistoryDeleteAPIView',
]