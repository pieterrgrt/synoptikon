from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .. import auth, sso
from ..config import settings
from ..db import get_session
from ..i18n import _
from ..models import now
from . import render

router = APIRouter()


def _doel(volgende: str) -> str:
    return volgende if volgende.startswith("/") and not volgende.startswith("//") else "/"


@router.get("/login")
def login_form(request: Request, volgende: str = "/"):
    if auth.is_ingelogd(request):
        return RedirectResponse(_doel(volgende), status_code=303)
    p = auth.profiel_uit_sso(request)
    if p is not None:  # al ingelogd in een andere app op het domein
        resp = RedirectResponse(_doel(volgende), status_code=303)
        resp.set_cookie(auth.COOKIE, auth.maak_sessie_token(p), max_age=settings.session_days * 86400, httponly=True,
                        secure=settings.cookie_secure, samesite="lax", path="/")
        return resp
    return render(request, "login.html", volgende=volgende, fout=None, gebruikersnaam="")


@router.post("/login")
async def login(request: Request, gebruikersnaam: str = Form(...), wachtwoord: str = Form(...), volgende: str = Form("/"),
                db: Session = Depends(get_session)):
    wacht = auth.vertrager.wachttijd(gebruikersnaam)
    if wacht > 0:
        await asyncio.sleep(min(wacht, 5))
        wacht = auth.vertrager.wachttijd(gebruikersnaam)
        if wacht > 0:
            return render(request, "login.html", status_code=429, volgende=volgende, gebruikersnaam=gebruikersnaam,
                          fout=_("Te veel pogingen; wacht {s} s.", s=int(wacht)))
    p = auth.controleer(db, gebruikersnaam, wachtwoord)
    auth.vertrager.registreer(p is not None, gebruikersnaam)
    if p is None:
        return render(request, "login.html", status_code=401, volgende=volgende, gebruikersnaam=gebruikersnaam,
                      fout=_("Onbekende gebruikersnaam of onjuist wachtwoord."))
    p.laatst_ingelogd = now()
    resp = RedirectResponse(_doel(volgende), status_code=303)
    resp.set_cookie(
        auth.COOKIE,
        auth.maak_sessie_token(p),
        max_age=settings.session_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    resp.set_cookie("taal", p.taal, max_age=365 * 86400, secure=settings.cookie_secure, samesite="lax", path="/")
    sso.zet(resp, p.gebruikersnaam, settings.sso_geheim, settings.sso_domein, settings.cookie_secure)
    return resp


@router.post("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(auth.COOKIE, path="/")
    sso.wis(resp, settings.sso_domein)
    return resp
