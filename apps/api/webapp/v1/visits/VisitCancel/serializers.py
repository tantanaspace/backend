from rest_framework import serializers

from apps.visits.models import Visit


class VisitCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = ("cancel_reason",)
