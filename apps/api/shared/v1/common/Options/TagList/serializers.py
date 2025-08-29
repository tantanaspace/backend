from rest_framework import serializers
from apps.common.models import Tag

class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'title')