# Splitwise MCP

Talk to your Splitwise account from any MCP client. Two services:

- **Backend** — FastAPI on `:8001`. Owns all the logic: a Splitwise HTTP client
  plus a `service/` layer (`expenses`, `groups`, `settlements`).
- **MCP server** — `:8080`. Exposes the backend as MCP tools.

```
MCP client ──MCP──> mcp-server (:8080) ──HTTP──> backend (:8001) ──REST──> Splitwise API
```

## Layout

```
backend/
  config.py            # loads .env (API key, ports, currency)
  client.py            # SplitwiseClient: auth + GET/POST + error handling
  models.py            # pydantic request models
  main.py              # FastAPI app + routes  ->  python -m backend.main
  service/             # importable business logic
    expenses.py        # list / get / create / update / delete
    groups.py          # groups, friends, current user, balances
    settlements.py     # settle up (payment expense)
mcp-server/
  server.py            # FastMCP app + tools  ->  python mcp-server/server.py
```

## Setup

1. `pip install -r requirements.txt`
2. Put your Splitwise personal API key in `.env` (`SPLITWISE_API_KEY=...`).
   Get one at https://secure.splitwise.com/apps.

## Run (two terminals, from the repo root)

```powershell
# 1) backend
python -m backend.main

# 2) MCP server
python mcp-server/server.py
```

Backend docs: http://127.0.0.1:8001/docs  ·  MCP endpoint: http://127.0.0.1:8080/mcp

## MCP tools

Read: `get_current_user`, `list_groups`, `list_friends`, `get_balances`,
`list_expenses`, `get_expense`.
Write: `create_expense`, `update_expense`, `delete_expense`, `settle_up`.

> Write tools change real data — there is no Splitwise sandbox.
