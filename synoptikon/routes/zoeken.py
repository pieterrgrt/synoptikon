from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from ..db import get_session
from ..services.zoeken import zoek
from . import render

router = APIRouter()


@router.get("/zoeken")
def zoeken(request: Request, q: str = "", db: Session = Depends(get_session)):
    resultaat = zoek(db, q) if q.strip() else None
    return render(request, "zoeken.html", q=q, resultaat=resultaat)
