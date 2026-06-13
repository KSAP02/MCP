"""Settle-up service: record a payment between two users.

In Splitwise a settlement is just an expense with `payment=true` where the
payer's paid_share equals the amount and the payee's owed_share equals it.
"""
from __future__ import annotations

from typing import Optional

from ..client import SplitwiseClient
from ..config import DEFAULT_CURRENCY
from . import expenses


def settle_up(client: SplitwiseClient, from_user_id: int, to_user_id: int, amount: float,
              group_id: int = 0, currency_code: Optional[str] = None,
              description: str = "Payment") -> dict:
    users = [
        {"user_id": from_user_id, "paid_share": amount, "owed_share": 0},
        {"user_id": to_user_id, "paid_share": 0, "owed_share": amount},
    ]
    return expenses.create_expense(
        client,
        description=description,
        cost=amount,
        group_id=group_id,
        currency_code=currency_code or DEFAULT_CURRENCY,
        users=users,
        payment=True,
    )
