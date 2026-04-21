from unittest import TestCase
from unittest.mock import MagicMock, patch

from services._algorithms import brute_force, dynamic_programming, scip
from tests._helpers import get_sample_data


class TestAllAlgorithms(TestCase):
    """Test all algorithms."""

    def setUp(self) -> None:
        """Create a list of available assets."""
        assets = get_sample_data("sample_assets.json")
        self.available_assets = [asset for asset in assets if "2026-04-24" in asset.availability]

    def test_all_algorithms_same_result(self) -> None:
        """Test that all algorithms return the same result."""
        # ARRANGE
        activation_volume = 100
        # ACT
        bf_result = brute_force(activation_volume, self.available_assets)
        bf_result_codes = [asset.code for asset in bf_result]
        dp_result = dynamic_programming(activation_volume, self.available_assets)
        dp_result_codes = [asset.code for asset in dp_result]
        scip_result = scip(activation_volume, self.available_assets)
        scip_result_codes = [asset.code for asset in scip_result]
        # ASSERT
        expected_result = ["A-005", "A-006"]
        self.assertEqual(expected_result, bf_result_codes)
        self.assertEqual(expected_result, dp_result_codes)
        self.assertEqual(expected_result, scip_result_codes)


class TestBruteForce(TestCase):
    """Test the brute force algorithm."""

    def setUp(self) -> None:
        """Create a list of available assets."""
        assets = get_sample_data("sample_assets.json")
        self.available_assets = [asset for asset in assets if "2026-04-24" in asset.availability]

    def test_bf_ok(self) -> None:
        """Test the brute force algorithm, which should return the optimal solution."""
        # ARRANGE
        activation_volume = 100
        # ACT
        result = brute_force(activation_volume, self.available_assets)
        result_codes = [asset.code for asset in result]
        # ASSERT
        self.assertEqual(["A-005", "A-006"], result_codes)

    def test_bf_not_enough_power(self) -> None:
        """Test the brute force algorithm, which should return an empty list if not enough power is available."""
        # ARRANGE
        activation_volume = 10000
        # ACT
        with self.assertRaises(ValueError) as context:
            brute_force(activation_volume, self.available_assets)
        # ASSERT
        self.assertEqual("No valid asset selection found.", str(context.exception))

    def test_bf_no_available_assets(self) -> None:
        """Test the brute force algorithm, which should return an empty list if no assets are available."""
        # ARRANGE
        activation_volume = 100
        # ACT
        with self.assertRaises(ValueError) as context:
            brute_force(activation_volume, [])
        # ASSERT
        self.assertEqual("No valid asset selection found.", str(context.exception))


class TestDynamicProgramming(TestCase):
    """Test the dynamic programming algorithm."""

    def setUp(self) -> None:
        """Create a list of available assets."""
        assets = get_sample_data("sample_assets_100.json")
        self.available_assets = [asset for asset in assets if "2026-04-20" in asset.availability]

    def test_dp_ok(self) -> None:
        """Test the dynamic programming algorithm, which should return the optimal solution."""
        # ARRANGE
        activation_volume = 300
        # ACT
        result = dynamic_programming(activation_volume, self.available_assets)
        result_codes = [asset.code for asset in result]
        # ASSERT
        self.assertEqual(["A-037", "A-055", "A-073", "A-091"], result_codes)
        self.assertEqual(648.0, sum(asset.activation_cost for asset in result))

    def test_dp_not_enough_power(self) -> None:
        """Test the dynamic programming algorithm, which should raise an error if not enough power is available."""
        # ARRANGE
        activation_volume = 10000
        # ACT
        with self.assertRaises(ValueError) as context:
            dynamic_programming(activation_volume, self.available_assets)
        # ASSERT
        self.assertEqual("No valid asset selection found.", str(context.exception))

    def test_dp_no_available_assets(self) -> None:
        """Test the dynamic programming algorithm, which should raise an error if no assets are available."""
        # ARRANGE
        activation_volume = 300
        # ACT
        with self.assertRaises(ValueError) as context:
            dynamic_programming(activation_volume, [])
        # ASSERT
        self.assertEqual("No valid asset selection found.", str(context.exception))


class TestScip(TestCase):
    """Test the SCIP algorithm."""

    def setUp(self) -> None:
        """Create a list of available assets."""
        assets = get_sample_data("sample_assets_100.json")
        self.available_assets = [asset for asset in assets if "2026-04-20" in asset.availability]

    def test_scip_ok(self) -> None:
        """Test the SCIP algorithm, which should return the optimal solution."""
        # ARRANGE
        activation_volume = 300
        # ACT
        result = scip(activation_volume, self.available_assets)
        result_codes = [asset.code for asset in result]
        # ASSERT
        self.assertEqual(["A-037", "A-055", "A-073", "A-091"], result_codes)
        self.assertEqual(648.0, sum(asset.activation_cost for asset in result))

    def test_scip_not_enough_power(self) -> None:
        """Test the SCIP algorithm, which should raise an error if not enough power is available."""
        # ARRANGE
        activation_volume = 10000
        # ACT
        with self.assertRaises(ValueError) as context:
            scip(activation_volume, self.available_assets)
        # ASSERT
        self.assertEqual("No optimal solution found.", str(context.exception))

    def test_scip_no_available_assets(self) -> None:
        """Test the SCIP algorithm, which should raise an error if no assets are available."""
        # ARRANGE
        activation_volume = 300
        # ACT
        with self.assertRaises(ValueError) as context:
            scip(activation_volume, [])
        # ASSERT
        self.assertEqual("No optimal solution found.", str(context.exception))

    @patch("services._algorithms.Solver.CreateSolver")
    def test_scip_ortools_no_solver(self, mock_solver: MagicMock) -> None:
        """Test the SCIP algorithm, which should raise an error if ortools solver is not available."""
        # ARRANGE
        mock_solver.return_value = None
        # ACT
        with self.assertRaises(RuntimeError) as context:
            scip(100, self.available_assets)
        # ASSERT
        self.assertEqual("Failed to create SCIP solver", str(context.exception))
