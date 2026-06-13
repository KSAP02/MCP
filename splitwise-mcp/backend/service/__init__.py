"""Service layer: importable business logic, grouped by domain.

Import the submodules and call their functions with a SplitwiseClient instance:

    from backend.client import SplitwiseClient
    from backend.service import expenses, groups, settlements

    client = SplitwiseClient()
    groups.get_current_user(client)
"""
from . import expenses, groups, settlements

__all__ = ["expenses", "groups", "settlements"]
