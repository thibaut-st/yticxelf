import logging
from typing import TypedDict

from core.config import settings
from models import ActivationAssetHistoryRepository, ActivationRepository, AssetModel, AssetRepository
from schemas.activation import ActivationIn
from services._algorithms import algorithm_map

_logger = logging.getLogger(__name__)


class AssetSelection(TypedDict):
    """
    Asset selection type.

    Attributes:
        selected_assets: list of selected assets from the optimization algorithm.
        total_volume_selected: total volume of the selected assets.
        total_cost_selected: total cost of the selected assets.

    """

    selected_assets: list[AssetModel]
    total_volume_selected: int
    total_cost_selected: float


def optimize_asset_selection(activation: ActivationIn) -> AssetSelection:
    """
    Given an activation, optimize the asset selection.

    :param activation: The activation request from the TSO.
    :return: The optimized asset selection list.
    :raises ValueError: If there are not enough assets available for the requested volume.
    """
    requested_date = activation.date.isoformat()
    requested_volume = activation.volume

    # Get all assets from the database and filter them by availability
    asset_record_list = AssetRepository.get_all_assets()
    available_assets = [asset for asset in asset_record_list if requested_date in asset.availability]

    # Raise an error if there are not enough assets available for the requested volume,
    # or if there is no asset available for the requested date
    __check_availability(requested_volume, available_assets)

    # Call the algorithm that will optimize the asset selection
    optimization_algorithm = settings.optimization_algorithm
    _logger.info(
        "Optimizing asset selection for requested volume %s, with algorithm: %s",
        requested_volume,
        optimization_algorithm,
    )
    selected_assets = algorithm_map[optimization_algorithm](requested_volume, available_assets)
    _logger.info("Asset selection optimized: %s", [selected_asset.code for selected_asset in selected_assets])
    total_volume_selected = sum(asset.volume for asset in selected_assets)
    total_cost_selected = sum(asset.activation_cost for asset in selected_assets)

    # Save the activation and the history of this activation
    activation_record = ActivationRepository.save(activation.date, activation.volume)
    ActivationAssetHistoryRepository.save(activation_record, selected_assets)

    return {
        "selected_assets": selected_assets,
        "total_volume_selected": total_volume_selected,
        "total_cost_selected": total_cost_selected,
    }


def __check_availability(requested_volume: int, available_assets: list[AssetModel]) -> None:
    """
    Check if there are enough assets available for the requested volume.

    Raises a ValueError if there are not enough assets available.

    :param requested_volume: The requested volume from the activation.
    :param available_assets: The list of available assets from the database.
    :raises ValueError: If there are not enough assets available.
    """
    if not available_assets:
        raise ValueError("No assets available for the requested date")

    total_volume_available = sum(asset.volume for asset in available_assets)
    if total_volume_available < requested_volume:
        error_message = (
            f"Not enough assets available for the requested volume. "
            f"Available: {total_volume_available}, Requested: {requested_volume}"
        )
        _logger.error(error_message)
        raise ValueError(error_message)
