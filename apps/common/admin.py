from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# from leaflet.admin import LeafletGeoAdmin
from modeltranslation.admin import TabbedTranslationAdmin

from apps.common.models import Country, GlobalSettings, CompanyProfile, Region, UserVenueFavourite, UserSearchHistory, Facility, Tag, Story
from apps.common.translation import *  # noqa


@admin.register(GlobalSettings)
class GlobalSettingsAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'backoffice_url'
    )

    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the only instance
        return False


@admin.register(CompanyProfile)
class CompanyProfileAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    list_display = (
        'id',
        'support_email',
        'support_phone_number',
        'web_site_link'
    )

    fieldsets = (
        (_('Social Media Links'), {
            'fields': (
                'instagram_link',
                'telegram_link',
                'web_site_link'
            )
        }),
        (_('Support Contact Information'), {
            'fields': (
                'support_email',
                'support_telegram_link',
                'support_phone_number'
            )
        }),
        (_('About'), {
            'fields': ('about',)
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the only instance
        return False
    

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'alpha_2', 'alpha_3', 'numeric')
    search_fields = ('name', 'alpha_2', 'alpha_3', 'numeric')
    ordering = ('name',)
    list_per_page = 25


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'code')
    search_fields = ('name', 'country__name', 'country__alpha_2', 'code')
    list_filter = ('country',)
    autocomplete_fields = ('country',)
    ordering = ('country__name', 'name')
    list_per_page = 25


@admin.register(UserVenueFavourite)
class UserVenueFavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'venue', 'created_at')
    list_filter = ('created_at', 'venue__company')
    search_fields = ('user__full_name', 'user__phone_number', 'venue__name')
    ordering = ('-created_at',)
    autocomplete_fields = ('user', 'venue')
    
    fieldsets = (
        (None, {
            'fields': ('user', 'venue')
        }),
    )


@admin.register(UserSearchHistory)
class UserSearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__full_name', 'user__phone_number')
    ordering = ('-created_at',)
    autocomplete_fields = ('user',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'text')
        }),
    )


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ('title',)
    
    fieldsets = (
        (None, {
            'fields': ('title',)
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ('title',)
    
    fieldsets = (
        (None, {
            'fields': ('title',)
        }),
    )


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('venue', 'link', 'is_active', 'created_at')
    list_filter = ('is_active', 'venue__company', 'created_at')
    search_fields = ('venue__name', 'link')
    ordering = ('-created_at',)
    autocomplete_fields = ('venue',)
    
    fieldsets = (
        (None, {
            'fields': ('venue', 'media', 'link', 'is_active')
        }),
    )
