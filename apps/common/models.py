from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
# from django.contrib.gis.db import models as gis_models
from phonenumber_field.modelfields import PhoneNumberField
from versatileimagefield.fields import VersatileImageField

from solo.models import SingletonModel

from apps.common.managers import SoftDeleteQuerySet

class AbstractTimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True
        
class AbstractSoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False, verbose_name=_("Is deleted"))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Deleted at"))

    objects = SoftDeleteQuerySet.as_manager()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super().delete()

    class Meta:
        abstract = True

class GlobalSettings(SingletonModel):
    """
    Global application settings.
    """
    backoffice_url = models.URLField(
        _('Backoffice URL'),
        help_text=_('URL of the backoffice'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('Global Settings')
        verbose_name_plural = _('Global Settings')

class CompanyProfile(SingletonModel):
    """
    Singleton model for managing company profile and support information.
    This model stores company-wide settings, support information, and other company details.
    Only one instance of this model can exist.
    """
    instagram_link = models.URLField(_("Instagram Link"))
    telegram_link = models.URLField(_("Telegram Link"))
    web_site_link = models.URLField(_("Web Site Link"))
    # Support Contact Information
    support_email = models.EmailField(
        verbose_name=_('Support Email'),
        help_text=_('General support email address')
    )
    support_telegram_link = models.URLField(_("Support Telegram Link"))
    support_phone_number = PhoneNumberField(_("Phone Number"))


    about = models.TextField(
        verbose_name=_('About'),
        help_text=_('Information about the company team')
    )

    class Meta:
        verbose_name = _('Company Profile')
        verbose_name_plural = _('Company Profile')

    def __str__(self):
        return "Company Profile"


class Country(AbstractTimeStampedModel):
    name = models.CharField(max_length=128)
    alpha_2 = models.CharField(max_length=2, unique=True)
    alpha_3 = models.CharField(max_length=3, unique=True)
    numeric = models.CharField(max_length=3, unique=True)

    def __str__(self):
        return self.name


class Region(AbstractTimeStampedModel):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')
    name = models.CharField(max_length=128)
    code = models.CharField(max_length=16, unique=True)
    # geometry = gis_models.MultiPolygonField(null=True, blank=True, srid=4326)


    def __str__(self):
        return f"{self.name}, {self.country.alpha_2}"


class UserVenueFavourite(AbstractTimeStampedModel):
    venue = models.ForeignKey('venues.Venue', related_name='user_venue_favourites', on_delete=models.CASCADE, verbose_name=_('Venue'))
    user = models.ForeignKey('users.User', related_name='user_venue_favourites', on_delete=models.CASCADE, verbose_name=_('User'))

    class Meta:
        verbose_name = _('User Venue Favourite')
        verbose_name_plural = _('User Venue Favourites')
        unique_together = ('venue', 'user')

    def __str__(self):
        return f'{self.user} → {self.venue}'


class UserSearchHistory(AbstractTimeStampedModel):
    text = models.CharField(_('Text'), max_length=255)
    user = models.ForeignKey('users.User', related_name='search_histories', on_delete=models.CASCADE, verbose_name=_('User'))

    class Meta:
        verbose_name = _('User Search History')
        verbose_name_plural = _('User Search Histories')
        ordering = ['-id']

    def __str__(self):
        return f'{self.user} - {self.text}'


class Facility(AbstractTimeStampedModel):
    title = models.CharField(_('Title'), max_length=255)
    icon = VersatileImageField(_('Icon'), upload_to='facilities/icons/', blank=True, null=True)
    quick_access = models.BooleanField(_('Quick Access'), default=False)

    class Meta:
        verbose_name = _('Facility')
        verbose_name_plural = _('Facilities')

    def __str__(self):
        return self.title


class Tag(AbstractTimeStampedModel):
    title = models.CharField(_('Title'), max_length=255)

    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')

    def __str__(self):
        return self.title


class StoryGroup(AbstractTimeStampedModel):
    """Story group/page that contains multiple story items"""
    title = models.CharField(_('Title'), max_length=255, blank=True)
    background_image = VersatileImageField(
        _('Background Image'),
        upload_to='stories/background_images/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(_("Is Active"), default=True)
    expires_at = models.DateTimeField(_('Expires At'), null=True, blank=True)
    order = models.PositiveIntegerField(_('Order'), default=0)
    
    class Meta:
        verbose_name = _('Story Group')
        verbose_name_plural = _('Story Groups')
        ordering = ('order', '-created_at')
    
    def __str__(self):
        return f'Story Group - {self.title or "Untitled"} ({self.story_items.count()} items)'
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class StoryItem(AbstractTimeStampedModel):
    """Individual story item within a story group"""
    story_group = models.ForeignKey(StoryGroup, on_delete=models.CASCADE, related_name='story_items', verbose_name=_('Story Group'))
    
    media = models.FileField(_('Media'), upload_to='stories/')
    venue = models.ForeignKey('venues.Venue', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Venue'))
    description = models.TextField(_('Text'), blank=True)
    link = models.URLField(_('Link'), blank=True)
    order = models.PositiveIntegerField(_('Order'), default=0)
    is_active = models.BooleanField(_("Is Active"), default=True)
    
    class Meta:
        verbose_name = _('Story Item')
        verbose_name_plural = _('Story Items')
        ordering = ('story_group', 'order', 'created_at')
    
    def __str__(self):
        return f'Story Item {self.order} - {self.story_group}'
    
    def save(self, *args, **kwargs):
        if not self.order:
            # Auto-assign order if not set
            last_order = StoryItem.objects.filter(story_group=self.story_group).aggregate(
                models.Max('order')
            )['order__max'] or 0
            self.order = last_order + 1
        super().save(*args, **kwargs)


class OTPLog(AbstractTimeStampedModel):
    class CarrierStatus(models.TextChoices):
        WAITING = 'WAITING', _("Waiting")
        STORED = 'STORED', _("Stored")
        ACCEPTED = 'ACCEPTED', _("Accepted")
        REJECTED = 'REJECTED', _("Rejected")
        DELIVERED = 'DELIVERED', _("Delivered")

    message_id = models.CharField(_('Message ID'), max_length=255)
    phone_number = PhoneNumberField(_('Phone Number'))
    text = models.TextField(_('Text'))

    is_sent = models.BooleanField(_('Is sent'), default=False)
    sent_at = models.DateTimeField(_('Sent at'), null=True)

    is_delivered = models.BooleanField(_('Is delivered'), default=False)
    delivered_at = models.DateTimeField(_('Delivered at'), null=True)

    response_log = models.JSONField(_('Response log'), default=dict, blank=True)

    callback_log = models.JSONField(_('Callback log'), default=dict, blank=True)

    status = models.CharField(_('Carrier status'), max_length=20, choices=CarrierStatus.choices,
                              default=CarrierStatus.WAITING)

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return str(self.phone_number)
