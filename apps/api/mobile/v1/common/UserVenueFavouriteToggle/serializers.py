from rest_framework import serializers
from apps.common.models import UserVenueFavourite

class UserVenueFavouriteToggleSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault(), write_only=True)
    
    class Meta:
        model = UserVenueFavourite
        fields = ('venue', 'user')
        