"""Full-text zoeken over vragen, bronnen, begrippen, analyses en wetteksten."""
from __future__ import annotations

import logging
import re
import time
import unicodedata
from bisect import bisect_right
from dataclasses import dataclass, field

from markupsafe import escape
from sqlalchemy import bindparam, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, selectinload

from ..i18n import BRONTAAL, taal, vt
from ..models import Antwoord, Begrip, Bron, Vraag, WettekstArtikel
from .artikelen import Ref, herken

log = logging.getLogger(__name__)

_TOKEN = re.compile(r"[\w§:\-\.]+", re.UNICODE)


def _prefix(t: str) -> bool:
    """Alleen gewone woorden van vier letters of meer als prefix ("lever" → "levering"); getallen en afkortingen
    precies ("GG" is niet "GGED", "1" is niet "1240"). Een kort prefix doorloopt bovendien half de index."""
    return t.isalpha() and len(t) >= 4 and not t.isupper()


def fts_query(q: str, nabij: bool = False) -> str:
    """Zet vrije invoer om in een veilige FTS5-MATCH-expressie.

    Elke term komt tussen aanhalingstekens, zodat "3:84" of "§ 929" geen syntaxfouten geven; woorden worden een
    prefix (zie `_prefix`). `nabij`: alle termen dicht bij elkaar (een verwijzing als "Art. 1 GG" in de tekst van
    een ander artikel) in plaats van ergens in het artikel.
    """
    termen = [t.strip('"').strip() for t in _TOKEN.findall(q)]
    termen = [t for t in termen if re.search(r"\w", t)]  # aan "§" alleen heeft de tokenizer niets
    if not termen:
        return ""
    delen = [f'"{t}"*' if _prefix(t) else f'"{t}"' for t in termen]
    if nabij and len(delen) > 1:
        return f"NEAR({' '.join(delen)}, 6)"
    return " ".join(delen)


# --- bij welke wet hoort een artikel -------------------------------------------------------------------------------
# De artikelen van één wettekst krijgen bij het importeren opeenvolgende id's (importers/store.py). Daarom komt de wet
# van een FTS-treffer uit het geheugen (`wet_van`, als SQL-functie op elke verbinding, zie db.py) in plaats van uit
# een opzoeking in de grote tabel wettekst_artikel per treffer: de zoekquery filtert en sorteert op stelsel en kern
# zonder de artikelen zelf te lezen. Na een import worden de reeksen bijgewerkt (`reeksen`).

_REEKSEN: tuple[tuple, list[int], list[int], list[int]] = ((), [], [], [])  # stand, begin, eind, wettekst-id


def wet_van(rowid: int | None) -> int | None:
    _stand, begin, eind, wet = _REEKSEN
    if rowid is None:
        return None
    i = bisect_right(begin, rowid) - 1
    return wet[i] if i >= 0 and rowid <= eind[i] else None


def reeksen(db: Session) -> None:
    """Werkt de reeksen bij als er artikelen of wetten bij- of afgekomen zijn (de controle kost drie indexopzoekingen)."""
    global _REEKSEN
    stand = tuple(db.execute(text("SELECT (SELECT max(id) FROM wettekst_artikel), (SELECT count(*) FROM wettekst), "
                                  "(SELECT max(id) FROM wettekst)")).one())
    oud, begin, eind, wet = _REEKSEN
    if stand == oud:
        return
    vanaf = 0
    # Alleen artikelen bij (het hoogste oude id bestaat nog, dus geen id is hergebruikt): de oude reeksen kloppen nog;
    # die van verwijderde artikelen doen er niet toe, want die vindt de FTS-index niet meer.
    if oud and oud[0] and stand[0] and stand[0] > oud[0] and db.scalar(text("SELECT 1 FROM wettekst_artikel WHERE id = :i"), {"i": oud[0]}):
        vanaf = oud[0]
    else:
        begin, eind, wet = [], [], []
    nieuw = []
    for wid, lo, hi, n in db.execute(text("SELECT wettekst_id, min(id), max(id), count(*) FROM wettekst_artikel WHERE id > :v "
                                          "GROUP BY wettekst_id"), {"v": vanaf}).all():
        if hi - lo + 1 == n:
            nieuw.append((lo, hi, wid))
            continue
        # Niet aaneengesloten (zeldzaam): in stukken.
        ids = db.scalars(text("SELECT id FROM wettekst_artikel WHERE wettekst_id = :w AND id > :v ORDER BY id"), {"w": wid, "v": vanaf}).all()
        lo = vorig = ids[0]
        for i in ids[1:]:
            if i != vorig + 1:
                nieuw.append((lo, vorig, wid))
                lo = i
            vorig = i
        nieuw.append((lo, vorig, wid))
    samen = sorted([*zip(begin, eind, wet), *nieuw])
    _REEKSEN = (stand, [r[0] for r in samen], [r[1] for r in samen], [r[2] for r in samen])


