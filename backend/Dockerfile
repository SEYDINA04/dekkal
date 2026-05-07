FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc g++ libgomp1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv --no-cache-dir

COPY pyproject.toml .
RUN uv pip install --system --no-cache .

COPY . .

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
