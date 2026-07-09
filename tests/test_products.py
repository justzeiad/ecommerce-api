import pytest
from rest_framework import status


pytestmark = pytest.mark.django_db


class TestProductList:
    url = "/api/v1/products/"

    def test_list_products_public(self, api_client, product, inactive_product):
        resp = api_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        slugs = [p["slug"] for p in resp.data]
        assert product.slug in slugs
        assert inactive_product.slug not in slugs  # inactive hidden from public

    def test_list_products_admin_sees_all(self, admin_client, product, inactive_product):
        resp = admin_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        slugs = [p["slug"] for p in resp.data]
        assert product.slug in slugs
        assert inactive_product.slug in slugs

    def test_filter_by_category(self, api_client, product, category):
        resp = api_client.get(self.url, {"category": category.id})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1

    def test_filter_by_is_active(self, admin_client, product, inactive_product):
        resp = admin_client.get(self.url, {"is_active": True})
        assert resp.status_code == status.HTTP_200_OK
        assert all(p["is_active"] for p in resp.data)

    def test_search(self, api_client, product):
        resp = api_client.get(self.url, {"search": "Test"})
        assert resp.status_code == status.HTTP_200_OK
        assert len(resp.data) == 1

    def test_ordering(self, api_client, product, category):
        from products.models import Product
        Product.objects.create(
            name="Aardvark", slug="aardvark", description="Cheap",
            price=1.00, category=category, stock=5, is_active=True,
        )
        resp = api_client.get(self.url, {"ordering": "price"})
        assert resp.status_code == status.HTTP_200_OK
        prices = [float(p["price"]) for p in resp.data]
        assert prices == sorted(prices)


class TestProductDetail:
    url = "/api/v1/products/"

    def test_detail_by_slug_public(self, api_client, product):
        resp = api_client.get(f"{self.url}{product.slug}/")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["slug"] == product.slug

    def test_detail_inactive_hidden_from_public(self, api_client, inactive_product):
        resp = api_client.get(f"{self.url}{inactive_product.slug}/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    def test_detail_admin_sees_inactive(self, admin_client, inactive_product):
        resp = admin_client.get(f"{self.url}{inactive_product.slug}/")
        assert resp.status_code == status.HTTP_200_OK


class TestProductCreate:
    url = "/api/v1/products/"

    def test_create_as_admin(self, admin_client, category):
        data = {
            "name": "New Product", "description": "Brand new",
            "price": 14.99, "category": category.id, "stock": 5,
        }
        resp = admin_client.post(self.url, data)
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["name"] == "New Product"

    def test_create_as_regular_user(self, auth_client, category):
        data = {
            "name": "New Product", "description": "Brand new",
            "price": 14.99, "category": category.id, "stock": 5,
        }
        resp = auth_client.post(self.url, data)
        assert resp.status_code == status.HTTP_403_FORBIDDEN

    def test_create_unauthenticated(self, api_client, category):
        data = {
            "name": "New Product", "description": "Brand new",
            "price": 14.99, "category": category.id, "stock": 5,
        }
        resp = api_client.post(self.url, data)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestProductUpdate:
    def test_update_as_admin(self, admin_client, product):
        url = f"/api/v1/products/{product.slug}/"
        resp = admin_client.patch(url, {"price": "19.99"})
        assert resp.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert float(product.price) == 19.99

    def test_update_as_regular_user(self, auth_client, product):
        url = f"/api/v1/products/{product.slug}/"
        resp = auth_client.patch(url, {"price": "19.99"})
        assert resp.status_code == status.HTTP_403_FORBIDDEN


class TestProductDelete:
    def test_delete_as_admin(self, admin_client, product):
        url = f"/api/v1/products/{product.slug}/"
        resp = admin_client.delete(url)
        assert resp.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_as_regular_user(self, auth_client, product):
        url = f"/api/v1/products/{product.slug}/"
        resp = auth_client.delete(url)
        assert resp.status_code == status.HTTP_403_FORBIDDEN
