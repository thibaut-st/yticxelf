import json
from pathlib import Path

from models.asset import AssetModel

__SAMPLE_ASSETS_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_assets.json"

__ASSET_DUMMY_DATA = json.loads(__SAMPLE_ASSETS_PATH.read_text(encoding="utf-8"))

ASSET_DUMMY_MODELS = []

for asset in __ASSET_DUMMY_DATA:
    asset_model = AssetModel(
        code=asset["code"],
        name=asset["name"],
        activation_cost=asset["activation_cost"],
        availability=asset["availability"],
        volume=asset["volume"],
    )
    ASSET_DUMMY_MODELS.append(asset_model)
