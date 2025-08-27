from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users.models import (
    User,
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal info"), {
            "fields": (
                "full_name",
                "date_of_birth",
                "gender",
                "role",
                "avatar",
                "language",
                "is_notification_enabled",
                "telegram_id",
            )
        }),
        (_("Permissions"), {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        (_("Important dates"), {
            "fields": (
                "last_login",
                "date_joined"
            ),
            "classes": ("collapse",)
        }),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone_number",
                "full_name",
                "role",
                "password1",
                "password2"
            ),
        }),
    )
    list_display = (
        "phone_number",
        "full_name",
        "role",
        "is_active",
        "is_staff",
        "last_login"
    )
    list_display_links = ("full_name", "phone_number")
    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login"
    )
    search_fields = (
        "full_name",
        "phone_number",
    )
    ordering = ("-date_joined",)
    filter_horizontal = ("groups", "user_permissions",)
    readonly_fields = ("last_login", "date_joined")