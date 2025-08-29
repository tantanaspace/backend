from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from apps.venues.models import Venue
from apps.api.mobile.v1.common.UserVenueFavouriteList.serializers import UserFavouriteVenueListSerializer

class UserVenueFavouriteListAPIView(ListAPIView):    
    serializer_class = UserFavouriteVenueListSerializer
    permission_classes = (IsAuthenticated,)
    search_fields = ('name',)
    
    def get_queryset(self):
        user = self.request.user
        return Venue.objects.filter(
            user_venue_favourites__user=user
        ).select_related('company').prefetch_related('background_image')


__all__ = [
    'UserVenueFavouriteListAPIView',
]
