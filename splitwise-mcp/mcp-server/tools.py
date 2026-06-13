"""Tool implementations for the Splitwise MCP server.

Each function here is a plain Python function that calls the FastAPI backend
(config.BACKEND_URL) over HTTP. They carry the type hints and docstrings that
FastMCP turns into the tool schema; server.py just registers them.

These functions know nothing about MCP, so they're easy to test directly.
"""
from __future__ import annotations

from typing import Any, Optional

import httpx

import config


def _backend(method: str, path: str, *, params: Optional[dict] = None,
             json: Optional[dict] = None) -> Any:
    """Call the backend and return parsed JSON, or a structured error dict."""
    url = f"{config.BACKEND_URL}{path}"
    try:
        resp = httpx.request(method, url, params=params, json=json, timeout=config.REQUEST_TIMEOUT)
    except httpx.HTTPError as exc:
        return {"error": f"Could not reach backend at {config.BACKEND_URL}: {exc}"}

    try:
        data = resp.json()
    except ValueError:
        return {"error": f"Backend returned non-JSON ({resp.status_code})", "body": resp.text}

    if resp.status_code >= 400:
        return {
            "error": data.get("error", "Backend error") if isinstance(data, dict) else "Backend error",
            "status": resp.status_code,
            "details": data.get("details") if isinstance(data, dict) else None,
        }
    return data


# ---------------------------------------------------------------------------
# Read tools
# ---------------------------------------------------------------------------

def get_current_user() -> Any:
    """Get the authenticated Splitwise user's profile (id, name, email, default currency).

    Useful as a connectivity check and to learn your own user_id.
    """
    return _backend("GET", "/me")


def list_groups() -> Any:
    """List all Splitwise groups you belong to, including members and group balances.

    Use this to resolve a group name to its group_id before creating an expense.
    """
    return _backend("GET", "/groups")


def list_friends() -> Any:
    """List your Splitwise friends with their user_id and your balance with each.

    Use this to resolve a person's name to their user_id before creating an
    expense or settling up.
    """
    return _backend("GET", "/friends")


def get_balances() -> Any:
    """Summarize who owes you and who you owe across all friends.

    Positive amount means the friend owes you; negative means you owe them.
    """
    return _backend("GET", "/balances")


def list_expenses(group_id: Optional[int] = None, friend_id: Optional[int] = None,
                  dated_after: Optional[str] = None, dated_before: Optional[str] = None,
                  limit: int = 20) -> Any:
    """List recent expenses, newest first.

    Optionally filter by group_id, friend_id, or a date range. Dates are ISO
    8601 timestamps, e.g. "2026-01-01T00:00:00Z".
    """
    params = {
        "group_id": group_id,
        "friend_id": friend_id,
        "dated_after": dated_after,
        "dated_before": dated_before,
        "limit": limit,
    }
    return _backend("GET", "/expenses", params={k: v for k, v in params.items() if v is not None})


def get_expense(expense_id: int) -> Any:
    """Get the full details of a single expense by its id, including each user's shares."""
    return _backend("GET", f"/expenses/{expense_id}")


# ---------------------------------------------------------------------------
# Write tools  (these change real data in your Splitwise account)
# ---------------------------------------------------------------------------

def create_expense(description: str, cost: float, group_id: int = 0,
                   split_equally: bool = False, users: Optional[list[dict]] = None,
                   currency_code: Optional[str] = None, category_id: Optional[int] = None,
                   details: Optional[str] = None, date: Optional[str] = None) -> Any:
    """Create a new expense in Splitwise.

    Provide EITHER:
      - split_equally=True, with a group_id, to split `cost` evenly among members; or
      - an explicit `users` list, e.g.
        [{"user_id": 123, "paid_share": 30.0, "owed_share": 10.0},
         {"user_id": 456, "paid_share": 0,    "owed_share": 10.0},
         {"user_id": 789, "paid_share": 0,    "owed_share": 10.0}]
        The paid_share totals and owed_share totals must EACH equal `cost`.

    Resolve names to user_ids with list_friends / list_groups first.
    group_id=0 means a non-group expense between friends.
    """
    body = {
        "description": description,
        "cost": cost,
        "group_id": group_id,
        "split_equally": split_equally,
        "users": users,
        "currency_code": currency_code,
        "category_id": category_id,
        "details": details,
        "date": date,
    }
    return _backend("POST", "/expenses", json=body)


def update_expense(expense_id: int, description: Optional[str] = None, cost: Optional[float] = None,
                   group_id: Optional[int] = None, users: Optional[list[dict]] = None,
                   currency_code: Optional[str] = None, category_id: Optional[int] = None,
                   details: Optional[str] = None, date: Optional[str] = None) -> Any:
    """Update an existing expense. Only the fields you pass are changed.

    If you change the amount or who's involved, pass a full `users` list whose
    paid_share and owed_share totals each equal the new cost.
    """
    body = {
        "description": description,
        "cost": cost,
        "group_id": group_id,
        "users": users,
        "currency_code": currency_code,
        "category_id": category_id,
        "details": details,
        "date": date,
    }
    body = {k: v for k, v in body.items() if v is not None}
    return _backend("PUT", f"/expenses/{expense_id}", json=body)


def delete_expense(expense_id: int) -> Any:
    """Delete an expense by id. Splitwise marks it deleted; this affects real balances."""
    return _backend("DELETE", f"/expenses/{expense_id}")


def settle_up(from_user_id: int, to_user_id: int, amount: float, group_id: int = 0,
              description: str = "Payment", currency_code: Optional[str] = None) -> Any:
    """Record a payment: from_user_id pays to_user_id `amount`, reducing what they owe.

    Use list_friends to resolve user_ids. group_id=0 settles a non-group balance.
    """
    body = {
        "from_user_id": from_user_id,
        "to_user_id": to_user_id,
        "amount": amount,
        "group_id": group_id,
        "description": description,
        "currency_code": currency_code,
    }
    return _backend("POST", "/settle", json=body)


# All tool functions, in the order they should be registered with MCP.
ALL_TOOLS = [
    get_current_user,
    list_groups,
    list_friends,
    get_balances,
    list_expenses,
    get_expense,
    create_expense,
    update_expense,
    delete_expense,
    settle_up,
]
