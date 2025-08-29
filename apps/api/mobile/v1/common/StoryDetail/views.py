from rest_framework.generics import RetrieveAPIView

from apps.api.mobile.v1.common.StoryDetail.serializers import StoryDetailSerializer
from apps.common.models import Story

from rest_framework.permissions import AllowAny


class StoryDetailAPIView(RetrieveAPIView):
    queryset = Story.objects.select_related('venue', 'venue__company').prefetch_related('venue__categories')
    serializer_class = StoryDetailSerializer
    permission_classes = [AllowAny]

__all__ = [
    'StoryDetailAPIView',
]