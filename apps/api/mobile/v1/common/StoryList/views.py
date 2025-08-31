from rest_framework.generics import ListAPIView
from apps.common.models import StoryGroup
from apps.api.mobile.v1.common.StoryList.serializers import StoryListSerializer
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db.models import Q

class StoryListAPIView(ListAPIView):
    queryset = StoryGroup.objects.filter(is_active=True).filter(
        Q(expires_at__gte=timezone.now()) | Q(expires_at__isnull=True)
    ).prefetch_related('story_items').order_by('order')

    serializer_class = StoryListSerializer
    permission_classes = [AllowAny]

__all__ = [
    'StoryListAPIView',
]