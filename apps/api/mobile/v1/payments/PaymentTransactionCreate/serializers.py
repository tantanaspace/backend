from rest_framework import serializers

from apps.payments.models import PaymentTransaction


class TransactionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentTransaction
        fields = (
            'id',
            'amount',
            'provider',
            'payment_url'
        )
        extra_kwargs = {"payment_url": {"read_only": True}}
