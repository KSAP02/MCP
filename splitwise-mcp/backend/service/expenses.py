"""Expense service: list, fetch, create, update, delete expenses.

The main value here is `create_expense`, which translates a clean
{user_id, paid_share, owed_share} list into Splitwise's awkward flat
`users__0__user_id` form-encoded shape and validates the share totals.
"""
from __future__ import annotations

from typing import Any, Optional

from ..client import SplitwiseClient, SplitwiseError
from ..config import DEFAULT_CURRENCY


def list_expenses(client: SplitwiseClient, group_id: Optional[int] = None,
                  friend_id: Optional[int] = None, dated_after: Optional[str] = None,
                  dated_before: Optional[str] = None, limit: int = 20, offset: int = 0) -> list[dict]:
    params = {
        "group_id": group_id,
        "friend_id": friend_id,
        "dated_after": dated_after,
        "dated_before": dated_before,
        "limit": limit,
        "offset": offset,
    }
    return client.get("get_expenses", params).get("expenses", [])


def get_expense(client: SplitwiseClient, expense_id: int) -> Optional[dict]:
    return client.get(f"get_expense/{expense_id}").get("expense")


def create_expense(client: SplitwiseClient, description: str, cost: float, group_id: int = 0,
                   currency_code: Optional[str] = None, category_id: Optional[int] = None,
                   split_equally: bool = False, users: Optional[list[dict]] = None,
                   details: Optional[str] = None, date: Optional[str] = None,
                   payment: bool = False) -> dict:
    if not split_equally and not users:
        raise SplitwiseError(
            "Provide either split_equally=True or an explicit `users` list.", status_code=400
        )

    data: dict[str, Any] = {
        "description": description,
        "cost": _money(cost),
        "group_id": group_id if group_id is not None else 0,
        "currency_code": currency_code or DEFAULT_CURRENCY,
        "category_id": category_id,
        "details": details,
        "date": date,
        "payment": payment,
    }

    if split_equally:
        data["split_equally"] = True
    else:
        _validate_shares(cost, users or [])
        data.update(_flatten_users(users or []))

    result = client.post("create_expense", data)
    created = result.get("expenses", [])
    return created[0] if created else result


def update_expense(client: SplitwiseClient, expense_id: int, **fields: Any) -> dict:
    data: dict[str, Any] = {}
    for key in ("description", "cost", "group_id", "currency_code", "category_id", "details", "date"):
        value = fields.get(key)
        if value is not None:
            data[key] = _money(value) if key == "cost" else value

    users = fields.get("users")
    if users:
        data.update(_flatten_users(users))

    result = client.post(f"update_expense/{expense_id}", data)
    updated = result.get("expenses", [])
    return updated[0] if updated else result


def delete_expense(client: SplitwiseClient, expense_id: int) -> dict:
    result = client.post(f"delete_expense/{expense_id}")
    return {"success": result.get("success", True), "expense_id": expense_id}


# --- helpers ---

def _flatten_users(users: list[dict]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for i, u in enumerate(users):
        data[f"users__{i}__user_id"] = u["user_id"]
        if u.get("paid_share") is not None:
            data[f"users__{i}__paid_share"] = _money(u["paid_share"])
        if u.get("owed_share") is not None:
            data[f"users__{i}__owed_share"] = _money(u["owed_share"])
    return data


def _validate_shares(cost: float, users: list[dict]) -> None:
    total_cost = float(cost)
    owed = sum(float(u.get("owed_share") or 0) for u in users)
    paid = sum(float(u.get("paid_share") or 0) for u in users)
    if abs(owed - total_cost) > 0.01:
        raise SplitwiseError(
            f"owed_share total ({owed:.2f}) must equal cost ({total_cost:.2f}).", status_code=400
        )
    if abs(paid - total_cost) > 0.01:
        raise SplitwiseError(
            f"paid_share total ({paid:.2f}) must equal cost ({total_cost:.2f}).", status_code=400
        )


def _money(value: Any) -> str:
    return f"{float(value):.2f}"
