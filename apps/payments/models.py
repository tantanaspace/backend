import base64

from django.db import models
from django.conf import settings
from django.utils import timezone
from auditlog.registry import auditlog
from django.utils.translation import gettext_lazy as _

from apps.common.models import AbstractTimeStampedModel, AbstractSoftDeleteModel


class BankCard(AbstractTimeStampedModel, AbstractSoftDeleteModel):
    class VendorType(models.TextChoices):
        HUMO = ('humo', _('Humo'))
        UZCARD = ('uzcard', _('Uzcard'))
        VISA = ('visa', _('Visa'))
        MASTERCARD = ('mastercard', _('Mastercard'))
        UNIONPAY = ('unionpay', _('Unionpay'))

    user = models.ForeignKey('users.User', on_delete=models.PROTECT, related_name='bank_cards')
    pan = models.CharField(_('PAN'), max_length=32)
    expire_date = models.CharField(max_length=255, verbose_name=_("Expire Date"))
    phone_number_mask = models.CharField(max_length=255, verbose_name=_("Phone Number Mask"))
    cid = models.TextField(verbose_name=_("Cid"))
    is_confirmed = models.BooleanField(default=False, verbose_name=_("Is Confirmed"))
    vendor = models.CharField(_('Vendor'), max_length=32, choices=VendorType.choices, null=True, blank=True)

    objects = models.Manager()


    class Meta:
        verbose_name = _('BankCard')
        verbose_name_plural = _('BankCards')
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'pan', 'expire_date', 'cid'],
                condition=models.Q(is_deleted=False),
                name='unique_bank_card_active'
            )
        ]

    def __str__(self):
        return f'{self.pan} - {self.expire_date}'

class PaymentTransaction(AbstractTimeStampedModel):
    class StatusType(models.TextChoices):
        PENDING = 'pending', _('Pending')
        ACCEPTED = 'accepted', _('Accepted')
        REJECTED = 'rejected', _('Rejected')
        CANCELED = 'canceled', _('Canceled')

    class ProviderType(models.TextChoices):
        CARD = 'CARD', _('CARD')
        CLICK = 'CLICK', _('CLICK')
        PAYME = 'PAYME', _('PAYME')
        UZUM = 'UZUM', _('UZUM')
        PAYLOV = 'PAYLOV', _('PAYLOV')
        PAYNET = 'PAYNET', _('PAYNET')
        MANUAL = 'MANUAL', _('MANUAL')


    user = models.ForeignKey("users.User", on_delete=models.PROTECT, related_name='payment_transactions')
    visit = models.ForeignKey("visits.Visit", on_delete=models.PROTECT, related_name='payment_transactions')
    card = models.ForeignKey(BankCard, on_delete=models.PROTECT, related_name='payment_transactions',
                             verbose_name=_('Card id'), null=True, blank=True)
    provider = models.CharField(_("Provider"), choices=ProviderType.choices)
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2)
    status = models.CharField(_('Status'), max_length=32, choices=StatusType.choices, default=StatusType.PENDING)
    remote_id = models.CharField(_('Remote id'), max_length=255, null=True, blank=True)
    paid_at = models.DateTimeField(verbose_name=_("Paid at"), null=True, blank=True)
    rejected_at = models.DateTimeField(verbose_name=_("Rejected at"), null=True, blank=True)
    canceled_at = models.DateTimeField(verbose_name=_("Canceled at"), null=True, blank=True)
    extra = models.JSONField(_('Extra'), null=True, blank=True)

    class Meta:
        db_table = 'PaymentTransaction'
        verbose_name = _('PaymentTransaction')
        verbose_name_plural = _('PaymentTransactions')
        ordering = ('remote_id',)

    def __str__(self):
        return f"{self.provider} | {self.amount}"

    def success_process(self):
        self.status = self.StatusType.ACCEPTED
        self.paid_at = timezone.now()
        self.save(update_fields=['status', 'paid_at'])

        self.user.update_balance()

    def reject_process(self):
        self.status = self.StatusType.REJECTED
        self.rejected_at = timezone.now()
        self.save(update_fields=['status', 'rejected_at'])

    def cancel_process(self):
        self.status = self.StatusType.CANCELED
        self.canceled_at = timezone.now()
        self.save(update_fields=['status', 'canceled_at'])

        self.user.update_balance()

    @property
    def payment_url(self):
        payment_url = ""
        if self.provider == PaymentTransaction.ProviderType.PAYME:
            merchant_id = settings.PAYMENT_CREDENTIALS.get('payme', {}).get('merchant_id')
            params = f"m={merchant_id};ac.order_id={self.id};a={self.amount * 100};"
            encode_params = base64.b64encode(params.encode("utf-8"))
            encode_params = str(encode_params, "utf-8")
            payment_url = f"{settings.PAYMENT_CREDENTIALS.get('payme', {}).get('callback_url')}/{encode_params}"

        elif self.provider == PaymentTransaction.ProviderType.PAYLOV:
            merchant_id = settings.PAYMENT_CREDENTIALS.get('paylov', {}).get('merchant_id')
            query = f"merchant_id={merchant_id}&amount={self.amount}&account.order_id={self.id}"
            encode_params = base64.b64encode(query.encode("utf-8"))
            encode_params = str(encode_params, "utf-8")
            payment_url = f"{settings.PAYMENT_CREDENTIALS.get('paylov', {}).get('callback_url')}/{encode_params}"

        elif self.provider == PaymentTransaction.ProviderType.CLICK:
            merchant_id = settings.PAYMENT_CREDENTIALS.get('click', {}).get('merchant_id')
            service_id = settings.PAYMENT_CREDENTIALS.get('click', {}).get('merchant_service_id')
            params = (
                f"?service_id={service_id}&merchant_id={merchant_id}&"
                f"amount={self.amount}&transaction_param={self.id}"
            )
            payment_url = f"{settings.PAYMENT_CREDENTIALS.get('click', {}).get('callback_url')}/{params}"

        return payment_url

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.provider == PaymentTransaction.ProviderType.MANUAL and not self.pk:
            self.status = self.StatusType.ACCEPTED
            self.paid_at = timezone.now()
            super().save(force_insert, using, update_fields=None)
            # todo: add user update balance logic
        else:
            super().save(force_insert, force_update, using, update_fields)


class PaymentRequestLog(AbstractTimeStampedModel):
    provider = models.CharField(max_length=50, verbose_name=_("Provider"),
                                    choices=PaymentTransaction.ProviderType.choices)
    method = models.CharField(max_length=255, verbose_name=_('Method'), null=True, blank=True)
    request_data = models.JSONField(verbose_name=_("Request Data"), null=True, blank=True)
    response_data = models.JSONField(verbose_name=_("Response Data"), null=True, blank=True)

    class Meta:
        verbose_name = _('PaymentRequestLog')
        verbose_name_plural = _('PaymentRequestLogs')


auditlog.register(PaymentTransaction)