# Hoe lang de full-text in de wetteksten mag duren voor er een goedkopere zoekopdracht voor in de plaats komt.
BUDGET = 1.0


def _met_budget(db: Session, stmt, params: dict, budget: float):
    """Voert een query uit en breekt hem af na `budget` seconden (sqlite3-progress-handler); None bij afbreken."""
    raw = db.connection().connection.driver_connection
    einde = time.monotonic() + budget
    raw.set_progress_handler(lambda: time.monotonic() > einde, 20000)
    try:
        return db.execute(stmt, params).all()
    except OperationalError as e:
        if "interrupt" not in str(e):
            raise
        return None
    finally:
        raw.set_progress_handler(None, 0)


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
                  wettekst_id: int | None = None, stelsels: list[str] | None = None,
                  voorkeur: list[str] | None = None) -> list[tuple[WettekstArtikel, str]]:
    """Artikelen waarvan nummer, opschrift of tekst de woorden bevat, met een fragment.

    De wetten uit het register (BGB, BW, Code civil …) eerst, dan de stelsels in `voorkeur` (die van de gebruiker),
    dan op relevantie (bm25: een treffer in het opschrift telt zwaarder dan in de tekst). `stelsel` of `stelsels`
    beperkt tot die stelsels (None = alle), `wet` tot één afkorting (GG, StGB), `wettekst_id` tot één geïmporteerde
    tekst. Een artikelverwijzing ("Art. 1 GG") zoekt naar artikelen die haar noemen: de termen dicht bij elkaar.

    Eerst de id's (alleen de FTS-index en de kleine tabel wettekst), dan de fragmenten en artikelen van die ene
    pagina. Duurt het langer dan `BUDGET`, dan zonder relevantie (in volgorde van de index).
    """
    match = fts_query(q, nabij=bool(herken(q)))
    if not match:
        return []
    reeksen(db)
    codes = [stelsel] if stelsel else list(stelsels or [])
    waar = ["wettekst_artikel_fts MATCH :m"]
    params: dict = {"m": match, "l": limiet, "o": vanaf}
    if codes:
        waar.append("w.stelsel_code IN :codes")
        params["codes"] = codes
    if wet:
        waar.append("w.wet = :wet")
        params["wet"] = wet
    if wettekst_id:
        waar.append("w.id = :wid")
        params["wid"] = wettekst_id
        _s, begin, eind, wetten = _REEKSEN
        stukken = [(b, e) for b, e, w in zip(begin, eind, wetten) if w == wettekst_id]
        if len(stukken) == 1:  # dan beperkt de FTS-index zelf al tot de artikelen van deze wet
            waar.append("wettekst_artikel_fts.rowid BETWEEN :lo AND :hi")
            params.update(lo=stukken[0][0], hi=stukken[0][1])
    voor = list(voorkeur or [])
    orde = "w.kern DESC, " + ("w.stelsel_code IN :voor DESC, " if voor else "")
    if voor:
        params["voor"] = voor
    sql = ("SELECT wettekst_artikel_fts.rowid FROM wettekst_artikel_fts JOIN wettekst w ON w.id = wet_van(wettekst_artikel_fts.rowid) WHERE " + " AND ".join(waar)
           + " ORDER BY " + orde + "{rang} LIMIT :l OFFSET :o")

    def stmt(rang: str):
        s = text(sql.format(rang=rang))
        for naam in ("codes", "voor"):
            if naam in params:
                s = s.bindparams(bindparam(naam, expanding=True))
        return s

    rijen = _met_budget(db, stmt("bm25(wettekst_artikel_fts, 2.0, 4.0, 1.0)"), params, BUDGET)
    if rijen is None:
        log.info("wetsartikelen %r: boven het budget, zonder relevantie", q)
        rijen = _met_budget(db, stmt("wettekst_artikel_fts.rowid"), params, BUDGET) or []
    ids = [r[0] for r in rijen]
    if not ids:
        return []
    fragment = dict(db.execute(
        text("SELECT rowid, " + _SNIP.format(tabel="wettekst_artikel_fts", kolom=2) + " FROM wettekst_artikel_fts "
             "WHERE wettekst_artikel_fts MATCH :m AND rowid IN :ids").bindparams(bindparam("ids", expanding=True)),
        {"m": match, "ids": ids}).all())
    artikelen = {wa.id: wa for wa in db.scalars(select(WettekstArtikel).where(WettekstArtikel.id.in_(ids))
                                                .options(selectinload(WettekstArtikel.wettekst)))}
    return [(artikelen[i], fragment.get(i) or "") for i in ids if i in artikelen]


