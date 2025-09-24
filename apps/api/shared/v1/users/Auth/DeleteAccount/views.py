from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class DeleteAccountAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"success": True}, status=status.HTTP_200_OK)


__all__ = [
    "DeleteAccountAPIView",
]
