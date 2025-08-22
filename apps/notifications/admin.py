from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TabbedTranslationAdmin

from apps.notifications.models import NotificationTemplate, Notification, UserNotification
from apps.notifications.translation import *  # noqa


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    list_display = ('title', 'type', 'created_at', 'updated_at')
    search_fields = ('title', 'type')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'body_text', 'body_html', 'key')
        }),
    )


@admin.register(Notification)
class NotificationAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    list_display = ('title', 'type', 'status', 'is_for_everyone', 'created_at', 'updated_at')
    list_filter = ('status', 'type', 'is_for_everyone', 'created_at', 'updated_at')
    search_fields = ('title', 'body_text', 'body_html')
    ordering = ('-created_at',)
    autocomplete_fields = ['users']
    raw_id_fields = ['template']
    fieldsets = (
        (None, {
            'fields': ('title', 'body_text', 'body_html', 'is_for_everyone', 'only_push', 'type', 'status', 'template')
        }),
        (_("User Selection"), {
            'fields': ('users',)
        }),
    )


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('notification', 'user', 'is_sent', 'is_read', 'sent_at', 'created_at')
    list_filter = ('is_sent', 'is_read', 'created_at')
    search_fields = ('notification__title', 'user__username')
    ordering = ('-created_at',)
    raw_id_fields = ('notification', 'user')
    fieldsets = (
        (None, {
            'fields': ('notification', 'user', 'is_sent', 'is_read', 'sent_at', 'data')
        }),
    )
