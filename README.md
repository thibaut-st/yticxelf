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
4. Assets' codes are unique.

#### Trade-offs

1. The dates in the Asset's availability model are saved as simple JSON lists.
2. Since the dates are simple JSON lists, 
the service needs to sort the list manually instead of using a database filter.
3. No migrations, the database is created with sample data by a helper.

## Technical context

This project uses FastAPI, a Python web API framework, and Uvicorn, an ASGI server used to run the app locally.

### Prerequisites

- Python 3.14+
- `uv` (Python package and environment manager, similar to `pipenv` or `poetry`)

## Setup

### Install dependencies

```bash
uv sync
```

### Environment variables

Copy `.env.dist` to `.env` and set the environment variables:
- `OPTIMIZATION_ALGORITHM`
  - `bf`: Brute-force algorithm.
  - `scip`: SCIP algorithm, run from the OR-Tools library.

### Run locally

To get a working local database, run:

```bash
uv run python -m data.load_sample_assets
```

This debug helper deletes `data/flexcity.db` if it exists, recreates the schema from the SQLAlchemy models, 
and loads the sample assets from `data/sample_assets.json`.

Then start the development server:

```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000/api/v1/`.

## API

### Auto-generated documentation

Once the server is running, you can access:

- Swagger UI: `http://127.0.0.1:8000/api/v1/docs`
- OpenAPI schema: `http://127.0.0.1:8000/api/v1/openapi.json`
- ReDoc: `http://127.0.0.1:8000/api/v1/redoc`

### Endpoint

- `POST /request/activation`: Request activation of assets.
    - Input: 
      ```json
      {"date": <date as str>, "volume": <int>}
      ```
    - Output: 
      ```json
      {
        "assets": [
          {
            "code": <str>,
            "name": <str>,
            "activation_cost": <float>,
            "availability": [
              <date as str>,
              ...
            ],
            "volume": <int>
          },
          ...
        ],
        "total_volume": <int>,
        "total_cost": <float>
      }
      ```

## Example request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/request/activation" \
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

- `uv run python -m unittest` (run the unit tests)
- `uv run coverage run -m unittest` (run the unit tests with coverage)
- `uv run coverage report -m` (show the coverage report; `data/` and `tests/` are excluded)
- `uv run mypy .` (type checking)
- `uv run ruff check .` (code style linting)
- Requests in `test_main.http`

## Current behavior

- The API currently exposes `POST /request/activation`.
- The request body contains `date` and `volume`: `date` must be a string of format `YYYY-MM-DD` and `volume` must be a positive integer.
- The endpoint reads assets from the SQLite database in `data/flexcity.db`.
- The helper `uv run python -m data.load_sample_assets` resets that database and loads the sample assets from
  `data/sample_assets.json`.
- Asset availability is stored as JSON lists of ISO date strings and filtered in Python for the requested date.
- Asset selection uses a brute-force combination search to minimize total activation cost while covering the requested
  volume.
- On success, the API returns the selected assets plus `total_volume` and `total_cost`.
- The current implementation also persists activation and activation-history rows in SQLite.
- If the requested volume cannot be covered by available assets, the API returns `409 Conflict` with a detailed error
  message.
