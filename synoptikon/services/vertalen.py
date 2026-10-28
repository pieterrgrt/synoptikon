"""Vertaalgeheugen voor eigen inhoud: welke teksten zijn er, wat is vertaald, wat ontbreekt.

Elke Nederlandse tekst die de app via `vt()` toont, staat hier in
`bronteksten`, met een label en een link naar de plek waar hij staat. De
vertalingen worden op de hash van de Nederlandse tekst bewaard (zie
`i18n.py`); dezelfde tekst op twee plekken (een rol als "hoofdregel")
wordt dus één keer vertaald.

Uitwisselen gaat als JSON {Nederlandse tekst: vertaling}: leesbaar,
onafhankelijk van database-id's, en te gebruiken als seed
(`seed/vertalingen/<taal>.json`).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..i18n import BRONTAAL, TALEN, geheugen, sleutel
from ..models import (
    Antwoord,
    AntwoordBron,
    Begrip,
    BegripRelatie,
    Bron,
    Concordantie,
    Correspondentie,
    CorrespondentieArtikel,
    InhoudVertaling,
    Notitie,
    Omzetting,
    Stelsel,
    Vraag,
)

DOELTALEN = [t for t in TALEN if t != BRONTAAL]
SEED = Path(__file__).resolve().parents[1] / "seed" / "vertalingen"


@dataclass
class Brontekst:
    hash: str
    tekst: str
    soort: str  # "vraag", "analyse", "definitie" …
    waar: str  # korte aanduiding: vraagtitel, term, stelsel
    url: str


def bronteksten(db: Session) -> list[Brontekst]:
    """Alle vertaalbare eigen inhoud, één keer per unieke tekst, in een vaste volgorde."""
    uit: dict[str, Brontekst] = {}

    def neem(tekst: str | None, soort: str, waar: str, url: str) -> None:
        if tekst and tekst.strip():
            h = sleutel(tekst)
            uit.setdefault(h, Brontekst(h, tekst.replace("\r\n", "\n").strip(), soort, waar, url))

    for s in db.scalars(select(Stelsel).order_by(Stelsel.volgorde)):
        neem(s.naam, "stelsel", s.code, f"/stelsels/{s.code}")
        neem(s.toelichting, "stelsel", s.code, f"/stelsels/{s.code}")
    for v in db.scalars(select(Vraag).order_by(Vraag.id).options(selectinload(Vraag.notities))):
        url = f"/vragen/{v.slug}"
        neem(v.titel, "vraag", v.titel, url)
        neem(v.rechtsgebied, "rechtsgebied", v.titel, url)
        for t in v.tag_list:
            neem(t, "tag", v.titel, url)
        neem(v.omschrijving, "omschrijving", v.titel, url)
        for n in v.notities:
            neem(n.tekst, "notitie", v.titel, url)
    for a in db.scalars(select(Antwoord).order_by(Antwoord.vraag_id, Antwoord.stelsel_code).options(selectinload(Antwoord.vraag))):
        url = f"/vragen/{a.vraag.slug}#{a.stelsel_code}"
        neem(a.kern, "kern", f"{a.stelsel_code} · {a.vraag.titel}", url)
        neem(a.analyse, "analyse", f"{a.stelsel_code} · {a.vraag.titel}", url)
    for ab in db.scalars(select(AntwoordBron).order_by(AntwoordBron.id).options(selectinload(AntwoordBron.bron), selectinload(AntwoordBron.antwoord).selectinload(Antwoord.vraag))):
        url = f"/vragen/{ab.antwoord.vraag.slug}#bron-{ab.id}"
        neem(ab.rol, "rol", ab.bron.citeertitel, url)
        neem(ab.notitie, "annotatie", ab.bron.citeertitel, url)
    for b in db.scalars(select(Bron).where(Bron.opmerking.is_not(None)).order_by(Bron.id)):
        neem(b.opmerking, "opmerking", b.citeertitel, f"/bronnen/{b.id}")
    for g in db.scalars(select(Begrip).order_by(Begrip.stelsel_code, Begrip.term)):
        neem(g.definitie, "definitie", f"{g.stelsel_code} · {g.term}", f"/begrippen/{g.id}")
    for r in db.scalars(select(BegripRelatie).order_by(BegripRelatie.id).options(selectinload(BegripRelatie.van), selectinload(BegripRelatie.naar))):
        neem(r.toelichting, "relatie", f"{r.van.term} ↔ {r.naar.term}", f"/begrippen/{r.van_id}")
    for c in db.scalars(select(Correspondentie).order_by(Correspondentie.id)):
        url = f"/artikelen/thema/{c.id}"
        neem(c.titel, "thema", c.titel, url)
        neem(c.rechtsgebied, "rechtsgebied", c.titel, url)
        neem(c.toelichting, "thema", c.titel, url)
    for ca in db.scalars(select(CorrespondentieArtikel).order_by(CorrespondentieArtikel.id)):
        url = f"/artikelen/thema/{ca.correspondentie_id}"
        neem(ca.rol, "rol", ca.stelsel_code, url)
        neem(ca.opmerking, "opmerking", ca.stelsel_code, url)
    for o in db.scalars(select(Omzetting).order_by(Omzetting.id)):
        neem(o.opmerking, "omzetting", o.celex, f"/eu/{o.celex}#omzetting")
    for c in db.scalars(select(Concordantie).order_by(Concordantie.id)):
        neem(c.toelichting, "concordantie", f"{c.oud} {c.wet}", "/concordantie")
    return list(uit.values())


def vertalingen(db: Session, taal: str) -> dict[str, InhoudVertaling]:
    return {v.hash: v for v in db.scalars(select(InhoudVertaling).where(InhoudVertaling.taal == taal))}


def stand(db: Session) -> dict[str, tuple[int, int]]:
    """Per doeltaal: (vertaald, totaal) voor de huidige inhoud."""
    hashes = {b.hash for b in bronteksten(db)}
    uit = {}
    for t in DOELTALEN:
        klaar = set(db.scalars(select(InhoudVertaling.hash).where(InhoudVertaling.taal == t)).all())
        uit[t] = (len(hashes & klaar), len(hashes))
    return uit


def zet(db: Session, taal: str, tekst_nl: str, vertaling: str | None, herkomst: str = "eigen") -> None:
    """Vertaling opslaan, of verwijderen als `vertaling` leeg is."""
    h = sleutel(tekst_nl)
    v = db.get(InhoudVertaling, (h, taal))
    if not (vertaling or "").strip():
        if v is not None:
            db.delete(v)
    elif v is None:
        db.add(InhoudVertaling(hash=h, taal=taal, tekst=vertaling.strip(), herkomst=herkomst))
    else:
        v.tekst, v.herkomst = vertaling.strip(), herkomst
    geheugen.ongeldig()


def ontbrekend(db: Session, taal: str) -> dict[str, str]:
    """{Nederlandse tekst: ""} voor alles wat in `taal` nog ontbreekt; om te vertalen en terug te lezen."""
    klaar = vertalingen(db, taal)
    return {b.tekst: "" for b in bronteksten(db) if b.hash not in klaar}


def laad(db: Session, taal: str, paren: dict[str, str], herkomst: str = "claude", overschrijf: bool = False) -> int:
    """{Nederlandse tekst: vertaling} opslaan. Bestaande vertalingen blijven staan, tenzij `overschrijf`.

    Een zelf ingevoerde of nagekeken vertaling ("eigen") wordt nooit door een machinevertaling overschreven.
    """
    n = 0
    for nl, vertaling in paren.items():
        if not (nl or "").strip() or not (vertaling or "").strip():
            continue
        v = db.get(InhoudVertaling, (sleutel(nl), taal))
        if v is not None and (not overschrijf or (v.herkomst == "eigen" and herkomst != "eigen")):
            continue
        zet(db, taal, nl, vertaling, herkomst)
        n += 1
    return n


def laad_seed(db: Session) -> dict[str, int]:
    uit = {}
    for t in DOELTALEN:
        pad = SEED / f"{t}.json"
        if pad.exists():
            uit[t] = laad(db, t, json.loads(pad.read_text(encoding="utf-8")))
    return uit
