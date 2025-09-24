from rest_framework.generics import ListAPIView

from apps.api.mobile.v1.venues.VenueList.filters import VenueListFilter
from apps.api.mobile.v1.venues.VenueList.serializers import VenueListSerializer
from apps.venues.models import Venue


class VenueListAPIView(ListAPIView):
    queryset = (
        Venue.objects.filter(is_active=True)
        .select_related("company", "background_image")
        .prefetch_related("categories", "facilities", "tags", "working_hours")
    )
    filterset_class = VenueListFilter
    search_fields = ("name",)
    serializer_class = VenueListSerializer


__all__ = [
    "VenueListAPIView",
]
