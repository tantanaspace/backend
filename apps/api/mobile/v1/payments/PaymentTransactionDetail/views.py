from rest_framework.generics import RetrieveAPIView

from apps.api.mobile.v1.payments.PaymentTransactionDetail.serializers import (
    TransactionDetailSerializer,
)
from apps.payments.models import PaymentTransaction
from apps.users.permissions import IsDefaultUser


class TransactionDetailAPIView(RetrieveAPIView):
    serializer_class = TransactionDetailSerializer
    queryset = PaymentTransaction.objects.all()
    permission_classes = [IsDefaultUser]


__all__ = ["TransactionDetailAPIView"]
