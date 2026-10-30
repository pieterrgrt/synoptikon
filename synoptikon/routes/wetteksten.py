from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import Wettekst, WettekstArtikel
from ..services.helpers import actieve_stelsels
from . import render

router = APIRouter()


@router.get("/wetteksten")
def lijst(request: Request, db: Session = Depends(get_session)):
    # De wetten uit het register per stuk; de bulkimport (alle Duitse wetten, alle EU-handelingen) als telling per stelsel.
    wetten = db.scalars(select(Wettekst).where(Wettekst.kern.is_(True))
                        .order_by(Wettekst.stelsel_code, Wettekst.wet.is_not(None), Wettekst.titel, Wettekst.versie.desc())).all()
    ids = [w.id for w in wetten]
    aantallen = dict(db.execute(select(WettekstArtikel.wettekst_id, func.count()).where(WettekstArtikel.wettekst_id.in_(ids))
                                .group_by(WettekstArtikel.wettekst_id)).all())
    bulk = db.execute(select(Wettekst.stelsel_code, func.count(), func.max(Wettekst.opgehaald)).where(Wettekst.kern.is_(False))
                      .group_by(Wettekst.stelsel_code)).all()
    return render(request, "wetteksten.html", wetten=wetten, aantallen=aantallen, bulk=bulk, stelsels=actieve_stelsels(db))


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
