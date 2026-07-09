import pytest
from rest_framework import status
from orders.models import Order


pytestmark = pytest.mark.django_db


class TestCreateOrder:
    url = "/api/v1/orders/create/"

    def test_create_from_cart(self, auth_client, cart):
        resp = auth_client.post(self.url, {"shipping_address": "123 Main St"})
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["status"] == "pending"
        assert float(resp.data["total_amount"]) == 59.98
        assert Order.objects.filter(user=cart.user).count() == 1

    def test_empty_cart(self, auth_client, user):
        resp = auth_client.post(self.url, {"shipping_address": "123 Main St"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "empty" in str(resp.data).lower()

    def test_insufficient_stock(self, auth_client, cart, product):
        product.stock = 0
        product.save()
        resp = auth_client.post(self.url, {"shipping_address": "123 Main St"})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "stock" in str(resp.data).lower()

    def test_unauthenticated(self, api_client):
        resp = api_client.post(self.url, {"shipping_address": "123 Main St"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestListOrders:
    url = "/api/v1/orders/"

    def test_list_user_orders(self, auth_client, order):
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1
        assert resp.data[0]["status"] == "pending"

    def test_other_user_orders_not_visible(self, auth_client, order):
        """A second user shouldn't see the first user's orders"""
        from users.models import User
        other = User.objects.create_user(email="other@example.com", password="pass123")
        from rest_framework_simplejwt.tokens import RefreshToken
        client = type(auth_client)()
        refresh = RefreshToken.for_user(other)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        resp = client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 0

    def test_unauthenticated(self, api_client):
        resp = api_client.get(self.url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestOrderDetail:
    def test_detail(self, auth_client, order):
        url = f"/api/v1/orders/{order.id}/"
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["id"] == order.id

    def test_detail_other_user_not_found(self, auth_client, order):
        from users.models import User
        other = User.objects.create_user(email="other2@example.com", password="pass123")
        from rest_framework_simplejwt.tokens import RefreshToken
        client = type(auth_client)()
        refresh = RefreshToken.for_user(other)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        url = f"/api/v1/orders/{order.id}/"
        resp = client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_unauthenticated(self, api_client, order):
        url = f"/api/v1/orders/{order.id}/"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_detail_not_found(self, auth_client):
        resp = auth_client.get("/api/v1/orders/99999/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
