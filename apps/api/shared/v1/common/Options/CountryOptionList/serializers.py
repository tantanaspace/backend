from rest_framework import serializers
from apps.common.models import Country

class CountryOptionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id',
            'name',
        )