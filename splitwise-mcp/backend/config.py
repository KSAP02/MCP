"""Central configuration, loaded from the .env file at repo root."""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# --- Splitwise API ---
SPLITWISE_API_KEY = os.getenv("SPLITWISE_API_KEY", "")
SPLITWISE_BASE_URL = os.getenv("SPLITWISE_BASE_URL", "https://secure.splitwise.com/api/v3.0")
DEFAULT_CURRENCY = os.getenv("DEFAULT_CURRENCY", "USD")
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))

# --- Backend (FastAPI) ---
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8001"))
BACKEND_URL = os.getenv("BACKEND_URL", f"http://{BACKEND_HOST}:{BACKEND_PORT}")

# --- MCP server ---
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8080"))
