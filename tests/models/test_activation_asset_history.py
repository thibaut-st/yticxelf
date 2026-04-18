from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import (
    ActivationAssetHistoryModel,
    ActivationAssetHistoryRepository,
    ActivationRepository,
    AssetModel,
    AssetRepository,
)
from tests.models.base import RepositoryTestCase


class TestActivationAssetHistoryRepository(RepositoryTestCase):
    """Test the ActivationAssetHistory repository helper."""

    def test_activation_asset_history_repository_save_persists_snapshot_rows(self) -> None:
        """Persist one history row per selected asset with snapshot values."""
        # ARRANGE
        with Session(self.engine, expire_on_commit=False) as session:
            session.add_all(
                [
                    AssetModel(
                        code="A-003",
                        name="Asset 3",
                        activation_cost=90.0,
                        availability=["2026-04-20"],
                        volume=40,
                    ),
                    AssetModel(
                        code="A-004",
                        name="Asset 4",
                        activation_cost=110.0,
                        availability=["2026-04-20"],
                        volume=60,
                    ),
                ],
            )
            session.commit()

        activation = ActivationRepository.save(
            activation_date=date(2026, 4, 20),
            activation_volume=100,
        )
        selected_assets = AssetRepository.get_all_assets()

        # ACT
        ActivationAssetHistoryRepository.save(
            activation=activation,
            assets=selected_assets,
        )

        with Session(self.engine, expire_on_commit=False) as session:
            history_entries = session.scalars(
                select(ActivationAssetHistoryModel).order_by(ActivationAssetHistoryModel.asset_id),
            ).all()

        # ASSERT
        self.assertEqual(2, len(history_entries))
        self.assertTrue(all(entry.activation_id == activation.id for entry in history_entries))
        self.assertEqual(
            sorted((asset.id, asset.volume, asset.activation_cost) for asset in selected_assets),
            sorted(
                (
                    entry.asset_id,
                    entry.volume_at_selection,
                    entry.activation_cost_at_selection,
                )
                for entry in history_entries
            ),
        )
