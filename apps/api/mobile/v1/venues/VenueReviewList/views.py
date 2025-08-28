from rest_framework.generics import ListAPIView

from apps.venues.models import VenueReview
from apps.api.mobile.v1.venues.VenueReviewList.serializers import VenueReviewListSerializer

class VenueReviewListAPIView(ListAPIView):
    queryset = VenueReview.objects.all()
    serializer_class = VenueReviewListSerializer
    
    def get_queryset(self):
        venue_id = self.kwargs['venue_id']
        return VenueReview.objects.filter(venue=venue_id, is_approved=True)
        