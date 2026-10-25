"""Artikelen: opzoeken, plaats in de systematiek en corresponderende artikelen.

`/artikelen/NL/3:84` toont waar art. 3:84 BW in het BW staat, de thema's
waarin het voorkomt en per thema de artikelen uit de andere stelsels, elk met
hun eigen plaats in hun eigen systematiek.
"""
from __future__ import annotations

from collections import OrderedDict
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import Correspondentie, CorrespondentieArtikel, Stelsel
from ..services import correspondentie as corr
from ..services.artikelen import Ref, herken, lees, sleutel
from ..services.helpers import actieve_stelsels, leeg_naar_none
from . import render

router = APIRouter()


def _codes(db: Session) -> list[str]:
    return [s.code for s in actieve_stelsels(db)]


@router.get("/artikelen")
def overzicht(request: Request, q: str = "", stelsel: str = "", db: Session = Depends(get_session)):
    kandidaten: list[Ref] = []
    if q.strip():
        kandidaten = herken(q, stelsel or None)
        if len(kandidaten) == 1:
            return RedirectResponse(kandidaten[0].url, status_code=303)
    thema_s = corr.alle_correspondenties(db)
    groepen: OrderedDict[str, list[Correspondentie]] = OrderedDict()
    for c in thema_s:
        groepen.setdefault(c.rechtsgebied or "Overig", []).append(c)
    stelsels = actieve_stelsels(db)
    gebruikt = {a.stelsel_code for c in thema_s for a in c.artikelen}
    kolommen = [s for s in stelsels if s.code in gebruikt] or stelsels
    return render(
        request,
        "artikelen.html",
        q=q,
        f_stelsel=stelsel,
        kandidaten=kandidaten,
        groepen=groepen,
        kolommen=kolommen,
        stelsels=stelsels,
        aantal=len(thema_s),
    )


# --- thema's ------------------------------------------------------------------------


@router.get("/artikelen/thema/{cid}")
def thema(request: Request, cid: int, db: Session = Depends(get_session)):
    c = db.get(Correspondentie, cid)
    if c is None:
        raise HTTPException(404)
    ctx = corr.Context(db)
    stelsels = actieve_stelsels(db)
    kolommen = corr.per_stelsel(ctx, c, [s.code for s in stelsels])
    namen = {s.code: s.naam for s in db.scalars(select(Stelsel)).all()}
    return render(request, "thema.html", c=c, kolommen=kolommen, namen=namen, stelsels=stelsels)


@router.post("/artikelen/thema")
def thema_maak(
    titel: str = Form(...),
    rechtsgebied: str = Form(""),
    toelichting: str = Form(""),
    stelsel_code: str = Form(""),
    verwijzing: str = Form(""),
    rol: str = Form(""),
    db: Session = Depends(get_session),
):
    titel = titel.strip()
    if db.scalar(select(Correspondentie).where(Correspondentie.titel == titel)):
        raise HTTPException(400, "Er bestaat al een thema met deze titel")
    c = Correspondentie(titel=titel, rechtsgebied=leeg_naar_none(rechtsgebied), toelichting=leeg_naar_none(toelichting))
    db.add(c)
    if stelsel_code and verwijzing.strip():
        _voeg_lid_toe(c, stelsel_code, verwijzing, rol, "")
    db.flush()
    return RedirectResponse(f"/artikelen/thema/{c.id}", status_code=303)


@router.post("/artikelen/thema/{cid}/bewerken")
def thema_opslaan(cid: int, titel: str = Form(...), rechtsgebied: str = Form(""), toelichting: str = Form(""), db: Session = Depends(get_session)):
    c = db.get(Correspondentie, cid)
    if c is None:
        raise HTTPException(404)
    c.titel, c.rechtsgebied, c.toelichting = titel.strip(), leeg_naar_none(rechtsgebied), leeg_naar_none(toelichting)
    return RedirectResponse(f"/artikelen/thema/{c.id}", status_code=303)


@router.post("/artikelen/thema/{cid}/verwijderen")
def thema_verwijderen(cid: int, db: Session = Depends(get_session)):
    c = db.get(Correspondentie, cid)
    if c:
        db.delete(c)
    return RedirectResponse("/artikelen", status_code=303)


