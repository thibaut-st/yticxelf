from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from schemas.activation import ActivationIn
from schemas.asset import Asset, AssetListOut
from services.asset_selection import optimize_asset_selection

app = FastAPI()


@app.post("/activation-request")
async def request_activation(activation: ActivationIn) -> AssetListOut:
    """Request an activation."""
    try:
        selected_assets = optimize_asset_selection(activation=activation)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(e)) from e

    return AssetListOut(
        assets=[Asset(**asset) for asset in selected_assets["selected_assets"]],
        total_volume=selected_assets["total_volume_selected"],
        total_cost=selected_assets["total_cost_selected"],
    )
