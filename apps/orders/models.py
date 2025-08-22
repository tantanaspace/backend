from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import AbstractTimeStampedModel


class Order(AbstractTimeStampedModel):
    class OrderStatus(models.TextChoices):
        STARTED = 'started', _('Started')
        FINISHED = 'finished', _('Finished')
        PAYMENT = 'payment', _('Payment')
        CLOSED = 'closed', _('Closed')

    visit = models.OneToOneField('visits.Visit', on_delete=models.CASCADE, related_name='order',
                                 verbose_name=_('Visit'))
    status = models.CharField(_('Status'), max_length=20, choices=OrderStatus.choices, default=OrderStatus.STARTED)
    percentage_of_service = models.FloatField(_('Percentage of Service'), default=0)
    service_fee = models.DecimalField(_('Service Fee'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('Total Amount'), max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-id']

    def __str__(self):
        return f'Order #{self.id} - {self.get_status_display()} ({self.visit})'


class OrderItem(AbstractTimeStampedModel):
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items', verbose_name=_('Order'))
    product_name = models.CharField(_('Product Name'), max_length=255)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_('Total Price'), max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f'{self.product_name} x {self.quantity} (Order #{self.order_id})'
