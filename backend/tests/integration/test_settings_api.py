"""
Integration tests for Settings API endpoints including fee presets.

Tests the complete flow from HTTP request to database and back.
"""

import pytest
from httpx import AsyncClient
from decimal import Decimal


@pytest.mark.asyncio
class TestFeePresetsAPI:
    """Test suite for fee preset endpoints."""

    async def test_get_fee_presets_empty(self, client: AsyncClient):
        """Test getting presets when none exist returns empty lists."""
        # Arrange
        location_id = 1

        # Act
        response = await client.get(
            "/api/settings/fee-presets",
            params={"location_id": location_id}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "presets_by_fee_type" in data
        assert data["presets_by_fee_type"]["shipping"] == []
        assert data["presets_by_fee_type"]["installation"] == []
        assert data["presets_by_fee_type"]["custom"] == []

    async def test_create_fee_presets(self, client: AsyncClient):
        """Test creating fee presets for a location and fee type."""
        # Arrange
        location_id = 1
        fee_type = "shipping"
        presets = [10, 30, 50, 100]

        # Act - Create/Update presets
        response = await client.post(
            "/api/settings/fee-presets",
            json={
                "location_id": location_id,
                "fee_type": fee_type,
                "presets": presets
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["fee_type"] == fee_type
        assert data["presets"] == presets

        # Verify - Get all presets
        get_response = await client.get(
            "/api/settings/fee-presets",
            params={"location_id": location_id}
        )
        assert get_response.status_code == 200
        get_data = get_response.json()
        assert get_data["presets_by_fee_type"]["shipping"] == presets

    async def test_create_presets_deduplicates_and_sorts(self, client: AsyncClient):
        """Test that creating presets deduplicates and sorts values."""
        # Arrange
        location_id = 2
        fee_type = "installation"
        presets = [50, 30, 30, 100, 10]  # Duplicates and unsorted

        # Act
        response = await client.post(
            "/api/settings/fee-presets",
            json={
                "location_id": location_id,
                "fee_type": fee_type,
                "presets": presets
            }
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["presets"] == [10, 30, 50, 100]  # Sorted and deduplicated

    async def test_create_presets_validates_max_8(self, client: AsyncClient):
        """Test that creating more than 8 presets is rejected."""
        # Arrange
        location_id = 3
        fee_type = "custom"
        presets = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # 9 presets - exceeds limit

        # Act
        response = await client.post(
            "/api/settings/fee-presets",
            json={
                "location_id": location_id,
                "fee_type": fee_type,
                "presets": presets
            }
        )

        # Assert
        assert response.status_code == 422  # Pydantic validation error

    async def test_create_presets_validates_non_negative(self, client: AsyncClient):
        """Test that creating presets with negative values is rejected."""
        # Arrange
        location_id = 4
        fee_type = "shipping"
        presets = [10, -5, 30]  # Contains negative value

        # Act
        response = await client.post(
            "/api/settings/fee-presets",
            json={
                "location_id": location_id,
                "fee_type": fee_type,
                "presets": presets
            }
        )

        # Assert
        assert response.status_code == 422  # Pydantic validation error

    async def test_create_presets_validates_fee_type(self, client: AsyncClient):
        """Test that creating presets with invalid fee type is rejected."""
        # Arrange
        location_id = 5
        fee_type = "invalid_type"  # Invalid fee type
        presets = [10, 30, 50]

        # Act
        response = await client.post(
            "/api/settings/fee-presets",
            json={
                "location_id": location_id,
                "fee_type": fee_type,
                "presets": presets
            }
        )

        # Assert
        assert response.status_code == 422  # Pydantic validation error
