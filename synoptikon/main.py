"""FastAPI-applicatie: templates, authenticatie en routers."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup, escape
from starlette.middleware.base import BaseHTTPMiddleware

from . import __version__, md
from .auth import is_ingelogd
from .config import settings
from .db import init_db
from .models import RECHTSFAMILIES, RELATIE_TYPES
from .routes import auth as auth_routes
from .routes import artikelen, begrippen, bronnen, invoer, stelsels, vragen, wetteksten, zoeken
from .services.artikelen import ref_uit_bron, wetnaam
from .services.helpers import per_familie

HIER = Path(__file__).parent

# Vlaggen staan als SVG in static/vlaggen/<code>.svg; een stelsel zonder vlag krijgt alleen zijn code.
VLAGGEN = {p.stem.upper() for p in (HIER / "static" / "vlaggen").glob("*.svg")}


def vlag(code: str | None) -> Markup:
    if not code or code.upper() not in VLAGGEN:
        return Markup("")
    return Markup('<img class="vlag vlag-{0}" src="/static/vlaggen/{0}.svg" alt="" aria-hidden="true">').format(code.lower())


def stelsel_code(code: str | None) -> Markup:
    """Vlag plus code, zoals in lijsten en badges."""
    return vlag(code) + Markup('<span class="stelsel-code">{}</span>').format(escape(code or ""))


templates = Jinja2Templates(directory=str(HIER / "templates"))
templates.env.filters["md"] = md.render
templates.env.filters["md_inline"] = md.render_inline
templates.env.globals["RELATIE_TYPES"] = RELATIE_TYPES
templates.env.globals["versie"] = __version__
templates.env.globals["ui_lang"] = settings.ui_lang
templates.env.globals["auth_mode"] = settings.auth_mode
templates.env.globals["artikel_ref"] = ref_uit_bron
templates.env.globals["vlag"] = vlag
templates.env.globals["sc"] = stelsel_code
templates.env.globals["wetnaam"] = wetnaam
templates.env.globals["RECHTSFAMILIES"] = RECHTSFAMILIES
templates.env.globals["per_familie"] = per_familie


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Synoptikon", version=__version__, lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=str(HIER / "static")), name="static")

# Pictogrammen ook zonder login: startpagina's, dashboards en telefoons halen
# ze op vaste paden op, zonder sessiecookie.
_OPEN_PADEN = ("/login", "/static/", "/gezond", "/favicon.ico", "/apple-touch-icon")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        pad = request.url.path
        if pad.startswith(_OPEN_PADEN) or is_ingelogd(request):
            response = await call_next(request)
        else:
            volgende = pad + (f"?{request.url.query}" if request.url.query else "")
            response = RedirectResponse(f"/login?volgende={volgende}", status_code=303)
        # Bescheiden beveiligingskoppen; nginx mag ze overschrijven.
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "same-origin")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; font-src 'self'",
        )
        return response


app.add_middleware(AuthMiddleware)


@app.get("/gezond")
def gezond():
    return {"status": "ok", "versie": __version__}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(HIER / "static" / "favicon.ico")


@app.get("/apple-touch-icon.png", include_in_schema=False)
@app.get("/apple-touch-icon-precomposed.png", include_in_schema=False)
def apple_touch_icon():
    return FileResponse(HIER / "static" / "apple-touch-icon.png")


for router in (auth_routes.router, vragen.router, bronnen.router, begrippen.router, stelsels.router, artikelen.router, zoeken.router, invoer.router, wetteksten.router):
    app.include_router(router)
