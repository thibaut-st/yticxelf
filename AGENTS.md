# Repository Guidelines

## Project Structure & Module Organization

`main.py` is the FastAPI entrypoint and currently defines the `POST /request/activation` route. Keep request handling
thin there and push business logic into `services/`. `core/config.py` loads environment-backed settings, including
`OPTIMIZATION_ALGORITHM`. `data/` contains the SQLite engine/session setup, the sample-data loader, and JSON sample
datasets. `models/` holds SQLAlchemy models plus repository helpers, `schemas/` holds Pydantic API models, and `tests/`
contains the automated `unittest` suite. `test_main.http` is the manual HTTP client collection, and
`.pre-commit-config.yaml` defines the local quality hooks.

## Build, Test, and Development Commands

Use `uv` for environment and dependency management.

- `uv sync` installs the project dependencies.
- Copy `.env.dist` to `.env` and set `OPTIMIZATION_ALGORITHM` to `scip` or `bf`.
- `uv run python -m data.load_sample_assets` recreates `data/flexcity.db` from `data/sample_assets.json`.
- `uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000` starts the local API.
- `uv run python -m unittest -v` runs the automated test suite.
- `uv run coverage run -m unittest` and `uv run coverage report -m` run the suite with coverage reporting.
- `uv run mypy .` runs strict type checking.
- `uv run ruff check .` runs linting.
- `uv run pre-commit run --all-files` runs the configured local hooks.
- The requests in `test_main.http` cover manual API checks against a running server.

## Coding Style & Naming Conventions

Follow PEP 8 with 4-space indentation and the repository `ruff` line length of 120. Use `snake_case` for functions,
variables, and modules, and `CamelCase` for classes and Pydantic or SQLAlchemy models. Keep imports grouped as standard
library, third-party, and local modules. Type annotations are expected throughout the codebase because `mypy` runs in
strict mode. Prefer small route handlers, explicit schema types, and service-layer functions that can be tested
independently from FastAPI and the database.

## Testing Guidelines

Use the built-in `unittest` test runner, not `pytest`. Add API tests under `tests/test_*.py`, service tests under
`tests/services/`, and repository tests under `tests/models/`. For repository tests, follow `tests/models/base.py` and
bind repositories to an isolated in-memory SQLite database instead of the on-disk `data/flexcity.db`. Cover both success
paths and failure or validation paths for endpoint changes. Update `test_main.http` whenever the public request or
response contract changes. `tests/speed_test.py` is for manual algorithm benchmarking and is not part of the default
`unittest` discovery run.

## Documentation Maintenance

Keep `README.md` aligned with the actual local workflow: `.env` setup, database bootstrap, local URLs, and the current
request and response contract. The local development endpoint is `/request/activation`; if `root_path` or deployment
routing changes, document the difference between live local URLs and OpenAPI server metadata clearly. Update `README.md`
and `test_main.http` in the same change whenever endpoint paths, payload validation, sample responses, or startup
commands change.

## Commit & Pull Request Guidelines

Recent history uses short, imperative subjects and often includes ticket prefixes such as `F-004 - Add SCIP algorithm`.
Keep commit titles concise, present tense, and under about 72 characters. PRs should summarize the behavior change, list
the verification commands you ran, and call out dependency, environment, or data-model changes. For API changes, include
sample requests and responses from `curl`, `test_main.http`, or automated tests.

## Configuration Tips

Target Python `>=3.14` as declared in `pyproject.toml`. `.env` is ignored by Git; use `.env.dist` as the template and
avoid committing local environment changes. `OPTIMIZATION_ALGORITHM=scip` is the sensible default for larger datasets,
while `bf` is mainly useful for very small cases or algorithm comparisons. Avoid hand-editing `uv.lock` except when
resolving merge conflicts. Be careful with `uv run python -m data.load_sample_assets`: it deletes and recreates
`data/flexcity.db`.
