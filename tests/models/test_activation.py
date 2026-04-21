from datetime import date
from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models import ActivationAssetHistoryModel, ActivationModel, ActivationRepository, AssetModel, AssetRepository
from tests.models.base import RepositoryTestCase


class TestActivationRepository(RepositoryTestCase):
    """Test the Activation repository helper."""

    def test_activation_repository_save_persists_and_returns_activation(self) -> None:
        """Persist an activation and return its stored model."""
        # ACT
        activation = ActivationRepository.save(
            activation_date=date(2026, 4, 20),
            activation_volume=125,
        )

        # ASSERT
        self.assertIsInstance(activation.id, UUID)
        self.assertEqual(date(2026, 4, 20), activation.date)
        self.assertEqual(125, activation.volume)

        with Session(self.engine, expire_on_commit=False) as session:
            stored_activation = session.get(ActivationModel, activation.id)

        self.assertIsNotNone(stored_activation)
        if stored_activation is None:
            self.fail("Expected the activation row to be persisted.")
        self.assertEqual(date(2026, 4, 20), stored_activation.date)
        self.assertEqual(125, stored_activation.volume)

    def test_activation_repository_save_with_history(self) -> None:
        """Save an activation and its selected assets in a single transaction."""
        # ARRANGE
        with Session(self.engine, expire_on_commit=False) as session:
            session.add_all(
                [
                    AssetModel(
                        code="A-001",
                        name="Asset 1",
                        activation_cost=80.0,
                        availability=["2026-04-20"],
                        volume=30,
                    ),
                    AssetModel(
                        code="A-002",
                        name="Asset 2",
                        activation_cost=95.0,
                        availability=["2026-04-20"],
                        volume=70,
                    ),
                ],
            )
            session.commit()

        selected_assets = AssetRepository.get_all_assets()

        # ACT
        activation = ActivationRepository.save_with_history(
            activation_date=date(2026, 4, 20),
            activation_volume=100,
            assets=selected_assets,
        )

        with Session(self.engine, expire_on_commit=False) as session:
            stored_activation = session.get(ActivationModel, activation.id)
            history_entries = list(cast("ActivationModel", stored_activation).history_entries)

        # ASSERT
        self.assertIsNotNone(stored_activation)
        if stored_activation is None:
            self.fail("Expected the activation row to be persisted.")
        self.assertEqual(date(2026, 4, 20), stored_activation.date)
        self.assertEqual(100, stored_activation.volume)
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

    def test_activation_repository_save_with_history_rolls_back_activation_when_history_fails(self) -> None:
        """Rollback the activation insert if history insert fails."""
        # ARRANGE
        with Session(self.engine, expire_on_commit=False) as session:
            asset = AssetModel(
                code="A-001",
                name="Asset 1",
                activation_cost=80.0,
                availability=["2026-04-20"],
                volume=30,
            )
            session.add(asset)
            session.commit()

        selected_asset = AssetRepository.get_all_assets()[0]

        # ACT
        with self.assertRaises(IntegrityError):
            ActivationRepository.save_with_history(
                activation_date=date(2026, 4, 20),
                activation_volume=100,
                assets=[selected_asset, selected_asset],
            )

        with Session(self.engine, expire_on_commit=False) as session:
            stored_activations = session.scalars(select(ActivationModel)).all()
            history_entries = session.scalars(select(ActivationAssetHistoryModel)).all()

        # ASSERT
        self.assertEqual([], stored_activations)
        self.assertEqual([], history_entries)
