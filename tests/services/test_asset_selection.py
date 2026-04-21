from datetime import date
from unittest import TestCase
from unittest.mock import Mock, patch

from models import AssetModel
from schemas.activation import ActivationIn
from services.asset_selection import optimize_asset_selection
from tests.dummy_data import ASSET_DUMMY_MODELS


@patch("services.asset_selection.ActivationRepository.save", new=Mock())
@patch("services.asset_selection.ActivationAssetHistoryRepository.save", new=Mock())
class TestAssetSelectionBruteForce(TestCase):
    """Test the asset selection service."""

    @patch("services.asset_selection.AssetRepository.get_all_assets", new=Mock(return_value=ASSET_DUMMY_MODELS))
    def test_optimize_asset_selection_ok(self) -> None:
        """Test the optimize_asset_selection function."""
        # ARRANGE
        activation = ActivationIn(
            date=date.fromisoformat("2026-04-20"),
            volume=100,
        )
        expected_result = {
            "selected_assets": [
                AssetModel(
                    code="A-007",
                    name="Asset 7",
                    activation_cost=210.0,
                    availability=["2026-04-20", "2026-04-21", "2026-04-22"],
                    volume=120,
                )
            ],
            "total_cost_selected": 210.0,
            "total_volume_selected": 120,
        }
        # ACT
        result = optimize_asset_selection(activation)
        # ASSERT
        self.assertEqual(1, len(result["selected_assets"]))
        self.assertEqual(expected_result["selected_assets"][0].code, result["selected_assets"][0].code)  # type: ignore[index]
        self.assertEqual(expected_result["total_cost_selected"], result["total_cost_selected"])
        self.assertEqual(expected_result["total_volume_selected"], result["total_volume_selected"])

    @patch("services.asset_selection.AssetRepository.get_all_assets", new=Mock(return_value=ASSET_DUMMY_MODELS))
    def test_optimize_asset_selection_not_enough_power(self) -> None:
        """Test the optimize_asset_selection function."""
        # ARRANGE
        activation = ActivationIn(
            date=date.fromisoformat("2026-04-20"),
            volume=9999,
        )
        # ACT
        with self.assertRaises(ValueError) as context_manager:
            optimize_asset_selection(activation)
        # ASSERT
        self.assertEqual(
            "Not enough assets available for the requested volume. Available: 355, Requested: 9999",
            str(context_manager.exception),
        )

    @patch("services.asset_selection.AssetRepository.get_all_assets", new=Mock(return_value=[]))
    def test_optimize_asset_selection_no_assets(self) -> None:
        """Test the optimize_asset_selection function, which should raise an error if no assets are available."""
        # ARRANGE
        activation = ActivationIn(
            date=date.fromisoformat("2026-04-20"),
            volume=10000,
        )
        # ACT
        with self.assertRaises(ValueError) as context_manager:
            optimize_asset_selection(activation)
        # ASSERT
        self.assertEqual("No assets available for the requested date", str(context_manager.exception))
