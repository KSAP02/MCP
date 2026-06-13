"""Groups, friends, current user, and balance summaries."""
from __future__ import annotations

from typing import Optional

from ..client import SplitwiseClient


def get_current_user(client: SplitwiseClient) -> Optional[dict]:
    return client.get("get_current_user").get("user")


def list_groups(client: SplitwiseClient) -> list[dict]:
    return client.get("get_groups").get("groups", [])


def get_group(client: SplitwiseClient, group_id: int) -> Optional[dict]:
    return client.get(f"get_group/{group_id}").get("group")


def list_friends(client: SplitwiseClient) -> list[dict]:
    return client.get("get_friends").get("friends", [])


def get_balances(client: SplitwiseClient) -> list[dict]:
    """Summarize outstanding balances with each friend.

    Positive amount => the friend owes you; negative => you owe the friend.
    """
    summary: list[dict] = []
    for friend in list_friends(client):
        for bal in friend.get("balance", []):
            name = f"{friend.get('first_name', '')} {friend.get('last_name') or ''}".strip()
            summary.append({
                "friend_id": friend.get("id"),
                "name": name,
                "amount": float(bal.get("amount", 0)),
                "currency_code": bal.get("currency_code"),
            })
    return summary
