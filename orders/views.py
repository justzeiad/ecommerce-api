from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderCreateSerializer, OrderListSerializer
from cart.models import Cart


class OrderListView(generics.ListAPIView):
    """List all orders for the authenticated user"""
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')


class OrderCreateView(generics.CreateAPIView):
    """Create an order from the user's cart"""
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get user's cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = cart.items.select_related('product').all()
        if not cart_items:
            return Response(
                {'error': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate stock for all items
        for item in cart_items:
            if item.quantity > item.product.stock:
                return Response(
                    {'error': f'Insufficient stock for {item.product.name}. Only {item.product.stock} available.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Calculate total amount
        total_amount = sum(item.subtotal for item in cart_items)

        # Create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            shipping_address=serializer.validated_data['shipping_address']
        )

        # Create order items and update product stock
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price  # Snapshot price at purchase time
            )
            # Reduce product stock
            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        # Clear the cart
        cart_items.delete()

        # Return the created order
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve a specific order"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        return get_object_or_404(self.get_queryset(), id=order_id)
