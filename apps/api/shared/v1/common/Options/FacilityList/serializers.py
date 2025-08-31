from rest_framework import serializers
from apps.common.models import Facility


class FacilityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = ('id', 'title', 'quick_access')