from rest_framework import serializers
from .models import Cart, CartItem
from products.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_details = ProductListSerializer(source='product', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_details', 'quantity', 'subtotal', 'added_at']
        read_only_fields = ['added_at']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        if product and quantity > product.stock:
            raise serializers.ValidationError(
                f"Only {product.stock} items available in stock."
            )
        
        if product and not product.is_active:
            raise serializers.ValidationError("This product is not available.")
        
        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_price', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate_product_id(self, value):
        from products.models import Product
        try:
            product = Product.objects.get(id=value)
            if not product.is_active:
                raise serializers.ValidationError("This product is not available.")
            if product.stock == 0:
                raise serializers.ValidationError("This product is out of stock.")
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
