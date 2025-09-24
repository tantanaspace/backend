from rest_framework.generics import CreateAPIView

from apps.api.mobile.v1.payments.PaymentTransactionCreate.serializers import (
    TransactionCreateSerializer,
)
from apps.payments.models import PaymentTransaction
from apps.users.permissions import IsDefaultUser


class TransactionCreateAPIView(CreateAPIView):
    serializer_class = TransactionCreateSerializer
    queryset = PaymentTransaction.objects.all()
    permission_classes = [IsDefaultUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


__all__ = ["TransactionCreateAPIView"]
