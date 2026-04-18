import json
import logging
import timeit
from functools import partial
from pathlib import Path
from unittest import TestCase

from models import AssetModel
from services._algorithms import brute_force, scip

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
            Average: 62.009606200 s per call for 1 run

            20 assets available for 2026-05-05
            Average: 3.234501900000032 s per call for 5 runs
        """
        runs = 1
        date = "2026-05-05"
        asset_record_list = self._get_sample_data("sample_assets_100.json")
        available_assets = [asset for asset in asset_record_list if date in asset.availability]

        scip_partial = partial(brute_force, 100, available_assets)
        total = timeit.timeit(scip_partial, number=runs)

        _logger.info("%s assets available for %s", len(available_assets), date)
        _logger.info("Average: %s s per call for %s runs", total / runs, runs)

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
        asset_record_list = self._get_sample_data("sample_assets_10000.json")
        available_assets = [asset for asset in asset_record_list if date in asset.availability]

        scip_partial = partial(scip, 300, available_assets)
        total = timeit.timeit(scip_partial, number=runs)

        _logger.info("%s assets available for %s", len(available_assets), date)
        _logger.info("Average: %s s per call for %s runs", total / runs, runs)

    @staticmethod
    def _get_sample_data(file_name: str) -> list[AssetModel]:
        """
        Get sample data from a JSON file as a list of AssetModel objects.

        :param file_name: The name of the JSON file.
        :return: A list of AssetModel objects extracted from the JSON file.
        """
        sample_path = Path(__file__).resolve().parent.parent / "data" / file_name
        sample_assets = json.loads(sample_path.read_text(encoding="utf-8"))
        return [AssetModel(**asset_data) for asset_data in sample_assets]
