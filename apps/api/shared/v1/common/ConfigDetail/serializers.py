from rest_framework import serializers
from apps.common.models import GlobalSettings

class ConfigDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = (
            'backoffice_url',
        )