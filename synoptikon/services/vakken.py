"""Vakken: bewaren in het vak waar je mee bezig bent, zonder dat je een lijst kiest.

'Project' en 'vak' zijn hetzelfde: een Leerlijst met een `vak` ("ZR Ia", "KartR", …). Bij bewaren bepaalt Synoptikon het vak:
wat je expres koos, anders wat uit het onderwerp volgt (`afleiden`), anders het vak waarin je het laatst bewaarde
(`Profiel.laatste_vak`). Het vak wisselen is een correctie achteraf (`verplaats`), geen voorwaarde vooraf.

De vakken zijn de codes van Wunderkammer (`app/jura/faecher.py`, WiSe 2026/27); Wunderkammer koppelt een lijst aan een
spoor op die code. Dat register is een andere app (andere container), dus staat de lijst hier nog een keer: houd ze gelijk.
"""
from __future__ import annotations

import re

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Kaart, Leerlijst, Profiel
from .artikelen import HOOFDWET
from .notities import LIJST_PREFIX  # lijsten met voorstellen uit notities zijn nooit het doel

# Sinds 02-11-2026 vakken in plaats van modules: Modul W = KapMR + KartR, Modul GÖ = EuGesR, Modul UG = Digi
# (Grundlagen und Grundfragen der Digitalisierung). De oude modulecodes blijven alleen als naam van oude lijsten.
VAKKEN = ("ZR Ia", "KapMR", "KartR", "EuGesR", "Digi", "Sachenrecht")

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


def laatste(db: Session, profiel_id: int) -> str | None:
    p = db.get(Profiel, profiel_id)
    return p.laatste_vak if p is not None else None


def onthoud(db: Session, profiel_id: int, vak: str | None) -> None:
    p = db.get(Profiel, profiel_id)
    if p is not None and vak:
        p.laatste_vak = vak[:60]


def kies(db: Session, profiel_id: int, gekozen: str = "", stelsel: str | None = None, wet: str | None = None,
         nummer: str | None = None) -> str | None:
    """Gekozen vak, anders afgeleid uit het onderwerp, anders het laatst gebruikte (als dat over dit stelsel kan gaan)."""
    if gekozen.strip():
        return gekozen.strip()
    vak = afleiden(stelsel, wet, nummer)
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
