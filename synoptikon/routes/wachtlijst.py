"""Wachtlijst voor de opening: een e-mailadres achterlaten of weer weghalen. Zonder inloggen bereikbaar
(main._OPEN_PADEN); een anonieme bezoeker van / komt hier terecht."""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from .. import i18n
from ..db import get_session
from ..i18n import _
from ..models import Wachtlijst
from . import render

router = APIRouter()

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _adres(email: str) -> str | None:
    email = email.strip().lower()
    return email if len(email) <= 254 and _EMAIL.match(email) else None


@router.get("/wachtlijst")
def pagina(request: Request, stand: str = ""):
    return render(request, "wachtlijst.html", stand=stand if stand in ("op", "af") else "", fout=None, email="")


@router.post("/wachtlijst")
def aanmelden(request: Request, email: str = Form(""), actie: str = Form("op"), website: str = Form(""),
              db: Session = Depends(get_session)):
    if website:  # verborgen veld: alleen bots vullen het in
        return RedirectResponse("/wachtlijst?stand=op", status_code=303)
    adres = _adres(email)
    if adres is None:
        return render(request, "wachtlijst.html", status_code=400, stand="", fout=_("Ongeldig e-mailadres."),
                      email=email[:254])
    if actie == "af":
        db.execute(delete(Wachtlijst).where(Wachtlijst.email == adres))
        return RedirectResponse("/wachtlijst?stand=af", status_code=303)
    # Al aangemeld geeft hetzelfde antwoord, zodat de pagina niet verraadt wie erop staat.
    if db.scalar(select(Wachtlijst.id).where(Wachtlijst.email == adres)) is None:
        db.add(Wachtlijst(email=adres, taal=i18n.taal()))
    return RedirectResponse("/wachtlijst?stand=op", status_code=303)
