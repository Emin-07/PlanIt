from fastapi.testclient import TestClient


class TestUserEndpoints:
    """Test user-related endpoints."""

    def test_register_user(self, client: TestClient, user_create_data: dict):
        """Test user registration endpoint."""
        response = client.post("/users/", json=user_create_data)

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["email"] == user_create_data["email"]
        assert data["username"] == user_create_data["username"]
        assert "password" not in data  # Password should not be exposed

    # def test_register_user_duplicate_email(
    #     self, client: TestClient, test_user, user_data: dict
    # ):
    #     """Test registration with duplicate email."""
    #     response = client.post("/users/", json=user_data)

    #     assert response.status_code == 400
    #     assert "email" in response.json()["detail"].lower()

    # def test_login_success(self, client: TestClient, test_user):
    #     """Test successful login."""
    #     response = client.post(
    #         "/jwt/login/",
    #         json={"email": test_user.email, "password": "TestPass123!"},
    #     )

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert "access_token" in data
    #     assert data["token_type"] == "bearer"
    #     assert "user" in data

    # def test_login_wrong_password(self, client: TestClient, test_user):
    #     """Test login with wrong password."""
    #     response = client.post(
    #         "/jwt/login/",
    #         json={"email": test_user.email, "password": "WrongPassword!"},
    #     )

    #     assert response.status_code == 401

    # def test_get_current_user(self, client: TestClient, test_user):
    #     """Test getting current authenticated user."""
    #     headers = get_auth_headers_for_test_user(client, test_user)

    #     response = client.get("/users/me", headers=headers)

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["id"] == test_user.id
    #     assert data["email"] == test_user.email

    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without authentication."""
        response = client.get("/users/")
        assert response.status_code == 401

    # def test_update_user_profile(self, client: TestClient, test_user):
    #     """Test updating user profile."""
    #     headers = get_auth_headers_for_test_user(client, test_user)
    #     update_data = {"username": "updatedusername"}

    #     response = client.patch("/users/me", json=update_data, headers=headers)

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["username"] == "updatedusername" TODO: create section with me
    # like delete me, update me, get me(already have)
