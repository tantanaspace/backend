from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from apps.users.api_endpoints.OTP.serializers import CheckOTPSerializer, SendSMSSerializer


class CheckOTPView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = CheckOTPSerializer


class SendSMSView(CreateAPIView):
    serializer_class = SendSMSSerializer
    permission_classes = (AllowAny,)
