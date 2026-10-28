from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..auth import huidig_profiel
from ..db import get_session
from ..models import Bron, Concordantie, Systematiek, Vertaling, WettekstArtikel
from ..services import leren
from ..services.helpers import actieve_stelsels, leeg_naar_none, parse_datum
from . import render

router = APIRouter()

SOORTEN = {"wet": "wet", "rechtspraak": "rechtspraak", "literatuur": "literatuur", "softlaw": "soft law"}


@router.get("/bronnen")
def bronnen_lijst(request: Request, stelsel: str | None = None, soort: str | None = None, db: Session = Depends(get_session)):
    q = select(Bron).options(selectinload(Bron.stelsel)).order_by(Bron.stelsel_code, Bron.soort, Bron.citeertitel)
    if stelsel:
        q = q.where(Bron.stelsel_code == stelsel)
    if soort:
        q = q.where(Bron.soort == soort)
    bronnen = db.scalars(q).all()
    return render(request, "bronnen.html", bronnen=bronnen, stelsels=actieve_stelsels(db), soorten=SOORTEN, f_stelsel=stelsel, f_soort=soort)


def _systematiek_opties(db: Session) -> list[Systematiek]:
    return list(db.scalars(select(Systematiek).options(selectinload(Systematiek.parent)).order_by(Systematiek.stelsel_code, Systematiek.volgorde)).all())


@router.get("/bronnen/nieuw")
def bron_nieuw(request: Request, stelsel: str | None = None, db: Session = Depends(get_session)):
    return render(request, "bron_form.html", bron=None, stelsels=actieve_stelsels(db), soorten=SOORTEN, systematiek=_systematiek_opties(db), vooraf_stelsel=stelsel)


def _vul_bron(bron: Bron, form: dict) -> None:
    bron.stelsel_code = form["stelsel_code"]
    bron.soort = form["soort"]
    bron.citeertitel = form["citeertitel"].strip()
    bron.titel = leeg_naar_none(form.get("titel"))
    bron.tekst = leeg_naar_none(form.get("tekst"))
    bron.taal = form["taal"].strip().lower()
    bron.vindplaats_type = leeg_naar_none(form.get("vindplaats_type"))
    bron.vindplaats = leeg_naar_none(form.get("vindplaats"))
    bron.url = leeg_naar_none(form.get("url"))
    bron.geldig_van = parse_datum(form.get("geldig_van"))
    bron.geldig_tot = parse_datum(form.get("geldig_tot"))
    bron.opmerking = leeg_naar_none(form.get("opmerking"))
    sys_id = leeg_naar_none(form.get("systematiek_id"))
    bron.systematiek_id = int(sys_id) if sys_id else None


@router.post("/bronnen/nieuw")
async def bron_maak(request: Request, db: Session = Depends(get_session)):
    form = dict(await request.form())
    bron = Bron()
    _vul_bron(bron, form)
    db.add(bron)
    db.flush()
    terug = form.get("terug") or f"/bronnen/{bron.id}"
    return RedirectResponse(terug, status_code=303)


@router.get("/bronnen/{bron_id}")
def bron_detail(request: Request, bron_id: int, db: Session = Depends(get_session)):
    bron = db.get(Bron, bron_id)
    if bron is None:
        raise HTTPException(404)
    concordanties = [c for c in db.scalars(select(Concordantie).where(Concordantie.stelsel_code == bron.stelsel_code)).all() if c.wet in bron.citeertitel and (c.oud in bron.citeertitel or (c.nieuw and c.nieuw in bron.citeertitel))]
    artikel = bron.wettekst_artikel
    p = huidig_profiel(request)
    bewaard = bron.id in leren.bewaarde_bronnen(db, p.id if p else 1)
    return render(request, "bron_detail.html", bron=bron, concordanties=concordanties, artikel=artikel, soorten=SOORTEN, bron_bewaard=bewaard)


