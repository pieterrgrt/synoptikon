"""Routers. `render` is de gedeelde template-helper; hij haalt de
Jinja-omgeving lui op om kringimporten met main.py te vermijden."""
from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse


def render(request: Request, naam: str, status_code: int = 200, **context: Any) -> HTMLResponse:
    from ..main import templates

    context.setdefault("request", request)
    return templates.TemplateResponse(request, naam, context, status_code=status_code)
