from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Float, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.db import Base, SessionLocal

if TYPE_CHECKING:
    from models import ActivationModel, AssetModel


class ActivationAssetHistoryModel(Base):
    """History row linking an activation to the assets selected for it."""

    __tablename__ = "activation_asset_history"
    __table_args__ = (
        UniqueConstraint(
            "activation_id",
            "asset_id",
            name="uq_activation_asset_history_activation_asset",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True, native_uuid=False), primary_key=True, default=uuid4)
    activation_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey("activations.id"),
        nullable=False,
    )
    asset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True, native_uuid=False),
        ForeignKey("assets.id"),
        nullable=False,
    )
    volume_at_selection: Mapped[int] = mapped_column(nullable=False)
    activation_cost_at_selection: Mapped[float] = mapped_column(Float, nullable=False)

    activation: Mapped[ActivationModel] = relationship(back_populates="history_entries")
    asset: Mapped[AssetModel] = relationship(back_populates="history_entries")


class ActivationAssetHistoryRepository:
    """Repository for managing activation asset history."""

    @staticmethod
    def save(activation: ActivationModel, assets: list[AssetModel]) -> None:
        """
        Save multiple activation asset history entries in a single transaction.

        For each asset in the list, create a new activation asset history entry associated with the activation.

        :param activation: The activation that selected the asset.
        :param assets: The list of assets that was selected.
        :return: The saved activation asset history entry.
        """
        with SessionLocal() as session:
            for asset in assets:
                activation_asset_history = ActivationAssetHistoryModel(
                    activation=activation,
                    asset=asset,
                    volume_at_selection=asset.volume,
                    activation_cost_at_selection=asset.activation_cost,
                )
                session.add(activation_asset_history)
            session.commit()
