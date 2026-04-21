FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/usr/local/app/.venv/bin:${PATH}" \
    OPTIMIZATION_ALGORITHM=scip \
    SAMPLE_ASSETS_FILE=sample_assets_10000.json \
    FLEXCITY_DATABASE_PATH=/var/lib/flexcity/flexcity.db

WORKDIR /usr/local/app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project \
    && uv cache clean

COPY core ./core
COPY data ./data
COPY models ./models
COPY schemas ./schemas
COPY services ./services
COPY main.py ./

RUN mkdir -p /var/lib/flexcity \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && chown app:app /var/lib/flexcity

USER app

VOLUME ["/var/lib/flexcity"]

EXPOSE 8000

ENTRYPOINT ["sh", "-c", "python -m data.load_sample_assets && exec \"$@\"", "--"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
