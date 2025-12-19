from rest_framework import serializers
from .models import Payment
from orders.serializers import OrderSerializer


class PaymentSerializer(serializers.ModelSerializer):
    order_details = OrderSerializer(source='order', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_details', 'stripe_payment_intent_id',
            'amount', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['stripe_payment_intent_id', 'created_at', 'updated_at']


class PaymentCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()

    def validate_order_id(self, value):
        from orders.models import Order
        try:
            order = Order.objects.get(id=value)
            # Ensure order belongs to the user
            request = self.context.get('request')
            if order.user != request.user:
                raise serializers.ValidationError("This order does not belong to you.")
            
            # Check if payment already exists
            if hasattr(order, 'payment'):
                raise serializers.ValidationError("Payment already exists for this order.")
            
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found.")
        
        return value


class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'stripe_payment_intent_id', 'amount', 'status', 'created_at']
