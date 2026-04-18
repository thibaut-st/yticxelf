from sqlalchemy.orm import Session

from models import AssetModel, AssetRepository
from tests.models.base import RepositoryTestCase


class TestAssetRepository(RepositoryTestCase):
    """Test the Asset repository helper."""

    def test_asset_repository_get_all_assets_returns_persisted_assets(self) -> None:
        """Return all assets stored in the database."""
        # ARRANGE
        with Session(self.engine, expire_on_commit=False) as session:
            session.add_all(
                [
                    AssetModel(
                        code="A-001",
                        name="Asset 1",
                        activation_cost=100.0,
                        availability=["2026-04-20"],
                        volume=50,
                    ),
                    AssetModel(
                        code="A-002",
                        name="Asset 2",
                        activation_cost=120.0,
                        availability=["2026-04-21"],
                        volume=75,
                    ),
                ],
            )
            session.commit()

        # ACT
        stored_assets = AssetRepository.get_all_assets()

        # ASSERT
        self.assertEqual(2, len(stored_assets))
        self.assertSetEqual({"A-001", "A-002"}, {asset.code for asset in stored_assets})
