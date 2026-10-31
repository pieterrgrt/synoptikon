"""`/bewaard`: alle wetsartikelen en uitspraken die jij hebt bewaard, per vak (services/bewaard.py)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import huidig_profiel
from ..db import get_session
from . import render
from ..models import Stelsel
from ..services import bewaard

router = APIRouter()


@router.get("/bewaard")
def bewaard_lijst(request: Request, vak: str | None = None, db: Session = Depends(get_session)):
    p = huidig_profiel(request)
    pid = p.id if p is not None else 1
    ov = bewaard.overzicht(db, pid, vak=vak)
    # Alle vakken voor de tabs, ook die van het niet-gekozen vak: anders kun je niet terug.
    alle = bewaard.overzicht(db, pid) if vak is not None else ov
    families = {c: f for c, f in db.execute(select(Stelsel.code, Stelsel.familie)).all()}
    return render(request, "bewaard.html", ov=ov, vakken=[g.vak for g in alle.groepen], gekozen=vak,
                  families=families, totaal=alle)
