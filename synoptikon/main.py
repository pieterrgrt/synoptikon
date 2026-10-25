"""FastAPI-applicatie: templates, authenticatie en routers."""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.base import BaseHTTPMiddleware

from . import __version__, md
from .auth import is_ingelogd
from .config import settings
from .db import init_db
from .models import RELATIE_TYPES
from .routes import auth as auth_routes
from .routes import artikelen, begrippen, bronnen, invoer, stelsels, vragen, wetteksten, zoeken
from .services.artikelen import ref_uit_bron

HIER = Path(__file__).parent

templates = Jinja2Templates(directory=str(HIER / "templates"))
templates.env.filters["md"] = md.render
templates.env.filters["md_inline"] = md.render_inline
templates.env.globals["RELATIE_TYPES"] = RELATIE_TYPES
templates.env.globals["versie"] = __version__
templates.env.globals["ui_lang"] = settings.ui_lang
templates.env.globals["auth_mode"] = settings.auth_mode
templates.env.globals["artikel_ref"] = ref_uit_bron


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Synoptikon", version=__version__, lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=str(HIER / "static")), name="static")

_OPEN_PADEN = ("/login", "/static/", "/gezond")


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


for router in (auth_routes.router, vragen.router, bronnen.router, begrippen.router, stelsels.router, artikelen.router, zoeken.router, invoer.router, wetteksten.router):
    app.include_router(router)
