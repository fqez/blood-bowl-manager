"""Tests for authentication bypass in testing."""

import pytest
from httpx import AsyncClient

from tests.conftest import mock_no_authentication


class TestAuthenticationBypass:
    """Test that authentication can be bypassed for testing."""

    @classmethod
    def setup_class(cls):
        mock_no_authentication()

    @pytest.mark.anyio
    async def test_public_endpoint_accessible(self, client_test: AsyncClient):
        """Test that public endpoints are accessible without auth."""
        response = await client_test.get("/perks/")
        assert response.status_code == 200

    @pytest.mark.anyio
    async def test_teams_endpoint_accessible(self, client_test: AsyncClient):
        """Test that teams endpoint is accessible."""
        response = await client_test.get("/teams/")
        assert response.status_code == 200
