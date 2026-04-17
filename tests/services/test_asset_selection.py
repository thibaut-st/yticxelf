from datetime import date
from unittest import TestCase
from unittest.mock import patch

from schemas.activation import ActivationIn
from services.asset_selection import optimize_asset_selection
from tests.dummy_data import ASSET_DUMMY_DATA


@patch("services.asset_selection.ASSET_DATA", ASSET_DUMMY_DATA)
class TestAssetSelectionBruteForce(TestCase):
    """Test the asset selection service."""

    def test_optimize_asset_selection_ok(self) -> None:
        """Test the optimize_asset_selection function."""
        # ARRANGE
        activation = ActivationIn(
            date=date.fromisoformat("2026-04-20"),
            volume=100,
        )
        expected_result = [
            {
                "code": "A-007",
                "name": "Asset 7",
                "activation_cost": 210.0,
                "availability": [date(2026, 4, 20), date(2026, 4, 21), date(2026, 4, 22)],
                "volume": 120,
            }
        ]
        # ACT
        result = optimize_asset_selection(activation)
        # ASSERT
        self.assertEqual(expected_result, result)

    def test_optimize_asset_selection_not_enough_power(self) -> None:
        """Test the optimize_asset_selection function."""
        # ARRANGE
        activation = ActivationIn(
            date=date.fromisoformat("2026-04-20"),
            volume=9999,
        )
        expected_result = list(filter(lambda asset: activation.date in asset["availability"], ASSET_DUMMY_DATA))
        # ACT
        result = optimize_asset_selection(activation)
        # ASSERT
        self.assertEqual(expected_result, result)
