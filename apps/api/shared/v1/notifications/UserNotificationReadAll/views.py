from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.models import UserNotification


class UserNotificationReadAllView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = None  # todo: custom swagger_auto_schema

    def get_queryset(self):
        return UserNotification.objects.filter(
            user_id=self.request.user.id, is_read=False
        )

    def post(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        updates_count = queryset.update(is_read=True)
        return Response(data={"updates_notification_count": updates_count})


__all__ = ["UserNotificationReadAllView"]
