"""Opzoeken (`/opzoeken`): de enige zoekingang. Het veld in de kop komt hier ook uit; `/zoeken` stuurt hierheen.

Zie services/opzoeken.py voor wat er in welke volgorde gezocht wordt. Daaronder staan de full-text-treffers in de
wetteksten (eerst de wetten uit het register) en in de eigen inhoud, en het logboek van vandaag.
"""
from __future__ import annotations

import inspect
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..auth import huidig_profiel
from ..db import get_session
from ..i18n import _
from ..models import Kaart, Leerlijst, Opzoeking
from ..services import claude, leren, opzoeken, zoeken
from ..services.artikelen import Ref
from ..services.helpers import actieve_stelsels
from ..services.stelselkeuze import stelselkeuze
from . import render

router = APIRouter()
PER_PAGINA = 20


def _pid(request: Request) -> int:
    p = huidig_profiel(request)
    return p.id if p is not None else 1


@router.get("/zoeken")
def zoeken_oud(request: Request):
    return RedirectResponse(f"/opzoeken?{request.url.query}" if request.url.query else "/opzoeken", status_code=307)


@router.get("/opzoeken")
def pagina(request: Request, q: str = "", stelsel: str = "", alle: int = 0, p: int = 1, o: int | None = None,
           db: Session = Depends(get_session)):
    pid = _pid(request)
    q = q.strip()
    stelsel = stelsel.upper() if stelsel else ""
    # Zonder gekozen stelsel zoekt Opzoeken in mijn stelsels; `alle=1` ook in alle andere.
    keuze = stelselkeuze(db, request, [stelsel])
    codes = keuze.codes if keuze.overig and not stelsel and not alle else None
    uitkomst = resultaat = None
    verborgen = 0
    if q:
        uitkomst = _met_stelsels(opzoeken.lokaal, db, q, stelsel, stelsels=codes)
        resultaat = _met_stelsels(zoeken.zoek, db, q, limiet=PER_PAGINA, stelsel=stelsel, stelsels=codes)
        if p > 1:
            resultaat.wetteksten = [zoeken.Treffer("wettekst", Ref(wa.wettekst.stelsel_code, wa.nummer, wa.wettekst.wet).citeer, s,
                                                   Ref(wa.wettekst.stelsel_code, wa.nummer, wa.wettekst.wet).url, wa.wettekst.stelsel_code, wa.opschrift)
                                    for wa, s in _met_stelsels(zoeken.wetsartikelen, db, q, stelsel, PER_PAGINA, vanaf=(p - 1) * PER_PAGINA, stelsels=codes)]
        if codes is not None:
            verborgen = _alleen_eigen(uitkomst, resultaat, set(codes))
        if p == 1:
            opzoeken.log_lokaal(db, pid, q, uitkomst)
    lijsten = leren.lijsten_van(db, pid)
    return render(
        request, "opzoeken.html", q=q, f_stelsel=stelsel, p=max(1, p), uitkomst=uitkomst, resultaat=resultaat,
        stelsels=keuze.alle, beperkt=codes is not None, alle=bool(alle), verborgen=verborgen,
        logboek=opzoeken.vandaag(db, pid), lijsten=lijsten,
        gekozen_lijst=_gekozen(request, lijsten), claude_aan=claude.beschikbaar(), open_id=o,
        bewaarde_refs=leren.bewaarde_refs(db, pid), per_pagina=PER_PAGINA,
    )


def _met_stelsels(functie, *args, stelsels: list[str] | None, **kw):
    """Roept een zoekfunctie aan met `stelsels=` als die de parameter kent (services/opzoeken.py, zoeken.py)."""
    if stelsels is not None and "stelsels" in inspect.signature(functie).parameters:
        kw["stelsels"] = stelsels
    return functie(*args, **kw)


def _alleen_eigen(uitkomst, resultaat, codes: set[str]) -> int:
    """Haalt treffers uit andere stelsels weg (voor zover de zoekfunctie dat niet zelf deed) en telt ze.

    Een artikel dat met naam en toenaam is opgezocht (§ 1295 ABGB) blijft staan als er anders niets overblijft. Wat
    geen stelsel heeft (vragen, EU-handelingen) blijft altijd staan."""
    weg = 0

    def filter_(lijst, attr="stelsel"):
        nonlocal weg
        houden = [x for x in lijst if not getattr(x, attr, None) or getattr(x, attr) in codes]
        weg += len(lijst) - len(houden)
        return houden

    arts = [g for g in uitkomst.artikelen if not g.stelsel or g.stelsel in codes]
    if arts:
        weg += len(uitkomst.artikelen) - len(arts)
        uitkomst.artikelen = arts
    uitkomst.wetten = filter_(uitkomst.wetten)
    uitkomst.uitspraken = filter_(uitkomst.uitspraken)
    for veld in ("wetteksten", "bronnen", "begrippen", "antwoorden", "vertalingen"):
        setattr(resultaat, veld, filter_(getattr(resultaat, veld)))
    return weg


def _gekozen(request: Request, lijsten: list[Leerlijst]) -> int | None:
    try:
        lid = int(request.cookies.get("lijst", ""))
    except ValueError:
        lid = None
    if lid and any(l.id == lid for l in lijsten):
        return lid
    return lijsten[0].id if lijsten else None


