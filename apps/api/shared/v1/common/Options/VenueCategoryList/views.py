from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.api.shared.v1.common.Options.VenueCategoryList.serializers import (
    VenueCategoryListSerializer,
)
from apps.venues.models import VenueCategory


class VenueCategoryListAPIView(ListAPIView):
    queryset = VenueCategory.objects.filter(is_active=True)
    serializer_class = VenueCategoryListSerializer
    permission_classes = [AllowAny]
    filterset_fields = ("id", "title", "category_type", "recommended")
    search_fields = ("title",)
    ordering = ("id", "title", "order")


__all__ = [
    "VenueCategoryListAPIView",
]
