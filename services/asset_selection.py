from dummy_data import ASSET_DUMMY_DATA
from schemas.activation import ActivationIn
from schemas.asset import Asset


def optimize_asset_selection(activation: ActivationIn) -> list[Asset]:
    """
    Given an activation, optimize the asset selection.

    :param activation: The activation request from the TSO.
    :return: The optimized asset selection list.
    """
    date = activation.date
    return [Asset(**asset) for asset in ASSET_DUMMY_DATA if date in asset["availability"]]  # type: ignore[arg-type, operator]
