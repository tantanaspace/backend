from ast import mod
from re import T
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import AbstractTimeStampedModel


class Company(AbstractTimeStampedModel):
    name = models.CharField(_('Name'), max_length=255)
    logo = models.ImageField(_('Logo'), upload_to='companies/logos/')
    external_id = models.CharField(_('External ID'), max_length=255, blank=True, null=True)
    parsing_id = models.CharField(_('Parsing ID'), max_length=500, blank=True, null=True, help_text=_('ID from parsing system'))

    class Meta:
        verbose_name = _('Company')
        verbose_name_plural = _('Companies')

    def __str__(self):
        return self.name


class VenueCategory(AbstractTimeStampedModel):
    title = models.CharField(_('Title'), max_length=255)
    icon = models.ImageField(_('Icon'), upload_to='venue/categories/')
    order = models.PositiveIntegerField(_('Order'))
    is_active = models.BooleanField(_('Is Active'), default=True)
    parsing_id = models.CharField(_('Parsing ID'), max_length=500, blank=True, null=True, help_text=_('ID from parsing system'))

    class Meta:
        verbose_name = _('Venue Category')
        verbose_name_plural = _('Venue Categories')
        ordering = ['order']

    def __str__(self):
        return self.title


class Venue(AbstractTimeStampedModel):
    company = models.ForeignKey('venues.Company', on_delete=models.CASCADE, verbose_name=_('Company'))
    name = models.CharField(_('Name'), max_length=255)
    background_image = models.OneToOneField('venues.VenueImage', on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='background_for', verbose_name=_('Background Image'))
    category = models.ManyToManyField('venues.VenueCategory', blank=True, verbose_name=_('Categories'))
    description = models.TextField(_('Description'), blank=True, null=True)
    location = models.CharField(_('Location'), max_length=255)
    longitude = models.FloatField(_("Longitude"))
    latitude = models.FloatField(_("Latitude"))
    facilities = models.ManyToManyField('common.Facility', blank=True, verbose_name=_('Facilities'))
    tags = models.ManyToManyField('common.Tag', blank=True, verbose_name=_('Tags'))
    rating = models.DecimalField(_('Rating'), max_digits=3, decimal_places=2, default=0)
    external_id = models.CharField(_('External ID'), max_length=255, blank=True, null=True)
    parsing_id = models.CharField(_('Parsing ID'), max_length=500, blank=True, null=True, help_text=_('ID from parsing system'))

    class Meta:
        verbose_name = _('Venue')
        verbose_name_plural = _('Venues')

    def __str__(self):
        return self.name


class VenueZone(AbstractTimeStampedModel):
    name = models.CharField(_('Name'), max_length=255)
    photo_view = models.ImageField(_('Photo View'), upload_to='venue/zones/')
    external_id = models.CharField(_('External ID'), max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = _('Venue Zone')
        verbose_name_plural = _('Venue Zones')

    def __str__(self):
        return self.name


class VenueWorkingHour(AbstractTimeStampedModel):
    class Weekday(models.TextChoices):
        MONDAY = 'mon', _('Monday')
        TUESDAY = 'tue', _('Tuesday')
        WEDNESDAY = 'wed', _('Wednesday')
        THURSDAY = 'thu', _('Thursday')
        FRIDAY = 'fri', _('Friday')
        SATURDAY = 'sat', _('Saturday')
        SUNDAY = 'sun', _('Sunday')

    opening_time = models.TimeField(_('Opening Time'))
    closing_time = models.TimeField(_('Closing Time'))
    weekday = models.CharField(_('Weekday'), max_length=10, choices=Weekday.choices)
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, verbose_name=_('Venue'))

    class Meta:
        verbose_name = _('Venue Working Hour')
        verbose_name_plural = _('Venue Working Hours')
        ordering = ['venue', 'weekday', 'opening_time']

    def __str__(self):
        return f'{self.venue} - {self.get_weekday_display()}'


class VenueImage(AbstractTimeStampedModel):
    order = models.PositiveIntegerField(_('Order'))
    image = models.ImageField(_('Image'), upload_to='venue/images/')
    is_main = models.BooleanField(_('Is Main'), default=False)
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='images', verbose_name=_('Venue'))
    parsing_id = models.CharField(_('Parsing ID'), max_length=500, blank=True, null=True, help_text=_('ID from parsing system'))

    class Meta:
        verbose_name = _('Venue Image')
        verbose_name_plural = _('Venue Images')
        ordering = ['order']

    def __str__(self):
        return f'{self.venue} - {self.order}'


class VenueSocialMedia(AbstractTimeStampedModel):
    class SocialType(models.TextChoices):
        FACEBOOK = 'facebook', _('Facebook')
        INSTAGRAM = 'instagram', _('Instagram')
        TELEGRAM = 'telegram', _('Telegram')
        TWITTER = 'twitter', _('Twitter')
        TIKTOK = 'tiktok', _('TikTok')
        OTHER = 'other', _('Other')

    social_type = models.CharField(_('Social Type'), max_length=50, choices=SocialType.choices)
    link = models.URLField(_('Link'))
    is_active = models.BooleanField(_('Is Active'), default=True)
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, related_name='social_links',
                              verbose_name=_('Venue'))

    class Meta:
        verbose_name = _('Venue Social Media')
        verbose_name_plural = _('Venue Social Media')

    def __str__(self):
        return f'{self.venue} - {self.get_social_type_display()}'


class VenueReview(AbstractTimeStampedModel):
    user = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('User'))
    full_name = models.CharField(_('Full Name'), max_length=255)
    description = models.TextField(_('Description'))
    rating = models.DecimalField(_('Rating'), max_digits=3, decimal_places=2)
    is_approved = models.BooleanField(_('Is Approved'), null=True, blank=True)
    parsing_id = models.CharField(_('Parsing ID'), max_length=500, blank=True, null=True, help_text=_('ID from parsing system'))

    class Meta:
        verbose_name = _('Venue Review')
        verbose_name_plural = _('Venue Reviews')
        ordering = ['-id']

    def __str__(self):
        return f'{self.full_name} ({self.rating})'
