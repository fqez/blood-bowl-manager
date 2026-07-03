import pytest
from httpx import AsyncClient

from app import app
from auth.jwt_bearer import get_current_user
from models.user.user import User


@pytest.fixture(autouse=True)
def clear_auth_overrides():
    app.dependency_overrides.pop(get_current_user, None)
    yield
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.anyio
async def test_logout_accepts_refresh_token_without_authorization(
    client_test: AsyncClient,
):
    response = await client_test.post(
        "/auth/register",
        json={
            "username": "logout_coach",
            "email": "logout@example.com",
            "password": "StrongPass1!",
        },
    )

    assert response.status_code == 201
    refresh_token = response.json()["refresh_token"]

    created_user = await User.find_one(User.email == "logout@example.com")
    assert created_user is not None
    assert len(created_user.refresh_tokens) == 1

    logout_response = await client_test.post(
        "/auth/logout",
        json={"refresh_token": refresh_token},
    )

    assert logout_response.status_code == 204

    logged_out_user = await User.find_one(User.email == "logout@example.com")
    assert logged_out_user is not None
    assert logged_out_user.refresh_tokens == []


@pytest.mark.anyio
async def test_logout_requires_access_or_refresh_token(client_test: AsyncClient):
    response = await client_test.post("/auth/logout")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"