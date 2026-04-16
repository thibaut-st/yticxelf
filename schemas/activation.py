from datetime import date

from pydantic import BaseModel


class ActivationIn(BaseModel):
    """
    Pydantic schema for activation request.

    Attributes:
        date: date of the activation
        volume: integer, corresponding of the number of kW needed

    """

    date: date
    volume: int
