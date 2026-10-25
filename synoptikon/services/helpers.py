from __future__ import annotations

import re
import unicodedata
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Stelsel, Vraag


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
    return list(db.scalars(select(Stelsel).where(Stelsel.actief == True).order_by(Stelsel.volgorde)).all())  # noqa: E712
