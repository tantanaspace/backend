from rest_framework.generics import RetrieveAPIView

from apps.api.webapp.v1.visits.VisitDetail.serializers import VisitDetailSerializer
from apps.users.permissions import IsHostUser
from apps.visits.models import Visit


class VisitDetailAPIView(RetrieveAPIView):
    serializer_class = VisitDetailSerializer
    permission_classes = [IsHostUser]
    lookup_url_kwarg = "visit_id"

    def get_queryset(self):
        return Visit.objects.filter(venue=self.request.user.venue)


__all__ = [
    "VisitDetailAPIView",
]
