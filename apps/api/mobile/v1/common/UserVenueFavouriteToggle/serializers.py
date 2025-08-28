from rest_framework import serializers
from apps.common.models import UserVenueFavourite

class UserVenueFavouriteToggleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = UserVenueFavourite
        fields = ('venue',)
        