def zoek(db: Session, q: str, limiet: int = 30, stelsel: str = "", stelsels: list[str] | None = None,
         wetteksten: bool = True) -> Zoekresultaat:
    """Full-text in alles. `stelsel` of `stelsels` beperkt de bronnen, begrippen, analyses en wetteksten tot die
    stelsels (None of leeg = alle); EU-handelingen alleen als EU erbij is. `wetteksten`: ook de wetsartikelen."""
    res = Zoekresultaat(q=q)
    match = fts_query(q)
    if not match:
        return res
    codes = [stelsel] if stelsel else list(stelsels or [])
    params = {"m": match, "l": limiet, "codes": codes}

    def beperk(sql: str, tabel: str):
        if codes:
            sql = sql.replace(" ORDER BY", f" AND rowid IN (SELECT id FROM {tabel} WHERE stelsel_code IN :codes) ORDER BY")
        s = text(sql)
        return s.bindparams(bindparam("codes", expanding=True)) if codes else s

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
        beperk(
            "SELECT rowid, " + _SNIP.format(tabel="bron_fts", kolom=2) + " AS s "
            "FROM bron_fts WHERE bron_fts MATCH :m ORDER BY rank LIMIT :l", "bron"
        ),
        params,
    ).all()
    for rowid, snippet in rows:
        b = db.get(Bron, rowid)
        if b:
            res.bronnen.append(Treffer("bron", b.citeertitel, snippet or "", f"/bronnen/{b.id}", b.stelsel_code, b.titel))

    rows = db.execute(
        beperk(
            "SELECT rowid, " + _SNIP.format(tabel="begrip_fts", kolom=1) + " AS s "
            "FROM begrip_fts WHERE begrip_fts MATCH :m ORDER BY rank LIMIT :l", "begrip"
        ),
        params,
    ).all()
    for rowid, snippet in rows:
        g = db.get(Begrip, rowid)
        if g:
            res.begrippen.append(Treffer("begrip", g.term, snippet or "", f"/begrippen/{g.id}", g.stelsel_code))

    rows = db.execute(
        beperk(
            "SELECT rowid, " + _SNIP.format(tabel="antwoord_fts", kolom=1) + " AS s "
            "FROM antwoord_fts WHERE antwoord_fts MATCH :m ORDER BY rank LIMIT :l", "antwoord"
        ),
        params,
    ).all()
    for rowid, snippet in rows:
        a = db.get(Antwoord, rowid)
        if a:
            res.antwoorden.append(
                Treffer("antwoord", vt(a.vraag.titel), snippet or "", f"/vragen/{a.vraag.slug}#{a.stelsel_code}", a.stelsel_code)
            )

    for wa, snippet in (wetsartikelen(db, q, stelsel, limiet, stelsels=stelsels) if wetteksten else []):
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

    for h in (eu.zoek(db, q, per_pagina=10, tel=False)[0] if not codes or "EU" in codes else []):
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
