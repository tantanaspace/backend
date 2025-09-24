from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.payments.models import PaymentTransaction


@receiver(post_save, sender=PaymentTransaction)
def payment_successful(sender, instance, **kwargs):
    if instance.status == PaymentTransaction.StatusType.ACCEPTED:
        pass
        # todo: send notification to user
