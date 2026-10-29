"""FastAPI-applicatie: templates, authenticatie en routers."""
from __future__ import annotations

import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from markupsafe import Markup, escape
from starlette.middleware.base import BaseHTTPMiddleware

from . import __version__, i18n, md
from .auth import COOKIE, huidig_profiel, is_ingelogd, maak_sessie_token, profiel_uit_sso
from .config import settings
from .db import init_db
from .models import RECHTSFAMILIES, RELATIE_TYPES
from .routes import auth as auth_routes
from .routes import artikelen, begrippen, bronnen, eu, gedeeld, invoer, leren, opzoeken, profielen, stelsels, vertalingen, vragen, wetteksten, wunderkammer
from .services import wetboek
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
templates.env.globals["wetref"] = wetboek.ref
templates.env.globals["wet_titel"] = wetboek.toon_titel
templates.env.globals["wet_afk"] = wetboek.toon_afkorting
templates.env.globals["RECHTSFAMILIES"] = RECHTSFAMILIES
templates.env.globals["per_familie"] = per_familie
# Versie van css/js voor de cache: nginx bewaart /static/ zeven dagen als immutable.
templates.env.globals["sv"] = str(max(int(f.stat().st_mtime) for d in ("css", "js") for f in (HIER / "static" / d).iterdir()))
templates.env.globals["_"] = i18n._
templates.env.globals["n_"] = i18n.n_
templates.env.globals["vt"] = i18n.vt
templates.env.globals["TALEN"] = i18n.TALEN
templates.env.globals["huidige_taal"] = i18n.taal
templates.env.globals["toont_origineel"] = i18n.toont_origineel


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    global _gewarmd
    if not _gewarmd:
        _gewarmd = True
        threading.Thread(target=_warm, daemon=True).start()
    yield


_gewarmd = False


def _warm() -> None:
    """Plaatsing van de artikelen in de systematiek alvast berekenen (enkele seconden per groot stelsel); één keer per proces."""
    from .db import session_factory
    from .models import Stelsel

    try:
        from .services.artikelen import laad_wetnamen
        with session_factory()() as db:
            laad_wetnamen(db)
            for s in db.query(Stelsel).all():
                wetboek.plaatsing(db, s.code)
    except Exception:  # alleen een versnelling; de pagina's rekenen het anders zelf uit
        pass


app = FastAPI(title="Synoptikon", version=__version__, lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/static", StaticFiles(directory=str(HIER / "static")), name="static")

# Pictogrammen ook zonder login: startpagina's, dashboards en telefoons halen
# ze op vaste paden op, zonder sessiecookie.
# /api/wk/ heeft een eigen token (routes/wunderkammer.py) in plaats van de sessiecookie.
_OPEN_PADEN = ("/login", "/aanmelden", "/static/", "/gezond", "/favicon.ico", "/apple-touch-icon", "/api/wk/", "/taal")
# Wat een lezer mag posten: zijn eigen profiel, taal, leerlijsten (ook delen, liken, reageren, overnemen) en uitloggen.
_LEZER_POST = ("/logout", "/profiel/", "/taal", "/leren", "/gedeeld/")


def _taal_van(request: Request) -> str:
    """Profiel → cookie → Accept-Language."""
    p = getattr(request.state, "profiel", None)
    if p is not None and p.taal in i18n.TALEN:
        return p.taal
    cookie = request.cookies.get("taal")
    if cookie in i18n.TALEN:
        return cookie
    return i18n.kies_taal(request.headers.get("accept-language"))


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        pad = request.url.path
        open_pad = pad.startswith(_OPEN_PADEN)
        ingelogd = not open_pad and is_ingelogd(request)
        via_sso = None
        if not open_pad and not ingelogd:
            via_sso = profiel_uit_sso(request)  # elders op het domein ingelogd (Wunderkammer)
            ingelogd = via_sso is not None
        if open_pad and not pad.startswith(("/static/", "/api/wk/")):
            huidig_profiel(request)  # voor de taal op /login en /taal
        i18n.zet_taal(_taal_van(request), origineel=request.cookies.get("inhoud") == "origineel")
        profiel = getattr(request.state, "profiel", None)
        if ingelogd and request.method not in ("GET", "HEAD") and not pad.startswith(_LEZER_POST) \
                and profiel is not None and not profiel.mag_bewerken:
            response = PlainTextResponse(i18n._("Dit profiel mag alleen lezen."), status_code=403)
        elif open_pad or ingelogd:
            response = await call_next(request)
        else:
            volgende = pad + (f"?{request.url.query}" if request.url.query else "")
            response = RedirectResponse(f"/login?volgende={volgende}", status_code=303)
        if via_sso is not None:
            response.set_cookie(COOKIE, maak_sessie_token(via_sso), max_age=settings.session_days * 86400, httponly=True,
                                secure=settings.cookie_secure, samesite="lax", path="/")
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


for router in (auth_routes.router, profielen.router, vragen.router, bronnen.router, begrippen.router, stelsels.router, artikelen.router, opzoeken.router, invoer.router, wetteksten.router, eu.router, vertalingen.router, gedeeld.router, leren.router, wunderkammer.router):
    app.include_router(router)
