from rest_framework.generics import ListAPIView

from apps.api.mobile.v1.common.StoryDetail.serializers import StoryDetailSerializer
from apps.common.models import StoryItem

from rest_framework.permissions import AllowAny


class StoryDetailAPIView(ListAPIView):
    serializer_class = StoryDetailSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        story_group_id = self.kwargs['story_group_id']
        return StoryItem.objects.filter(is_active=True, story_group_id=story_group_id).select_related(
            'venue', 'venue__company'
            ).prefetch_related('venue__categories').order_by('order')

__all__ = [
    'StoryDetailAPIView',
]