from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import JSON, Float, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.db import Base, SessionLocal

if TYPE_CHECKING:
    from models import ActivationAssetHistoryModel


class AssetModel(Base):
    """Asset stored in the database."""

    __tablename__ = "assets"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True, native_uuid=False), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(length=50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    activation_cost: Mapped[float] = mapped_column(Float, nullable=False)
    availability: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    volume: Mapped[int] = mapped_column(nullable=False)

    history_entries: Mapped[list[ActivationAssetHistoryModel]] = relationship(back_populates="asset")


class AssetRepository:
    """Repository for managing assets."""

    @staticmethod
    def get_all_assets() -> list[AssetModel]:
        """Get all assets from the database."""
        with SessionLocal.begin() as session:
            return session.query(AssetModel).all()
