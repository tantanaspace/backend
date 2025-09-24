from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.payments.models import PaymentTransaction
from apps.payments.tasks import send_payment_successful_notification


@receiver(post_save, sender=PaymentTransaction)
def payment_successful(sender, instance, **kwargs):
    if instance.status == PaymentTransaction.StatusType.ACCEPTED and instance.is_notification_sent is False:
        pass
        # send_payment_successful_notification.delay(instance.id)
