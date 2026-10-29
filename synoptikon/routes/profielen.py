"""Profielen: eigen profiel (naam, taal, wachtwoord), beheer van de vijf plekken, taalkeuze."""
from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import auth
from ..config import settings
from ..db import get_session
from ..i18n import TALEN, _
from ..models import ROLLEN, Profiel
from . import render

router = APIRouter()

MIN_LENGTE = 10


def _terug(terug: str) -> str:
    return terug if terug.startswith("/") and not terug.startswith("//") else "/"


def _mijn(request: Request, db: Session) -> Profiel:
    p = auth.huidig_profiel(request)
    if p is None:
        raise HTTPException(401)
    return db.get(Profiel, p.id)


def _beheerder(request: Request) -> None:
    p = auth.huidig_profiel(request)
    if p is None or not p.is_beheerder:
        raise HTTPException(403, _("Alleen de beheerder beheert profielen."))


def _wachtwoord_fout(nieuw: str, nogmaals: str) -> str | None:
    if len(nieuw) < MIN_LENGTE:
        return _("Een wachtwoord heeft minstens {n} tekens.", n=MIN_LENGTE)
    if nieuw != nogmaals:
        return _("De wachtwoorden verschillen.")
    return None


def _cookie(resp, p: Profiel) -> None:
    resp.set_cookie(auth.COOKIE, auth.maak_sessie_token(p), max_age=settings.session_days * 86400,
                    httponly=True, secure=settings.cookie_secure, samesite="lax", path="/")


@router.post("/taal")
def kies_taal(request: Request, taal: str = Form(...), terug: str = Form("/"), db: Session = Depends(get_session)):
    if taal not in TALEN:
        raise HTTPException(400)
    p = auth.huidig_profiel(request) if auth.is_ingelogd(request) else None
    if p is not None:
        db.get(Profiel, p.id).taal = taal
    resp = RedirectResponse(_terug(terug), status_code=303)
    resp.set_cookie("taal", taal, max_age=365 * 86400, secure=settings.cookie_secure, samesite="lax", path="/")
    return resp


@router.post("/taal/inhoud")
def inhoud_origineel(origineel: str = Form("0"), terug: str = Form("/")):
    """Vertaalde inhoud tonen of de Nederlandse oorspronkelijke tekst."""
    resp = RedirectResponse(_terug(terug), status_code=303)
    if origineel == "1":
        resp.set_cookie("inhoud", "origineel", max_age=365 * 86400, secure=settings.cookie_secure, samesite="lax", path="/")
    else:
        resp.delete_cookie("inhoud", path="/")
    return resp


def _wk_stand(db: Session, p: Profiel) -> dict:
    """Voor het blok Wunderkammer op /profiel: is de koppeling ingesteld, en wat staat er in herhaling."""
    from ..models import Kaart, KaartStand, Leerlijst

    n = db.scalar(select(func.count()).select_from(KaartStand).join(Kaart).join(Leerlijst).where(Leerlijst.profiel_id == p.id)) or 0
    return dict(wk_ingesteld=settings.wk_ingesteld, wk_url=settings.wk_url, wk_herhaling=n)


@router.get("/profiel")
def profiel(request: Request, db: Session = Depends(get_session), klaar: str = ""):
    p = _mijn(request, db)
    return render(request, "profiel.html", p=p, fout=None, klaar=klaar, **_wk_stand(db, p))


@router.post("/profiel/gegevens")
def profiel_gegevens(request: Request, naam: str = Form(...), taal: str = Form(...), db: Session = Depends(get_session)):
    p = _mijn(request, db)
    p.naam = naam.strip()[:80] or p.naam
    if taal in TALEN:
        p.taal = taal
    resp = RedirectResponse("/profiel?klaar=gegevens", status_code=303)
    resp.set_cookie("taal", p.taal, max_age=365 * 86400, secure=settings.cookie_secure, samesite="lax", path="/")
    return resp


