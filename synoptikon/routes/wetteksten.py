from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..db import get_session
from ..models import Wettekst
from ..services.helpers import actieve_stelsels
from . import render

router = APIRouter()


@router.get("/wetteksten")
def lijst(request: Request, db: Session = Depends(get_session)):
    wetten = db.scalars(select(Wettekst).options(selectinload(Wettekst.artikelen)).order_by(Wettekst.stelsel_code, Wettekst.titel, Wettekst.versie.desc())).all()
    return render(request, "wetteksten.html", wetten=wetten, stelsels=actieve_stelsels(db))


@router.get("/wetteksten/{wettekst_id}")
def detail(request: Request, wettekst_id: int, q: str = "", db: Session = Depends(get_session)):
    w = db.get(Wettekst, wettekst_id)
    if w is None:
        raise HTTPException(404)
    artikelen = w.artikelen
    if q.strip():
        qq = q.strip().lower()
        artikelen = [a for a in artikelen if qq in a.nummer.lower() or qq in (a.opschrift or "").lower()]
    return render(request, "wettekst_detail.html", w=w, artikelen=artikelen[:400], q=q, totaal=len(w.artikelen))
