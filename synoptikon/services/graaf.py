"""Gegevens voor de begrippenkaart (graaf) als JSON-structuur."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import Begrip, BegripRelatie, Vraag


def begrippenkaart(db: Session, vraag: Vraag | None = None, stelsels: list[str] | None = None) -> dict:
    q = select(Begrip).options(selectinload(Begrip.stelsel), selectinload(Begrip.vragen))
    begrippen = list(db.scalars(q).all())
    if vraag is not None:
        ids = {vb.begrip_id for vb in vraag.begrippen}
        begrippen = [g for g in begrippen if g.id in ids]
    if stelsels:
        begrippen = [g for g in begrippen if g.stelsel_code in stelsels]
    ids = {g.id for g in begrippen}

    relaties = db.scalars(select(BegripRelatie)).all()
    knopen = [
        {
            "id": g.id,
            "term": g.term,
            "stelsel": g.stelsel_code,
            "taal": g.taal,
            "definitie": g.definitie or "",
            "vindplaats": g.vindplaats or "",
            "vragen": [vb.vraag.slug for vb in g.vragen],
        }
        for g in begrippen
    ]
    kanten = [
        {"id": r.id, "van": r.van_id, "naar": r.naar_id, "type": r.type, "label": r.type_label, "toelichting": r.toelichting or ""}
        for r in relaties
        if r.van_id in ids and r.naar_id in ids
    ]
    return {"knopen": knopen, "kanten": kanten}
