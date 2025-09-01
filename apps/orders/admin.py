from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'visit', 'total_amount', 'service_fee', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('id', 'visit__id', 'visit__venue__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('visit',)
    
    fieldsets = (
        (_('Order Information'), {
            'fields': ('visit',)
        }),
        (_('Financial Details'), {
            'fields': ('percentage_of_service', 'service_fee', 'total_amount')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'order', 'quantity', 'unit_price', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product_name', 'order__id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    autocomplete_fields = ('order',)
    
    fieldsets = (
        (_('Item Information'), {
            'fields': ('order', 'product_name', 'quantity')
        }),
        (_('Pricing'), {
            'fields': ('unit_price', 'total_price')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
