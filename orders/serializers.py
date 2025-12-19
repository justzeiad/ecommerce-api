from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductListSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_details', 'quantity', 'price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'user_email', 'total_amount', 'status',
            'shipping_address', 'items', 'total_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'total_amount', 'created_at', 'updated_at']


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(max_length=500)

    def validate(self, data):
        # Will be validated in the view that the cart is not empty
        return data


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing orders"""
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'total_amount', 'status', 'total_items', 'created_at']
