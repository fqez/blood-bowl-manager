"""Tests fixtures."""

import pytest
from asgi_lifespan import LifespanManager
from beanie import init_beanie
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

import models as models
from app import app
from auth.jwt_bearer import get_current_user


async def mock_database():
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client["database_name"],
        recreate_views=True,
        document_models=models.__all__,
    )


def mock_no_authentication():
    app.dependency_overrides[get_current_user] = lambda: "test-user"


@pytest.fixture
async def client_test(mocker):
    """
    Create an instance of the client.
    :return: yield HTTP client.
    """

    mocker.patch("app.initiate_database", new=mock_database)

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport, base_url="http://test", follow_redirects=True
        ) as ac:
            yield ac


@pytest.fixture
def anyio_backend():
    return "asyncio"
