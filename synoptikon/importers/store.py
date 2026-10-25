"""Opslag van geïmporteerde wetteksten: ruw bestand op schijf, artikelen in de database."""
from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Wettekst, WettekstArtikel
from . import Geparseerd


def _veilig(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.\-]+", "_", s)[:80]


def sla_op(db: Session, stelsel_code: str, g: Geparseerd) -> Wettekst:
    bestand = None
    if g.ruw:
        map_ = settings.wetteksten_dir / stelsel_code / _veilig(g.wet_id) / _veilig(g.versie)
        map_.mkdir(parents=True, exist_ok=True)
        pad = map_ / f"ruw.{g.ruw_extensie}"
        pad.write_bytes(g.ruw)
        bestand = str(pad.relative_to(settings.wetteksten_dir))

    bestaand = db.scalar(select(Wettekst).where(Wettekst.stelsel_code == stelsel_code, Wettekst.wet_id == g.wet_id, Wettekst.versie == g.versie))
    if bestaand:
        db.delete(bestaand)
        db.flush()
    w = Wettekst(stelsel_code=stelsel_code, wet_id=g.wet_id, titel=g.titel, versie=g.versie, bron_url=g.bron_url, bestand=bestand)
    gezien: set[str] = set()
    for i, a in enumerate(g.artikelen):
        if a.nummer in gezien:
            continue
        gezien.add(a.nummer)
        w.artikelen.append(WettekstArtikel(nummer=a.nummer, opschrift=a.opschrift, tekst=a.tekst, pad=a.pad, volgorde=i))
    db.add(w)
    db.flush()
    return w
