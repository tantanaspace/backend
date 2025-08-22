from rest_framework import serializers

from apps.notifications.models import UserNotification


class UserNotificationListSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='notification.title')
    body = serializers.CharField(source='notification.body_text') # todo: fix use body_html or body_text

    class Meta:
        model = UserNotification
        fields = (
            'id',
            'title',
            'body',
            'data',
            'is_read',
            'created_at'
        )
