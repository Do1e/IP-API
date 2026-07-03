FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder
ENV UV_INDEX_URL=https://mirror.nju.edu.cn/pypi/web/simple \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.14-slim-bookworm AS runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends libssl3 libffi8 && \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY . /app
CMD ["python", "-m", "src.main"]
