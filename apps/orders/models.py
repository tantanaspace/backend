from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import AbstractTimeStampedModel


class Order(AbstractTimeStampedModel):
    visit = models.OneToOneField('visits.Visit', on_delete=models.CASCADE, related_name='order',
                                 verbose_name=_('Visit'))
    percentage_of_service = models.FloatField(_('Percentage of Service'), default=0)
    service_fee = models.DecimalField(_('Service Fee'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('Total Amount'), max_digits=12, decimal_places=2, default=0)
    waiter_full_name = models.CharField(_('Waiter Full Name'), max_length=255)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-id']

    def __str__(self):
        return f'Order #{self.id} - {self.waiter_full_name} | {self.visit_id}'


class OrderItem(AbstractTimeStampedModel):
    class OrderItemStatus(models.TextChoices):
        ORDERED = 'ordered', _('Ordered')
        SERVED = 'served', _('Served')
        CANCELLED = 'cancelled', _('Cancelled')

    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='items', verbose_name=_('Order'))
    status = models.CharField(_('Status'), max_length=20, choices=OrderItemStatus.choices, default=OrderItemStatus.ORDERED)
    product_name = models.CharField(_('Product Name'), max_length=255)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2)
    total_price = models.DecimalField(_('Total Price'), max_digits=12, decimal_places=2)
    ordered_at = models.DateTimeField(_('Ordered At'), null=True, blank=True)
    served_at = models.DateTimeField(_('Served At'), null=True, blank=True)
    cancelled_at = models.DateTimeField(_('Cancelled At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f'{self.product_name} x {self.quantity} (Order #{self.order_id})'

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
