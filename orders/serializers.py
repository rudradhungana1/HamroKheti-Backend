from rest_framework import serializers

from notification.models import Notification
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity_ordered', 'price', "product_name"]

    def get_product_name(self, obj):
        return obj.product.name


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id','order_items', 'total_price', 'created_at', "status", "type", "delivery_partner",
                  "checkout_type","payment_type", "transaction_uuid"]

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        order = Order.objects.create(**validated_data)
        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)
            product = order_item_data['product']
            farmer = product.user
            Notification.objects.create(user=farmer, message=f'You have received a new order for your product {product.name}')
        return order


class OrderAdminSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)
    ordered_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'order_items', 'total_price', 'created_at', "status", "ordered_by",
                  "type", "delivery_partner", "checkout_type", "payment_type", "transaction_uuid"]

    def get_ordered_by(self, obj):
        return obj.customer.profile.full_name