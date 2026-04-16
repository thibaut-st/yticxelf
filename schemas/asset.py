from datetime import date

from pydantic import BaseModel


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

    code: str
    name: str
    activation_cost: float
    availability: list[date]
    volume: int


class AssetListOut(BaseModel):
    """
    Pydantic schema for asset list response.

    Attributes:
        assets: list of assets.

    """

    assets: list[Asset]
