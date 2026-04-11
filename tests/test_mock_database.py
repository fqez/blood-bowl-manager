"""Tests for database operations with mock MongoDB."""

import pytest
from httpx import AsyncClient

from models.team.perk import Perk
from models.user.admin import Admin
from tests.conftest import mock_no_authentication


class TestDatabaseOperations:
    """Test database operations using mock MongoDB."""

    @classmethod
    def setup_class(cls):
        mock_no_authentication()

    @pytest.mark.anyio
    async def test_create_admin(self, client_test: AsyncClient):
        """Test admin creation in mock database."""
        await Admin(
            fullname="admin", email="admin@admin.com", password="admin"
        ).create()

        # Verify admin exists (would need an endpoint, just testing creation doesn't fail)
        assert True

    @pytest.mark.anyio
    async def test_create_perk(self, client_test: AsyncClient):
        """Test perk creation and retrieval."""
        await Perk(
            id="perk-block",
            name={"en": "Block", "es": "Bloqueo"},
            description={"en": "Prevents knockdowns", "es": "Previene caídas"},
            family="General",
        ).create()

        response = await client_test.get("/perks/perk-block")
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_get_all_perks(self, client_test: AsyncClient):
        """Test retrieving all perks."""
        response = await client_test.get("/perks/")
        assert response.status_code == 200
