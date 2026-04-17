# Flexcity

## Description

### Reminder of the subject

Provide the list of selected assets.

Create an HTTP endpoint for receiving the TSO request (also known as the activation) with the following information in
the body:

- Date: date of the activation
- Volume: integer, corresponding to the number of kW needed

Flexcity has a list of assets, defined by the following properties :

- Code: string.
- Name: string.
- Activation cost: double in €, same price whether partial or full capacity.
- Availability: list of dates when the asset is available. For example, an asset can only be available only 1 day of the
  current week.
- Volume: integer, correspond to the number of kW that can be activated for this asset.

Expected behavior:

1. When receiving the activation from the TSO, the service must select a set of available assets whose combined volumes
   will cover
   at least the requested volume.
2. We want to minimize the total activation cost. A non-optimal algorithm is acceptable if it simplifies your
   implementation. If you see the
   optimization challenge, feel free to try a smarter approach or explain it during the interview.
3. The service must answer to the endpoint with the list of assets to activate with their associated powers and prices.

### Trade-offs and assumptions

#### Assumptions

1. If there is not enough power to activate the requested volume, the service must return an error.
   The request body could have an optional parameter `select_all_available` to indicate that the service should select
   all available assets on power shortage.
2. The date is a simple date and not a datetime.
3. The date can be in the future or past.

## Technical context

This project uses FastAPI, a Python web API framework, and Uvicorn, an ASGI server used to run the app locally.

## Run locally

Prerequisites:

- Python 3.14+
- `uv` (Python package and environment manager, similar to `pipenv` or `poetry`)

## Install dependencies

```bash
uv sync
```

## Run locally

Start the development server:

```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000`.

## API docs

Once the server is running, you can access:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Example request

```bash
curl -X POST "http://127.0.0.1:8000/activation-request" \
  -H "Content-Type: application/json" \
  -d "{\"date\":\"2026-04-20\",\"volume\":100}"
```

Example success response:

```json
{
  "assets": [
    {
      "code": "A-007",
      "name": "Asset 7",
      "activation_cost": 210.0,
      "availability": [
        "2026-04-20",
        "2026-04-21",
        "2026-04-22"
      ],
      "volume": 120
    }
  ],
  "total_volume": 120,
  "total_cost": 210.0
}
```

Example capacity-shortage response:

```json
{
  "detail": "Not enough assets available for the requested volume. Available: 355, Requested: 9999"
}
```

## Checks

Automated and manual checks currently used in this repository:

- `uv run python -m unittest` (unit tests)
- `uv run mypy .` (type checking)
- `uv run ruff check .` (code style linting)
- Requests in `test_main.http`

## Current behavior

- The API currently exposes `POST /activation-request`.
- The request body contains `date` and `volume`.
- `volume` must be a positive integer.
- If the requested volume cannot be covered by available assets, the API returns `409 Conflict` with a detailed error
  message.
- The API returns a JSON response with the list of assets to activate.
