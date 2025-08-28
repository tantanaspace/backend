from rest_framework.generics import ListAPIView

from apps.venues.models import VenueCategory
from apps.api.mobile.v1.venues.VenueCategoryList.serializers import VenueCategoryListSerializer


class VenueCategoryListAPIView(ListAPIView):
    queryset = VenueCategory.objects.filter(is_active=True).order_by('order')
    serializer_class = VenueCategoryListSerializer

__all__ = [
    'VenueCategoryListAPIView',
]