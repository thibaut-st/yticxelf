from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from data.db import Base, SessionLocal

if TYPE_CHECKING:
    from models import ActivationAssetHistoryModel


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
        with SessionLocal() as session:
            session.add(activation)
            session.commit()
        return activation