def _voeg_lid_toe(c: Correspondentie, stelsel_code: str, verwijzing: str, rol: str, opmerking: str) -> CorrespondentieArtikel:
    ref = lees(stelsel_code, verwijzing)
    if ref is None:
        raise HTTPException(400, f"Kan '{verwijzing}' niet lezen als artikel uit {stelsel_code}")
    volgorde = max([a.volgorde for a in c.artikelen] or [0]) + 10
    lid = CorrespondentieArtikel(
        stelsel_code=stelsel_code, wet=ref.wet, nummer=ref.nummer, tot=ref.tot, detail=ref.detail,
        rol=leeg_naar_none(rol), opmerking=leeg_naar_none(opmerking), volgorde=volgorde,
    )
    c.artikelen.append(lid)
    return lid


@router.post("/artikelen/thema/{cid}/artikel")
def lid_maak(
    cid: int,
    stelsel_code: str = Form(...),
    verwijzing: str = Form(...),
    rol: str = Form(""),
    opmerking: str = Form(""),
    terug: str = Form(""),
    db: Session = Depends(get_session),
):
    c = db.get(Correspondentie, cid)
    if c is None or db.get(Stelsel, stelsel_code) is None:
        raise HTTPException(404)
    _voeg_lid_toe(c, stelsel_code, verwijzing, rol, opmerking)
    return RedirectResponse(terug if terug.startswith("/") and not terug.startswith("//") else f"/artikelen/thema/{c.id}", status_code=303)


@router.post("/artikelen/koppel")
def koppel(
    thema_id: int = Form(...),
    stelsel_code: str = Form(...),
    verwijzing: str = Form(...),
    rol: str = Form(""),
    opmerking: str = Form(""),
    terug: str = Form(""),
    db: Session = Depends(get_session),
):
    return lid_maak(thema_id, stelsel_code, verwijzing, rol, opmerking, terug, db)


@router.post("/artikelen/thema/{cid}/artikel/{aid}/verwijderen")
def lid_verwijderen(cid: int, aid: int, db: Session = Depends(get_session)):
    a = db.get(CorrespondentieArtikel, aid)
    if a and a.correspondentie_id == cid:
        db.delete(a)
    return RedirectResponse(f"/artikelen/thema/{cid}", status_code=303)


# Als laatste: het pad-patroon zou anders /artikelen/thema/… opslokken.
@router.get("/artikelen/{stelsel}/{nummer:path}")
def artikel(request: Request, stelsel: str, nummer: str, wet: str | None = None, db: Session = Depends(get_session)):
    st = db.get(Stelsel, stelsel.upper())
    if st is None:
        raise HTTPException(404)
    ref = lees(st.code, nummer)
    if ref is None or ref.nummer is None:
        raise HTTPException(404, "Onleesbaar artikelnummer")
    ref = Ref(st.code, ref.nummer, wet or None)
    if ref.nummer != nummer:
        return RedirectResponse(ref.url, status_code=303)
    ctx = corr.Context(db)
    codes = _codes(db)
    thema_s = []
    for c, eigen in corr.thema_s_voor(db, ref.stelsel, ref.nummer, ref.wet):
        thema_s.append((c, eigen, corr.per_stelsel(ctx, c, codes, behalve=eigen[0] if len(eigen) == 1 else None)))
    pad = ctx.pad(ref)
    buren = _buren(ctx, ref, pad)
    return render(
        request,
        "artikel.html",
        ref=ref,
        stelsel=st,
        pad=pad,
        tekst=ctx.tekst(ref),
        thema_s=thema_s,
        concordanties=corr.concordanties_voor(db, ref.stelsel, ref.nummer) if not ref.wet else [],
        gebruik=corr.gebruik(ctx, ref),
        buren=buren,
        alle_thema_s=db.scalars(select(Correspondentie).order_by(Correspondentie.titel)).all(),
        stelsels=actieve_stelsels(db),
    )


def _buren(ctx: corr.Context, ref: Ref, pad: list) -> list[Ref]:
    """Andere artikelen uit dezelfde knoop die in een thema voorkomen (om verder te bladeren)."""
    if not pad:
        return []
    knoop = pad[-1]
    gezien, uit = {ref.nummer}, []
    for _c, a in corr.leden_in_knoop(ctx, knoop):
        if a.nummer not in gezien and a.tot is None:
            gezien.add(a.nummer)
            uit.append(Ref(a.stelsel_code, a.nummer))
    uit.sort(key=lambda r: sleutel(r.stelsel, r.nummer) or ())
    return uit
