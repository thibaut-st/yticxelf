import logging
from copy import deepcopy
from typing import Literal, TypedDict

from data import ASSET_DATA, AssetData
from schemas.activation import ActivationIn
from services._algorithms import _algorithm_map

_logger = logging.getLogger(__name__)


class AssetSelection(TypedDict):
    """
    Asset selection type.

    Attributes:
        selected_assets: list of selected assets from the optimization algorithm.
        total_volume_selected: total volume of the selected assets.
        total_cost_selected: total cost of the selected assets.

    """

    selected_assets: list[AssetData]
    total_volume_selected: int
    total_cost_selected: float


def optimize_asset_selection(activation: ActivationIn, algorithm: Literal["bf"] = "bf") -> AssetSelection:
    """
    Given an activation, optimize the asset selection.

    :param activation: The activation request from the TSO.
    :param algorithm: The algorithm to use for optimization (default: brute force).
    :return: The optimized asset selection list.
    """
    date = activation.date

    assets = deepcopy(ASSET_DATA)
    available_assets = [asset for asset in assets if date in asset["availability"]]

    total_volume_available = sum(asset["volume"] for asset in available_assets)
    if total_volume_available < activation.volume:
        _logger.warning("Not enough assets available for the requested volume. Returning all available assets.")
        selected_assets = available_assets
    else:
        selected_assets = _algorithm_map[algorithm](activation.volume, available_assets)

    total_volume_selected = sum(asset["volume"] for asset in selected_assets)
    total_cost_selected = sum(asset["activation_cost"] for asset in selected_assets)

    return {
        "selected_assets": selected_assets,
        "total_volume_selected": total_volume_selected,
        "total_cost_selected": total_cost_selected,
    }
