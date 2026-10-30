"""Markeren in een artikel of uitspraak: tekst selecteren, een soort kiezen, bewaren (static/js/markeren.js).

De markeringen zijn van het profiel. Ze kleuren de tekst (`markeer`-filter) en zijn materiaal voor kaarten
(services/markeringen.py, services/leren.py)."""
from __future__ import annotations

import re

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..auth import huidig_profiel
from ..db import get_session
from ..models import MARKERINGSOORTEN, Markering
from ..services import markeringen, vakken
from ..services.artikelen import Ref

router = APIRouter()


def _pid(request: Request) -> int:
    p = huidig_profiel(request)
    return p.id if p is not None else 1


def context_artikel(db: Session, pid: int, ref: Ref, tekst) -> dict:
    """Voor artikel.html: de markeringen bij de getoonde tekst (een bron of de wettekst) en waar nieuwe aan gehangen worden."""
    m = re.fullmatch(r"/bronnen/(\d+)", getattr(tekst, "url", "") or "") if tekst is not None else None
    if m:
        return context_bron(db, pid, int(m.group(1)), ref.stelsel, ref.wet, ref.nummer)
    return dict(markeringen=markeringen.van_artikel(db, pid, ref.stelsel, ref.wet, ref.nummer),
                markeer=dict(stelsel=ref.stelsel, wet=ref.wet or "", nummer=ref.nummer, vak=vakken.kies(db, pid, "", ref.stelsel, ref.wet, ref.nummer) or ""))


def context_bron(db: Session, pid: int, bron_id: int, stelsel: str | None = None, wet: str | None = None, nummer: str | None = None) -> dict:
    from ..models import Bron

    b = db.get(Bron, bron_id)
    return dict(markeringen=markeringen.van_bron(db, pid, bron_id),
                markeer=dict(bron=bron_id, vak=vakken.kies(db, pid, "", stelsel or (b.stelsel_code if b else None), wet, nummer) or ""))


@router.post("/markeringen")
def nieuw(request: Request, quote: str = Form(...), voor: str = Form(""), na: str = Form(""), soort: str = Form("kern"),
          notitie: str = Form(""), vak: str = Form(""), bron_id: int | None = Form(None), stelsel: str = Form(""), wet: str = Form(""),
          nummer: str = Form(""), db: Session = Depends(get_session)):
    pid = _pid(request)
    m = markeringen.maak(db, pid, quote, voor, na, soort, vak, notitie, bron_id, stelsel, wet, nummer)
    if m is None:
        raise HTTPException(422)
    vakken.onthoud(db, pid, m.vak)
    return JSONResponse({"id": m.id})


def _eigen(request: Request, db: Session, mid: int) -> Markering:
    m = db.get(Markering, mid)
    if m is None or m.profiel_id != _pid(request):
        raise HTTPException(404)
    return m


@router.post("/markeringen/{mid}")
def wijzig(request: Request, mid: int, soort: str = Form(""), notitie: str = Form(None), vak: str = Form(None), terug: str = Form(""),
           db: Session = Depends(get_session)):
    m = _eigen(request, db, mid)
    if soort in MARKERINGSOORTEN:
        m.soort = soort
    if notitie is not None:
        m.notitie = notitie.strip() or None
    if vak is not None:
        m.vak = vak.strip() or None
    return _terug(terug, m)


@router.post("/markeringen/{mid}/verwijder")
def verwijder(request: Request, mid: int, terug: str = Form(""), db: Session = Depends(get_session)):
    m = _eigen(request, db, mid)
    db.delete(m)
    return _terug(terug, None)


def _terug(terug: str, m):
    if terug.startswith("/") and not terug.startswith("//"):
        return RedirectResponse(terug, status_code=303)
    return JSONResponse({"id": m.id if m else None})
