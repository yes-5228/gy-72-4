from rest_framework import serializers

from apps.orders.serializers import OrderSerializer

from .models import DeliveryTask


class DeliveryTaskSerializer(serializers.ModelSerializer):
    order_detail = OrderSerializer(source="order", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = DeliveryTask
        fields = [
            "id",
            "order",
            "order_detail",
            "courier_name",
            "courier_phone",
            "route",
            "status",
            "status_label",
            "estimated_arrival",
            "delivered_at",
            "updated_at",
        ]
