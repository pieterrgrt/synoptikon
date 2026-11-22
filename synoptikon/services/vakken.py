"""Vakken: bewaren in het vak waar je mee bezig bent, zonder dat je een lijst kiest.

'Project' en 'vak' zijn hetzelfde: een Leerlijst met een `vak` ("ZR Ia", "KartR", …). Bij bewaren bepaalt Synoptikon het vak:
wat je expres koos, anders je lopende keuze, anders wat uit het onderwerp volgt (`afleiden`), anders het vak waarin je het
laatst bewaarde (`Profiel.laatste_vak`).

De lopende keuze (sinds 03-11-2026, op Pieters verzoek, wunderkammer#63): wie bewaart, kiest een vak of project, en alles
wat daarna komt hoort daarbij, ook als het onderwerp naar een ander vak wijst, tot je zelf iets anders kiest. Elke keer
bewaren houdt de keuze open (`Profiel.vak_sinds`); na `VENSTER` zonder bewaren vraagt ☆ opnieuw (`actief` is dan None).
Het vak wisselen na het bewaren ('Ander vak', `verplaats`) is ook een nieuwe keuze.

Ieder profiel heeft eigen vakken (`Profiel.vakken`, te wijzigen op /profiel). Die staan in de kiezers van Leren, Leessets
en Klausur, en `afleiden` geeft alleen een vak dat in die lijst staat: § 929 BGB wordt alleen 'Sachenrecht' bij wie dat vak
heeft. Profiel 1 begon met `START`, de codes van Wunderkammer (`app/jura/faecher.py`, WiSe 2026/27); Wunderkammer koppelt
een lijst aan een spoor op die code.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Kaart, Leerlijst, Profiel, now
from .artikelen import HOOFDWET
from .notities import LIJST_PREFIX  # lijsten met voorstellen uit notities zijn nooit het doel

# Sinds 02-11-2026 vakken in plaats van modules: Modul W = KapMR + KartR, Modul GÖ = EuGesR, Modul UG = Digi
# (Grundlagen und Grundfragen der Digitalisierung). De oude modulecodes blijven alleen als naam van oude lijsten.
# Alleen nog de beginstand van profiel 1 (db._NA_KOLOM); de rest leest `van`/`mijn`.
START = ("ZR Ia", "KapMR", "KartR", "EuGesR", "Digi", "Sachenrecht")
MAX_VAKKEN = 30


def van(p: Profiel | None) -> list[str]:
    """De vakken van dit profiel, in de volgorde waarin het ze opgaf."""
    return [v for v in (p.vakken or "").split(",") if v] if p is not None else []


def mijn(db: Session, profiel_id: int) -> list[str]:
    return van(db.get(Profiel, profiel_id))


def lees(tekst: str) -> str | None:
    """Wat iemand op /profiel invult (komma's of regels) als opslag: zonder dubbele, elk hooguit 60 tekens. Leeg = None."""
    gezien: dict[str, str] = {}
    for v in re.split(r"[,\n]", tekst):
        v = " ".join(v.split())[:60]
        if v and v.lower() not in gezien and len(gezien) < MAX_VAKKEN:
            gezien[v.lower()] = v
    return ",".join(gezien.values()) or None


def _eigen(vak: str | None, lijst: list[str]) -> str | None:
    """Het afgeleide vak in de schrijfwijze van het profiel, of None als het profiel dat vak niet heeft."""
    return next((v for v in lijst if vak and v.lower() == vak.lower()), None)

# Het laatst gebruikte vak geldt niet over de grens tussen EU-recht en nationaal recht: een arrest na § 929 BGB wordt niet
# Sachenrecht. Vergelijken tussen nationale stelsels mag wel. (Kartell-, kapitaalmarkt- en digitaal recht zijn zowel EU als
# nationaal, dus daar geldt geen grens.)
_ALLEEN_EU: set[str] = set()
_NIET_EU = {"ZR Ia", "Sachenrecht"}

# Bereiken van BGB-paragrafen: Allgemeiner Teil (ZR Ia), digitale Produkte (§§ 327-327u, Digi) en Sachenrecht.
_BGB = [(1, 240, "ZR Ia"), (327, 327, "Digi"), (854, 1296, "Sachenrecht")]
# Duitse wetten die bij één vak horen.
_DE_WET = {"GWB": "KartR", "WPHG": "KapMR", "WPPG": "KapMR", "WPÜG": "KapMR", "BÖRSG": "KapMR", "KAGB": "KapMR",
           "URHG": "Digi", "URHDAG": "Digi", "DDG": "Digi", "TTDSG": "Digi", "TDDDG": "Digi"}
_EU_VERDRAG = {"AEUV", "VWEU", "TFEU", "TFUE"}
_KARTELL = range(101, 110)  # Art. 101-109 AEUV: mededinging en staatssteun


def afleiden(stelsel: str | None, wet: str | None = None, nummer: str | None = None) -> str | None:
    """Het vak waar dit onderwerp 'vanzelf' bij hoort, of None als dat niet volgt. Een arrest geeft alleen zijn stelsel."""
    stelsel = (stelsel or "").upper()
    wet = (wet or HOOFDWET.get(stelsel) or "").upper()
    if stelsel == "DE" and wet == "BGB" and nummer:
        m = re.match(r"\d+", nummer.strip().lstrip("§ "))
        if m:
            n = int(m.group())
            return next((v for lo, hi, v in _BGB if lo <= n <= hi), None)
    if stelsel == "DE" and wet in _DE_WET:
        return _DE_WET[wet]
    if stelsel == "EU" and nummer and wet in _EU_VERDRAG:
        m = re.match(r"\d+", nummer.strip().lstrip("Art. "))
        if m and int(m.group()) in _KARTELL:
            return "KartR"
    return None


VENSTER = timedelta(hours=2)  # 'net een ander artikel bewaard': binnen dit venster geldt de keuze zonder te vragen


def actief_van(p: Profiel | None, nu: datetime | None = None) -> str | None:
    """De lopende keuze van dit profiel, of None als die er niet is of het venster voorbij is."""
    if p is None or not p.laatste_vak or p.vak_sinds is None:
        return None
    # SQLite geeft de tijd zonder zone terug; beide in UTC, dus zonder zone vergelijken.
    verstreken = (nu or now()).replace(tzinfo=None) - p.vak_sinds.replace(tzinfo=None)
    return p.laatste_vak if verstreken <= VENSTER else None


def actief(db: Session, profiel_id: int) -> str | None:
    return actief_van(db.get(Profiel, profiel_id))


def laatste(db: Session, profiel_id: int) -> str | None:
    p = db.get(Profiel, profiel_id)
    return p.laatste_vak if p is not None else None


def onthoud(db: Session, profiel_id: int, vak: str | None) -> None:
    p = db.get(Profiel, profiel_id)
    if p is not None and vak:
        p.laatste_vak = vak[:60]
        p.vak_sinds = now()


def kies(db: Session, profiel_id: int, gekozen: str = "", stelsel: str | None = None, wet: str | None = None,
         nummer: str | None = None) -> str | None:
    """Gekozen vak, anders de lopende keuze, anders afgeleid uit het onderwerp (als het profiel dat vak heeft), anders het laatst gebruikte (als dat over
    dit stelsel kan gaan). De lopende keuze kent geen grens tussen EU en nationaal: die koos je zelf."""
    if gekozen.strip():
        return gekozen.strip()[:60]
    if lopend := actief(db, profiel_id):
        return lopend
    vak = _eigen(afleiden(stelsel, wet, nummer), mijn(db, profiel_id))
    if vak:
        return vak
    vorig = laatste(db, profiel_id)
    eu = (stelsel or "").upper() == "EU"
    if stelsel and ((vorig in _ALLEEN_EU and not eu) or (vorig in _NIET_EU and eu)):
        return None
    return vorig


def lijst_voor(db: Session, profiel_id: int, vak: str) -> Leerlijst:
    """De leerlijst van een vak: de oudste die dat vak heeft (niet de notitielijsten), anders een nieuwe die naar het vak heet."""
    lijst = db.scalar(select(Leerlijst).where(
        Leerlijst.profiel_id == profiel_id, func.lower(Leerlijst.vak) == vak.lower(),
        ~Leerlijst.naam.startswith(LIJST_PREFIX)).order_by(Leerlijst.id))
    if lijst is None:
        lijst = Leerlijst(profiel_id=profiel_id, naam=vak, vak=vak, naar_wk=True)
        db.add(lijst)
        db.flush()
    return lijst


def verplaats(db: Session, profiel_id: int, kaarten: list[Kaart], vak: str) -> Leerlijst:
    """Zet kaarten over naar de lijst van een ander vak (de correctie na bewaren) en onthoudt dat vak."""
    doel = lijst_voor(db, profiel_id, vak.strip())
    for k in kaarten:
        k.lijst = doel
    onthoud(db, profiel_id, doel.vak)
    return doel
