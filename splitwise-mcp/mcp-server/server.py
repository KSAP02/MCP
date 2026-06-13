"""Splitwise MCP server (port 8080).

Thin entrypoint: it builds the FastMCP app from config, registers every tool
implementation in tools.py, and runs. All the actual logic lives in tools.py.

Run with:  python mcp-server/server.py
Transport: streamable-http  (endpoint: http://127.0.0.1:8080/mcp)
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

import config
import tools

mcp = FastMCP("splitwise", host=config.MCP_HOST, port=config.MCP_PORT)

# Register each implementation in tools.py as an MCP tool. FastMCP derives the
# tool name, input schema, and description from the function's signature and
# docstring, so the definitions stay single-sourced in tools.py.
for fn in tools.ALL_TOOLS:
    mcp.tool()(fn)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
