# Build context is the repo root (see docker-compose.yml) so we can reuse the
# shared requirements.txt.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# server.py is a standalone script (no package), so copy the dir contents flat.
COPY mcp-server/ ./

EXPOSE 8080

# server.py binds to MCP_HOST/MCP_PORT from the environment (set to 0.0.0.0
# in docker-compose.yml) and calls the backend at BACKEND_URL.
CMD ["python", "server.py"]
