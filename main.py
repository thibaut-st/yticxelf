from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from schemas.activation import ActivationIn
from schemas.asset import Asset, AssetListOut
from services.asset_selection import optimize_asset_selection

app = FastAPI(
    root_path="/api/v1",
    title="Flexcity Backend Technical Test",
    description="""
    Expose an API that allows the TSO to request an activation.

    The activate will select the assets that will be used to reach the requested volume.

    The selected assets needs to reach the requested volume for a minimum cost.
    """,
)


@app.post(
    "/request/activation",
    summary="Request an activation",
    description="""
          Request an activation at a given date for a given volume.

          Example:
            Input: {
                "date": "2026-04-20",
                "volume": 100
            }
            Output: {
                "assets": [
                    {
                        "code": "A-013",
                        "name": "Asset 13",
                        "activation_cost": 150.0,
                        "availability": ["2026-04-20"],
                        "volume": 100
                    }
                ],
                "total_volume": 100,
                "total_cost": 150.0
            }
          """,
)
async def request_activation(activation: ActivationIn) -> AssetListOut:
    """Request an activation."""
    try:
        selected_assets = optimize_asset_selection(activation=activation)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.CONFLICT, detail=str(e)) from e

    return AssetListOut(
        assets=[Asset.model_validate(asset) for asset in selected_assets["selected_assets"]],
        total_volume=selected_assets["total_volume_selected"],
        total_cost=selected_assets["total_cost_selected"],
    )
