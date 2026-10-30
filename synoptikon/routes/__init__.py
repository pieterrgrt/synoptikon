"""Routers. `render` is de gedeelde template-helper; hij haalt de
Jinja-omgeving lui op om kringimporten met main.py te vermijden."""
from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse

from ..config import settings


def render(request: Request, naam: str, status_code: int = 200, **context: Any) -> HTMLResponse:
    from ..main import templates

    context.setdefault("request", request)
    profiel = getattr(request.state, "profiel", None)
    context.setdefault("profiel", profiel)
    context.setdefault("mag_bewerken", profiel is None or profiel.mag_bewerken)
    # Koppeling met Wunderkammer aan voor dit profiel: dan pas verwijzen de pagina's ernaar.
    context.setdefault("wk", settings.wk_ingesteld and (profiel is None or profiel.wunderkammer))
    context.setdefault("aanmelden", bool(settings.aanmeldcode))
    # Mijn stelsels (services/stelselkeuze.py): de macro's in _stelsels.html zetten de rest onder 'meer stelsels…'.
    context.setdefault("mijn", profiel.stelsel_codes if profiel is not None else None)
    context.setdefault("wk_url", settings.wk_url)
    from ..services.vakken import VAKKEN

    context.setdefault("vakken_keuze", VAKKEN)  # voor het vak wisselen onder 'bewaard' (routes/opzoeken.py)
    return templates.TemplateResponse(request, naam, context, status_code=status_code)
