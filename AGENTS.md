# Repository Guidelines

## Project Structure & Module Organization
`main.py` is the FastAPI entrypoint and currently contains all routes. `README.md` is the human-facing startup guide, `pyproject.toml` defines project metadata and runtime dependencies, and `uv.lock` pins resolved versions for reproducible installs. `test_main.http` contains IDE-friendly HTTP requests for manual endpoint checks. If the API grows, split route groups into packages such as `app/routes/` and move shared schemas into `app/schemas/` instead of expanding `main.py` indefinitely.

## Build, Test, and Development Commands
Use `uv` for environment and dependency management.

- `uv sync` installs dependencies from `pyproject.toml` and `uv.lock`.
- `uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000` starts the local development server.
- `uv run python -m compileall .` performs a quick syntax check before opening a PR.
- `curl http://127.0.0.1:8000/hello/User` or the requests in `test_main.http` verify endpoint behavior manually.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indentation. Use `snake_case` for functions and variables, `CamelCase` for classes and future Pydantic models, and lowercase module names. Keep imports grouped as standard library, third-party, and local modules. Prefer small route handlers and typed parameters; split code by feature once unrelated endpoints start to accumulate. No formatter or linter is configured yet, so keep formatting consistent and lines readable.

## Testing Guidelines
There is no automated test suite yet. Until one is added, update `test_main.http` whenever an endpoint, parameter, or response changes and manually exercise requests against a local server. When automated tests are introduced, place them under `tests/` and name files `test_<feature>.py` so `pytest` usage is straightforward. Each route should have at least one success case and one validation or error case.

## Documentation Maintenance
Keep `README.md` focused on local startup and API docs access. When the run command, default host/port, or public endpoints change, update `README.md` and `test_main.http` in the same change so the human docs and manual checks stay consistent.

## Commit & Pull Request Guidelines
The current Git history uses short imperative subjects such as `Initial commit`; keep commit titles concise, present tense, and under about 72 characters. PRs should summarize behavior changes, list the commands or requests used for verification, and call out dependency or Python-version changes. For API changes, include sample requests and responses from `curl` or the IDE HTTP client.

## Configuration Tips
Target Python `>=3.14` as declared in `pyproject.toml`. Keep secrets out of source control and avoid hand-editing `uv.lock` except when resolving merge conflicts.
