from rest_framework.generics import RetrieveAPIView

from apps.api.webapp.v1.visits.VisitDetail.serializers import VisitDetailSerializer
from apps.visits.models import Visit
from apps.users.permissions import IsHostUser

class VisitDetailAPIView(RetrieveAPIView):
    serializer_class = VisitDetailSerializer
    permission_classes = [IsHostUser]
    lookup_field = 'visit_id'

    def get_queryset(self):
        return Visit.objects.filter(venue=self.request.user.venue)


__all__ = [
    'VisitDetailAPIView',
]