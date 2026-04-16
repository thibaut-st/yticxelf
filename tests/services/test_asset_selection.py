from datetime import date
from unittest import TestCase
from unittest.mock import patch

from schemas.activation import ActivationIn
from schemas.asset import Asset
from services.asset_selection import optimize_asset_selection

mock_asset_list = [
    {
        "code": "A-001",
        "name": "Asset 1",
        "activation_cost": 120.0,
        "availability": [date(2026, 4, 20), date(2026, 4, 21), date(2026, 4, 22)],
        "volume": 50,
    }
]


class TestAssetSelection(TestCase):
    """Test the asset selection service."""

    @patch("services.asset_selection.ASSET_DUMMY_DATA", mock_asset_list)
    def test_optimize_asset_selection(self) -> None:
        """Test the optimize_asset_selection function."""
        # ARRANGE
        activation = ActivationIn(
            date=date.fromisoformat("2026-04-20"),
            volume=100,
        )
        expected_result = [
            Asset(
                code="A-001",
                name="Asset 1",
                activation_cost=120.0,
                availability=[date(2026, 4, 20), date(2026, 4, 21), date(2026, 4, 22)],
                volume=50,
            )
        ]
        # ACT
        result = optimize_asset_selection(activation)
        # ASSERT
        self.assertEqual(expected_result, result)
