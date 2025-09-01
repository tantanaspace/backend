from hashlib import blake2b
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class Visit(models.Model):
    class VisitStatus(models.TextChoices):
        BOOKED = 'booked', _('Booked')
        STARTED = 'started', _('Started')
        FINISHED = 'finished', _('Finished')
        PAYMENT = 'payment', _('Payment')
        CLOSED = 'closed', _('Closed')
        CANCELLED = 'cancelled', _('Cancelled')

    class CreatedBy(models.TextChoices):
        USER = 'user', _('User')
        HOST = 'host', _('Host')

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='visits', verbose_name=_('User'), null=True, blank=True)
    user_phone_number = PhoneNumberField(_('User Phone Number'))
    user_full_name = models.CharField(_('User Full Name'), max_length=255)
    
    host = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='hosted_visits', verbose_name=_('Host'), null=True, blank=True)
    created_by = models.CharField(_('Created By'), max_length=20, choices=CreatedBy.choices, default=CreatedBy.USER)

    
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='visits', verbose_name=_('Venue'))
    zone = models.ForeignKey('venues.VenueZone', on_delete=models.SET_NULL, related_name='visits', null=True, blank=True,
                             verbose_name=_('Zone'))
    table_number = models.CharField(_('Table Number'), max_length=255, null=True, blank=True)

    booked_date = models.DateField(_('Booked Date'))
    booked_time = models.TimeField(_('Booked Time'))

    number_of_guests = models.PositiveIntegerField(_('Number of Guests'))
    status = models.CharField(_('Status'), max_length=20, choices=VisitStatus.choices, default=VisitStatus.BOOKED)

    started_at = models.DateTimeField(_('Started At'), null=True, blank=True)
    finished_at = models.DateTimeField(_('Finished At'), null=True, blank=True)
    paid_at = models.DateTimeField(_('Paid At'), null=True, blank=True)
    closed_at = models.DateTimeField(_('Closed At'), null=True, blank=True)
    cancelled_at = models.DateTimeField(_('Cancelled At'), null=True, blank=True)
    cancel_reason = models.TextField(_('Cancel Reason'), null=True, blank=True)


    class Meta:
        verbose_name = _('Visit')
        verbose_name_plural = _('Visits')
        ordering = ['-booked_date', '-booked_time']

    def __str__(self):
        return f'Visit #{self.id} - {self.venue} ({self.user})'


class VisitGuest(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name=_('User'))
    visit = models.ForeignKey('visits.Visit', on_delete=models.CASCADE, related_name='guests',
                              verbose_name=_('Visit'))
    is_joined = models.BooleanField(_('Is Joined'), default=False)
    joined_at = models.DateTimeField(_('Joined At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Visit Guest')
        verbose_name_plural = _('Visit Guests')
        unique_together = ('user', 'visit')

    def __str__(self):
        return f'{self.user} @ Visit #{self.visit_id}'
