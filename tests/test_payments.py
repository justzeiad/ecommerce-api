import json
import pytest
from unittest.mock import patch, MagicMock
from rest_framework import status


pytestmark = pytest.mark.django_db


class TestCreatePaymentIntent:
    url = "/api/v1/payments/create/"

    @patch("stripe.PaymentIntent.create")
    def test_create_payment_intent(self, mock_stripe, auth_client, order):
        mock_stripe.return_value = MagicMock(
            id="pi_mock_123", client_secret="secret_mock_123"
        )
        resp = auth_client.post(self.url, {"order_id": order.id})
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["client_secret"] == "secret_mock_123"
        assert resp.data["status"] == "pending"
        assert float(resp.data["amount"]) == float(order.total_amount)

    def test_create_unauthenticated(self, api_client, order):
        resp = api_client.post(self.url, {"order_id": order.id})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_order_not_found(self, auth_client):
        resp = auth_client.post(self.url, {"order_id": 99999})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_other_users_order(self, auth_client, order):
        """User can't create payment for another user's order"""
        from users.models import User
        other = User.objects.create_user(email="other@example.com", password="pass123")
        from rest_framework_simplejwt.tokens import RefreshToken
        client = type(auth_client)()
        refresh = RefreshToken.for_user(other)
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        resp = client.post(self.url, {"order_id": order.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    @patch("stripe.PaymentIntent.create")
    def test_duplicate_payment(self, mock_stripe, auth_client, payment):
        mock_stripe.return_value = MagicMock(
            id="pi_mock_456", client_secret="secret_mock_456"
        )
        resp = auth_client.post(self.url, {"order_id": payment.order.id})
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert "already" in str(resp.data).lower()


class TestPaymentStatus:
    def test_get_status(self, auth_client, payment):
        url = f"/api/v1/payments/status/{payment.order.id}/"
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["status"] == "pending"

    def test_get_status_unauthenticated(self, api_client, payment):
        url = f"/api/v1/payments/status/{payment.order.id}/"
        resp = api_client.get(url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_status_not_found(self, auth_client):
        url = "/api/v1/payments/status/99999/"
        resp = auth_client.get(url)
        assert resp.status_code == status.HTTP_404_NOT_FOUND


class TestWebhook:
    url = "/api/v1/payments/webhook/"

    def test_webhook_success(self, api_client, payment):
        payload = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": payment.stripe_payment_intent_id}},
        }
        resp = api_client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        assert resp.status_code == status.HTTP_200_OK
        payment.refresh_from_db()
        assert payment.status == "succeeded"
        assert payment.order.status == "completed"

    def test_webhook_failure(self, api_client, payment):
        payload = {
            "type": "payment_intent.payment_failed",
            "data": {"object": {"id": payment.stripe_payment_intent_id}},
        }
        resp = api_client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        assert resp.status_code == status.HTTP_200_OK
        payment.refresh_from_db()
        assert payment.status == "failed"
        assert payment.order.status == "cancelled"

    def test_webhook_unknown_payment(self, api_client):
        payload = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_unknown"}},
        }
        resp = api_client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        assert resp.status_code == status.HTTP_200_OK  # webhook doesn't error
