from modeltranslation.translator import TranslationOptions, register

from apps.notifications.models import NotificationTemplate, Notification


@register(NotificationTemplate)
class NotificationTemplateTranslationOption(TranslationOptions):
    fields = ('title', 'body_text', 'body_html')


@register(Notification)
class NotificationTranslationOption(TranslationOptions):
    fields = ('title', 'body_text', 'body_html')


__all__ = [
    'NotificationTemplateTranslationOption',
    'NotificationTranslationOption',
]
