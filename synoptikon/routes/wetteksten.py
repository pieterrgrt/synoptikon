from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import Bijwerking, Wettekst, WettekstArtikel
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
    profiel = getattr(request.state, "profiel", None)
    bijhouden = _bijhouden(db) if profiel is None or profiel.is_beheerder else None
    return render(request, "wetteksten.html", wetten=wetten, aantallen=aantallen, bulk=bulk, stelsels=actieve_stelsels(db),
                  bijhouden=bijhouden)


def _bijhouden(db: Session) -> list[dict]:
    """Per stelsel: wetten, artikelen, tekst in MB, laatst gecontroleerd en gewijzigd, en de laatste ronde van
    `synoptikon bijwerken` met haar fouten. Uit de kolommen aantal/grootte; alleen rijen van vóór die kolommen worden
    geteld (eenmalig, tot de eerste bijwerkronde ze invult)."""
    per = {code: {"code": code, "wetten": n, "artikelen": art or 0, "mb": (gr or 0) / 1e6, "gecontroleerd": gec, "gewijzigd": gew,
                  "ronde": None, "fouten": []}
           for code, n, art, gr, gec, gew in db.execute(
               select(Wettekst.stelsel_code, func.count(), func.sum(Wettekst.aantal), func.sum(Wettekst.grootte),
                      func.max(Wettekst.gecontroleerd), func.max(Wettekst.opgehaald)).group_by(Wettekst.stelsel_code))}
    for code, art, gr in db.execute(select(Wettekst.stelsel_code, func.count(), func.sum(func.length(WettekstArtikel.tekst)))
                                    .join(WettekstArtikel, WettekstArtikel.wettekst_id == Wettekst.id)
                                    .where(Wettekst.aantal.is_(None)).group_by(Wettekst.stelsel_code)):
        per[code]["artikelen"] += art
        per[code]["mb"] += (gr or 0) / 1e6
    # De laatste 200 logregels zijn genoeg voor een week rondes over alle bronnen.
    for b in db.scalars(select(Bijwerking).order_by(Bijwerking.begin.desc(), Bijwerking.id.desc()).limit(200)):
        rij = per.get(b.stelsel or "")
        if rij is None:
            continue
        if rij["ronde"] is None:
            rij["ronde"] = b
        if b.fouten and b.melding and len(rij["fouten"]) < 3:
            rij["fouten"].append((b.begin, b.melding.splitlines()[0]))
    return sorted(per.values(), key=lambda r: r["code"])


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
