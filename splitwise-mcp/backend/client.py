"""Low-level HTTP client for the Splitwise REST API (v3.0).

This is the only module that talks HTTP to Splitwise. Everything above it
(the service layer) deals in clean Python dicts and never sees a URL.
"""
from __future__ import annotations

from typing import Any, Optional

import httpx

from .config import REQUEST_TIMEOUT, SPLITWISE_API_KEY, SPLITWISE_BASE_URL


class SplitwiseError(Exception):
    """Raised when the Splitwise API (or the network) returns an error."""

    def __init__(self, message: str, status_code: int = 502, payload: Any = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload


class SplitwiseClient:
    """Thin wrapper over Splitwise's REST API using a personal API key."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None,
                 timeout: Optional[float] = None):
        self.api_key = api_key if api_key is not None else SPLITWISE_API_KEY
        self.base_url = (base_url or SPLITWISE_BASE_URL).rstrip("/")
        self.timeout = timeout or REQUEST_TIMEOUT

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    def _request(self, method: str, path: str, params: Optional[dict] = None,
                 data: Optional[dict] = None) -> Any:
        if not self.api_key:
            raise SplitwiseError(
                "SPLITWISE_API_KEY is not set. Add it to your .env file.", status_code=500
            )
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            resp = httpx.request(
                method, url, headers=self._headers(), params=params, data=data, timeout=self.timeout
            )
        except httpx.HTTPError as exc:
            raise SplitwiseError(f"Network error calling Splitwise: {exc}") from exc

        if resp.status_code == 401:
            raise SplitwiseError("Unauthorized — check your Splitwise API key.", status_code=401)
        if resp.status_code == 403:
            raise SplitwiseError("Forbidden — your key lacks access to this resource.", status_code=403)
        if resp.status_code == 404:
            raise SplitwiseError(f"Not found: {path}", status_code=404)
        if resp.status_code == 429:
            raise SplitwiseError("Rate limited by Splitwise — try again shortly.", status_code=429)
        if resp.status_code >= 400:
            raise SplitwiseError(
                f"Splitwise API error ({resp.status_code}): {resp.text}", status_code=resp.status_code
            )

        try:
            payload = resp.json()
        except ValueError as exc:
            raise SplitwiseError("Invalid JSON returned by Splitwise.", payload=resp.text) from exc

        # Splitwise often returns HTTP 200 with an `errors` object on write failures.
        self._raise_for_payload_errors(payload)
        return payload

    @staticmethod
    def _raise_for_payload_errors(payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        errors = payload.get("errors")
        if not errors:
            return
        if isinstance(errors, dict) and any(errors.values()):
            raise SplitwiseError(_flatten_errors(errors), status_code=400, payload=errors)
        if isinstance(errors, list) and errors:
            raise SplitwiseError("; ".join(map(str, errors)), status_code=400, payload=errors)

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        return self._request("GET", path, params=_clean(params))

    def post(self, path: str, data: Optional[dict] = None) -> Any:
        return self._request("POST", path, data=_clean(data))


def _clean(d: Optional[dict]) -> Optional[dict]:
    """Drop keys whose value is None so we don't send empty params/fields."""
    if not d:
        return None
    return {k: v for k, v in d.items() if v is not None}


def _flatten_errors(errors: dict) -> str:
    parts: list[str] = []
    for _key, msgs in errors.items():
        if isinstance(msgs, list):
            parts.extend(str(m) for m in msgs)
        else:
            parts.append(str(msgs))
    return "; ".join(parts) or "Unknown Splitwise error"
