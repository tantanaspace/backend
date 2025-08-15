from django.db import models
from django.utils.translation import gettext_lazy as _


class SendOTPType(models.TextChoices):
    """
    Enum for SMS types
    """
    AUTH = "auth", _("Auth")
    FORGOT_PASSWORD = "forgot_password", _("Forgot Password")
