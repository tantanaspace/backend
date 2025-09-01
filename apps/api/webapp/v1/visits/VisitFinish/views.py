from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from apps.visits.models import Visit
from apps.users.permissions import IsHostUser

class VisitFinishAPIView(GenericAPIView):
    permission_classes = [IsHostUser]  
    lookup_url_kwarg = 'visit_id'

    def get_queryset(self):
        return Visit.objects.filter(venue=self.request.user.venue)

    def post(self, request, *args, **kwargs):
        visit = self.get_object()
        visit.finished_at = timezone.now()
        visit.status = Visit.VisitStatus.FINISHED
        visit.save(update_fields=['finished_at', 'status'])

        return Response({'success': True}, status=status.HTTP_200_OK)


__all__ = [
    'VisitFinishAPIView',
]