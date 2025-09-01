from rest_framework.generics import CreateAPIView

from apps.visits.models import Visit
from apps.api.webapp.v1.visits.BookCreate.serializers import BookCreateSerializer
from apps.users.permissions import IsHostUser

class BookCreateAPIView(CreateAPIView):
    serializer_class = BookCreateSerializer
    permission_classes = [IsHostUser]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user, venue=self.request.user.venue, created_by=Visit.CreatedBy.HOST)


__all__ = [
    'BookCreateAPIView',
]