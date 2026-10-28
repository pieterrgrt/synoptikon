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


def sla_op(db: Session, stelsel_code: str, g: Geparseerd, wet: str | None = None, taal: str | None = None, kern: bool = True,
           vervang: bool = False) -> Wettekst:
    """`wet`: citeerafkorting waaronder de artikelen gevonden worden (None = hoofdcodificatie).

    `kern=False` voor een bulkimport (alle wetten van een bron): geen ruw bestand op schijf, niet in het overzicht en de
    systematiek. `vervang`: oudere versies van dezelfde wet weg (bulk houdt één versie per wet bij)."""
    bestand = None
    if g.ruw and kern:
        map_ = settings.wetteksten_dir / stelsel_code / _veilig(g.wet_id) / _veilig(g.versie)
        map_.mkdir(parents=True, exist_ok=True)
        pad = map_ / f"ruw.{g.ruw_extensie}"
        pad.write_bytes(g.ruw)
        bestand = str(pad.relative_to(settings.wetteksten_dir))

    q = select(Wettekst).where(Wettekst.stelsel_code == stelsel_code, Wettekst.wet_id == g.wet_id)
    for bestaand in db.scalars(q if vervang else q.where(Wettekst.versie == g.versie)).all():
        db.delete(bestaand)
    db.flush()
    w = Wettekst(stelsel_code=stelsel_code, wet_id=g.wet_id, wet=wet or None, titel=g.titel[:300], versie=g.versie, bron_url=g.bron_url,
                 bestand=bestand, taal=taal, kern=kern)
    gezien: set[str] = set()
    for i, a in enumerate(g.artikelen):
        if a.nummer[:40] in gezien:
            continue
        gezien.add(a.nummer[:40])
        w.artikelen.append(WettekstArtikel(nummer=a.nummer[:40], opschrift=(a.opschrift or None) and a.opschrift[:300], tekst=a.tekst,
                                           pad=(a.pad or None) and a.pad[:400], volgorde=i))
    db.add(w)
    db.flush()
    return w
