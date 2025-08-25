from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# from django.contrib.gis.db import models as gis_models
from phonenumber_field.modelfields import PhoneNumberField

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
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, verbose_name=_('Venue'))
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name=_('User'))

    class Meta:
        verbose_name = _('User Venue Favourite')
        verbose_name_plural = _('User Venue Favourites')
        unique_together = ('venue', 'user')

    def __str__(self):
        return f'{self.user} → {self.venue}'


class UserSearchHistory(AbstractTimeStampedModel):
    text = models.CharField(_('Text'), max_length=255)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name=_('User'))

    class Meta:
        verbose_name = _('User Search History')
        verbose_name_plural = _('User Search Histories')
        ordering = ['-id']

    def __str__(self):
        return f'{self.user} - {self.text}'


class Facility(AbstractTimeStampedModel):
    title = models.CharField(_('Title'), max_length=255)

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


class Story(AbstractTimeStampedModel):
    venue = models.ForeignKey('venues.Venue', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('Venue'))
    media = models.FileField(_('Media'), upload_to='stories/')
    link = models.URLField(_('Link'))
    is_active = models.BooleanField(_("Is Active"), default=True)

    class Meta:
        verbose_name = _('Story')
        verbose_name_plural = _('Stories')

    def __str__(self):
        return f'Story - {self.venue if self.venue else "No Venue"}'
