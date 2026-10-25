"""Systematiek opbouwen uit een geïmporteerde wettekst.

Elke importer bewaart per artikel het pad ("Boek 3 Vermogensrecht in het
algemeen › Titel 4 Verkrijging en verlies van goederen › Afdeling 2
Overdracht"). Daaruit volgt de volledige boom, tot op paragraaf- of
sous-sectionniveau, met exacte bereiken.

Bestaande knopen worden herkend aan hun eerste twee woorden onder dezelfde
ouder ("Titel 4", "Buch 3", "Livre III"), zodat de seed-boom en zelf
aangemaakte knopen hun code, bronnen en correspondenties houden; alleen het
bereik wordt bijgewerkt. Ontbrekende knopen worden aangemaakt.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Systematiek, Wettekst
from .artikelen import formatteer_bereik, sleutel

PREFIX = {"NL": "BW", "DE": "BGB", "FR": "CC"}


def _sleutel_label(label: str) -> str:
    """'Titel 4 · Verkrijging…' en 'Titel 4 Verkrijging…' → 'titel 4'; 'Livre Ier :' → 'livre i'."""
    woorden = re.sub(r"[·:.,]", " ", label).split()
    if not woorden:
        return ""
    if len(woorden) == 1:
        return woorden[0].lower()
    nr = woorden[1].lower()
    nr = {"ier": "i", "1er": "1", "première": "1", "premier": "1"}.get(nr, nr)
    if len(woorden) > 2 and woorden[2].lower() in ("bis", "ter", "quater"):
        nr += woorden[2].lower()
    return f"{woorden[0].lower()} {nr}"


def _mooi_label(stuk: str) -> str:
    """'Titel 4 Verkrijging en verlies' → 'Titel 4 · Verkrijging en verlies'; 'Livre III : Des …' → 'Livre III · Des …'."""
    stuk = re.sub(r"\s+", " ", stuk).strip()
    m = re.match(r"^(\S+ \S+?)(?:\s*[:.·-]\s*|\s+)(.+)$", stuk)
    if not m or not re.search(r"\d|^[IVXLC]+$|^(Ier|1er|préliminaire|bis)$", m.group(1).split(" ", 1)[1], re.I):
        return stuk
    return f"{m.group(1)} · {m.group(2)}"


@dataclass
class _Knoop:
    stuk: str
    nummers: list[str] = field(default_factory=list)
    kinderen: dict[str, "_Knoop"] = field(default_factory=dict)
    eerste: int = 0


@dataclass
class Resultaat:
    nieuw: int = 0
    bijgewerkt: int = 0
    artikelen: int = 0


def bouw_uit_wettekst(db: Session, w: Wettekst) -> Resultaat:
    stelsel = w.stelsel_code
    wortel = _Knoop("")
    res = Resultaat()
    for i, a in enumerate(w.artikelen):
        if not a.pad or sleutel(stelsel, a.nummer) is None:
            continue
        res.artikelen += 1
        knoop = wortel
        for stuk in [s.strip() for s in a.pad.split("›") if s.strip()]:
            k = _sleutel_label(stuk)
            if k not in knoop.kinderen:
                knoop.kinderen[k] = _Knoop(stuk, eerste=i)
            knoop = knoop.kinderen[k]
            knoop.nummers.append(a.nummer)

    bestaand = list(db.scalars(select(Systematiek).where(Systematiek.stelsel_code == stelsel)).all())
    codes = {k.code for k in bestaand}
    per_ouder: dict[int | None, list[Systematiek]] = {}
    for k in bestaand:
        per_ouder.setdefault(k.parent_id, []).append(k)

    def code_voor(ouder: Systematiek | None, stuk: str) -> str:
        woorden = _sleutel_label(stuk).split()
        deel = woorden[1] if len(woorden) > 1 else woorden[0] if woorden else "x"
        basis = f"{ouder.code if ouder else PREFIX.get(stelsel, w.wet_id.upper())}-{deel.upper() if not deel.isdigit() else deel}"
        code, n = basis, 2
        while code in codes:
            code, n = f"{basis}-{n}", n + 1
        codes.add(code)
        return code

    def verwerk(boom: _Knoop, ouder: Systematiek | None) -> None:
        kinderen = per_ouder.setdefault(ouder.id if ouder else None, [])
        index = {_sleutel_label(k.label): k for k in kinderen}
        for sleutel_, sub in sorted(boom.kinderen.items(), key=lambda kv: kv[1].eerste):
            knoop = index.get(sleutel_)
            bereik = formatteer_bereik(stelsel, sub.nummers) or None
            if knoop is None:
                knoop = Systematiek(stelsel_code=stelsel, parent=ouder, code=code_voor(ouder, sub.stuk), label=_mooi_label(sub.stuk), bereik=bereik)
                db.add(knoop)
                db.flush()
                kinderen.append(knoop)
                per_ouder[knoop.id] = []
                res.nieuw += 1
            elif knoop.bereik != bereik:
                knoop.bereik = bereik
                res.bijgewerkt += 1
            verwerk(sub, knoop)
        _hersorteer(stelsel, kinderen)

    verwerk(wortel, None)
    db.flush()
    return res


def _hersorteer(stelsel: str, kinderen: list[Systematiek]) -> None:
    """Volgorde onder één ouder op het eerste artikel; knopen zonder bereik achteraan, in hun oude volgorde."""
    from .artikelen import parse_bereik

    def k(knoop: Systematiek):
        b = parse_bereik(stelsel, knoop.bereik)
        return (0, b[0], knoop.volgorde or 0) if b else (1, (), knoop.volgorde or 0)

    try:
        geordend = sorted(kinderen, key=k)
    except TypeError:  # onvergelijkbare sleutels (bijv. verschillende boeken): niets doen
        return
    for i, knoop in enumerate(geordend):
        knoop.volgorde = (i + 1) * 10
