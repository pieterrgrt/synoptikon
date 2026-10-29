"""Mijn stelsels: welke stelsels een profiel ziet.

De vlag `Stelsel.actief` is van de beheerder ("beschikbaar in de app"); de keuze per profiel (`Profiel.stelsels`, te
zetten op /profiel) bepaalt wat in kiezers, filters en kolommen staat. De andere actieve stelsels staan op elke pagina
onder een uitklap 'meer stelsels…', per regio (seed/regios.py). Een profiel zonder keuze ziet alles, zoals vroeger.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from fastapi import Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..i18n import _
from ..models import Stelsel, Wettekst, WettekstArtikel
from ..seed.regios import REGIOS, VOORSTEL_PER_TAAL, regio
from .helpers import actieve_stelsels


def mijn_codes(request: Request) -> list[str] | None:
    """De gekozen stelselcodes van het profiel van dit verzoek, of None (nog niet gekozen of geen profiel)."""
    p = getattr(request.state, "profiel", None)
    return p.stelsel_codes if p is not None else None


@dataclass
class Keuze:
    eigen: list[Stelsel]
    overig: list[Stelsel] = field(default_factory=list)

    @property
    def alle(self) -> list[Stelsel]:
        return self.eigen + self.overig

    @property
    def codes(self) -> list[str]:
        return [s.code for s in self.eigen]


def splits(stelsels, codes, gekozen=()) -> tuple[list, list]:
    """(eigen, overig): `codes` is de keuze van het profiel (None = alles eigen); wat in `gekozen` staat (het filter
    van nu, een aangevinkt vakje) blijft bij de eigen stelsels, zodat het niet in de uitklap verdwijnt."""
    if codes is None:
        return list(stelsels), []
    if isinstance(gekozen, str):
        gekozen = [gekozen]
    zet = set(codes) | {g for g in gekozen if g}
    eigen = [s for s in stelsels if s.code in zet]
    return eigen, [s for s in stelsels if s.code not in zet]


def stelselkeuze(db: Session, request: Request, ook=()) -> Keuze:
    """De actieve stelsels, gesplitst in die van het profiel (plus `ook`) en de rest; elk deel op rechtsfamilie."""
    return Keuze(*splits(actieve_stelsels(db), mijn_codes(request), ook))


def ook_uit(request: Request) -> list[str]:
    """`?ook=AT&ook=PL` of `?ook=AT,PL`: stelsels die er voor deze pagina bij komen."""
    return [c.strip().upper() for w in request.query_params.getlist("ook") for c in w.split(",") if c.strip()]


@dataclass
class Regio:
    sleutel: str
    naam: str
    stelsels: list


def per_regio(stelsels) -> list[Regio]:
    """Groepeert stelsels per regio, in de volgorde van REGIOS; binnen een regio de volgorde zoals gegeven."""
    groepen: dict[str, list] = {}
    for s in stelsels:
        groepen.setdefault(regio(s.code), []).append(s)
    return [Regio(k, _(naam), groepen[k]) for k, naam in REGIOS.items() if k in groepen]


def voorstel(db: Session, taal: str) -> list[str]:
    """Voorstel voor een nieuw profiel: de stelsels bij de taal van het profiel die beschikbaar zijn, anders de
    stelsels met die taal (plus EU), anders alles."""
    actief = actieve_stelsels(db)
    codes = {s.code for s in actief}
    uit = [c for c in VOORSTEL_PER_TAAL.get(taal, []) if c in codes]
    if not uit:
        uit = [s.code for s in actief if s.taal == taal] + (["EU"] if "EU" in codes else [])
    return uit or [s.code for s in actief]


def bewaar(db: Session, profiel_id: int, codes) -> list[str]:
    """Slaat de keuze op (alleen bestaande stelsels, in de volgorde van de stelsels); leeg wordt het voorstel."""
    from ..models import Profiel

    p = db.get(Profiel, profiel_id)
    bekend = [s.code for s in db.scalars(select(Stelsel).order_by(Stelsel.volgorde)).all()]
    gekozen = {str(c).upper() for c in codes}
    uit = [c for c in bekend if c in gekozen] or voorstel(db, p.taal)
    p.stelsels = ",".join(uit)
    return uit


# --- overzicht op /stelsels -------------------------------------------------------------------------------------------

_cache: dict = {}


def aantallen(db: Session) -> dict[str, tuple[int, int]]:
    """Per stelsel (aantal wetten, aantal artikelen). Tellen over alle artikelen kost bij een volle database een
    seconde; de uitkomst blijft staan tot er een wet of artikel bijkomt (de hoogste id's) of na tien minuten."""
    sleutel = (db.scalar(select(func.max(Wettekst.id))), db.scalar(select(func.max(WettekstArtikel.id))))
    if _cache.get("sleutel") == sleutel and time.monotonic() - _cache.get("tijd", 0) < 600:
        return _cache["waarde"]
    wetten = dict(db.execute(
        select(Wettekst.stelsel_code, func.count(func.distinct(Wettekst.wet_id)))
        .where((Wettekst.stelsel_code != "EU") | ~Wettekst.wet_id.like("%.%"))  # EU: handelingen, niet de taalversies
        .group_by(Wettekst.stelsel_code)).all())
    artikelen = dict(db.execute(
        select(Wettekst.stelsel_code, func.count(WettekstArtikel.id)).join(WettekstArtikel, WettekstArtikel.wettekst_id == Wettekst.id)
        .group_by(Wettekst.stelsel_code)).all())
    waarde = {c: (wetten.get(c, 0), artikelen.get(c, 0)) for c in set(wetten) | set(artikelen)}
    _cache.update(sleutel=sleutel, tijd=time.monotonic(), waarde=waarde)
    return waarde


def met_open_bron() -> set[str]:
    """Stelsels met minstens één wet in het register (importers/register.py en register_<regio>.py): een open,
    machineleesbare bron die `synoptikon import-alles` kan ophalen."""
    from ..importers import register

    return {w.stelsel for w in register.WETTEN}
