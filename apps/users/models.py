from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from apps.common.models import BaseModel
from .choices import LANGUAGE_CHOICES, GENDER_CHOICES, DEFAULT_LANGUAGE
from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):
    """
    Custom user manager for User model that uses phone_number instead of username
    """

    def create_user(self, phone_number, full_name, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        if not full_name:
            raise ValueError('The Full Name field must be set')

        user = self.model(
            phone_number=phone_number,
            full_name=full_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, full_name, password, **extra_fields)


class User(AbstractUser, BaseModel):
    username = models.CharField(max_length=255, verbose_name=_("Username"), unique=True, null=True)
    phone_number = PhoneNumberField(unique=True, verbose_name=_("Phone Number"))
    full_name = models.CharField(max_length=255, verbose_name=_("Full Name"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Date of Birth"))
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default=DEFAULT_LANGUAGE,
        verbose_name=_("Language")
    )
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        null=True,
        blank=True,
        verbose_name=_("Gender")
    )
    photo = models.ImageField(
        upload_to='user_photos/',
        null=True,
        blank=True,
        verbose_name=_("Profile Photo")
    )
    is_notification_enabled = models.BooleanField(default=True, verbose_name=_("Notification Enabled"))

    # Use phone_number as the username field
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    # Use custom user manager
    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        db_table = 'users'
        ordering = ['-created_at']

    @property
    def tokens(self):
        token = RefreshToken.for_user(self)
        return {"access": str(token.access_token), "refresh": str(token)}

    def has_usable_password(self):
        """Check if user has a usable password"""
        return bool(self.password and self.password.strip())

    def __str__(self):
        return self.full_name or str(self.phone_number)

    def get_full_name(self):
        return self.full_name
