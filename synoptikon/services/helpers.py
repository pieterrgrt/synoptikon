from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import RECHTSFAMILIES, Stelsel, Vraag


def slugify(tekst: str) -> str:
    tekst = unicodedata.normalize("NFKD", tekst).encode("ascii", "ignore").decode()
    tekst = re.sub(r"[^a-zA-Z0-9]+", "-", tekst).strip("-").lower()
    return tekst[:100] or "vraag"


def unieke_slug(db: Session, titel: str, huidige_id: int | None = None) -> str:
    basis = slugify(titel)
    slug, n = basis, 2
    while True:
        bestaand = db.scalar(select(Vraag).where(Vraag.slug == slug))
        if bestaand is None or bestaand.id == huidige_id:
            return slug
        slug = f"{basis}-{n}"
        n += 1


def parse_datum(waarde: str | None) -> date | None:
    waarde = (waarde or "").strip()
    if not waarde:
        return None
    return date.fromisoformat(waarde)


def leeg_naar_none(waarde: str | None) -> str | None:
    waarde = (waarde or "").strip()
    return waarde or None


def actieve_stelsels(db: Session) -> list[Stelsel]:
    """Actieve stelsels, per rechtsfamilie gegroepeerd en binnen de familie op volgorde."""
    return op_familie(db.scalars(select(Stelsel).where(Stelsel.actief == True).order_by(Stelsel.volgorde)).all())  # noqa: E712


@dataclass
class Familie:
    sleutel: str
    naam: str
    kenmerk: str
    stelsels: list


def per_familie(stelsels) -> list[Familie]:
    """Groepeert stelsels per rechtsfamilie, in de volgorde van RECHTSFAMILIES; zonder familie achteraan."""
    groepen: dict[str, list] = {}
    for s in stelsels:
        groepen.setdefault(s.familie if s.familie in RECHTSFAMILIES else "", []).append(s)
    volgorde = [*RECHTSFAMILIES, ""]
    return [
        Familie(k, *(RECHTSFAMILIES.get(k) or ("Overig", "Nog niet ingedeeld bij een rechtsfamilie")), groepen[k])
        for k in volgorde
        if k in groepen
    ]


def op_familie(stelsels) -> list:
    """Dezelfde stelsels, zo geordend dat elke familie aaneengesloten staat."""
    return [s for f in per_familie(stelsels) for s in f.stelsels]


def stelsels_per_code(db: Session) -> dict[str, Stelsel]:
    return {s.code: s for s in db.scalars(select(Stelsel)).all()}
