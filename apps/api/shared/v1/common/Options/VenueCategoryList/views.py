from rest_framework.generics import ListAPIView
from apps.venues.models import VenueCategory
from apps.api.shared.v1.common.Options.VenueCategoryList.serializers import VenueCategoryListSerializer
from rest_framework.permissions import AllowAny

class VenueCategoryListAPIView(ListAPIView):
    queryset = VenueCategory.objects.filter(is_active=True)
    serializer_class = VenueCategoryListSerializer
    permission_classes = [AllowAny]
    filterset_fields = ('id', 'title', 'category_type', 'recommended')
    search_fields = ('title',)
    ordering = ('id', 'title', 'order')

__all__ = [
    'VenueCategoryListAPIView',
]