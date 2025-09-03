from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.common.models import AbstractSoftDeleteModel
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.modelfields import PhoneNumberField

from apps.users.managers import UserManager


class User(AbstractUser, AbstractSoftDeleteModel):
    class Language(models.TextChoices):
        ENGLISH = "en", _("English")
        RUSSIAN = "ru", _("Russian")
        UZBEK = "uz", _("Uzbek")

    class Role(models.TextChoices):
        USER = "user", _("User")
        HOST = "host", _("Host")
    
    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')

    username = None
    email = None
    first_name = None
    last_name = None

    EMAIL_FIELD = None
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["full_name", 'date_of_birth']

    phone_number = PhoneNumberField(_("Phone number"), max_length=64, unique=True)
    full_name = models.CharField(_("Full Name"), max_length=255)
    date_of_birth = models.DateField(_("Date of Birth"))
    role = models.CharField(_("Role"), max_length=20, choices=Role.choices, default=Role.USER)
    gender = models.CharField(_("Gender"), max_length=20, choices=Gender.choices, null=True, blank=True)
    language = models.CharField(_("Language"), max_length=3, choices=Language.choices, default=Language.UZBEK)
    avatar = models.ImageField(_('Avatar'), upload_to='users/avatar', null=True, blank=True)
    is_notification_enabled = models.BooleanField(default=True, verbose_name=_("Notification Enabled"))
    telegram_id = models.CharField(_('Telegram ID'), max_length=255, unique=True, null=True, blank=True)
    venue = models.ForeignKey('venues.Venue', on_delete=models.CASCADE, null=True, blank=True)

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.full_name} - {self.phone_number}"

    @property
    def tokens(self) -> dict:
        token = RefreshToken.for_user(self)
        token['role'] = self.role
        return {"access_token": str(token.access_token), "refresh_token": str(token)}

    def clean(self):
        if self.role == self.Role.HOST and self.venue is None:
            raise ValidationError({'venue': _("Venue is required for host")})

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.phone_number = f"deleted_{self.id}__{self.phone_number}"
        self.save(update_fields=['is_deleted', 'deleted_at', 'phone_number', 'is_active'])