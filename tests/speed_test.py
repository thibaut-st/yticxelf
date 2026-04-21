import logging
import timeit
from functools import partial
from unittest import TestCase

from models import AssetModel
from services._algorithms import brute_force, dynamic_programming, scip
from tests._helpers import get_sample_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

_logger = logging.getLogger(__name__)


class TestAlgorithms(TestCase):
    """Test the SCIP algorithm speed."""

    def test_bf(self) -> None:
        """
        Test the brute force algorithm speed.

        Results:
            file: sample_assets_100.json

            24 assets available for 2026-04-29
            Average: 62.0096s per call for 1 run

            20 assets available for 2026-05-05
            Average: 3.2345s per call for 5 runs
        """
        runs = 1
        date = "2026-05-05"
        asset_record_list = get_sample_data("sample_assets_100.json")
        available_assets = [asset for asset in asset_record_list if date in asset.availability]

        scip_partial = partial(brute_force, 100, available_assets)
        total = timeit.timeit(scip_partial, number=runs)

        self._log_result(available_assets, date, runs, total)

    def test_dp(self) -> None:
        """
        Test the dynamic programming algorithm speed.

        Results:
            file: sample_assets_10000.json
            2224 assets available for 2026-04-29
            Average: 0.0575s per call for 10 runs
        """
        runs = 10
        date = "2026-04-29"
        asset_record_list = get_sample_data("sample_assets_10000.json")
        available_assets = [asset for asset in asset_record_list if date in asset.availability]

        dp_partial = partial(dynamic_programming, 1200, available_assets)
        total = timeit.timeit(dp_partial, number=runs)

        self._log_result(available_assets, date, runs, total)

    def test_scip(self) -> None:
        """
        Test the SCIP algorithm speed.

        Results:
            file: sample_assets_10000.json
            2224 assets available for 2026-04-29
            Average: 0.044205460 s per call for 10 runs
        """
        runs = 10
        date = "2026-04-29"
        asset_record_list = get_sample_data("sample_assets_10000.json")
        available_assets = [asset for asset in asset_record_list if date in asset.availability]

        scip_partial = partial(scip, 1200, available_assets)
        total = timeit.timeit(scip_partial, number=runs)

        self._log_result(available_assets, date, runs, total)

    @staticmethod
    def _log_result(available_assets: list[AssetModel], date: str, runs: int, total: float) -> None:
        """
        Log the results of the test.

        :param available_assets: The list of available assets.
        :param date: The date for which the test was run.
        :param runs: The number of runs.
        :param total: The total time taken for the test.
        """
        _logger.info("%s assets available for %s", len(available_assets), date)
        _logger.info("Average: %.4fs per call for %s runs", total / runs, runs)
