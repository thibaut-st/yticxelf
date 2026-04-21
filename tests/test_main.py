from datetime import date
from http import HTTPStatus
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from data.db import Base, make_engine, make_session_factory
from main import app
from schemas.activation import ActivationIn
from tests._helpers import get_sample_data


class TestActivationRequestEndpoint(TestCase):
    """Test the activation request endpoint."""

    endpoint = "/request/activation"

    def setUp(self) -> None:
        """Create a test client for each test."""
        self.client = TestClient(app)

    def tearDown(self) -> None:
        """Close the test client after each test."""
        self.client.close()

    @patch("main.optimize_asset_selection")
    def test_request_activation_ok(self, mock_optimize: MagicMock) -> None:
        """Return the selected assets when the request is valid."""
        # ARRANGE
        activation_data = {
            "date": "2026-04-20",
            "volume": 100,
        }
        mock_optimize.return_value = {
            "selected_assets": [
                {
                    "code": "A-007",
                    "name": "Asset 7",
                    "activation_cost": 210.0,
                    "availability": [date(2026, 4, 20), date(2026, 4, 21), date(2026, 4, 22)],
                    "volume": 120,
                }
            ],
            "total_volume_selected": 120,
            "total_cost_selected": 210.0,
        }

        # ACT
        response = self.client.post(self.endpoint, json=activation_data)

        # ASSERT
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertDictEqual(
            {
                "assets": [
                    {
                        "code": "A-007",
                        "name": "Asset 7",
                        "activation_cost": 210.0,
                        "availability": ["2026-04-20", "2026-04-21", "2026-04-22"],
                        "volume": 120,
                    }
                ],
                "total_volume": 120,
                "total_cost": 210.0,
            },
            response.json(),
        )
        mock_optimize.assert_called_once()
        called_activation = mock_optimize.call_args.kwargs["activation"]
        self.assertIsInstance(called_activation, ActivationIn)
        self.assertEqual(date(2026, 4, 20), called_activation.date)
        self.assertEqual(100, called_activation.volume)

    @patch("main.optimize_asset_selection")
    def test_request_activation_conflict(self, mock_optimize: MagicMock) -> None:
        """Return a conflict when the service cannot satisfy the request."""
        # ARRANGE
        error_message = "Not enough assets available for the requested volume. Available: 355, Requested: 9999"
        mock_optimize.side_effect = ValueError(error_message)

        # ACT
        response = self.client.post(
            self.endpoint,
            json={
                "date": "2026-04-20",
                "volume": 9999,
            },
        )

        # ASSERT
        self.assertEqual(HTTPStatus.CONFLICT, response.status_code)
        self.assertDictEqual({"detail": error_message}, response.json())
        mock_optimize.assert_called_once()
        called_activation = mock_optimize.call_args.kwargs["activation"]
        self.assertIsInstance(called_activation, ActivationIn)
        self.assertEqual(date(2026, 4, 20), called_activation.date)
        self.assertEqual(9999, called_activation.volume)

    @patch("main.optimize_asset_selection")
    def test_request_activation_validation_errors(self, mock_optimize: MagicMock) -> None:
        """Reject invalid payloads before the service layer is invoked (Pydantic errors)."""
        # ARRANGE
        test_cases = (
            {
                "name": "missing date",
                "payload": {"volume": 100},
                "field": "date",
                "error_type": "missing",
                "message_fragment": "Field required",
            },
            {
                "name": "invalid date format",
                "payload": {"date": "2026/04/20", "volume": 100},
                "field": "date",
                "error_type": "date_from_datetime_parsing",
                "message_fragment": "Input should be a valid date or datetime",
            },
            {
                "name": "missing volume",
                "payload": {"date": "2026-04-20"},
                "field": "volume",
                "error_type": "missing",
                "message_fragment": "Field required",
            },
            {
                "name": "non-positive volume",
                "payload": {"date": "2026-04-20", "volume": 0},
                "field": "volume",
                "error_type": "greater_than",
                "message_fragment": "greater than 0",
            },
        )

        for test_case in test_cases:
            with self.subTest(test_case["name"]):
                # ARRANGE
                mock_optimize.reset_mock()

                # ACT
                response = self.client.post(self.endpoint, json=test_case["payload"])

                # ASSERT
                self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)
                mock_optimize.assert_not_called()
                error_detail = response.json()["detail"]
                self.assertEqual(1, len(error_detail))
                validation_error = error_detail[0]
                self.assertEqual(["body", test_case["field"]], validation_error["loc"])
                self.assertEqual(test_case["error_type"], validation_error["type"])
                self.assertIn(test_case["message_fragment"], validation_error["msg"])


