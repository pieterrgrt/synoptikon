"""Wat er aan wetteksten in de kast staat: de bibliotheek, per rechtsfamilie en per stelsel.

Dit voedt het overzicht op de hoofdpagina (`templates/_bibliotheek.html`): een boekenkast met een schap per
rechtsfamilie en een rug per wet, en een wereldkaart waarin elk stelsel getint is naar hoeveel ervan is opgeslagen.

Twee dingen om in het oog te houden.

* **De verdeling is extreem scheef.** EU 17.589 wetten tegenover 31 voor de hele Romaanse familie, terwijl Frankrijk
  met 3 wetten meer artikelen heeft dan Nederland met 642. Daarom is de maat **artikelen**, niet wetten, en loopt de
  breedte van een rug met de *wortel* van het aantal artikelen: anders is één rug het hele schap en zijn de andere
  onzichtbaar.
* **EU-wetten staan er in meer talen.** `Wettekst.wet_id` zonder punt is de hoofdversie, met punt (`12016E.nl`) een
  taalvariant van dezelfde handeling. Die tellen niet mee, anders staan de drie verdragen er zesmaal in.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..i18n import _
from ..models import RECHTSFAMILIES, Stelsel, Wettekst, WettekstArtikel
from .artikelen import wet_kort

# Zoveel ruggen per schap; wat er niet op past wordt één '+ N meer'-rug.
RUGGEN = 14
# De grootste wetten op de hoofdpagina, over alle stelsels heen.
GROOTSTE = 8


def _hoofdversies():
    """Alleen de hoofdversie van een wet: EU-taalvarianten (`12016E.nl`) zijn dezelfde handeling."""
    return (Wettekst.stelsel_code != "EU") | ~Wettekst.wet_id.like("%.%")


@dataclass
class Rug:
    """Eén wet in de kast."""

    stelsel: str
    wet_id: str
    naam: str          # de afkorting als die er is, anders de titel
    titel: str
    artikelen: int
    wettekst_id: int
    breedte: float = 0.0   # breedte van de rug in rem, door `_bouw` gezet

    @property
    def url(self) -> str:
        return f"/wetteksten/{self.wettekst_id}"


@dataclass
class Schap:
    """Eén rechtsfamilie."""

    sleutel: str
    naam: str
    omschrijving: str
    stelsels: list[str] = field(default_factory=list)
    wetten: int = 0
    artikelen: int = 0
    ruggen: list[Rug] = field(default_factory=list)

    @property
    def rest(self) -> int:
        """Wetten die niet als rug op het schap passen."""
        return max(0, self.wetten - len(self.ruggen))


@dataclass
class Land:
    """Eén stelsel, voor de wereldkaart en de legenda."""

    code: str
    naam: str
    familie: str | None
    familie_naam: str
    wetten: int
    artikelen: int
    tint: float = 0.0      # hoe vol op de kaart, 0..1

    @property
    def leeg(self) -> bool:
        return self.artikelen == 0


@dataclass
class Overzicht:
    wetten: int = 0
    artikelen: int = 0
    stelsels: int = 0          # stelsels met tekst
    stelsels_totaal: int = 0
    schappen: list[Schap] = field(default_factory=list)
    landen: list[Land] = field(default_factory=list)
    grootste: list[Rug] = field(default_factory=list)

    @property
    def leeg(self) -> bool:
        return self.artikelen == 0


_cache: dict = {}


def overzicht(db: Session, vernieuw: bool = False) -> Overzicht:
    """De hele bibliotheek in één keer. Tellen over 350.000 artikelen kost te veel voor elke paginaweergave, dus het
    blijft staan tot er een wet of artikel bijkomt (de hoogste id's) of na tien minuten — net als `stelselkeuze`."""
    sleutel = (db.scalar(select(func.max(Wettekst.id))), db.scalar(select(func.max(WettekstArtikel.id))))
    if not vernieuw and _cache.get("sleutel") == sleutel and time.monotonic() - _cache.get("tijd", 0) < 600:
        return _cache["waarde"]
    waarde = _bouw(db)
    _cache.update(sleutel=sleutel, tijd=time.monotonic(), waarde=waarde)
    return waarde


def _bouw(db: Session) -> Overzicht:
    stelsels = {s.code: s for s in db.scalars(select(Stelsel)).all()}

    # Per wet: hoeveel artikelen, en welke wettekst om naar te verwijzen.
    rijen = db.execute(
        select(Wettekst.stelsel_code, Wettekst.wet_id, Wettekst.wet, Wettekst.titel,
               func.min(Wettekst.id), func.count(WettekstArtikel.id))
        .join(WettekstArtikel, WettekstArtikel.wettekst_id == Wettekst.id)
        .where(_hoofdversies())
        .group_by(Wettekst.stelsel_code, Wettekst.wet_id)).all()

    per_stelsel: dict[str, list[Rug]] = {}
    for code, wet_id, wet, titel, wtid, n in rijen:
        naam = wet_kort(code, wet) or (titel or wet_id)
        per_stelsel.setdefault(code, []).append(
            Rug(stelsel=code, wet_id=wet_id, naam=naam, titel=titel or naam, artikelen=n, wettekst_id=wtid))

    uit = Overzicht(stelsels_totaal=len(stelsels))
    for code, ruggen in per_stelsel.items():
        uit.wetten += len(ruggen)
        uit.artikelen += sum(r.artikelen for r in ruggen)
    uit.stelsels = sum(1 for ruggen in per_stelsel.values() if ruggen)

    # Landen: alle stelsels, ook de lege — op de kaart zijn die een omtrek zonder vulling.
    for code, s in sorted(stelsels.items(), key=lambda kv: -sum(r.artikelen for r in per_stelsel.get(kv[0], []))):
        ruggen = per_stelsel.get(code, [])
        uit.landen.append(Land(code=code, naam=s.naam, familie=s.familie, familie_naam=s.familie_naam,
                               wetten=len(ruggen), artikelen=sum(r.artikelen for r in ruggen)))

    # Schappen in de orde van de taxonomie, niet op grootte: een boekenkast is geen ranglijst.
    for sleutel, (naam, omschrijving) in RECHTSFAMILIES.items():
        codes = [c for c, s in stelsels.items() if s.familie == sleutel]
        ruggen = sorted((r for c in codes for r in per_stelsel.get(c, [])), key=lambda r: -r.artikelen)
        if not ruggen:
            continue
        uit.schappen.append(Schap(
            sleutel=sleutel, naam=_(naam), omschrijving=_(omschrijving),
            stelsels=[c for c in codes if per_stelsel.get(c)],
            wetten=len(ruggen), artikelen=sum(r.artikelen for r in ruggen), ruggen=ruggen[:RUGGEN]))

    alle = [r for rs in per_stelsel.values() for r in rs]
    uit.grootste = sorted(alle, key=lambda r: -r.artikelen)[:GROOTSTE]

    # Maten voor de weergave hier, niet in de template: die hoeft niet te rekenen.
    grootste_wet = max((r.artikelen for r in alle), default=0)
    for r in alle:
        r.breedte = rugbreedte(r.artikelen, grootste_wet)
    # De tint normeren op het grootste *land*, niet op de EU: die is supranationaal en staat op de kaart als ring
    # om de lidstaten, niet als gevuld land. Normeren op 147.301 EU-artikelen zou elk land te licht maken.
    grootste_land = max((l.artikelen for l in uit.landen if l.familie != "supranationaal"), default=0)
    for l in uit.landen:
        l.tint = tint(l.artikelen, grootste_land)
    return uit


# --- maten voor de weergave ---------------------------------------------------------------------------------------


@lru_cache(maxsize=1)
def kaart() -> dict:
    """De wereldkaart: `{breedte, hoogte, landen: {code: svg-pad}}`, gebouwd door `scripts/bouw_wereldkaart.py`.

    Een bestand van 68 kB dat zelden verandert, dus één keer inlezen per proces. Ontbreekt het, dan geeft dit een
    leeg resultaat en laat de template de kaart weg; de boekenkast werkt dan nog.
    """
    bestand = Path(__file__).resolve().parents[1] / "static" / "kaart" / "wereld.json"
    try:
        d = json.loads(bestand.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(breedte=0, hoogte=0, landen={})
    return d


def rugbreedte(artikelen: int, grootste: int, min_rem: float = 1.6, max_rem: float = 5.0) -> float:
    """De breedte van een rug in rem: met de wortel van het aantal artikelen, zodat de staart zichtbaar blijft.

    Code de commerce (7.254 artikelen) is 2.300 keer zo groot als een wet van 3 artikelen; lineair zou de kleine een
    haarlijn zijn. Met de wortel wordt dat een factor 49, en met de ondergrens erbij blijft elke rug leesbaar.
    """
    if artikelen <= 0 or grootste <= 0:
        return min_rem
    deel = (artikelen / grootste) ** 0.5
    return round(min_rem + (max_rem - min_rem) * deel, 2)


# Onder deze dekking is een land op papier niet meer van leeg te onderscheiden.
TINT_ONDER = 0.2


def tint(artikelen: int, grootste: int) -> float:
    """Hoe vol een land op de kaart is, 0..1, op de wortel. Precies 0 betekent: niets opgeslagen.

    Alles wat er wél is krijgt minstens `TINT_ONDER`: Engeland & Wales (595 artikelen naast Duitsland met 107.000)
    zou anders een tint van 0,07 krijgen en op de kaart niet te onderscheiden zijn van een leeg stelsel — terwijl
    juist dat onderscheid de kaart moet laten zien.
    """
    if artikelen <= 0 or grootste <= 0:
        return 0.0
    return round(max(TINT_ONDER, min(1.0, (artikelen / grootste) ** 0.5)), 3)
