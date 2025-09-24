from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from apps.notifications.models import Notification
from apps.notifications.tasks import send_notification


@receiver(post_save, sender=Notification)
def create_user_notification_all(sender, instance, created, **kwargs):
    """This works when a notification is for everyone."""
    if created and instance.is_for_everyone:
        transaction.on_commit(
            lambda: send_notification.delay(
                instance.id, is_for_everyone=True, only_push=instance.only_push
            )
        )


@receiver(m2m_changed, sender=Notification.users.through)
def create_user_notification(sender, instance, action, **kwargs):
    """This works when a notification is not for everyone."""
    if action == "post_add":
        if instance.is_for_everyone:
            instance.users.clear()
        else:
            transaction.on_commit(
                lambda: send_notification.delay(
                    instance.id,
                    is_for_everyone=False,
                    users_id=list(instance.users.values_list("id", flat=True)),
                    only_push=instance.only_push,
                )
            )