class TestActivationRequestEndToEnd(TestCase):
    """
    Test the activation request endpoint end-to-end with an in-memory database.

    The default configurations are used (algorithm=dp, sample assets size=10000).
    """

    def setUp(self) -> None:
        """Create an isolated database and bind all repositories to it."""
        self.engine = make_engine("sqlite+pysqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.session_factory = make_session_factory(self.engine)
        self.assets = get_sample_data("sample_assets_10000.json")

        with self.session_factory.begin() as session:
            session.add_all(asset for asset in self.assets)

        self.client = TestClient(app)

    def test_activation_ok(self) -> None:
        """Test the activation request endpoint is working as expected."""
        # ARRANGE
        activation_data = {
            "date": "2026-04-20",
            "volume": 100,
        }
        # ACT
        response = self.client.post("/request/activation", json=activation_data)
        # ASSERT
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(2, len(response.json()["assets"]))
        self.assertEqual(129, response.json()["total_volume"])
        self.assertEqual(186.0, response.json()["total_cost"])

        asset_codes = [asset["code"] for asset in response.json()["assets"]]
        self.assertEqual(["A-001", "A-091"], sorted(asset_codes))

    def test_activation_conflict(self) -> None:
        """Test the activation request endpoint return a conflict."""
        # ARRANGE
        activation_data = {
            "date": "2030-04-20",
            "volume": 100,
        }
        # ACT
        response = self.client.post("/request/activation", json=activation_data)
        # ASSERT
        self.assertEqual(HTTPStatus.CONFLICT, response.status_code)
        self.assertEqual("No assets available for the requested date", response.json()["detail"])

        # ====

        # ARRANGE
        activation_data = {
            "date": "2026-04-20",
            "volume": 10000,
        }
        # ACT
        response = self.client.post("/request/activation", json=activation_data)
        # ASSERT
        self.assertEqual(HTTPStatus.CONFLICT, response.status_code)
        self.assertEqual(
            "Not enough assets available for the requested volume. Available: 387, Requested: 10000",
            response.json()["detail"],
        )

    def test_activation_wrong_input(self) -> None:
        """Test the activation request endpoint return a pydantic unprocessable entity error."""
        # ARRANGE
        activation_data = {
            "date": "wrong_data_format",
            "volume": 100,
        }
        # ACT
        response = self.client.post("/request/activation", json=activation_data)
        # ASSERT
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)
        self.assertEqual(
            [
                {
                    "ctx": {"error": "invalid character in year"},
                    "input": "wrong_data_format",
                    "loc": ["body", "date"],
                    "msg": "Input should be a valid date or datetime, invalid character in year",
                    "type": "date_from_datetime_parsing",
                }
            ],
            response.json()["detail"],
        )

        # ====

        # ARRANGE
        activation_data = {
            "date": "2026-04-20",
            "volume": "wrong_format",
        }
        # ACT
        response = self.client.post("/request/activation", json=activation_data)
        # ASSERT
        self.assertEqual(HTTPStatus.UNPROCESSABLE_ENTITY, response.status_code)
        self.assertEqual(
            [
                {
                    "input": "wrong_format",
                    "loc": ["body", "volume"],
                    "msg": "Input should be a valid integer, unable to parse string as an integer",
                    "type": "int_parsing",
                }
            ],
            response.json()["detail"],
        )
