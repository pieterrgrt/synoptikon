"""Snel invoeren: mobielvriendelijk formulier voor bron, notitie of begrip bij een vraag."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import Antwoord, AntwoordBron, Begrip, Bron, Notitie, Vraag, VraagBegrip
from ..services.helpers import actieve_stelsels, leeg_naar_none
from .bronnen import SOORTEN
from . import render

router = APIRouter()


@router.get("/invoer")
def formulier(request: Request, vraag: str | None = None, tab: str = "bron", db: Session = Depends(get_session)):
    vragen = db.scalars(select(Vraag).order_by(Vraag.gewijzigd.desc())).all()
    return render(request, "invoer.html", vragen=vragen, stelsels=actieve_stelsels(db), soorten=SOORTEN, vooraf_vraag=vraag, tab=tab, klaar=request.query_params.get("klaar"))


def _vraag(db: Session, slug: str) -> Vraag:
    v = db.scalar(select(Vraag).where(Vraag.slug == slug))
    if v is None:
        raise HTTPException(404, "Vraag niet gevonden")
    return v


def _antwoord(db: Session, vraag: Vraag, code: str) -> Antwoord:
    a = vraag.antwoord_voor(code)
    if a is None:
        a = Antwoord(vraag=vraag, stelsel_code=code)
        db.add(a)
        db.flush()
    return a


@router.post("/invoer/bron")
def bron(
    vraag_slug: str = Form(...),
    stelsel_code: str = Form(...),
    soort: str = Form(...),
    citeertitel: str = Form(...),
    titel: str = Form(""),
    tekst: str = Form(""),
    taal: str = Form(""),
    vindplaats_type: str = Form(""),
    vindplaats: str = Form(""),
    url: str = Form(""),
    rol: str = Form(""),
    notitie: str = Form(""),
    db: Session = Depends(get_session),
):
    vraag = _vraag(db, vraag_slug)
    stelsel = next((s for s in actieve_stelsels(db) if s.code == stelsel_code), None)
    if stelsel is None:
        raise HTTPException(400, "Onbekend stelsel")
    b = Bron(
        stelsel_code=stelsel_code,
        soort=soort,
        citeertitel=citeertitel.strip(),
        titel=leeg_naar_none(titel),
        tekst=leeg_naar_none(tekst),
        taal=(taal.strip().lower() or stelsel.taal),
        vindplaats_type=leeg_naar_none(vindplaats_type),
        vindplaats=leeg_naar_none(vindplaats),
        url=leeg_naar_none(url),
    )
    db.add(b)
    a = _antwoord(db, vraag, stelsel_code)
    a.bronnen.append(AntwoordBron(bron=b, rol=leeg_naar_none(rol), notitie=leeg_naar_none(notitie), volgorde=len(a.bronnen)))
    return RedirectResponse(f"/invoer?vraag={vraag.slug}&tab=bron&klaar=bron", status_code=303)


@router.post("/invoer/notitie")
def notitie(vraag_slug: str = Form(...), stelsel_code: str = Form(""), tekst: str = Form(...), db: Session = Depends(get_session)):
    vraag = _vraag(db, vraag_slug)
    vraag.notities.append(Notitie(tekst=tekst.strip(), stelsel_code=leeg_naar_none(stelsel_code)))
    return RedirectResponse(f"/invoer?vraag={vraag.slug}&tab=notitie&klaar=notitie", status_code=303)


@router.post("/invoer/begrip")
def begrip(
    vraag_slug: str = Form(...),
    stelsel_code: str = Form(...),
    term: str = Form(...),
    taal: str = Form(""),
    definitie: str = Form(""),
    vindplaats: str = Form(""),
    db: Session = Depends(get_session),
):
    vraag = _vraag(db, vraag_slug)
    stelsel = next((s for s in actieve_stelsels(db) if s.code == stelsel_code), None)
    if stelsel is None:
        raise HTTPException(400, "Onbekend stelsel")
    g = db.scalar(select(Begrip).where(Begrip.stelsel_code == stelsel_code, Begrip.term == term.strip()))
    if g is None:
        g = Begrip(stelsel_code=stelsel_code, term=term.strip(), taal=(taal.strip().lower() or stelsel.taal), definitie=leeg_naar_none(definitie), vindplaats=leeg_naar_none(vindplaats))
        db.add(g)
        db.flush()
    if not any(vb.begrip_id == g.id for vb in vraag.begrippen):
        vraag.begrippen.append(VraagBegrip(begrip_id=g.id))
    return RedirectResponse(f"/invoer?vraag={vraag.slug}&tab=begrip&klaar=begrip", status_code=303)
