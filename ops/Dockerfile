# Une seule image, deux roles choisis par AGENT_ROLE (ET-007, ET-009).
# syntax=docker/dockerfile:1.7

FROM python:3.13-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
COPY backend ./backend
RUN uv sync --locked --no-dev --no-editable

FROM python:3.13-slim AS runtime
LABEL org.opencontainers.image.title="Agent de production controlee de livrables" \
      org.opencontainers.image.description="Fondations MS-0 - API et travailleur" \
      org.opencontainers.image.licenses="Proprietary"
RUN groupadd --gid 10001 forge && useradd --uid 10001 --gid 10001 --create-home forge
WORKDIR /app
COPY --from=builder --chown=forge:forge /app/.venv /app/.venv
COPY --chown=forge:forge backend/src ./backend/src
COPY --chown=forge:forge rulepacks ./rulepacks
COPY --chown=forge:forge ops/entrypoint.sh /app/entrypoint.sh
RUN chmod 0555 /app/entrypoint.sh
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/backend/src" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AGENT_ROLE=api
USER 10001:10001
EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
