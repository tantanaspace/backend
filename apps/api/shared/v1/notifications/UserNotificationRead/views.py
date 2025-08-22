from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated

from apps.notifications.models import UserNotification


class UserNotificationReadAPIView(RetrieveModelMixin, GenericAPIView):
    queryset = UserNotification.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = None  # todo: custom swagger_auto_schema

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def get_object(self):
        instance = super().get_object()

        if not instance.is_read:
            instance.is_read = True
            instance.save(update_fields=['is_read'])
        return instance

    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()

        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read'])

        return Response({'is_read': notification.is_read})

    def post(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


__all__ = ['UserNotificationReadAPIView']
