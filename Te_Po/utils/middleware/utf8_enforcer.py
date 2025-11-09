"""Unicode normalisation middleware shared by Tiwhanawhana services."""

from __future__ import annotations

import locale
import os
import unicodedata
from typing import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

_MI_NZ_LOCALE = "mi_NZ.UTF-8"


def _ensure_locale() -> None:
    """Ensure LANG/LC_ALL favour mi_NZ.UTF-8 for Māori macron support."""
    os.environ.setdefault("LANG", _MI_NZ_LOCALE)
    os.environ.setdefault("LC_ALL", _MI_NZ_LOCALE)
    try:
        locale.setlocale(locale.LC_ALL, _MI_NZ_LOCALE)
    except locale.Error:
        # Locale might not be installed on container; continue gracefully.
        pass


class UnicodeEnforcerMiddleware(BaseHTTPMiddleware):
    """Normalize textual request bodies to NFC and enforce UTF-8 encoding."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        content_type = request.headers.get("content-type", "")
        if content_type.startswith("text/") or "application/json" in content_type:
            body = await request.body()
            try:
                text = body.decode("utf-8")
            except UnicodeDecodeError:
                return Response(
                    status_code=400,
                    content="Payload must be UTF-8 encoded.",
                    media_type="text/plain",
                )
            normalised = unicodedata.normalize("NFC", text)
            request._body = normalised.encode("utf-8")  # type: ignore[attr-defined]
        _ensure_locale()
        response = await call_next(request)
        response.headers.setdefault("Content-Language", _MI_NZ_LOCALE)
        return response


def apply_utf8_middleware(app: ASGIApp) -> None:
    """Attach the Unicode enforcer middleware to the provided app."""
    app.add_middleware(UnicodeEnforcerMiddleware)
    _ensure_locale()
