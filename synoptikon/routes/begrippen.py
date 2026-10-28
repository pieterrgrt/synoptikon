from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..db import get_session
from ..i18n import _
from ..models import RELATIE_TYPES, Begrip, BegripRelatie, Vraag
from ..services import export, graaf
from ..services.helpers import actieve_stelsels, leeg_naar_none
from . import render

router = APIRouter()

# Teksten die kaart.js zelf toont; de pagina geeft ze vertaald mee.
KAART_TEKSTEN = ("faux ami", "geen equivalent", "deels", "equivalent", "Nog geen begrippen.", "Sluiten", "Geen relaties.", "Open begrip")


@router.get("/begrippen")
def kaart(request: Request, vraag: str | None = None, db: Session = Depends(get_session)):
    vraag_obj = db.scalar(select(Vraag).where(Vraag.slug == vraag)) if vraag else None
    data = graaf.begrippenkaart(db, vraag_obj)
    vragen = db.scalars(select(Vraag).order_by(Vraag.titel)).all()
    met_begrip = {k["stelsel"] for k in data["knopen"]}
    kaart_stelsels = [s for s in actieve_stelsels(db) if s.code in met_begrip]
    teksten = {t: _(t) for t in KAART_TEKSTEN}
    return render(request, "begrippenkaart.html", data=data, kaart_stelsels=kaart_stelsels, vragen=vragen, vraag=vraag_obj, kaart_teksten=teksten)


@router.get("/begrippen/kaart.json")
def kaart_json(vraag: str | None = None, db: Session = Depends(get_session)):
    vraag_obj = db.scalar(select(Vraag).where(Vraag.slug == vraag)) if vraag else None
    return JSONResponse(graaf.begrippenkaart(db, vraag_obj))


@router.get("/begrippen/lijst")
def lijst(request: Request, db: Session = Depends(get_session)):
    begrippen = db.scalars(
        select(Begrip).options(selectinload(Begrip.relaties_uit), selectinload(Begrip.relaties_in)).order_by(Begrip.term)
    ).all()
    per_stelsel: dict[str, list[Begrip]] = {}
    for g in begrippen:
        per_stelsel.setdefault(g.stelsel_code, []).append(g)
    return render(request, "begrippen_lijst.html", per_stelsel=per_stelsel, stelsels=actieve_stelsels(db))


@router.get("/begrippen/export.json")
def export_json(db: Session = Depends(get_session)):
    relaties = db.scalars(
        select(BegripRelatie).options(
            selectinload(BegripRelatie.van).selectinload(Begrip.vragen),
            selectinload(BegripRelatie.naar).selectinload(Begrip.vragen),
        )
    ).all()
    return Response(
        export.begrippenparen_json(list(relaties)),
        media_type="application/json; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="synoptikon-begrippenparen.json"'},
    )


@router.get("/begrippen/nieuw")
def nieuw(request: Request, db: Session = Depends(get_session)):
    return render(request, "begrip_form.html", begrip=None, stelsels=actieve_stelsels(db))


@router.post("/begrippen/nieuw")
def maak(
    stelsel_code: str = Form(...),
    term: str = Form(...),
    taal: str = Form(...),
    definitie: str = Form(""),
    vindplaats: str = Form(""),
    terug: str = Form(""),
    db: Session = Depends(get_session),
):
    g = Begrip(stelsel_code=stelsel_code, term=term.strip(), taal=taal.strip().lower(), definitie=leeg_naar_none(definitie), vindplaats=leeg_naar_none(vindplaats))
    db.add(g)
    db.flush()
    return RedirectResponse(terug or f"/begrippen/{g.id}", status_code=303)


@router.get("/begrippen/{begrip_id}")
def detail(request: Request, begrip_id: int, db: Session = Depends(get_session)):
    g = db.get(Begrip, begrip_id)
    if g is None:
        raise HTTPException(404)
    anderen = db.scalars(select(Begrip).where(Begrip.id != g.id).order_by(Begrip.stelsel_code, Begrip.term)).all()
    verbonden = {r.andere(g).id for r in g.relaties}
    return render(request, "begrip_detail.html", begrip=g, anderen=[a for a in anderen if a.id not in verbonden], relatie_types=RELATIE_TYPES)


@router.get("/begrippen/{begrip_id}/bewerken")
def bewerken(request: Request, begrip_id: int, db: Session = Depends(get_session)):
    g = db.get(Begrip, begrip_id)
    if g is None:
        raise HTTPException(404)
    return render(request, "begrip_form.html", begrip=g, stelsels=actieve_stelsels(db))


@router.post("/begrippen/{begrip_id}/bewerken")
def opslaan(
    begrip_id: int,
    stelsel_code: str = Form(...),
    term: str = Form(...),
    taal: str = Form(...),
    definitie: str = Form(""),
    vindplaats: str = Form(""),
    db: Session = Depends(get_session),
):
    g = db.get(Begrip, begrip_id)
    if g is None:
        raise HTTPException(404)
    g.stelsel_code, g.term, g.taal = stelsel_code, term.strip(), taal.strip().lower()
    g.definitie, g.vindplaats = leeg_naar_none(definitie), leeg_naar_none(vindplaats)
    return RedirectResponse(f"/begrippen/{g.id}", status_code=303)


@router.post("/begrippen/{begrip_id}/verwijderen")
def verwijderen(begrip_id: int, db: Session = Depends(get_session)):
    g = db.get(Begrip, begrip_id)
    if g:
        db.delete(g)
    return RedirectResponse("/begrippen/lijst", status_code=303)


@router.post("/begrippen/{begrip_id}/relatie")
def relatie_maak(begrip_id: int, naar_id: int = Form(...), type: str = Form(...), toelichting: str = Form(""), db: Session = Depends(get_session)):
    if type not in RELATIE_TYPES or naar_id == begrip_id:
        raise HTTPException(400)
    g, ander = db.get(Begrip, begrip_id), db.get(Begrip, naar_id)
    if g is None or ander is None:
        raise HTTPException(404)
    bestaand = db.scalar(
        select(BegripRelatie).where(
            ((BegripRelatie.van_id == g.id) & (BegripRelatie.naar_id == ander.id)) | ((BegripRelatie.van_id == ander.id) & (BegripRelatie.naar_id == g.id))
        )
    )
    if bestaand:
        bestaand.type, bestaand.toelichting = type, leeg_naar_none(toelichting)
    else:
        db.add(BegripRelatie(van_id=g.id, naar_id=ander.id, type=type, toelichting=leeg_naar_none(toelichting)))
    return RedirectResponse(f"/begrippen/{g.id}", status_code=303)


@router.post("/begrippen/relatie/{relatie_id}/verwijderen")
def relatie_verwijderen(relatie_id: int, terug: str = Form("/begrippen/lijst"), db: Session = Depends(get_session)):
    r = db.get(BegripRelatie, relatie_id)
    if r:
        db.delete(r)
    return RedirectResponse(terug, status_code=303)
