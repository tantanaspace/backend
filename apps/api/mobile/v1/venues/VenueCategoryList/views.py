from rest_framework.generics import ListAPIView

from apps.api.mobile.v1.venues.VenueCategoryList.serializers import (
    VenueCategoryListSerializer,
)
from apps.venues.models import VenueCategory


class VenueCategoryListAPIView(ListAPIView):
    queryset = VenueCategory.objects.filter(is_active=True).order_by("order")
    serializer_class = VenueCategoryListSerializer


__all__ = [
    "VenueCategoryListAPIView",
]
