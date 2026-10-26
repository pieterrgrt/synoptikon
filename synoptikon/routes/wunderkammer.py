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
"""
from __future__ import annotations

import hmac
import json
import re
from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import settings
from ..db import get_session
from ..models import Begrip, BegripRelatie
from ..services import export
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
