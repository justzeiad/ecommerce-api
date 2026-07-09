import pytest
from rest_framework import status
from cart.models import Cart, CartItem


pytestmark = pytest.mark.django_db


class TestGetCart:
    url = "/api/v1/cart/"

    def test_get_cart_auto_creates(self, auth_client, user):
        assert not Cart.objects.filter(user=user).exists()
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert Cart.objects.filter(user=user).exists()

    def test_get_cart_with_items(self, auth_client, cart):
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["total_items"] == 2

    def test_get_cart_unauthenticated(self, api_client):
        resp = api_client.get(self.url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestAddItem:
    url = "/api/v1/cart/add/"

    def test_add_new_item(self, auth_client, product):
        resp = auth_client.post(self.url, {"product_id": product.id, "quantity": 1})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["total_items"] == 1

    def test_add_existing_item_increases_quantity(self, auth_client, cart, product):
        resp = auth_client.post(self.url, {"product_id": product.id, "quantity": 1})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["total_items"] == 3  # was 2, added 1 more

    def test_add_exceeds_stock(self, auth_client, product):
        resp = auth_client.post(self.url, {"product_id": product.id, "quantity": 999})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_add_unauthenticated(self, api_client, product):
        resp = api_client.post(self.url, {"product_id": product.id, "quantity": 1})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestUpdateItem:
    def test_update_quantity(self, auth_client, cart):
        item = cart.items.first()
        url = f"/api/v1/cart/update/{item.id}/"
        resp = auth_client.put(url, {"quantity": 5})
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["total_items"] == 5

    def test_update_exceeds_stock(self, auth_client, cart):
        item = cart.items.first()
        url = f"/api/v1/cart/update/{item.id}/"
        resp = auth_client.put(url, {"quantity": 999})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_nonexistent_item(self, auth_client):
        url = "/api/v1/cart/update/99999/"
        resp = auth_client.put(url, {"quantity": 1})
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestRemoveItem:
    def test_remove_item(self, auth_client, cart):
        item = cart.items.first()
        url = f"/api/v1/cart/remove/{item.id}/"
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["total_items"] == 0


class TestClearCart:
    url = "/api/v1/cart/clear/"

    def test_clear_cart(self, auth_client, cart):
        resp = auth_client.post(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["total_items"] == 0

    def test_clear_empty_cart(self, auth_client, user):
        resp = auth_client.post(self.url)
        assert resp.status_code == status.HTTP_200_OK



