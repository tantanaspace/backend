from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.orders.models import Order, OrderItem
from apps.venues.models import VenueZone
from apps.visits.models import Visit, VisitGuest


class VisitDetailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "full_name", "avatar", "phone_number")


class VisitDetailGuestSerializer(serializers.ModelSerializer):
    user = VisitDetailUserSerializer(read_only=True)

    class Meta:
        model = VisitGuest
        fields = ("id", "user", "is_joined", "joined_at")


class VisitDetailOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
            "status",
            "ordered_at",
            "served_at",
            "cancelled_at",
        )


class VisitDetailOrderSerializer(serializers.ModelSerializer):
    items = VisitDetailOrderItemSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "total_amount",
            "service_fee",
            "percentage_of_service",
            "waiter_full_name",
            "items",
        )


class VisitDetailZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenueZone
        fields = (
            "id",
            "name",
        )


class VisitDetailSerializer(serializers.ModelSerializer):
    user = VisitDetailUserSerializer(read_only=True)
    zone = VisitDetailZoneSerializer(read_only=True)
    order = VisitDetailOrderSerializer(read_only=True)
    guests = VisitDetailGuestSerializer(read_only=True, many=True)

    class Meta:
        model = Visit
        fields = (
            "id",
            "user",
            "zone",
            "booked_date",
            "booked_time",
            "number_of_guests",
            "status",
            "started_at",
            "finished_at",
            "paid_at",
            "closed_at",
            "order",
            "guests",
        )
