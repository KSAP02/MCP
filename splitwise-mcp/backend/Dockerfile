# Build context is the repo root (see docker-compose.yml) so we can reuse the
# shared requirements.txt and keep `backend` importable as a package.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package; WORKDIR /app stays on sys.path so `backend.main:app`
# and the package's relative imports resolve.
COPY backend ./backend

EXPOSE 8001

# Bind 0.0.0.0 so the port is reachable from outside the container.
# --port honors BACKEND_PORT if you change it in .env (defaults to 8001).
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${BACKEND_PORT:-8001}
