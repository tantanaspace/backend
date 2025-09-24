from rest_framework.generics import ListAPIView

from apps.api.mobile.v1.venues.MapVenueList.filters import MapVenueListFilter
from apps.api.mobile.v1.venues.MapVenueList.serializers import MapVenueListSerializer
from apps.venues.models import Venue


class MapVenueListAPIView(ListAPIView):
    queryset = (
        Venue.objects.filter(is_active=True)
        .select_related("company", "background_image")
        .prefetch_related("categories", "facilities", "tags", "working_hours")
    )
    filterset_class = MapVenueListFilter
    search_fields = ("name",)
    serializer_class = MapVenueListSerializer
    pagination_class = None


__all__ = [
    "MapVenueListAPIView",
]
