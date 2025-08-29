from rest_framework.generics import ListAPIView
from apps.common.models import Story
from apps.api.mobile.v1.common.StoryList.serializers import StoryListSerializer
from rest_framework.permissions import AllowAny


class StoryListAPIView(ListAPIView):
    queryset = Story.objects.filter(is_active=True)
    serializer_class = StoryListSerializer
    permission_classes = [AllowAny]

__all__ = [
    'StoryListAPIView',
]