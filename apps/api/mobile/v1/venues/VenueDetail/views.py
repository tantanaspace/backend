from rest_framework.generics import RetrieveAPIView

from apps.api.mobile.v1.venues.VenueDetail.serializers import VenueDetailSerializer
from apps.venues.models import Venue
from django.db.models import Count, Avg
class VenueDetailAPIView(RetrieveAPIView):
    queryset = Venue.objects.select_related('company', 'background_image').prefetch_related(
        'categories', 'facilities', 'working_hours', 'images', 'social_links'
    ).annotate(
        reviews_count=Count('reviews', distinct=True),
    )
    serializer_class = VenueDetailSerializer
    lookup_url_kwarg = 'venue_id'

    
    

__all__ = [
    'VenueDetailAPIView'
]