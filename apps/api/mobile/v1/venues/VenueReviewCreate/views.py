from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from apps.api.mobile.v1.venues.VenueReviewCreate.serializers import (
    VenueReviewCreateSerializer,
)
from apps.venues.models import VenueReview


class VenueReviewCreateAPIView(CreateAPIView):
    serializer_class = VenueReviewCreateSerializer
    queryset = VenueReview.objects.all()
    permission_classes = (IsAuthenticated,)


__all__ = [
    "VenueReviewCreateAPIView",
]
