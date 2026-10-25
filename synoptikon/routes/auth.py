from __future__ import annotations

import asyncio

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

from .. import auth
from ..config import settings
from . import render

router = APIRouter()


@router.get("/login")
def login_form(request: Request, volgende: str = "/"):
    if auth.is_ingelogd(request):
        return RedirectResponse(volgende if volgende.startswith("/") else "/", status_code=303)
    return render(request, "login.html", volgende=volgende, fout=None, geen_hash=not settings.password_hash)


@router.post("/login")
async def login(request: Request, wachtwoord: str = Form(...), volgende: str = Form("/")):
    wacht = auth.vertrager.wachttijd()
    if wacht > 0:
        await asyncio.sleep(min(wacht, 5))
        if auth.vertrager.wachttijd() > 0:
            return render(request, "login.html", status_code=429, volgende=volgende, fout=f"Te veel pogingen; wacht {int(wacht)} s.", geen_hash=False)
    gelukt = auth.verify_password(wachtwoord, settings.password_hash)
    auth.vertrager.registreer(gelukt)
    if not gelukt:
        return render(request, "login.html", status_code=401, volgende=volgende, fout="Onjuist wachtwoord.", geen_hash=not settings.password_hash)
    doel = volgende if volgende.startswith("/") and not volgende.startswith("//") else "/"
    resp = RedirectResponse(doel, status_code=303)
    resp.set_cookie(
        auth.COOKIE,
        auth.maak_sessie_token(),
        max_age=settings.session_days * 86400,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )
    return resp


@router.post("/logout")
def logout():
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(auth.COOKIE, path="/")
    return resp
