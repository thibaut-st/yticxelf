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

## Technical context

This project uses FastAPI, a Python web API framework, and Uvicorn, an ASGI server used to run the app locally.

## Run locally

Prerequisites:

- Python 3.14+
- `uv` (Python package and environment manager, similar to `pipenv` or `poetry`)

Install dependencies:

```bash
uv sync
```

Start the development server:

```bash
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.

## API docs

Once the server is running, you can access:

- Swagger UI at `http://127.0.0.1:8000/docs`
- The OpenAPI schema at `http://127.0.0.1:8000/openapi.json`
- ReDoc at `http://127.0.0.1:8000/redoc`

Useful endpoints:

- `GET /`
- `GET /hello/{name}`

Example:

```bash
curl http://127.0.0.1:8000/hello/User
```
