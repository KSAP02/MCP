"""Pydantic request models for the FastAPI backend.

Responses are passed through as Splitwise's raw JSON (dicts/lists) so we don't
have to mirror every field of their schema; these models only validate input.
"""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ExpenseShare(BaseModel):
    """One participant's stake in an expense."""

    user_id: int
    paid_share: Optional[float] = Field(default=None, description="How much this user paid.")
    owed_share: Optional[float] = Field(default=None, description="How much this user owes.")


class CreateExpenseRequest(BaseModel):
    description: str
    cost: float
    group_id: int = Field(default=0, description="0 means a non-group (friend) expense.")
    currency_code: Optional[str] = None
    category_id: Optional[int] = None
    split_equally: bool = Field(
        default=False, description="If true, split evenly among group members; ignore `users`."
    )
    users: Optional[List[ExpenseShare]] = Field(
        default=None, description="Explicit per-user shares. paid_share and owed_share totals must each equal cost."
    )
    details: Optional[str] = None
    date: Optional[str] = Field(default=None, description="ISO 8601 timestamp, e.g. 2026-06-12T00:00:00Z.")


class UpdateExpenseRequest(BaseModel):
    description: Optional[str] = None
    cost: Optional[float] = None
    group_id: Optional[int] = None
    currency_code: Optional[str] = None
    category_id: Optional[int] = None
    users: Optional[List[ExpenseShare]] = None
    details: Optional[str] = None
    date: Optional[str] = None


class SettleUpRequest(BaseModel):
    from_user_id: int = Field(description="The user who is paying.")
    to_user_id: int = Field(description="The user receiving the payment.")
    amount: float
    group_id: int = 0
    currency_code: Optional[str] = None
    description: str = "Payment"
