from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.api.shared.v1.common.EskizCallback.serializers import EskizCallbackSerializer
from apps.common.models import OTPLog


class EskizCallbackAPIView(GenericAPIView):
    serializer_class = EskizCallbackSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request_id = serializer.validated_data.get("request_id")
        status = serializer.validated_data.get("status")
        delivered = status == "DELIVERED"
        delivered_at = timezone.now() if delivered else None

        OTPLog.objects.filter(message_id=request_id).update(
            status=status,
            is_delivered=delivered,
            callback_log=serializer.validated_data,
            delivered_at=delivered_at,
        )

        return Response(data=dict(success=True), status=200)


__all__ = ["EskizCallbackAPIView"]
