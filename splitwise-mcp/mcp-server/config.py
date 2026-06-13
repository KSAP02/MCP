"""Configuration for the MCP server, gathered from environment / .env.

Holds the backend URL the tools call, plus the host/port the MCP server binds.
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# Where the FastAPI backend lives. In docker-compose this is set to
# http://backend:8001; locally it falls back to BACKEND_HOST/BACKEND_PORT.
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    f"http://{os.getenv('BACKEND_HOST', '127.0.0.1')}:{os.getenv('BACKEND_PORT', '8001')}",
)

# Where this MCP server listens.
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", "8080"))

# Per-request timeout (seconds) when calling the backend.
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "30"))
