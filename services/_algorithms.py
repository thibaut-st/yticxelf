import logging
from collections.abc import Callable
from itertools import combinations
from math import inf
from uuid import UUID

from ortools.linear_solver.pywraplp import Solver

from core.config import AlgorithmType
from models import AssetModel

_logger = logging.getLogger(__name__)

type UseAsset = dict[UUID, bool]
type PowerUsed = dict[UUID, int]


def brute_force(activation_volume: int, available_assets: list[AssetModel]) -> list[AssetModel]:
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


def dynamic_programming(activation_volume: int, available_assets: list[AssetModel]) -> list[AssetModel]:
    """
    Dynamic programming algorithm to find the optimal combination of assets.

    :param activation_volume: The volume of the activation to reach.
    :param available_assets: The list of available assets.
    :return: The optimal combination of assets that reaches the activation volume for a minimum cost.
    """
    # Map asset codes to their corresponding AssetModel objects for faster lookup
    code_asset_map = {asset.code: asset for asset in available_assets}

    # Map to store the optimal solutions for each available volume in the assets
    # Initialize the table with volume 0 kWh at cost 0.00€
    covered_volume_minimal_cost = {0: 0.0}
    # Map to store the optimal assets chosen for each volume
    # Initialize the table with the empty tuple (no assets selected) for volume 0
    covered_volume_chosen_path: dict[int, tuple[str, ...]] = {0: ()}

    covered_volume_minimal_cost, covered_volume_chosen_path = _dp_calculate_solution(
        activation_volume,
        available_assets,
        covered_volume_minimal_cost,
        covered_volume_chosen_path,
    )

    # If target state was never reached, there is no valid solution
    # Meaning that covered_volume_minimal_cost[activation_volume] is not defined
    if activation_volume not in covered_volume_minimal_cost:
        raise ValueError("No valid asset selection found.")

    selected_asset_codes = covered_volume_chosen_path[activation_volume]
    return [code_asset_map[code] for code in selected_asset_codes]


def _dp_calculate_solution(
    activation_volume: int,
    available_assets: list[AssetModel],
    covered_volume_minimal_cost: dict[int, float],
    covered_volume_chosen_path: dict[int, tuple[str, ...]],
) -> tuple[dict[int, float], dict[int, tuple[str, ...]]]:
    """
    Loop through all available assets and calculate the optimal solution for each volume.

    :param activation_volume: The volume of the activation to reach.
    :param available_assets: The list of available assets.
    :param covered_volume_minimal_cost: The map to store the optimal solutions for each available volume.
    :param covered_volume_chosen_path: The map to store the optimal asset chosen for each volume.
    """
    for asset in available_assets:
        asset_code = asset.code
        asset_volume = asset.volume
        asset_cost = asset.activation_cost

        # Copy the previous values to initialize the next iteration
        # Read from the old map, write to the new map
        # Avoid modifying the original maps accidentally
        next_covered_volume_minimal_cost = covered_volume_minimal_cost.copy()
        next_covered_volume_chosen_path = covered_volume_chosen_path.copy()

        # Loop through all covered volumes and update the optimal solution for each volume
        for current_covered_volume, current_minimal_cost in covered_volume_minimal_cost.items():
            # Calculate the new covered volume, "min" ensure that we don't go over the activation volume
            new_covered_volume = min(activation_volume, current_covered_volume + asset_volume)
            # Calculate the new cost associated with the new covered volume
            new_cost = current_minimal_cost + asset_cost

            # Get the best known cost for the new covered volume (infinity if not known yet)
            best_know_cost = next_covered_volume_minimal_cost.get(new_covered_volume, inf)
            # Update the optimal solution if the new cost is lower than the best known cost
            if new_cost < best_know_cost:
                next_covered_volume_minimal_cost[new_covered_volume] = new_cost
                next_covered_volume_chosen_path[new_covered_volume] = covered_volume_chosen_path[
                    current_covered_volume
                ] + (asset_code,)

        # Update the current iteration's optimal solution with the new values, go to the next iteration (next asset)
        covered_volume_minimal_cost = next_covered_volume_minimal_cost
        covered_volume_chosen_path = next_covered_volume_chosen_path

    return covered_volume_minimal_cost, covered_volume_chosen_path


def scip(activation_volume: int, available_assets: list[AssetModel]) -> list[AssetModel]:
    """
    SCIP algorithm to find the optimal combination of assets.

    Use the OR-TOOLS library to solve the SCIP optimization problem.

    :param activation_volume: The volume of the activation to reach.
    :param available_assets: The list of available assets.
    :return: The optimal combination of assets that reaches the activation volume for a minimum cost.
    """
    # Create an OR-Tools solver for the SCIP optimization problem
    # Raises a RuntimeError if the solver cannot be created
    ortools_solver = Solver.CreateSolver("SCIP")
    if ortools_solver is None:
        raise RuntimeError("Failed to create SCIP solver")

    use_asset, power_used = _define_solver_variables(ortools_solver, available_assets)
    _set_solver_constraints(ortools_solver, use_asset, power_used, activation_volume, available_assets)
    _set_solver_objective(ortools_solver, use_asset, available_assets)

    # Solve the problem given the variables, constraints, and the objective.
    status = ortools_solver.Solve()

    if status not in (Solver.OPTIMAL, Solver.FEASIBLE):
        message = "No optimal solution found."
        _logger.warning(message)
        raise ValueError(message)

    return _get_selected_assets(use_asset, available_assets)


