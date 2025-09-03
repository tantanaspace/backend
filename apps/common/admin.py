from django.contrib import admin
from django.utils.translation import gettext_lazy as _

# from leaflet.admin import LeafletGeoAdmin
from modeltranslation.admin import TabbedTranslationAdmin

from apps.common.models import Country, GlobalSettings, CompanyProfile, Region, UserVenueFavourite, UserSearchHistory, Facility, Tag, OTPLog, StoryGroup, StoryItem
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
class FacilityAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    list_display = ('title', 'quick_access')
    search_fields = ('title',)
    ordering = ('title',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'icon', 'quick_access')
        }),
    )


@admin.register(Tag)
class TagAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    ordering = ('title',)
    
    fieldsets = (
        (None, {
            'fields': ('title',)
        }),
    )


class StoryItemInline(admin.TabularInline):
    model = StoryItem
    extra = 0
    fields = ('media', 'venue', 'description', 'link', 'order', 'is_active')
    ordering = ('order',)
    autocomplete_fields = ('story_group', 'venue')


@admin.register(StoryGroup)
class StoryGroupAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    list_display = ('title', 'background_image_preview', 'story_items_count', 'is_active', 'is_expired', 'order', 'created_at')
    list_filter = ('is_active', 'created_at', 'expires_at')
    search_fields = ('title',)
    ordering = ('order', '-created_at')
    readonly_fields = ('created_at', 'updated_at', 'background_image_preview')
    list_per_page = 25
    list_max_show_all = 500
    
    inlines = [StoryItemInline]
    
    fieldsets = (
        (None, {'fields': ('title', 'background_image', 'is_active', 'order')}),
        (_('Expiration'), {'fields': ('expires_at',)}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def story_items_count(self, obj):
        return obj.story_items.count()
    story_items_count.short_description = _('Story Items')
    
    def background_image_preview(self, obj):
        if obj.background_image:
            return f'<img src="{obj.background_image.thumbnail["100x100"].url}" width="50" height="50" />'
        return '-'
    background_image_preview.short_description = _('Background Image')
    background_image_preview.allow_tags = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('story_items')


@admin.register(StoryItem)
class StoryItemAdmin(TabbedTranslationAdmin, admin.ModelAdmin):
    list_display = ('story_group', 'venue', 'media_preview', 'order', 'is_active', 'created_at')
    list_filter = ('is_active', 'venue', 'story_group', 'created_at')
    search_fields = ('story_group__title', 'venue__name', 'description')
    ordering = ('story_group', 'order')
    readonly_fields = ('created_at', 'updated_at', 'media_preview')
    autocomplete_fields = ('story_group', 'venue')
    list_per_page = 100
    list_max_show_all = 1000
    list_select_related = ('story_group', 'venue')
    
    fieldsets = (
        (None, {'fields': ('story_group', 'venue', 'media', 'order', 'is_active')}),
        (_('Content'), {'fields': ('description', 'link')}),
        (_('Timestamps'), {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    def media_preview(self, obj):
        if obj.media:
            if obj.media.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return f'<img src="{obj.media.url}" width="50" height="50" />'
            else:
                return f'<video width="50" height="50" controls><source src="{obj.media.url}"></video>'
        return '-'
    media_preview.short_description = _('Media Preview')
    media_preview.allow_tags = True
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('story_group', 'venue')


@admin.register(OTPLog)
class OTPLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'phone_number',
        'message_id',
        'is_sent',
        'is_delivered',
        'status',
        'sent_at',
        'created_at'
    )
    
    list_filter = (
        'is_sent',
        'is_delivered',
        'status',
        'sent_at',
        'delivered_at',
        'created_at'
    )
    
    search_fields = (
        'phone_number',
        'message_id',
        'text'
    )
    
    readonly_fields = (
        'created_at',
        'updated_at',
        'message_id'
    )
    
    ordering = ('-created_at',)
    list_per_page = 50
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': (
                'message_id',
                'phone_number',
                'text'
            )
        }),
        (_('SMS Status'), {
            'fields': (
                'is_sent',
                'sent_at',
                'is_delivered',
                'delivered_at',
                'status'
            )
        }),
        (_('Logs'), {
            'fields': (
                'response_log',
                'callback_log'
            ),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        # OTPLog is created automatically, do not create manually
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow editing for status updates
        return True
    
    def has_delete_permission(self, request, obj=None):
        # Allow deletion for clearing old logs
        return True