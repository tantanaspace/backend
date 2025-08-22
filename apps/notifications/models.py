from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from fcm_django.models import AbstractFCMDevice
from fcm_django.settings import FCM_DJANGO_SETTINGS
from modeltranslation.utils import get_translation_fields

from apps.common.models import AbstractTimeStampedModel


class CustomFCMDevice(AbstractFCMDevice):
    class Meta:
        verbose_name = _("FCM device")
        verbose_name_plural = _("FCM devices")

        if not FCM_DJANGO_SETTINGS["MYSQL_COMPATIBILITY"]:
            indexes = [
                models.Index(fields=["registration_id", "user"]),
            ]


class NotificationTemplate(AbstractTimeStampedModel):
    TYPE_CHOICES = (
        # Booking lifecycle
        ('booking_created', _('Booking Created')),
        ('booking_reminder', _('Booking Reminder')),
        ('booking_updated', _('Booking Updated')),
        ('booking_cancelled', _('Booking Cancelled')),
        ('table_ready', _('Table Ready')),
        # Billing lifecycle
        ('bill_opened', _('Bill Opened')),
        ('bill_updated', _('Bill Updated')),
        ('bill_closed', _('Bill Closed')),
        # Payments
        ('payment_received', _('Payment Received')),
        ('payment_failed', _('Payment Failed')),
    )

    type = models.CharField(
        _('Type'),
        max_length=50,
        choices=TYPE_CHOICES,
        unique=True
    )
    title = models.CharField(_("Title"), max_length=255)
    body_text = models.TextField(_("Body (Plain Text)"))
    body_html = models.TextField(_("Body (HTML)"), null=True, blank=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("Notification template")
        verbose_name_plural = _("Notification templates")

    def clean(self):
        errors = list()

        is_complete_title = all(getattr(self, field) for field in get_translation_fields('title'))
        is_complete_body = all(getattr(self, field) for field in get_translation_fields('body_text'))

        if not (is_complete_title and is_complete_body):
            errors.append(
                _("You must provide a title and body text for all languages.")
            )

        if errors:
            raise ValidationError(errors)
        
    def __str__(self):
        return f"{self.get_type_display()}"


class Notification(AbstractTimeStampedModel):
    class NotificationType(models.TextChoices):
        # Booking lifecycle
        BOOKING_CREATED = "booking_created", _("Booking Created")
        BOOKING_REMINDER = "booking_reminder", _("Booking Reminder")
        BOOKING_UPDATED = "booking_updated", _("Booking Updated")
        BOOKING_CANCELLED = "booking_cancelled", _("Booking Cancelled")
        TABLE_READY = "table_ready", _("Table Ready")
        # Billing lifecycle
        BILL_OPENED = "bill_opened", _("Bill Opened")
        BILL_UPDATED = "bill_updated", _("Bill Updated")
        BILL_CLOSED = "bill_closed", _("Bill Closed")
        # Payments
        PAYMENT_RECEIVED = "payment_received", _("Payment Received")
        PAYMENT_FAILED = "payment_failed", _("Payment Failed")

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        IN_PROCESS = "in_process", _("In Process")
        COMPLETED = "completed", _("Completed")
        FAILED = "failed", _("Failed")

    title = models.CharField(_("Title"), max_length=255)
    body_text = models.TextField(_("Body (Plain Text)"))
    body_html = models.TextField(_("Body (HTML)"), null=True, blank=True)
    is_for_everyone = models.BooleanField(_("Is for everyone"), default=False)
    type = models.CharField(_("Type"), max_length=24, choices=NotificationType.choices)
    status = models.CharField(_('Status'), max_length=12, choices=Status.choices, default=Status.PENDING)
    users = models.ManyToManyField(
        "users.User",
        blank=True,
        verbose_name=_("Users")
    )
    template = models.ForeignKey(
        "NotificationTemplate",
        on_delete=models.SET_NULL,
        related_name="notifications",
        null=True,
        blank=True,
        verbose_name=_("Template")
    )
    only_push = models.BooleanField(_("Only Push"), default=False)
    data = models.JSONField(_('Data'), default=dict)

    objects = models.Manager()

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_notification_data(self):
        return self.data


class UserNotification(AbstractTimeStampedModel):
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name="user_notifications",
        verbose_name=_("User notification")
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="user_notifications",
        verbose_name=_("User id")
    )
    is_sent = models.BooleanField(_("Is sent"), default=False)
    is_read = models.BooleanField(_("Is read"), default=False)
    sent_at = models.DateTimeField(_("Sent At"), null=True, blank=True)
    data = models.JSONField(_('Data'), default=dict)

    objects = models.Manager()

    class Meta:
        verbose_name = _('UserNotification')
        verbose_name_plural = _("UserNotifications")
        ordering = ("-created_at",)

    def __str__(self):
        return f'notif_id: {self.notification_id} | user_id: {self.user_id}'
