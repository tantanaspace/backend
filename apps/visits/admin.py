from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from apps.visits.models import Visit, VisitGuest


class VisitGuestInline(admin.TabularInline):
    model = VisitGuest
    extra = 0
    fields = ('user', 'is_joined', 'joined_at')
    readonly_fields = ('joined_at',)
    autocomplete_fields = ('user',)
    ordering = ('-is_joined', 'user__full_name')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_info', 'venue', 'zone', 'booked_date', 'booked_time', 
        'number_of_guests', 'status', 'created_by', 'guests_count'
    )
    list_display_links = ('id', 'user_info')
    list_filter = (
        'status', 'created_by', 'booked_date', 'venue', 'zone', 
        'started_at', 'finished_at', 'cancelled_at'
    )
    search_fields = (
        'id', 'user__full_name', 'user__phone_number', 'user_full_name', 
        'user_phone_number', 'venue__name', 'host__full_name', 'table_number'
    )
    ordering = ('-booked_date', '-booked_time')
    autocomplete_fields = ('user', 'venue', 'zone', 'host')
    date_hierarchy = 'booked_date'
    readonly_fields = ('guests_count', 'visit_duration', 'cancelled_at')
    list_per_page = 25
    list_max_show_all = 1000
    list_select_related = ('user', 'venue', 'zone', 'host')
    
    inlines = [VisitGuestInline]
    
    fieldsets = (
        (_('Visit Information'), {
            'fields': (
                'user', 'user_phone_number', 'user_full_name', 
                'venue', 'zone', 'table_number', 'number_of_guests'
            )
        }),
        (_('Booking Details'), {
            'fields': ('booked_date', 'booked_time', 'status', 'created_by')
        }),
        (_('Host Information'), {
            'fields': ('host',),
            'classes': ('collapse',)
        }),
        (_('Timeline'), {
            'fields': (
                'started_at', 'finished_at', 'paid_at', 'closed_at', 
                'visit_duration'
            ),
            'classes': ('collapse',)
        }),
        (_('Cancellation'), {
            'fields': ('cancelled_at', 'cancel_reason'),
            'classes': ('collapse',)
        }),
        (_('Guests'), {
            'fields': ('guests_count',),
            'classes': ('collapse',)
        }),
    )
    
    def user_info(self, obj):
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.id])
            return format_html(
                '<a href="{}">{} ({})</a>',
                url, obj.user.full_name, obj.user.phone_number
            )
        return f"{obj.user_full_name} ({obj.user_phone_number})"
    user_info.short_description = _('User')
    user_info.admin_order_field = 'user__full_name'
    
    def guests_count(self, obj):
        count = obj.guests.count()
        joined_count = obj.guests.filter(is_joined=True).count()
        return f"{joined_count}/{count}"
    guests_count.short_description = _('Guests (Joined/Total)')
    
    def visit_duration(self, obj):
        if obj.started_at and obj.finished_at:
            duration = obj.finished_at - obj.started_at
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"
        return "-"
    visit_duration.short_description = _('Duration')
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'guests', 'guests__user'
        )


@admin.register(VisitGuest)
class VisitGuestAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user_info', 'visit_info', 'is_joined', 'joined_at', 'visit_status'
    )
    list_display_links = ('id', 'user_info')
    list_filter = (
        'is_joined', 'visit__status', 'visit__venue', 'joined_at', 
        'visit__booked_date'
    )
    search_fields = (
        'user__full_name', 'user__phone_number', 'visit__id', 
        'visit__venue__name', 'visit__user_full_name'
    )
    ordering = ('-id',)
    autocomplete_fields = ('user', 'visit')
    readonly_fields = ('joined_at',)
    list_per_page = 50
    list_max_show_all = 1000
    list_select_related = ('user', 'visit', 'visit__venue')
    
    fieldsets = (
        (_('Guest Information'), {
            'fields': ('user', 'visit')
        }),
        (_('Join Status'), {
            'fields': ('is_joined', 'joined_at')
        }),
    )
    
    def user_info(self, obj):
        url = reverse('admin:users_user_change', args=[obj.user.id])
        return format_html(
            '<a href="{}">{} ({})</a>',
            url, obj.user.full_name, obj.user.phone_number
        )
    user_info.short_description = _('User')
    user_info.admin_order_field = 'user__full_name'
    
    def visit_info(self, obj):
        url = reverse('admin:visits_visit_change', args=[obj.visit.id])
        return format_html(
            '<a href="{}">Visit #{} - {}</a>',
            url, obj.visit.id, obj.visit.venue.name
        )
    visit_info.short_description = _('Visit')
    visit_info.admin_order_field = 'visit__id'
    
    def visit_status(self, obj):
        status_colors = {
            'booked': 'blue',
            'started': 'orange', 
            'finished': 'green',
            'payment': 'purple',
            'closed': 'gray',
            'cancelled': 'red'
        }
        color = status_colors.get(obj.visit.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.visit.get_status_display()
        )
    visit_status.short_description = _('Visit Status')
    visit_status.admin_order_field = 'visit__status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'visit', 'visit__venue'
        )
