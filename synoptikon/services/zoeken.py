"""Full-text zoeken over vragen, bronnen, begrippen, analyses en wetteksten."""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from sqlalchemy import text
from sqlalchemy.orm import Session

from ..models import Antwoord, Begrip, Bron, Vraag, WettekstArtikel

_TOKEN = re.compile(r"[\w§:\-\.]+", re.UNICODE)


def fts_query(q: str) -> str:
    """Zet vrije invoer om in een veilige FTS5-MATCH-expressie.

    Elke term wordt een prefixzoekterm tussen aanhalingstekens, zodat
    "3:84" of "§ 929" geen syntaxfouten geven en "lever" ook "levering" vindt.
    """
    termen = [t.strip('"').strip() for t in _TOKEN.findall(q)]
    termen = [t for t in termen if t]
    if not termen:
        return ""
    return " ".join(f'"{t}"*' for t in termen)


@dataclass
class Treffer:
    soort: str  # vraag | bron | begrip | antwoord | wettekst
    titel: str
    snippet: str
    url: str
    stelsel: str | None = None
    extra: str | None = None


@dataclass
class Zoekresultaat:
    q: str
    vragen: list[Treffer] = field(default_factory=list)
    bronnen: list[Treffer] = field(default_factory=list)
    begrippen: list[Treffer] = field(default_factory=list)
    antwoorden: list[Treffer] = field(default_factory=list)
    wetteksten: list[Treffer] = field(default_factory=list)

    @property
    def aantal(self) -> int:
        return len(self.vragen) + len(self.bronnen) + len(self.begrippen) + len(self.antwoorden) + len(self.wetteksten)


_SNIP = "snippet({tabel}, {kolom}, '<mark>', '</mark>', '…', 24)"


def zoek(db: Session, q: str, limiet: int = 30) -> Zoekresultaat:
    res = Zoekresultaat(q=q)
    match = fts_query(q)
    if not match:
        return res

    rows = db.execute(
        text(
            "SELECT rowid, " + _SNIP.format(tabel="vraag_fts", kolom=1) + " AS s "
            "FROM vraag_fts WHERE vraag_fts MATCH :m ORDER BY rank LIMIT :l"
        ),
        {"m": match, "l": limiet},
    ).all()
    for rowid, snippet in rows:
        v = db.get(Vraag, rowid)
        if v:
            res.vragen.append(Treffer("vraag", v.titel, snippet or "", f"/vragen/{v.slug}", extra=v.rechtsgebied))

    rows = db.execute(
        text(
            "SELECT rowid, " + _SNIP.format(tabel="bron_fts", kolom=2) + " AS s "
            "FROM bron_fts WHERE bron_fts MATCH :m ORDER BY rank LIMIT :l"
        ),
        {"m": match, "l": limiet},
    ).all()
    for rowid, snippet in rows:
        b = db.get(Bron, rowid)
        if b:
            res.bronnen.append(Treffer("bron", b.citeertitel, snippet or "", f"/bronnen/{b.id}", b.stelsel_code, b.titel))

    rows = db.execute(
        text(
            "SELECT rowid, " + _SNIP.format(tabel="begrip_fts", kolom=1) + " AS s "
            "FROM begrip_fts WHERE begrip_fts MATCH :m ORDER BY rank LIMIT :l"
        ),
        {"m": match, "l": limiet},
    ).all()
    for rowid, snippet in rows:
        g = db.get(Begrip, rowid)
        if g:
            res.begrippen.append(Treffer("begrip", g.term, snippet or "", f"/begrippen/{g.id}", g.stelsel_code))

    rows = db.execute(
        text(
            "SELECT rowid, " + _SNIP.format(tabel="antwoord_fts", kolom=1) + " AS s "
            "FROM antwoord_fts WHERE antwoord_fts MATCH :m ORDER BY rank LIMIT :l"
        ),
        {"m": match, "l": limiet},
    ).all()
    for rowid, snippet in rows:
        a = db.get(Antwoord, rowid)
        if a:
            res.antwoorden.append(
                Treffer("antwoord", a.vraag.titel, snippet or "", f"/vragen/{a.vraag.slug}#{a.stelsel_code}", a.stelsel_code)
            )

    rows = db.execute(
        text(
            "SELECT rowid, " + _SNIP.format(tabel="wettekst_artikel_fts", kolom=2) + " AS s "
            "FROM wettekst_artikel_fts WHERE wettekst_artikel_fts MATCH :m ORDER BY rank LIMIT :l"
        ),
        {"m": match, "l": limiet},
    ).all()
    for rowid, snippet in rows:
        wa = db.get(WettekstArtikel, rowid)
        if wa:
            res.wetteksten.append(
                Treffer(
                    "wettekst",
                    f"{wa.wettekst.titel} {wa.nummer}",
                    snippet or "",
                    f"/wetteksten/{wa.wettekst_id}#{wa.nummer}",
                    wa.wettekst.stelsel_code,
                    wa.opschrift,
                )
            )
    return res
