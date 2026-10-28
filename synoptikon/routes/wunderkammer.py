"""Koppeling met Wunderkammer: een kleine JSON-API met een eigen token, zonder sessiecookie.

Wunderkammer (Pieters leer-app, module Jura) haalt hier de wettekst van de artikelen die in zijn kaarten staan, de
correspondentietabel en de begrippenparen op, en bewaart ze zelf (herhalen werkt dus ook als Synoptikon even weg is).
Alleen lezen; er wordt niets in Synoptikon geschreven.

- `SYNOPTIKON_WK_TOKEN` (≥ 24 tekens) aan; leeg = de routes bestaan niet (404).
- `Authorization: Bearer <token>`; Wunderkammer zet hetzelfde in `WK_SYNOPTIKON_TOKEN`.

Formaat `synoptikon-wunderkammer`, versie 1:

    GET  /api/wk/themen      {"format", "version", "exported", "correspondenties": [{id, titel, rechtsgebied, toelichting,
                              artikelen: [{stelsel, wet, nummer, tot, detail, rol, opmerking}]}], "begrippen": [paren]}
    POST /api/wk/artikelen   {"refs": [{stelsel, wet, nummer}]} (wet leeg = hoofdwet: BGB, BW, Code civil; max. 500)
                             → {"artikelen": [{stelsel, wet, nummer, opschrift, tekst, pad: [..], versie, bron_url}]}

De begrippenparen hebben de vorm van `/begrippen/export.json` (zie services/export.py).

Kaarten uit de leerlijsten (versie 2). Synoptikon maakt ze, Wunderkammer plant de herhaling en meldt de stand terug:

    GET  /api/wk/kaarten?profiel=pieter
                             {"format", "version": 2, "exported", "profiel", "lijsten": [{id, naam, vak, examen, omschrijving}],
                              "kaarten": [{uid, lijst, soort, soort_label, voor, achter, url, refs: [{stelsel, wet, nummer}],
                              zaak, vindplaats, gewijzigd}]}
                             Alleen actieve kaarten uit lijsten met "naar Wunderkammer"; voor/achter zijn HTML, url is een
                             pad in Synoptikon. Een uid die niet meer meekomt is verwijderd of uitgezet.
    POST /api/wk/kaarten/stand {"stand": [{uid, due, stability, reps, lapses, last_review, last_rating}]} → {"bijgewerkt": n}
"""
from __future__ import annotations

import hmac
import json
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..config import settings
from ..db import get_session
from ..i18n import zet_taal
from ..models import Begrip, BegripRelatie, Profiel
from ..services import export, leren
from ..services.artikelen import Ref
from ..services.correspondentie import alle_correspondenties, wettekst_artikel

router = APIRouter(prefix="/api/wk")
FORMAT = "synoptikon-wunderkammer"
MAX_REFS = 500


def token_ok(request: Request) -> None:
    want = settings.wk_token or ""
    if len(want) < 24:
        raise HTTPException(404)
    got = request.headers.get("authorization", "")
    if not got.startswith("Bearer ") or not hmac.compare_digest(got[7:].strip(), want):
        raise HTTPException(401, "Ongeldig token")


@router.get("/themen", dependencies=[Depends(token_ok)])
def themen(db: Session = Depends(get_session)):
    corr = [
        dict(id=c.id, titel=c.titel, rechtsgebied=c.rechtsgebied, toelichting=c.toelichting,
             artikelen=[dict(stelsel=a.stelsel_code, wet=a.wet, nummer=a.nummer, tot=a.tot, detail=a.detail, rol=a.rol,
                             opmerking=a.opmerking) for a in sorted(c.artikelen, key=lambda a: (a.volgorde, a.id))])
        for c in alle_correspondenties(db)
    ]
    relaties = db.scalars(select(BegripRelatie).options(
        selectinload(BegripRelatie.van).selectinload(Begrip.vragen),
        selectinload(BegripRelatie.naar).selectinload(Begrip.vragen))).all()
    paren = json.loads(export.begrippenparen_json(list(relaties)))["pairs"]
    return dict(format=FORMAT, version=1, exported=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                correspondenties=corr, begrippen=paren)


@router.post("/artikelen", dependencies=[Depends(token_ok)])
def artikelen(body: dict = Body(...), db: Session = Depends(get_session)):
    refs = body.get("refs")
    eigenaar = db.get(Profiel, 1)
    zet_taal(eigenaar.taal if eigenaar else "de")  # EU-verdragen in de taal van de eigenaar
    if not isinstance(refs, list) or len(refs) > MAX_REFS:
        raise HTTPException(422, f"refs: lijst van hoogstens {MAX_REFS}")
    uit = []
    for r in refs:
        if not isinstance(r, dict) or not r.get("stelsel") or not r.get("nummer"):
            continue
        ref = Ref(str(r["stelsel"]).upper(), str(r["nummer"]), r.get("wet") or None)
        a = wettekst_artikel(db, ref)
        if a is None:
            continue
        uit.append(dict(stelsel=ref.stelsel, wet=ref.wet, nummer=ref.nummer, opschrift=a.opschrift, tekst=a.tekst,
                        pad=[re.sub(r"\s+", " ", p).strip() for p in (a.pad or "").split("›") if p.strip()],
                        versie=a.wettekst.versie, bron_url=a.wettekst.bron_url))
    return dict(format=FORMAT, version=1, artikelen=uit)


@router.get("/kaarten", dependencies=[Depends(token_ok)])
def kaarten(profiel: str = "", db: Session = Depends(get_session)):
    p = db.scalar(select(Profiel).where(func.lower(Profiel.gebruikersnaam) == profiel.strip().lower())) if profiel.strip() else db.get(Profiel, 1)
    if p is None:
        raise HTTPException(404, "Onbekend profiel")
    zet_taal(p.taal)
    lijsten = [l for l in leren.lijsten_van(db, p.id) if l.naar_wk]
    bouwer = leren.Bouwer(db)
    uit = []
    for l in lijsten:
        for k in l.kaarten:
            if not k.actief:
                continue
            voor, achter, z = bouwer.html(k)
            ref = leren.ref_van(k)
            uit.append(dict(uid=k.uid, lijst=l.id, soort=k.soort, soort_label=k.soort_label, voor=voor, achter=achter, url=z.url,
                            refs=[dict(stelsel=ref.stelsel, wet=ref.wet, nummer=ref.nummer)] if ref else [],
                            zaak=k.zaak or (k.bron.citeertitel if k.bron else None), vindplaats=k.vindplaats,
                            gewijzigd=k.gewijzigd.isoformat()))
    return dict(format=FORMAT, version=2, exported=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                profiel=p.gebruikersnaam,
                lijsten=[dict(id=l.id, naam=l.naam, vak=l.vak, examen=l.examen.isoformat() if l.examen else None,
                              omschrijving=l.omschrijving) for l in lijsten],
                kaarten=uit)


@router.post("/kaarten/stand", dependencies=[Depends(token_ok)])
def kaarten_stand(body: dict = Body(...), db: Session = Depends(get_session)):
    stand = body.get("stand")
    if not isinstance(stand, list) or len(stand) > 5000:
        raise HTTPException(422, "stand: lijst van hoogstens 5000")
    return dict(bijgewerkt=leren.zet_stand(db, stand))