@router.post("/opzoeken/claude")
def vraag_claude(request: Request, q: str = Form(...), db: Session = Depends(get_session)):
    if not claude.beschikbaar():
        raise HTTPException(503, _("Claude staat uit: er is geen API-sleutel ingesteld."))
    o = opzoeken.met_claude(db, _pid(request), q)
    return RedirectResponse(f"/opzoeken?q={quote(q.strip())}&o={o.id}#opzoeking-{o.id}", status_code=303)


@router.get("/opzoeken/{oid}")
def opzoeking(request: Request, oid: int, db: Session = Depends(get_session)):
    """Eén opzoeking als fragment: de pagina vraagt dit op zolang Claude bezig is."""
    o = db.get(Opzoeking, oid)
    if o is None or o.profiel_id != _pid(request):
        raise HTTPException(404)
    lijsten = leren.lijsten_van(db, _pid(request))
    return render(request, "_opzoeking.html", o=o, lijsten=lijsten, gekozen_lijst=_gekozen(request, lijsten), groot=True)


@router.post("/opzoeken/{oid}/verwijder")
def opzoeking_weg(request: Request, oid: int, db: Session = Depends(get_session)):
    o = db.get(Opzoeking, oid)
    if o is None or o.profiel_id != _pid(request):
        raise HTTPException(404)
    db.delete(o)
    return RedirectResponse("/opzoeken", status_code=303)


def _lijst_voor(request: Request, db: Session, lijst: str) -> Leerlijst:
    """De gekozen lijst, of een nieuwe lijst 'Opgezocht' als er nog geen is."""
    pid = _pid(request)
    if lijst.isdigit():
        l = db.get(Leerlijst, int(lijst))
        if l is None or l.profiel_id != pid:
            raise HTTPException(404)
        return l
    bestaand = leren.lijsten_van(db, pid)
    if bestaand:
        return bestaand[0]
    l = Leerlijst(profiel_id=pid, naam=_("Opgezocht"), naar_wk=True)
    db.add(l)
    db.flush()
    return l


@router.post("/opzoeken/{oid}/bewaren")
def opzoeking_bewaren(request: Request, oid: int, lijst: str = Form(""), terug: str = Form(""), db: Session = Depends(get_session)):
    """Met één tik een kaart: een artikel als artikelkaart, een uitspraak als arrestkaart (de uitspraak wordt een bron)."""
    o = db.get(Opzoeking, oid)
    if o is None or o.profiel_id != _pid(request):
        raise HTTPException(404)
    r = o.resultaat or {}
    l = _lijst_voor(request, db, lijst)
    kaarten: list[Kaart] = []
    if r.get("nummer") and r.get("stelsel"):
        kaarten = leren.maak_kaarten(db, l, ["artikel"], ref=Ref(r["stelsel"], r["nummer"], r.get("wet") or None),
                                     notitie=r.get("toelichting") if r.get("bron") == "claude" else None)
    elif bron := opzoeken.bron_uit(db, o):
        kaarten = leren.maak_kaarten(db, l, ["arrest"], bron=bron, antwoord=r.get("toelichting") or "")
    else:
        kaarten = leren.maak_kaarten(db, l, ["vrij"], vraag=r.get("citeer") or o.invoer,
                                     antwoord="\n\n".join(x for x in (r.get("plaats"), r.get("toelichting")) if x) or "")
    if kaarten:
        o.kaart_id = kaarten[0].id
    elif o.kaart_id is None:  # stond er al in
        o.kaart_id = next((k.id for k in l.kaarten), None)
    resp = RedirectResponse(_veilig(terug) or f"/opzoeken#opzoeking-{o.id}", status_code=303)
    resp.set_cookie("lijst", str(l.id), max_age=365 * 86400, httponly=True, samesite="lax")
    return resp


@router.post("/leren/snel")
def snel_bewaren(request: Request, lijst: str = Form(""), stelsel: str = Form(""), wet: str = Form(""), nummer: str = Form(""),
                 bron: str = Form(""), terug: str = Form(""), db: Session = Depends(get_session)):
    """Eén tik bij een artikel of uitspraak: een kaart in de laatst gekozen lijst (die gaat naar Wunderkammer)."""
    from ..models import Bron

    l = _lijst_voor(request, db, lijst or str(_gekozen(request, leren.lijsten_van(db, _pid(request))) or ""))
    if stelsel and nummer:
        n = leren.maak_kaarten(db, l, ["artikel"], ref=Ref(stelsel.upper(), nummer, wet or None))
    elif bron.isdigit() and (b := db.get(Bron, int(bron))):
        n = leren.maak_kaarten(db, l, ["arrest"], bron=b)
    else:
        raise HTTPException(400)
    doel = _veilig(terug) or "/leren"
    teken = "&" if "?" in doel.split("#")[0] else "?"
    pad, _s, anker = doel.partition("#")
    resp = RedirectResponse(f"{pad}{teken}bewaard={len(n)}" + (f"#{anker}" if anker else ""), status_code=303)
    resp.set_cookie("lijst", str(l.id), max_age=365 * 86400, httponly=True, samesite="lax")
    return resp


def _veilig(terug: str) -> str:
    return terug if terug.startswith("/") and not terug.startswith("//") else ""
