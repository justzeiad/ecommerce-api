import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from products.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from payments.models import Payment


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    cache.clear()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="test@example.com", password="testpass123", first_name="Test", last_name="User"
    )


@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        email="admin@example.com", password="adminpass123"
    )


@pytest.fixture
def auth_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def category():
    return Category.objects.create(name="Electronics", slug="electronics")


@pytest.fixture
def product(category):
    return Product.objects.create(
        name="Test Product",
        slug="test-product",
        description="A test product",
        price=29.99,
        category=category,
        stock=10,
    )


@pytest.fixture
def inactive_product(category):
    return Product.objects.create(
        name="Inactive Product",
        slug="inactive-product",
        description="Not available",
        price=9.99,
        category=category,
        stock=0,
        is_active=False,
    )


@pytest.fixture
def cart(user, product):
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)
    return cart


@pytest.fixture
def order(cart, user):
    order = Order.objects.create(
        user=user, total_amount=59.98, shipping_address="123 Test St"
    )
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price,
        )
    return order


@pytest.fixture
def payment(order):
    return Payment.objects.create(
        order=order,
        stripe_payment_intent_id="pi_test_123",
        amount=order.total_amount,
        status="pending",
    )
