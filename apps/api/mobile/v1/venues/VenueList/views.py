from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.generics import ListAPIView

from apps.venues.models import Venue
from apps.api.mobile.v1.venues.VenueList.serializers import MapVenueListSerializer, VenueListSerializer
from apps.api.mobile.v1.venues.VenueList.filters import VenueListFilter


class VenueListAPIView(ListAPIView):
    queryset = Venue.objects.select_related('company', 'background_image').prefetch_related(
        'categories', 'facilities', 'tags', 'working_hours'
    )
    filterset_class = VenueListFilter
    search_fields = ('name',)

    def get_serializer_class(self):
        map = self.request.query_params.get('map', False)
        if map:
            return MapVenueListSerializer
        return VenueListSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'map',
                openapi.IN_QUERY,
                description="Map mode. Set to 'true' to get simplified information for the map",
                type=openapi.TYPE_STRING,
                enum=['true', 'false'],
                required=False,
                default='false'
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

__all__ = [
    'VenueListAPIView',
]