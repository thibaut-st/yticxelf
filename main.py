from typing import Annotated

from fastapi import FastAPI, Query

from schemas.activation import ActivationIn
from schemas.asset import Asset, AssetListOut
from services.asset_selection import optimize_asset_selection

app = FastAPI()


@app.get("/assets")
async def get_assets(filters: Annotated[ActivationIn, Query()]) -> AssetListOut:
    """Get assets."""
    selected_assets = optimize_asset_selection(activation=filters)
    return AssetListOut(
        assets=[Asset(**asset) for asset in selected_assets["selected_assets"]],
        total_volume=selected_assets["total_volume_selected"],
        total_cost=selected_assets["total_cost_selected"],
    )
