from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from django.db.models import Prefetch

from apps.venues.models import VenueCategory, Venue
from apps.api.mobile.v1.venues.RecommendedVenues.serializers import RecommendedVenuesSerializer


class RecommendedVenuesAPIView(ListAPIView):
    serializer_class = RecommendedVenuesSerializer
    permission_classes = (AllowAny,)
        
    def get_queryset(self):
        return VenueCategory.objects.filter(
            is_active=True, 
            recommended=True
        ).prefetch_related(
            Prefetch(
                'venues',
                queryset=Venue.objects.filter(
                    is_active=True
                ).select_related(
                    'background_image'
                ).order_by('?')[:4],
                to_attr='recommended_venues'
            )
        )