def _define_solver_variables(ortools_solver: Solver, available_assets: list[AssetModel]) -> tuple[UseAsset, PowerUsed]:
    """
    Define the variables used in the SCIP optimization problem.

    Defines use_asset and power_used as the variables used in the optimization problem.

    use_asset: A dictionary containing all the assets as a BoolVar (True/False)
        indicating if they are used or not in the solution.
    power_used: A dictionary containing the power used by each asset as an IntVar (between 0 and its volume).

    :param ortools_solver: The OR-tools solver.
    :param available_assets: The list of available assets.
    :return: A tuple containing the instantiated use_asset and power_used dictionaries.
    """
    use_asset: UseAsset = {}
    power_used: PowerUsed = {}
    for asset in available_assets:
        # parameters:
        #   lb = lower bound power usage (always 0)
        #   up = upper bound of the power of the asset (asset's volume)
        #   name = name of the variable's solver for solver internal use and debugging purpose
        use_asset[asset.id] = ortools_solver.BoolVar(name=f"use_asset_{asset.code}")
        power_used[asset.id] = ortools_solver.IntVar(lb=0, ub=asset.volume, name=f"power_used_{asset.code}")

    return use_asset, power_used


def _set_solver_constraints(
    ortools_solver: Solver,
    use_asset: UseAsset,
    power_used: PowerUsed,
    activation_volume: int,
    available_assets: list[AssetModel],
) -> None:
    """
    Set the constraints for the SCIP optimization problem and add them to the solver.

    Constraint 1: The chosen solution must activate at least the requested volume.

    Constraint 2: For each asset, the power can only be used if the asset is used,
        and the power used for this asset can't be superior to its max volume.

    Examples:
       use_asset[asset_id] = 0 -> power_used[asset_id] <= 0 -> can't provide power
       use_asset[asset_id] = 1 -> power_used[asset_id] <= asset.volume -> can provide power up to the maximum

    :param ortools_solver: The OR-tools solver.
    :param use_asset: The dictionary of the assets as a solver's boolean (used/not used).
    :param power_used: The dictionary of the power usage of the assets as a solver's integer (between 0 and max volume).
    :param activation_volume: The volume of the activation to reach.
    :param available_assets: The list of available assets.

    """
    # Constraint 1
    # power_sum: Sum of the power of the assets as an expression (power_used_a + power_used_b + ...)
    power_sum = ortools_solver.Sum(power_used[asset.id] for asset in available_assets)
    ortools_solver.Add(constraint=power_sum >= activation_volume, name="power_sum_geq")

    # Constraint 2
    for asset in available_assets:
        asset_id = asset.id
        ortools_solver.Add(power_used[asset_id] <= asset.volume * use_asset[asset_id], name="use_power_if_selected")


def _set_solver_objective(ortools_solver: Solver, use_asset: UseAsset, available_assets: list[AssetModel]) -> None:
    """
    Set the objective for the SCIP optimization problem.

    Objective: Minimize the total activation cost of the combination of assets.

    :param ortools_solver: The OR-tools solver.
    :param use_asset: The dictionary of the assets as a solver's boolean (used/not used).
    :param available_assets: The list of available assets.
    """
    # objective_to_minimize: Sum of the assets' costs activated or not,
    #   as an expression (cost_1 * 0|1 + cost_2 * 0|1 + ...)
    objective_to_minimize = ortools_solver.Sum(
        __get_asset(asset.id, available_assets).activation_cost * use_asset[asset.id] for asset in available_assets
    )
    # Minimize: Instruct the solver to make the total cost of the combination as small as possible.
    ortools_solver.Minimize(objective_to_minimize)


def _get_selected_assets(use_asset: UseAsset, available_assets: list[AssetModel]) -> list[AssetModel]:
    """
    Extract the selected assets from the solver's solution.

    After calling the solver Solve() method, the solution is stored in the use_asset dictionary for each asset.

    :param use_asset: The dictionary containing the solver's solution for each asset (updated by the solver).
    :param available_assets: The list of available assets at the beginning of the optimization.
    :return: The list of selected assets.
    """
    selected_assets = []
    for asset in available_assets:
        # round ensure that the value is an integer with value 0 or 1
        selected = round(use_asset[asset.id].solution_value())  # type: ignore[attr-defined]
        if selected == 1:  # 1 meaning that the asset is part of the found solution
            selected_assets.append(asset)

    return selected_assets


def __get_asset(asset_id: UUID, assets: list[AssetModel]) -> AssetModel:
    """
    Get the asset with the given ID from a list of assets.

    :param asset_id: The UUID of the asset to retrieve.
    :param assets: The list of assets to search in.
    :return: The asset with the given ID.
    """
    return next(asset for asset in assets if asset.id == asset_id)


algorithm_map: dict[AlgorithmType, Callable[[int, list[AssetModel]], list[AssetModel]]] = {
    "bf": brute_force,
    "dp": dynamic_programming,
    "scip": scip,
}
