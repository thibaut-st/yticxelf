from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Float, ForeignKey, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.db import Base

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
