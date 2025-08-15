from django.utils.translation import gettext_lazy as _

LANGUAGE_CHOICES = [
    ('uz', _('Uzbek')),
    ('ru', _('Russian')),
    ('en', _('English')),
]

GENDER_CHOICES = [
    ('male', _('Male')),
    ('female', _('Female'))
]

DEFAULT_LANGUAGE = 'uz'
