from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field, PositiveInt


class ActivationIn(BaseModel):
    """
    Pydantic schema for activation request.

    Attributes:
        date: date of the activation
        volume: integer, corresponding of the number of kW needed

    """

    date: Annotated[
        date, Field(description="The date of the activation, in YYYY-MM-DD format.", examples=["2026-04-20"])
    ]
    volume: Annotated[PositiveInt, Field(description="The volume of the activation, in kW.", examples=[100])]
