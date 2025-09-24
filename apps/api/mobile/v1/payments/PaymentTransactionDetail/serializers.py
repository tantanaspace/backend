from rest_framework import serializers

from apps.payments.models import PaymentTransaction


class TransactionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ("id", "amount", "provider", "status", "created_at")