@router.get("/bronnen/{bron_id}/bewerken")
def bron_bewerken(request: Request, bron_id: int, db: Session = Depends(get_session)):
    bron = db.get(Bron, bron_id)
    if bron is None:
        raise HTTPException(404)
    return render(request, "bron_form.html", bron=bron, stelsels=actieve_stelsels(db), soorten=SOORTEN, systematiek=_systematiek_opties(db), vooraf_stelsel=None)


@router.post("/bronnen/{bron_id}/bewerken")
async def bron_opslaan(request: Request, bron_id: int, db: Session = Depends(get_session)):
    bron = db.get(Bron, bron_id)
    if bron is None:
        raise HTTPException(404)
    _vul_bron(bron, dict(await request.form()))
    return RedirectResponse(f"/bronnen/{bron.id}", status_code=303)


@router.post("/bronnen/{bron_id}/verwijderen")
def bron_verwijderen(bron_id: int, db: Session = Depends(get_session)):
    bron = db.get(Bron, bron_id)
    if bron is None:
        raise HTTPException(404)
    db.delete(bron)
    return RedirectResponse("/bronnen", status_code=303)


@router.post("/bronnen/{bron_id}/vertaling")
def vertaling_opslaan(bron_id: int, taal: str = Form(...), tekst: str = Form(...), herkomst: str = Form("eigen"), db: Session = Depends(get_session)):
    bron = db.get(Bron, bron_id)
    if bron is None:
        raise HTTPException(404)
    taal = taal.strip().lower()
    bestaand = bron.vertaling(taal)
    if tekst.strip() == "":
        if bestaand:
            db.delete(bestaand)
    elif bestaand:
        bestaand.tekst = tekst.strip()
        bestaand.herkomst = herkomst
    else:
        bron.vertalingen.append(Vertaling(taal=taal, tekst=tekst.strip(), herkomst=herkomst))
    return RedirectResponse(f"/bronnen/{bron.id}", status_code=303)


@router.post("/bronnen/{bron_id}/tekst-uit-wettekst")
def tekst_uit_wettekst(bron_id: int, artikel_id: int = Form(...), db: Session = Depends(get_session)):
    """Neemt de tekst van een geïmporteerd wetsartikel over in de bron."""
    bron = db.get(Bron, bron_id)
    artikel = db.get(WettekstArtikel, artikel_id)
    if bron is None or artikel is None:
        raise HTTPException(404)
    bron.tekst = artikel.tekst
    bron.wettekst_artikel_id = artikel.id
    if not bron.titel and artikel.opschrift:
        bron.titel = artikel.opschrift
    return RedirectResponse(f"/bronnen/{bron.id}", status_code=303)


# --- concordantie ---------------------------------------------------------


@router.get("/concordantie")
def concordantie_lijst(request: Request, db: Session = Depends(get_session)):
    rijen = db.scalars(select(Concordantie).order_by(Concordantie.stelsel_code, Concordantie.wet, Concordantie.datum, Concordantie.oud)).all()
    return render(request, "concordantie.html", rijen=rijen, stelsels=actieve_stelsels(db))


@router.post("/concordantie")
def concordantie_maak(
    stelsel_code: str = Form(...),
    wet: str = Form(...),
    oud: str = Form(...),
    nieuw: str = Form(""),
    datum: str = Form(""),
    grond: str = Form(""),
    toelichting: str = Form(""),
    db: Session = Depends(get_session),
):
    db.add(
        Concordantie(
            stelsel_code=stelsel_code,
            wet=wet.strip(),
            oud=oud.strip(),
            nieuw=leeg_naar_none(nieuw),
            datum=parse_datum(datum),
            grond=leeg_naar_none(grond),
            toelichting=leeg_naar_none(toelichting),
        )
    )
    return RedirectResponse("/concordantie", status_code=303)


@router.post("/concordantie/{cid}/verwijderen")
def concordantie_verwijderen(cid: int, db: Session = Depends(get_session)):
    c = db.get(Concordantie, cid)
    if c:
        db.delete(c)
    return RedirectResponse("/concordantie", status_code=303)
