from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class Asset(BaseModel):
    """
    Pydantic schema for an asset.

    Attributes:
        code: string, asset code.
        name: string, asset name.
        activation_cost: double in €, same price whether partial or full capacity.
        availability: list of dates when the asset is available.
            For example, an asset can only be available only 1 day of the current week.
        volume: integer, correspond of the number of kW that can be activated for this asset.

    """

    model_config = ConfigDict(from_attributes=True)

    code: Annotated[str, Field(description="The asset unique code.", examples=["AS-0001"])]
    name: Annotated[str, Field(description="The asset name.", examples=["Asset 1"])]
    activation_cost: Annotated[float, Field(description="The asset activation cost, in €.", examples=[100.0])]
    availability: Annotated[
        list[date], Field(description="The asset availability dates.", examples=[date(2026, 4, 20)])
    ]
    volume: Annotated[int, Field(description="The asset maximum available volume, in kW.", examples=[100])]


class AssetListOut(BaseModel):
    """
    Pydantic schema for asset list response.

    Attributes:
        assets: list of assets.

    """

    assets: Annotated[
        list[Asset],
        Field(
            description="The list of assets selected for the activation.",
            examples=[
                Asset(
                    code="AS-0001", name="Asset 1", activation_cost=100.0, availability=[date(2026, 4, 20)], volume=100
                )
            ],
        ),
    ]
    total_volume: Annotated[int, Field(description="The total volume of the selected assets, in kW.", examples=[100])]
    total_cost: Annotated[
        float, Field(description="The total cost of the selected assets activation, in €.", examples=[100.0])
    ]
