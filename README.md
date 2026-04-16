# Flexcity

## Description

TBD

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
