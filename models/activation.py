from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.db import Base, SessionLocal
from models.activation_asset_history import ActivationAssetHistoryModel

if TYPE_CHECKING:
    from models import AssetModel


class ActivationModel(Base):
    """Activation request stored in the database."""

    __tablename__ = "activations"

    # native_uuid: sqlite does not support UUIDs natively
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True, native_uuid=False), primary_key=True, default=uuid4)
    date: Mapped[date]
    volume: Mapped[int]

    history_entries: Mapped[list[ActivationAssetHistoryModel]] = relationship(
        back_populates="activation",
        cascade="all, delete-orphan",
    )


class ActivationRepository:
    """Repository for managing activations."""

    @staticmethod
    def save(activation_date: date, activation_volume: int) -> ActivationModel:
        """
        Save an activation to the database.

        :param activation_date: The date of the activation.
        :param activation_volume: The volume of the activation.

        """
        activation = ActivationModel(date=activation_date, volume=activation_volume)
        with SessionLocal.begin() as session:
            session.add(activation)
        return activation

    @staticmethod
    def save_with_history(
        activation_date: date,
        activation_volume: int,
        assets: list[AssetModel],
    ) -> ActivationModel:
        """
        Save an activation and its selected asset history.

        :param activation_date: The requested activation date.
        :param activation_volume: The requested activation volume.
        :param assets: The selected assets for this activation.
        :return: The saved activation.
        """
        with SessionLocal.begin() as session:
            activation = ActivationModel(date=activation_date, volume=activation_volume)
            session.add(activation)
            session.flush()

            session.add_all(
                ActivationAssetHistoryModel(
                    activation_id=activation.id,
                    asset_id=asset.id,
                    volume_at_selection=asset.volume,
                    activation_cost_at_selection=asset.activation_cost,
                )
                for asset in assets
            )
        return activation
