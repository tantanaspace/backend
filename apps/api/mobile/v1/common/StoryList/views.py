from django.db.models import Q
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.api.mobile.v1.common.StoryList.serializers import StoryListSerializer
from apps.common.models import StoryGroup


class StoryListAPIView(ListAPIView):
    queryset = (
        StoryGroup.objects.filter(is_active=True)
        .filter(Q(expires_at__gte=timezone.now()) | Q(expires_at__isnull=True))
        .prefetch_related("story_items")
        .order_by("order")
    )

    serializer_class = StoryListSerializer
    permission_classes = [AllowAny]


__all__ = [
    "StoryListAPIView",
]
