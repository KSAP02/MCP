"""FastAPI backend exposing Splitwise operations over HTTP (port 8001).

Run with:  python -m backend.main      (from the repo root)
       or:  uvicorn backend.main:app --port 8001 --reload
"""
from __future__ import annotations

from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from . import config
from .client import SplitwiseClient, SplitwiseError
from .models import CreateExpenseRequest, SettleUpRequest, UpdateExpenseRequest
from .service import expenses, groups, settlements

app = FastAPI(title="Splitwise Backend", version="0.1.0")

# One shared client; the API key is read from .env at import time.
client = SplitwiseClient()


@app.exception_handler(SplitwiseError)
async def _splitwise_error_handler(_request, exc: SplitwiseError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "details": exc.payload},
    )


# --- read endpoints ---

@app.get("/health")
def health():
    return {"status": "ok", "service": "splitwise-backend"}


@app.get("/me")
def me():
    return groups.get_current_user(client)


@app.get("/groups")
def get_groups():
    return groups.list_groups(client)


@app.get("/groups/{group_id}")
def get_group(group_id: int):
    return groups.get_group(client, group_id)


@app.get("/friends")
def get_friends():
    return groups.list_friends(client)


@app.get("/balances")
def get_balances():
    return groups.get_balances(client)


@app.get("/expenses")
def get_expenses(group_id: Optional[int] = None, friend_id: Optional[int] = None,
                 dated_after: Optional[str] = None, dated_before: Optional[str] = None,
                 limit: int = 20, offset: int = 0):
    return expenses.list_expenses(
        client, group_id, friend_id, dated_after, dated_before, limit, offset
    )


@app.get("/expenses/{expense_id}")
def get_expense(expense_id: int):
    return expenses.get_expense(client, expense_id)


# --- write endpoints ---

@app.post("/expenses")
def create_expense(req: CreateExpenseRequest):
    users = [u.model_dump() for u in req.users] if req.users else None
    return expenses.create_expense(
        client,
        description=req.description,
        cost=req.cost,
        group_id=req.group_id,
        currency_code=req.currency_code,
        category_id=req.category_id,
        split_equally=req.split_equally,
        users=users,
        details=req.details,
        date=req.date,
    )


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, req: UpdateExpenseRequest):
    fields = req.model_dump(exclude_none=True)
    return expenses.update_expense(client, expense_id, **fields)


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):
    return expenses.delete_expense(client, expense_id)


@app.post("/settle")
def settle(req: SettleUpRequest):
    return settlements.settle_up(
        client,
        from_user_id=req.from_user_id,
        to_user_id=req.to_user_id,
        amount=req.amount,
        group_id=req.group_id,
        currency_code=req.currency_code,
        description=req.description,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host=config.BACKEND_HOST, port=config.BACKEND_PORT, reload=True)