@router.post("/profiel/wunderkammer")
def profiel_wunderkammer(request: Request, aan: str = Form(""), db: Session = Depends(get_session)):
    p = _mijn(request, db)
    p.wunderkammer = aan == "1"
    if p.wunderkammer:
        from ..services import wk

        wk.meld()  # Wunderkammer meteen laten ophalen
    return RedirectResponse("/profiel?klaar=wunderkammer#wunderkammer", status_code=303)


@router.post("/profiel/wachtwoord")
def profiel_wachtwoord(request: Request, huidig: str = Form(...), nieuw: str = Form(...), nogmaals: str = Form(...),
                       db: Session = Depends(get_session)):
    p = _mijn(request, db)
    fout = None
    if auth.controleer(db, p.gebruikersnaam, huidig) is None:
        fout = _("Het huidige wachtwoord klopt niet.")
    fout = fout or _wachtwoord_fout(nieuw, nogmaals)
    if fout:
        return render(request, "profiel.html", status_code=400, p=p, fout=fout, klaar="", **_wk_stand(db, p))
    p.wachtwoord_hash = auth.hash_password(nieuw)
    p.sessie_versie += 1  # andere apparaten opnieuw laten inloggen
    db.flush()
    resp = RedirectResponse("/profiel?klaar=wachtwoord", status_code=303)
    _cookie(resp, p)
    return resp


@router.get("/beheer/profielen")
def beheer(request: Request, db: Session = Depends(get_session), klaar: str = "", fout: str = ""):
    _beheerder(request)
    profielen = db.scalars(select(Profiel).order_by(Profiel.id)).all()
    return render(request, "profielen.html", profielen=profielen, ROLLEN=ROLLEN, klaar=klaar, fout=fout,
                  ik=auth.huidig_profiel(request).id, min_lengte=MIN_LENGTE)


@router.post("/beheer/profielen/{pid}")
def beheer_opslaan(request: Request, pid: int, gebruikersnaam: str = Form(...), naam: str = Form(...), rol: str = Form(...),
                   taal: str = Form(...), actief: str = Form(""), wachtwoord: str = Form(""),
                   db: Session = Depends(get_session)):
    _beheerder(request)
    p = db.get(Profiel, pid)
    if p is None:
        raise HTTPException(404)
    ik = auth.huidig_profiel(request).id
    gebruikersnaam = gebruikersnaam.strip().lower()
    fout = None
    if not gebruikersnaam.replace("-", "").replace(".", "").replace("_", "").isalnum():
        fout = _("Een gebruikersnaam bestaat uit letters, cijfers, punt, streepje of liggend streepje.")
    elif db.scalar(select(func.count()).select_from(Profiel).where(
            func.lower(Profiel.gebruikersnaam) == gebruikersnaam, Profiel.id != pid)):
        fout = _("Die gebruikersnaam is al in gebruik.")
    elif rol not in ROLLEN or taal not in TALEN:
        fout = _("Onbekende rol of taal.")
    elif pid == ik and (rol != "beheerder" or not actief):
        fout = _("Je kunt jezelf niet uitzetten of je beheerdersrol afnemen.")
    elif wachtwoord and len(wachtwoord) < MIN_LENGTE:
        fout = _("Een wachtwoord heeft minstens {n} tekens.", n=MIN_LENGTE)
    elif actief and not wachtwoord and not p.wachtwoord_hash and pid != 1:
        fout = _("Geef een wachtwoord om dit profiel aan te zetten.")
    if fout:
        return RedirectResponse(f"/beheer/profielen?fout={quote(fout)}#p{pid}", status_code=303)
    was_actief = p.actief
    p.gebruikersnaam, p.naam, p.rol, p.taal, p.actief = gebruikersnaam, naam.strip()[:80] or gebruikersnaam, rol, taal, bool(actief)
    if wachtwoord:
        p.wachtwoord_hash = auth.hash_password(wachtwoord)
        p.sessie_versie += 1
    elif was_actief and not p.actief:
        p.sessie_versie += 1
    db.flush()
    resp = RedirectResponse(f"/beheer/profielen?klaar={pid}#p{pid}", status_code=303)
    if pid == ik and wachtwoord:
        _cookie(resp, p)
    return resp
