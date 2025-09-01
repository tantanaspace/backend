from django.utils import timezone

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from apps.visits.models import Visit
from apps.api.webapp.v1.visits.VisitCancel.serializers import VisitCancelSerializer
from apps.users.permissions import IsHostUser

class VisitCancelAPIView(GenericAPIView):
    queryset = Visit.objects.all()
    serializer_class = VisitCancelSerializer
    permission_classes = [IsHostUser]
    lookup_url_kwarg = 'visit_id'
    
    def get_queryset(self):
        return super().get_queryset().filter(venue=self.request.user.venue)

    def post(self, request, *args, **kwargs):
        visit = self.get_object()
        serializer = self.get_serializer(visit, data=request.data)
        serializer.is_valid(raise_exception=True)
        visit.cancelled_at = timezone.now()
        visit.cancel_reason = serializer.validated_data['cancel_reason']
        visit.status = Visit.VisitStatus.CANCELLED
        visit.save(update_fields=['cancelled_at', 'cancel_reason', 'status'])
        return Response({'success': True}, status=status.HTTP_200_OK)


__all__ = [
    'VisitCancelAPIView',
]