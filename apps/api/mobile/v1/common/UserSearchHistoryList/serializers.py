from rest_framework import serializers

from apps.common.models import UserSearchHistory


class UserSearchHistoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSearchHistory
        fields = ("id", "text")
