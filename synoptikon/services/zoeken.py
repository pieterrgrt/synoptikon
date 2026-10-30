"""Full-text zoeken over vragen, bronnen, begrippen, analyses en wetteksten."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from markupsafe import escape
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..i18n import BRONTAAL, taal, vt
from ..models import Antwoord, Begrip, Bron, Vraag, WettekstArtikel
from .artikelen import Ref

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
    vertalingen: list[Treffer] = field(default_factory=list)  # eigen inhoud, gevonden in de vertaling
    eu: list[Treffer] = field(default_factory=list)

    @property
    def aantal(self) -> int:
        return sum(len(x) for x in (self.vragen, self.bronnen, self.begrippen, self.antwoorden, self.wetteksten, self.vertalingen, self.eu))


_SNIP = "snippet({tabel}, {kolom}, '<mark>', '</mark>', '…', 24)"


def wetsartikelen(db: Session, q: str, stelsel: str = "", limiet: int = 40, wet: str | None = None, vanaf: int = 0,
                  wettekst_id: int | None = None) -> list[tuple[WettekstArtikel, str]]:
    """Artikelen waarvan nummer, opschrift of tekst de woorden bevat, met een fragment.

    De wetten uit het register (BGB, BW, Code civil …) eerst, dan de rest; `wet` beperkt tot één afkorting (GG, StGB),
    `wettekst_id` tot één geïmporteerde tekst.
    """
    match = fts_query(q)
    if not match:
        return []
    rows = db.execute(
        text(
            "SELECT wettekst_artikel_fts.rowid, " + _SNIP.format(tabel="wettekst_artikel_fts", kolom=2) + " AS s "
            "FROM wettekst_artikel_fts JOIN wettekst_artikel a ON a.id = wettekst_artikel_fts.rowid JOIN wettekst w ON w.id = a.wettekst_id "
            "WHERE wettekst_artikel_fts MATCH :m AND (:st = '' OR w.stelsel_code = :st) AND (:wet = '' OR w.wet = :wet) AND (:wid = 0 OR w.id = :wid) "
            "ORDER BY w.kern DESC, rank LIMIT :l OFFSET :o"
        ),
        {"m": match, "st": stelsel, "wet": wet or "", "wid": wettekst_id or 0, "l": limiet, "o": vanaf},
    ).all()
    uit = []
    for rowid, snippet in rows:
        wa = db.get(WettekstArtikel, rowid)
        if wa:
            uit.append((wa, snippet or ""))
    return uit


def zoek(db: Session, q: str, limiet: int = 30, stelsel: str = "") -> Zoekresultaat:
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
            res.vragen.append(Treffer("vraag", vt(v.titel), snippet or "", f"/vragen/{v.slug}", extra=vt(v.rechtsgebied)))

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
                Treffer("antwoord", vt(a.vraag.titel), snippet or "", f"/vragen/{a.vraag.slug}#{a.stelsel_code}", a.stelsel_code)
            )

    for wa, snippet in wetsartikelen(db, q, stelsel, limiet):
        res.wetteksten.append(
            Treffer(
                "wettekst",
                f"{Ref(wa.wettekst.stelsel_code, wa.nummer, wa.wettekst.wet).citeer}",
                snippet,
                Ref(wa.wettekst.stelsel_code, wa.nummer, wa.wettekst.wet).url,
                wa.wettekst.stelsel_code,
                wa.opschrift,
            )
        )
    res.vertalingen = _in_vertalingen(db, q, limiet)
    from . import eu

    for h in eu.zoek(db, q, per_pagina=10)[0]:
        res.eu.append(Treffer("eu", h.roepnaam or h.citeer, escape(h.toon_titel[:240]), f"/eu/{h.celex}", "EU", h.soort_label))
    return res


def _vouw(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.casefold()) if not unicodedata.combining(c))


def _in_vertalingen(db: Session, q: str, limiet: int) -> list[Treffer]:
    """Eigen inhoud waarvan de vertaling in de taal van het verzoek alle woorden bevat (accent- en hoofdletterongevoelig)."""
    t = taal()
    if t == BRONTAAL:
        return []
    from .vertalen import bronteksten, vertalingen

    woorden = [_vouw(w) for w in re.findall(r"\w+", q)]
    if not woorden:
        return []
    klaar = vertalingen(db, t)
    uit = []
    for b in bronteksten(db):
        v = klaar.get(b.hash)
        if v is None:
            continue
        gevouwen = _vouw(v.tekst)
        if all(w in gevouwen for w in woorden):
            i = gevouwen.find(woorden[0])
            fragment = v.tekst[max(0, i - 60): i + 140]
            uit.append(Treffer(b.soort, vt(b.waar) or b.waar, escape(("…" if i > 60 else "") + fragment + "…"), b.url))
            if len(uit) >= limiet:
                break
    return uit
