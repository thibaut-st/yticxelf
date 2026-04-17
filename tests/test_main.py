from datetime import date
from http import HTTPStatus
from unittest import TestCase
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app
from schemas.activation import ActivationIn


class TestActivationRequestEndpoint(TestCase):
    """Test the activation request endpoint."""

    endpoint = "/activation-request"

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
