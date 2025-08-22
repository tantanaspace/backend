from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.visits.models import Visit, VisitGuest


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'venue', 'zone', 'booked_date', 'booked_time', 'number_of_guests', 'status')
    list_filter = ('status', 'booked_date', 'venue', 'zone')
    search_fields = ('id', 'user__full_name', 'user__phone_number', 'venue__name', 'waiter_full_name')
    ordering = ('-booked_date', '-booked_time')
    autocomplete_fields = ('user', 'venue', 'zone')
    date_hierarchy = 'booked_date'
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'venue', 'zone', 'number_of_guests')
        }),
        (_('Booking Details'), {
            'fields': ('booked_date', 'booked_time', 'status')
        }),
        (_('Service Information'), {
            'fields': ('waiter_full_name',)
        }),
        (_('Timestamps'), {
            'fields': ('started_at', 'finished_at', 'paid_at', 'closed_at')
        }),
    )


@admin.register(VisitGuest)
class VisitGuestAdmin(admin.ModelAdmin):
    list_display = ('user', 'visit', 'is_joined', 'joined_at')
    list_filter = ('is_joined', 'visit__status')
    search_fields = ('user__full_name', 'user__phone_number', 'visit__id')
    ordering = ('-id',)
    autocomplete_fields = ('user', 'visit')
    
    fieldsets = (
        (_('Guest Information'), {
            'fields': ('user', 'visit')
        }),
        (_('Status'), {
            'fields': ('is_joined', 'joined_at')
        }),
    )
