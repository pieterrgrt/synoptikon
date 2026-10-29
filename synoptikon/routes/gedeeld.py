"""Gedeelde leerlijsten (services/delen.py) en aanmelden met een uitnodigingscode.

- /gedeeld: lijsten die hun eigenaar voor alle studenten zichtbaar maakte, populairste of nieuwste eerst.
- /gedeeld/<deelcode>: één lijst met haar kaarten, likes en reacties; overnemen naar je eigen leerlijsten.
- /aanmelden: een account (rol lezer) voor wie `SYNOPTIKON_AANMELDCODE` heeft. Zo'n account krijgt geen
  domeincookie (Profiel.zelf_aangemeld): de gebruikersnaam is vrij gekozen en mag geen Wunderkammer-account openen.
"""
from __future__ import annotations

import hmac

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import auth
from ..config import settings
from ..db import get_session
from ..i18n import TALEN, _, taal as huidige_taal
from ..models import ZICHTBAAR, Leerlijst, LijstLike, LijstReactie, Profiel, now
from ..services import delen, leren
from . import render
from .profielen import MIN_LENGTE, _cookie, gebruikersnaam_fout

router = APIRouter()


def _ik(request: Request) -> Profiel:
    p = auth.huidig_profiel(request)
    if p is None:
        raise HTTPException(401)
    return p


def _gedeelde(request: Request, db: Session, code: str) -> tuple[Leerlijst, Profiel]:
    ik = _ik(request)
    lijst = db.scalar(select(Leerlijst).where(Leerlijst.deelcode == code))
    if lijst is None or not delen.mag_zien(lijst, ik.id):
        raise HTTPException(404)
    return lijst, ik


# --- delen ----------------------------------------------------------------------------------------------------------


@router.get("/gedeeld")
def overzicht(request: Request, volgorde: str = "populair", db: Session = Depends(get_session)):
    ik = _ik(request)
    mijn = db.scalars(select(Leerlijst).where(Leerlijst.profiel_id == ik.id, Leerlijst.zichtbaar != "prive")
                      .order_by(Leerlijst.naam)).all()
    return render(request, "gedeeld.html", lijsten=delen.openbaar(db, volgorde), mijn=mijn, volgorde=volgorde,
                  ZICHTBAAR=ZICHTBAAR)


@router.get("/gedeeld/{code}")
def lijst(request: Request, code: str, db: Session = Depends(get_session)):
    lijst, ik = _gedeelde(request, db, code)
    bouwer = leren.Bouwer(db)
    kaarten = [(k, bouwer.zijden(k)) for k in delen.kaarten(lijst)]
    geliket = db.get(LijstLike, (lijst.id, ik.id)) is not None
    al = db.scalar(select(Leerlijst.id).where(Leerlijst.profiel_id == ik.id, Leerlijst.overgenomen_van == lijst.id))
    return render(request, "gedeelde_lijst.html", lijst=lijst, kaarten=kaarten, geliket=geliket, ik=ik, al_overgenomen=al,
                  eigen=lijst.profiel_id == ik.id, mag_wissen=lambda r: delen.mag_reactie_wissen(r, lijst, ik))


@router.post("/gedeeld/{code}/like")
def like(request: Request, code: str, db: Session = Depends(get_session)):
    lijst, ik = _gedeelde(request, db, code)
    delen.like(db, lijst, ik.id)
    return RedirectResponse(f"/gedeeld/{code}", status_code=303)


@router.post("/gedeeld/{code}/reactie")
def reactie(request: Request, code: str, tekst: str = Form(...), db: Session = Depends(get_session)):
    lijst, ik = _gedeelde(request, db, code)
    r = delen.reageer(db, lijst, ik.id, tekst)
    db.flush()
    return RedirectResponse(f"/gedeeld/{code}" + (f"#r{r.id}" if r else "#reacties"), status_code=303)


@router.post("/gedeeld/{code}/reactie/{rid}/verwijder")
def reactie_verwijder(request: Request, code: str, rid: int, db: Session = Depends(get_session)):
    lijst, ik = _gedeelde(request, db, code)
    r = db.get(LijstReactie, rid)
    if r is None or r.lijst_id != lijst.id or not delen.mag_reactie_wissen(r, lijst, ik):
        raise HTTPException(404)
    db.delete(r)
    return RedirectResponse(f"/gedeeld/{code}#reacties", status_code=303)


@router.post("/gedeeld/{code}/overnemen")
def overnemen(request: Request, code: str, db: Session = Depends(get_session)):
    lijst, ik = _gedeelde(request, db, code)
    kopie = delen.overnemen(db, lijst, ik.id)
    return RedirectResponse(f"/leren/{kopie.id}?overgenomen_lijst=1", status_code=303)


@router.post("/leren/{lid}/delen")
def delen_instellen(request: Request, lid: int, zichtbaar: str = Form(...), db: Session = Depends(get_session)):
    ik = _ik(request)
    lijst = db.get(Leerlijst, lid)
    if lijst is None or lijst.profiel_id != ik.id:
        raise HTTPException(404)
    if zichtbaar not in ZICHTBAAR:
        raise HTTPException(400)
    delen.zet_zichtbaar(lijst, zichtbaar)
    return RedirectResponse(f"/leren/{lid}#delen", status_code=303)


# --- aanmelden ------------------------------------------------------------------------------------------------------


def _aanmelden_aan() -> bool:
    return bool(settings.aanmeldcode)


@router.get("/aanmelden")
def aanmelden_form(request: Request):
    if not _aanmelden_aan():
        raise HTTPException(404)
    return render(request, "aanmelden.html", fout=None, velden={}, min_lengte=MIN_LENGTE)


@router.post("/aanmelden")
def aanmelden(request: Request, code: str = Form(...), gebruikersnaam: str = Form(...), naam: str = Form(...),
              wachtwoord: str = Form(...), nogmaals: str = Form(...), db: Session = Depends(get_session)):
    if not _aanmelden_aan():
        raise HTTPException(404)
    gebruikersnaam = gebruikersnaam.strip().lower()
    velden = dict(gebruikersnaam=gebruikersnaam, naam=naam)
    fout = None
    if auth.vertrager.wachttijd("aanmelden") > 0:
        fout = _("Te veel pogingen; wacht {s} s.", s=int(auth.vertrager.wachttijd("aanmelden")))
    elif not hmac.compare_digest(code.strip().encode(), (settings.aanmeldcode or "").encode()):
        auth.vertrager.registreer(False, "aanmelden")
        fout = _("Die uitnodigingscode klopt niet.")
    else:
        fout = gebruikersnaam_fout(db, gebruikersnaam)
        if not fout and len(wachtwoord) < MIN_LENGTE:
            fout = _("Een wachtwoord heeft minstens {n} tekens.", n=MIN_LENGTE)
        elif not fout and wachtwoord != nogmaals:
            fout = _("De wachtwoorden verschillen.")
    if fout:
        return render(request, "aanmelden.html", status_code=400, fout=fout, velden=velden, min_lengte=MIN_LENGTE)
    taal = huidige_taal() if huidige_taal() in TALEN else "nl"
    p = Profiel(gebruikersnaam=gebruikersnaam, naam=naam.strip()[:80] or gebruikersnaam, rol="lezer", taal=taal, actief=True,
                wachtwoord_hash=auth.hash_password(wachtwoord), laatst_ingelogd=now(), zelf_aangemeld=True)
    db.add(p)
    db.flush()
    resp = RedirectResponse("/gedeeld", status_code=303)
    _cookie(resp, p)  # geen domeincookie: zie Profiel.zelf_aangemeld
    return resp

