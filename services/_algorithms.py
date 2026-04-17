from itertools import combinations

from models.asset import AssetModel


def _brute_force(activation_volume: int, available_assets: list[AssetModel]) -> list[AssetModel]:
    """
    Brute force algorithm to find the optimal combination of assets.

    :param activation_volume: The volume of the activation to reach.
    :param available_assets: The list of available assets.
    :return: The optimal combination of assets that reaches the activation volume for a minimum cost.
    """
    selected_assets = []
    final_cost = float("inf")  # Initialize the float with infinity

    # Iterate through all possible combinations of assets
    # iteration is the number of assets in the combination
    # range from 1 to the number of available assets
    for iteration in range(1, len(available_assets) + 1):
        asset_combination = combinations(available_assets, iteration)
        for asset_subset in asset_combination:
            combined_volume: int = sum(asset.volume for asset in asset_subset)
            combined_cost: float = sum(asset.activation_cost for asset in asset_subset)

            if combined_volume >= activation_volume and combined_cost < final_cost:
                selected_assets = list(asset_subset)  # update the selected assets to the current combination
                final_cost = combined_cost  # update the final cost to the current combination's cost

    return selected_assets


_algorithm_map = {
    "bf": _brute_force,
}
