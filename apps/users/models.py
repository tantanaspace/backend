from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.modelfields import PhoneNumberField

from apps.users.managers import UserManager


class User(AbstractUser):
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
    REQUIRED_FIELDS = ["full_name"]

    phone_number = PhoneNumberField(_("Phone number"), max_length=15, unique=True)
    full_name = models.CharField(_("Full Name"), max_length=255)
    date_of_birth = models.DateField(_("Date of Birth"), null=True, blank=True)
    role = models.CharField(_("Role"), max_length=20, choices=Role.choices)
    gender = models.CharField(_("Gender"), max_length=20, choices=Gender.choices, null=True, blank=True)
    language = models.CharField(_("Language"), max_length=3, choices=Language.choices, default=Language.UZBEK)
    avatar = models.ImageField(_('Avatar'), upload_to='users/avatar', null=True, blank=True)
    is_notification_enabled = models.BooleanField(default=True, verbose_name=_("Notification Enabled"))
    telegram_id = models.CharField(_('Telegram ID'), max_length=255, unique=True)

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