from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.venues.models import (
    Company, VenueCategory, Venue, VenueZone, VenueWorkingHour,
    VenueImage, VenueSocialMedia, VenueReview
)


class VenueWorkingHourInline(admin.TabularInline):
    model = VenueWorkingHour
    extra = 0
    fields = ('weekday', 'opening_time', 'closing_time')
    ordering = ('weekday',)
    autocomplete_fields = ('venue',)


class VenueImageInline(admin.TabularInline):
    model = VenueImage
    extra = 0
    fields = ('image', 'order', 'is_main')
    ordering = ('order',)
    autocomplete_fields = ('venue',)


class VenueSocialMediaInline(admin.TabularInline):
    model = VenueSocialMedia
    extra = 0
    fields = ('social_type', 'link', 'is_active')
    ordering = ('social_type',)
    autocomplete_fields = ('venue',)


class VenueReviewInline(admin.TabularInline):
    model = VenueReview
    extra = 0
    fields = ('full_name', 'rating', 'is_approved', 'description')
    readonly_fields = ('full_name', 'rating', 'description')
    ordering = ('-created_at',)
    max_num = 5
    autocomplete_fields = ('venue', 'user')

class VenueZoneInline(admin.TabularInline):
    model = VenueZone
    extra = 0
    fields = ('name', 'photo_view', 'external_id')
    autocomplete_fields = ('venue',)
    ordering = ('name',)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'external_id', 'parsing_id', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'external_id', 'parsing_id')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    list_max_show_all = 1000
    
    fieldsets = (
        (None, {'fields': ('name', 'logo', 'external_id', 'parsing_id')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(VenueCategory)
class VenueCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_type', 'order', 'recommended', 'is_active', 'created_at')
    list_editable = ('order', 'recommended', 'is_active')
    list_filter = ('category_type', 'is_active', 'recommended', 'created_at')
    search_fields = ('title',)
    ordering = ('order', 'title')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    list_max_show_all = 1000
    
    fieldsets = (
        (None, {'fields': ('title', 'icon', 'category_type', 'order', 'recommended', 'is_active')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'rating', 'is_active', 'created_at')
    list_filter = ('is_active', 'company', 'categories', 'rating', 'created_at')
    search_fields = ('name', 'description', 'external_id', 'parsing_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('categories', 'facilities', 'tags')
    autocomplete_fields = ('company', 'background_image')
    list_per_page = 25
    list_max_show_all = 500
    list_select_related = ('company',)
    
    inlines = [
        VenueWorkingHourInline,
        VenueImageInline,
        VenueSocialMediaInline,
        VenueReviewInline,
        VenueZoneInline,
    ]
    
    fieldsets = (
        (_('Basic'), {'fields': ('name', 'company', 'description', 'external_id', 'parsing_id')}),
        (_('Location'), {'fields': ('location', 'longitude', 'latitude')}),
        (_('Media & Categories'), {'fields': ('background_image', 'categories', 'facilities', 'tags')}),
        (_('Rating'), {'fields': ('rating',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company').prefetch_related(
            'categories', 'facilities', 'tags', 'background_image'
        )


@admin.register(VenueWorkingHour)
class VenueWorkingHourAdmin(admin.ModelAdmin):
    list_display = ('venue', 'weekday', 'opening_time', 'closing_time')
    list_filter = ('weekday', 'venue', 'created_at')
    search_fields = ('venue__name',)
    ordering = ('venue__name', 'weekday')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('venue',)
    list_per_page = 100
    list_max_show_all = 1000
    list_select_related = ('venue',)
    
    fieldsets = (
        (None, {'fields': ('venue', 'weekday', 'opening_time', 'closing_time')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('venue')


@admin.register(VenueImage)
class VenueImageAdmin(admin.ModelAdmin):
    list_display = ('venue', 'order', 'is_main', 'created_at')
    list_editable = ('order', 'is_main')
    list_filter = ('is_main', 'venue', 'created_at')
    search_fields = ('venue__name',)
    ordering = ('venue__name', 'order')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('venue',)
    list_per_page = 100
    list_max_show_all = 1000
    list_select_related = ('venue',)
    
    fieldsets = (
        (None, {'fields': ('venue', 'image', 'order', 'is_main')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('venue')


@admin.register(VenueSocialMedia)
class VenueSocialMediaAdmin(admin.ModelAdmin):
    list_display = ('venue', 'social_type', 'link', 'is_active')
    list_filter = ('social_type', 'is_active', 'venue')
    search_fields = ('venue__name', 'link')
    ordering = ('venue__name', 'social_type')
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('venue',)
    list_per_page = 100
    list_max_show_all = 1000
    list_select_related = ('venue',)
    
    fieldsets = (
        (None, {'fields': ('venue', 'social_type', 'link', 'is_active')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('venue')


@admin.register(VenueZone)
class VenueZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'external_id', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'external_id')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 100
    list_max_show_all = 1000
    
    fieldsets = (
        (None, {'fields': ('name', 'photo_view', 'venue', 'external_id')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(VenueReview)
class VenueReviewAdmin(admin.ModelAdmin):
    list_display = ('venue', 'full_name', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'venue', 'created_at')
    search_fields = ('full_name', 'description', 'venue__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('venue', 'user')
    list_per_page = 50
    list_max_show_all = 1000
    list_select_related = ('venue', 'user')
    
    fieldsets = (
        (None, {'fields': ('user', 'venue', 'full_name', 'description', 'rating', 'is_approved')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('venue', 'user')
