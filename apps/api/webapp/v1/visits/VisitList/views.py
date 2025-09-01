from rest_framework.generics import ListAPIView

from apps.users.permissions import IsHostUser
from apps.api.webapp.v1.visits.VisitList.serializers import VisitListSerializer
from apps.visits.models import Visit

class VisitListAPIView(ListAPIView):
    serializer_class = VisitListSerializer
    permission_classes = [IsHostUser]
    filterset_fields = ('status', 'booked_date', 'booked_time')

    def get_queryset(self):
        return Visit.objects.filter(venue=self.request.user.venue).order_by('-booked_date', '-booked_time')


__all__ = [
    'VisitListAPIView',
]