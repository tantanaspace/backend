from rest_framework import serializers

from apps.common.models import UserSearchHistory


class UserSearchHistoryCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault(), write_only=True
    )

    class Meta:
        model = UserSearchHistory
        fields = ("user", "text")
