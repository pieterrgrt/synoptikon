from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..db import get_session
from ..models import Antwoord, AntwoordBron, Bron, Stelsel, Systematiek, Vraag
from ..services.helpers import actieve_stelsels, leeg_naar_none
from . import render

router = APIRouter()


@router.get("/stelsels")
def overzicht(request: Request, db: Session = Depends(get_session)):
    stelsels = db.scalars(select(Stelsel).order_by(Stelsel.volgorde)).all()
    return render(request, "stelsels.html", stelsels=stelsels)


@router.post("/stelsels")
def stelsel_maak(code: str = Form(...), naam: str = Form(...), taal: str = Form(...), toelichting: str = Form(""), db: Session = Depends(get_session)):
    code = code.strip().upper()
    if db.get(Stelsel, code):
        raise HTTPException(400, "Stelsel bestaat al")
    volgorde = max([s.volgorde for s in db.scalars(select(Stelsel)).all()] or [0]) + 10
    db.add(Stelsel(code=code, naam=naam.strip(), taal=taal.strip().lower(), volgorde=volgorde, toelichting=leeg_naar_none(toelichting)))
    return RedirectResponse("/stelsels", status_code=303)


@router.post("/stelsels/{code}/actief")
def stelsel_actief(code: str, actief: str = Form("0"), db: Session = Depends(get_session)):
    s = db.get(Stelsel, code)
    if s is None:
        raise HTTPException(404)
    s.actief = actief == "1"
    return RedirectResponse("/stelsels", status_code=303)


@router.get("/stelsels/{code}")
def systematiek(request: Request, code: str, vraag: str | None = None, db: Session = Depends(get_session)):
    stelsel = db.get(Stelsel, code)
    if stelsel is None:
        raise HTTPException(404)
    wortels = db.scalars(
        select(Systematiek)
        .where(Systematiek.stelsel_code == code, Systematiek.parent_id.is_(None))
        .options(selectinload(Systematiek.kinderen).selectinload(Systematiek.kinderen).selectinload(Systematiek.kinderen).selectinload(Systematiek.bronnen))
        .order_by(Systematiek.volgorde)
    ).all()
    vraag_obj = db.scalar(select(Vraag).where(Vraag.slug == vraag).options(selectinload(Vraag.antwoorden).selectinload(Antwoord.bronnen).selectinload(AntwoordBron.bron))) if vraag else None
    gemarkeerd: dict[int, list[Bron]] = {}
    los: list[Bron] = []
    if vraag_obj:
        a = vraag_obj.antwoord_voor(code)
        for ab in (a.bronnen if a else []):
            if ab.bron.systematiek_id:
                gemarkeerd.setdefault(ab.bron.systematiek_id, []).append(ab.bron)
            else:
                los.append(ab.bron)
    # Alle bronnen (wet) zonder systematiekknoop, om ze te kunnen plaatsen.
    ongeplaatst = db.scalars(select(Bron).where(Bron.stelsel_code == code, Bron.soort == "wet", Bron.systematiek_id.is_(None))).all()
    vragen = db.scalars(select(Vraag).order_by(Vraag.titel)).all()
    alle_knopen = db.scalars(select(Systematiek).where(Systematiek.stelsel_code == code).order_by(Systematiek.volgorde)).all()
    return render(
        request,
        "systematiek.html",
        stelsel=stelsel,
        stelsels=actieve_stelsels(db),
        wortels=wortels,
        vraag=vraag_obj,
        vragen=vragen,
        gemarkeerd=gemarkeerd,
        los=los,
        ongeplaatst=ongeplaatst,
        alle_knopen=alle_knopen,
    )


@router.post("/stelsels/{code}/systematiek")
def knoop_maak(code: str, label: str = Form(...), knoopcode: str = Form(""), bereik: str = Form(""), parent_id: str = Form(""), db: Session = Depends(get_session)):
    if db.get(Stelsel, code) is None:
        raise HTTPException(404)
    parent = int(parent_id) if parent_id.strip() else None
    broers = db.scalars(select(Systematiek).where(Systematiek.stelsel_code == code, Systematiek.parent_id.is_(parent) if parent is None else Systematiek.parent_id == parent)).all()
    db.add(
        Systematiek(
            stelsel_code=code,
            parent_id=parent,
            code=knoopcode.strip() or label.strip()[:60],
            label=label.strip(),
            bereik=leeg_naar_none(bereik),
            volgorde=max([b.volgorde for b in broers] or [0]) + 10,
        )
    )
    return RedirectResponse(f"/stelsels/{code}", status_code=303)


@router.post("/stelsels/{code}/plaats")
def bron_plaats(code: str, bron_id: int = Form(...), systematiek_id: str = Form(""), db: Session = Depends(get_session)):
    bron = db.get(Bron, bron_id)
    if bron is None:
        raise HTTPException(404)
    bron.systematiek_id = int(systematiek_id) if systematiek_id.strip() else None
    return RedirectResponse(f"/stelsels/{code}", status_code=303)
