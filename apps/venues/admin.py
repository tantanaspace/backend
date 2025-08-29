from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.venues.models import (
    Company, VenueCategory, Venue, VenueZone, VenueWorkingHour,
    VenueImage, VenueSocialMedia, VenueReview
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'external_id', 'parsing_id', 'created_at')
    search_fields = ('name', 'external_id', 'parsing_id')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'logo', 'external_id', 'parsing_id')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VenueCategory)
class VenueCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'recommended', 'is_active', 'parsing_id', 'created_at')
    list_editable = ('order', 'recommended', 'is_active')
    search_fields = ('title', 'parsing_id')
    list_filter = ('is_active', 'created_at')
    ordering = ('order', 'title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'icon', 'order', 'recommended', 'is_active', 'parsing_id')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'location', 'rating', 'parsing_id', 'created_at')
    list_filter = ('company', 'categories', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'location', 'external_id', 'parsing_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('categories', 'facilities', 'tags')
    autocomplete_fields = ('company', 'background_image')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'company', 'description', 'external_id', 'parsing_id')
        }),
        (_('Location'), {
            'fields': ('location', 'longitude', 'latitude')
        }),
        (_('Media & Categories'), {
            'fields': ('background_image', 'categories', 'facilities', 'tags')
        }),
        (_('Rating'), {
            'fields': ('rating',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VenueZone)
class VenueZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'external_id', 'created_at')
    search_fields = ('name', 'external_id')
    list_filter = ('created_at', 'updated_at')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'photo_view', 'external_id')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VenueWorkingHour)
class VenueWorkingHourAdmin(admin.ModelAdmin):
    list_display = ('venue', 'weekday', 'opening_time', 'closing_time')
    list_filter = ('weekday', 'venue', 'created_at')
    search_fields = ('venue__name',)
    ordering = ('venue__name', 'weekday', 'opening_time')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('venue',)
    
    fieldsets = (
        (None, {
            'fields': ('venue', 'weekday', 'opening_time', 'closing_time')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ('venue', 'order', 'is_main', 'parsing_id', 'created_at')
    list_editable = ('order', 'is_main')
    list_filter = ('is_main', 'venue', 'created_at')
    search_fields = ('venue__name', 'parsing_id')
    ordering = ('venue__name', 'order')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('venue',)
    
    fieldsets = (
        (None, {
            'fields': ('venue', 'image', 'order', 'is_main', 'parsing_id')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VenueSocialMedia)
class VenueSocialMediaAdmin(admin.ModelAdmin):
    list_display = ('venue', 'social_type', 'link', 'is_active', 'created_at')
    list_filter = ('social_type', 'is_active', 'venue', 'created_at')
    search_fields = ('venue__name', 'link')
    ordering = ('venue__name', 'social_type')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('venue',)
    
    fieldsets = (
        (None, {
            'fields': ('venue', 'social_type', 'link', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(VenueReview)
class VenueReviewAdmin(admin.ModelAdmin):
    list_display = ('venue','full_name', 'rating', 'is_approved', 'user', 'parsing_id', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('full_name', 'description', 'user__full_name', 'parsing_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('user',)
    
    fieldsets = (
        (None, {
            'fields': ('user', 'venue', 'full_name', 'description', 'rating', 'is_approved', 'parsing_id')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
