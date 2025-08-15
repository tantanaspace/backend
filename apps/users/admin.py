from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin for the User model"""
    
    list_display = ('phone_number', 'full_name', 'language', 'gender', 'is_notification_enabled', 'is_active', 'date_joined')
    
    search_fields = ('phone_number', 'full_name', 'email')
    
    list_filter = ('language', 'gender', 'is_notification_enabled', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {'fields': ('full_name', 'email', 'date_of_birth', 'gender', 'photo')}),
        (_('Preferences'), {'fields': ('language', 'is_notification_enabled')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'password1', 'password2'),
        }),
    )
    ordering = ('-date_joined',)
    
    
