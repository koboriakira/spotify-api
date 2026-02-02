FROM python:3.11-slim

WORKDIR /workspace

# Install git and curl (for uv installation)
RUN apt update && \
    apt install -y git curl && \
    apt clean

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Python dependencies
COPY pyproject.toml README.md ./
RUN uv sync --frozen --all-extras || uv sync --all-extras
