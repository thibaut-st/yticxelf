from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from models.activation import ActivationModel, ActivationRepository
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
