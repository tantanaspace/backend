from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.api.mobile.v1.common.UserVenueFavouriteToggle.serializers import (
    UserVenueFavouriteToggleSerializer,
)
from apps.common.models import UserVenueFavourite


class UserVenueFavouriteToggleAPIView(GenericAPIView):
    serializer_class = UserVenueFavouriteToggleSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        venue_id = serializer.validated_data["venue"]
        user = request.user

        try:
            favourite = UserVenueFavourite.objects.get(venue=venue_id, user=user)
            favourite.delete()
            response_status = status.HTTP_204_NO_CONTENT
        except UserVenueFavourite.DoesNotExist:
            UserVenueFavourite.objects.create(venue=venue_id, user=user)
            response_status = status.HTTP_200_OK

        return Response(status=response_status)


__all__ = [
    "UserVenueFavouriteToggleAPIView",
]
