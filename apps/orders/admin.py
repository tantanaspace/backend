from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = (
        "product_name",
        "quantity",
        "unit_price",
        "total_price",
        "status",
        "ordered_at",
        "served_at",
    )
    readonly_fields = ("total_price", "ordered_at", "served_at", "cancelled_at")
    autocomplete_fields = ()
    ordering = ("-created_at",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("order")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "visit_info",
        "waiter_full_name",
        "total_amount",
        "service_fee",
        "percentage_of_service",
        "items_count",
        "created_at",
    )
    list_display_links = ("id", "visit_info")
    list_filter = ("created_at", "updated_at", "visit__status", "visit__venue")
    search_fields = (
        "id",
        "visit__id",
        "visit__venue__name",
        "visit__user_full_name",
        "visit__user__full_name",
        "waiter_full_name",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "items_count", "total_calculated")
    autocomplete_fields = ("visit",)
    list_per_page = 25
    list_max_show_all = 1000
    list_select_related = ("visit", "visit__venue", "visit__user")

    inlines = [OrderItemInline]

    fieldsets = (
        (_("Order Information"), {"fields": ("visit", "waiter_full_name")}),
        (
            _("Financial Details"),
            {
                "fields": (
                    "percentage_of_service",
                    "service_fee",
                    "total_amount",
                    "total_calculated",
                )
            },
        ),
        (_("Items Summary"), {"fields": ("items_count",), "classes": ("collapse",)}),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def visit_info(self, obj):
        url = reverse("admin:visits_visit_change", args=[obj.visit.id])
        return format_html(
            '<a href="{}">Visit #{} - {}</a>', url, obj.visit.id, obj.visit.venue.name
        )

    visit_info.short_description = _("Visit")
    visit_info.admin_order_field = "visit__id"

    def items_count(self, obj):
        count = obj.items.count()
        served_count = obj.items.filter(status=OrderItem.OrderItemStatus.SERVED).count()
        return f"{served_count}/{count}"

    items_count.short_description = _("Items (Served/Total)")

    def total_calculated(self, obj):
        calculated_total = sum(item.total_price for item in obj.items.all())
        return f"${calculated_total:.2f}"

    total_calculated.short_description = _("Calculated Total")

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .prefetch_related("items", "visit__venue", "visit__user")
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_name",
        "order_info",
        "quantity",
        "unit_price",
        "total_price",
        "status",
        "ordered_at",
        "served_at",
    )
    list_display_links = ("id", "product_name")
    list_filter = (
        "status",
        "created_at",
        "ordered_at",
        "served_at",
        "order__visit__venue",
        "order__visit__status",
    )
    search_fields = (
        "product_name",
        "order__id",
        "order__visit__id",
        "order__visit__venue__name",
        "order__waiter_full_name",
    )
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "total_price",
        "ordered_at",
        "served_at",
        "cancelled_at",
    )
    autocomplete_fields = ("order",)
    list_per_page = 50
    list_max_show_all = 1000
    list_select_related = ("order", "order__visit", "order__visit__venue")

    fieldsets = (
        (
            _("Item Information"),
            {"fields": ("order", "product_name", "quantity", "status")},
        ),
        (_("Pricing"), {"fields": ("unit_price", "total_price")}),
        (
            _("Timeline"),
            {
                "fields": ("ordered_at", "served_at", "cancelled_at"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def order_info(self, obj):
        url = reverse("admin:orders_order_change", args=[obj.order.id])
        return format_html(
            '<a href="{}">Order #{} - {}</a>',
            url,
            obj.order.id,
            obj.order.visit.venue.name,
        )

    order_info.short_description = _("Order")
    order_info.admin_order_field = "order__id"

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("order", "order__visit", "order__visit__venue")
        )
