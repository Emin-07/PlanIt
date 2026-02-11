from typing import Dict

from fastapi.testclient import TestClient

from schemas.user_schemas import UserSchema
from utils.auth_helper import create_access_token


def get_auth_headers_for_test_user(client: TestClient, test_user) -> Dict[str, str]:
    """Get auth headers for test user fixture."""
    # Use actual login endpoint or create token
    response = client.post(
        "jwt/login/", json={"email": test_user.email, "password": "TestPass123!"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
    else:
        # Fallback to direct token creation

        token = create_access_token(
            user=UserSchema(
                id=test_user.id,
                email=test_user.email,
                username=test_user.username,
                created_at=test_user.created_at,
            )
        )

    return {"Authorization": f"Bearer {token}"}


def get_auth_headers(client: TestClient, email: str, password: str) -> Dict[str, str]:
    """Get authentication headers by logging in."""
    response = client.post("/login/", json={"email": email, "password": password})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_auth_headers_for_user(client: TestClient, test_user) -> Dict[str, str]:
    """Get authentication headers for a specific user ID."""
    token = create_access_token(
        user=UserSchema(
            id=test_user.id,
            email=test_user.email,
            username=test_user.username,
            created_at=test_user.created_at,
        )
    )

    return {"Authorization": f"Bearer {token}"}
