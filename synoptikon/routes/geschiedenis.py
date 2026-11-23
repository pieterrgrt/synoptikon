"""Geschiedenis van gedeelde inhoud (services/wijzigingen.py): per rij alle versies, en een overzicht van alles."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import Wijziging
from ..services import wijzigingen
from . import render

router = APIRouter()


@router.get("/geschiedenis/{soort}/{rij_id}")
def geschiedenis(request: Request, soort: str, rij_id: int, fout: str | None = None, db: Session = Depends(get_session)):
    if soort not in wijzigingen.SOORTEN:
        raise HTTPException(404)
    bestaat = db.get(wijzigingen.SOORTEN[soort][0], rij_id) is not None
    ws = wijzigingen.geschiedenis(db, soort, rij_id, bestaat)
    if not ws:
        raise HTTPException(404)
    labels = wijzigingen.label_en_link(db, ws)
    return render(request, "geschiedenis.html", soort=soort, rij_id=rij_id, ws=ws, label=labels[ws[0].id], bestaat=bestaat,
                  verschillen={w.id: wijzigingen.verschillen(w) for w in ws}, fout=fout)


@router.post("/geschiedenis/{soort}/{rij_id}/terugzetten")
def terugzetten(soort: str, rij_id: int, wijziging: int = Form(...), ervoor: str = Form(""),
                db: Session = Depends(get_session)):
    w = db.get(Wijziging, wijziging)
    bestaat = db.get(wijzigingen.SOORTEN[soort][0], rij_id) is not None if soort in wijzigingen.SOORTEN else False
    if w is None or w.soort != soort or w.rij_id != rij_id or w not in wijzigingen.geschiedenis(db, soort, rij_id, bestaat):
        raise HTTPException(404)
    try:
        wijzigingen.terugzetten(db, w, ervoor == "1")
    except wijzigingen.TerugzettenMislukt:
        return RedirectResponse(f"/geschiedenis/{soort}/{rij_id}?fout=1", status_code=303)
    return RedirectResponse(f"/geschiedenis/{soort}/{rij_id}", status_code=303)


@router.get("/wijzigingen")
def overzicht(request: Request, profiel: int | None = None, db: Session = Depends(get_session)):
    q = select(Wijziging).order_by(Wijziging.id.desc()).limit(300)
    if profiel is not None:
        q = q.where(Wijziging.profiel_id == profiel)
    ws = list(db.scalars(q))
    return render(request, "wijzigingen.html", ws=ws, labels=wijzigingen.label_en_link(db, ws))
