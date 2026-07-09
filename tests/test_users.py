import pytest
from rest_framework import status


@pytest.mark.django_db
class TestUserRegistration:
    url = "/api/v1/accounts/register/"

    def test_register_success(self, api_client):
        data = {
            "email": "newuser@example.com",
            "password": "strongpass123",
            "password2": "strongpass123",
        }
        resp = api_client.post(self.url, data)
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["email"] == "newuser@example.com"

    def test_register_password_mismatch(self, api_client):
        data = {
            "email": "newuser@example.com",
            "password": "strongpass123",
            "password2": "differentpass",
        }
        resp = api_client.post(self.url, data)
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_fields(self, api_client):
        resp = api_client.post(self.url, {"email": "test@example.com"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    url = "/api/v1/accounts/login/"

    def test_login_obtain_token(self, api_client, user):
        resp = api_client.post(self.url, {"email": user.email, "password": "testpass123"})
        assert resp.status_code == status.HTTP_200_OK
        assert "access" in resp.data
        assert "refresh" in resp.data

    def test_login_invalid_credentials(self, api_client):
        resp = api_client.post(self.url, {"email": "wrong@example.com", "password": "wrong"})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client, user):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        resp = api_client.post("/api/v1/accounts/token/refresh/", {"refresh": str(refresh)})
        assert resp.status_code == status.HTTP_200_OK
        assert "access" in resp.data


@pytest.mark.django_db
class TestUserProfile:
    url = "/api/v1/accounts/profile/"

    def test_retrieve_profile(self, auth_client, user):
        resp = auth_client.get(self.url)
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["email"] == user.email

    def test_retrieve_profile_unauthenticated(self, api_client):
        resp = api_client.get(self.url)
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, auth_client, user):
        resp = auth_client.patch(self.url, {"first_name": "Updated"})
        assert resp.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == "Updated"


@pytest.mark.django_db
class TestUserDelete:
    url = "/api/v1/accounts/profile/delete/"

    def test_delete_account(self, auth_client, user):
        resp = auth_client.delete(self.url, {"current_password": "testpass123"}, format="json")
        assert resp.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert not user.is_active

    def test_delete_wrong_password(self, auth_client):
        resp = auth_client.delete(self.url, {"current_password": "wrongpass"}, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_unauthenticated(self, api_client):
        resp = api_client.delete(self.url, {"current_password": "test"}, format="json")
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
