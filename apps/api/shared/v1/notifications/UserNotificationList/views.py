from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.api.shared.v1.notifications.UserNotificationList.serializers import UserNotificationListSerializer
from apps.notifications.models import UserNotification


class UserNotificationListAPIView(ListAPIView):
    queryset = UserNotification.objects.select_related('notification').filter()
    serializer_class = UserNotificationListSerializer
    permission_classes = (IsAuthenticated,)

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.filter(user_id=self.request.user.id).order_by("-created_at")


__all__ = ['UserNotificationListAPIView']
