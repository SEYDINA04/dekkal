FROM python:3.13-slim

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv --no-cache-dir

# Copy workspace-level config (uv workspace)
COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml ./backend/

RUN uv sync --all-packages --no-dev

# Copy application code and model files
COPY backend/ ./backend/

WORKDIR /workspace/backend

EXPOSE 8001

CMD ["uv", "run", "--project", "/workspace", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
