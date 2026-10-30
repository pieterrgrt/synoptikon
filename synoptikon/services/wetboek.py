"""Bladeren door een geïmporteerde wet, zoals op Légifrance: inhoudsopgave → afdeling → artikel.

De inhoudsopgave komt uit de wettekst zelf: elk geïmporteerd artikel draagt
het pad van opschriften waaronder het staat ("Livre III › Titre III ›
Chapitre II"). Waar de bron geen pad meegeeft (de Codice civile van
Normattiva, enkele kleine Engelse wetten), komt het pad uit de systematiek
van Synoptikon, op artikelnummer. Artikelen zonder enig pad komen onder
"Overige artikelen".

Per wet wordt de boom één keer opgebouwd en bewaard zolang de geïmporteerde
versie dezelfde is.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..i18n import taal
from ..models import EuHandeling, EuTitel, Wettekst, WettekstArtikel
from . import eunamen
from .artikelen import Ref, plaatser, wet_kort

SCHEIDING = " › "
MAX_ARTIKELEN = 120  # meer artikelen in één afdeling: eerst een onderafdeling kiezen


@dataclass
class Deel:
    label: str
    pad: tuple[str, ...]
    kinderen: list["Deel"] = field(default_factory=list)
    artikelen: list[str] = field(default_factory=list)  # nummers direct onder dit deel, in volgorde
    aantal: int = 0  # alle artikelen eronder
    eerste: str | None = None
    laatste: str | None = None

    @property
    def sleutel(self) -> str:
        return SCHEIDING.join(self.pad)


@dataclass
class Inhoud:
    wortel: Deel
    per_pad: dict[tuple[str, ...], Deel]
    volgorde: list[Deel]  # alle delen, diepte eerst: voor vorige/volgende
    afgeleid: bool  # pad uit de systematiek in plaats van uit de bron


_CACHE: dict[int, tuple[object, Inhoud]] = {}
_CACHE_MAX = 200  # met duizenden wetten: alleen de laatst gelezen bewaren


def _basis(w: Wettekst) -> str:
    """Taalversies van één EU-tekst delen hun CELEX: 12016E, 12016E.fr, …"""
    return w.wet_id.split(".")[0] if w.stelsel_code == "EU" else w.wet_id


def _kies_taal(ws: list[Wettekst]) -> list[Wettekst]:
    """Per wet één versie: de meest recente, en bij EU-teksten in meer talen die van de interface (anders Duits)."""
    t = taal()
    beste: dict[str, Wettekst] = {}
    for w in ws:
        b = _basis(w)
        huidig = beste.get(b)
        if huidig is None or (w.taal == t and huidig.taal != t) or (w.taal == "de" and huidig.taal not in (t, "de")):
            beste[b] = w
    return list(beste.values())


def wetten(db: Session, stelsel: str, alle: bool = False) -> list[Wettekst]:
    """De meest recente versie van elke wet uit het register (`alle`: ook de bulkimport); de hoofdcodificatie eerst."""
    q = select(Wettekst).where(Wettekst.stelsel_code == stelsel)
    if not alle:
        q = q.where(Wettekst.kern.is_(True))
    gekozen = _kies_taal(list(db.scalars(q.order_by(Wettekst.opgehaald.desc())).all()))
    return sorted(gekozen, key=lambda w: (w.wet is not None, w.id))


# De wetten die je het vaakst opent, bovenaan het overzicht van een stelsel met duizenden wetten (DE: afkorting,
# EU: CELEX). Wat (nog) niet geïmporteerd is, valt weg.
BELANGRIJK: dict[str, list[str]] = {
    "DE": ["GG", "EGBGB", "HGB", "AktG", "GmbHG", "UmwG", "ZPO", "FamFG", "GVG", "InsO", "ZVG", "GBO", "WEG", "ErbbauRG",
           "BeurkG", "StGB", "StPO", "OWiG", "JGG", "VwVfG", "VwGO", "BVerfGG", "BauGB", "AO", "EStG", "UStG", "UWG", "GWB",
           "UrhG", "PatG", "MarkenG", "AGG", "BDSG", "DDG", "ProdHaftG", "VVG", "KSchG", "BetrVG", "TzBfG", "ArbGG",
           "AufenthG", "AsylG", "RDG", "BRAO"],
    "EU": ["12016M", "12016E", "12016P", "32016R0679", "32008R0593", "32007R0864", "32012R1215", "32019R1111", "32012R0650",
           "32015R0848", "32022R2065", "32022R1925", "32024R1689", "32023R2854", "32022R2554", "32022L2555", "31993L0013",
           "32011L0083", "32019L0771", "32019L0770", "31985L0374", "32005L0029", "32000L0031", "32006L0123"],
}


def belangrijk(db: Session, stelsel: str) -> list[Wettekst]:
    sleutels = BELANGRIJK.get(stelsel)
    if not sleutels:
        return []
    q = select(Wettekst).where(Wettekst.stelsel_code == stelsel)
    if stelsel == "EU":
        q = q.where(or_(Wettekst.wet_id.in_(sleutels), *[Wettekst.wet_id.like(f"{c}.%") for c in sleutels[:3]]))
    else:
        q = q.where(Wettekst.wet.in_(sleutels))
    gekozen = _kies_taal(list(db.scalars(q.order_by(Wettekst.opgehaald.desc())).all()))
    plek = {k: i for i, k in enumerate(sleutels)}
    return sorted(gekozen, key=lambda w: plek.get(_basis(w) if stelsel == "EU" else w.wet, 999))


def aantal_wetten(db: Session, stelsel: str) -> int:
    """Aantal wetten van een stelsel (EU: handelingen, niet hun taalversies)."""
    q = select(func.count(func.distinct(Wettekst.wet_id))).where(Wettekst.stelsel_code == stelsel)
    if stelsel == "EU":
        q = q.where(~Wettekst.wet_id.like("%.%"))
    return db.scalar(q) or 0


def zoek_wetten(db: Session, stelsel: str, q: str = "", pagina: int = 1, per_pagina: int = 100) -> tuple[list[Wettekst], int]:
    """Alle wetten van een stelsel, gezocht op titel of afkorting (EU ook op de titel in de taal van de interface)."""
    stmt = select(Wettekst).where(Wettekst.stelsel_code == stelsel)
    if stelsel == "EU":
        stmt = stmt.where(~Wettekst.wet_id.like("%.%"))  # één regel per handeling; de taalversie kiest `toon_titel`/lezen
    q = q.strip()
    if q:
        like = f"%{q}%"
        voorwaarden = [Wettekst.titel.ilike(like), Wettekst.wet.ilike(like), Wettekst.wet_id.ilike(like)]
        if stelsel == "EU":
            t = taal()
            voorwaarden.append(Wettekst.wet_id.in_(select(EuTitel.celex).where(EuTitel.taal == t, EuTitel.titel.ilike(like))))
            voorwaarden.append(Wettekst.wet_id.in_(select(EuHandeling.celex).where(or_(EuHandeling.titel.ilike(like), EuHandeling.roepnaam.ilike(like)))))
            sleutels = {w for w, per_taal in eunamen.KORT.items() if any(q.lower() in n.lower() for n in per_taal.values())}
            if sleutels:
                voorwaarden.append(Wettekst.wet.in_(sleutels))
        stmt = stmt.where(or_(*voorwaarden))
    totaal = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    # Wat men zoekt bovenaan: precies de afkorting ("PatG"), dan titels die ermee beginnen ("Patentgesetz"), dan de
    # kern, dan korte titels (de wet zelf vóór de verordeningen erbij).
    if q:
        volgorde = [(func.lower(Wettekst.wet) == q.lower()).desc(), Wettekst.titel.ilike(f"{q}%").desc(), Wettekst.wet.ilike(f"{q}%").desc(),
                    Wettekst.kern.desc(), func.length(Wettekst.titel), Wettekst.titel]
    else:
        volgorde = [Wettekst.kern.desc(), Wettekst.titel]
    rijen = db.scalars(stmt.order_by(*volgorde).offset((pagina - 1) * per_pagina).limit(per_pagina)).all()
    return list(rijen), totaal


def toon_titels(db: Session, ws: list[Wettekst]) -> dict[int, str]:
    """Titel per wet zoals ze getoond wordt: EU-teksten in de taal van de interface, de rest zoals in de bron."""
    t = taal()
    uit = {w.id: w.titel for w in ws}
    eu = [w for w in ws if w.stelsel_code == "EU"]
    if not eu:
        return uit
    celexen = [_basis(w) for w in eu]
    if t == "nl":
        vertaald = dict(db.execute(select(EuHandeling.celex, EuHandeling.titel).where(EuHandeling.celex.in_(celexen))).all())
    else:
        vertaald = dict(db.execute(select(EuTitel.celex, EuTitel.titel).where(EuTitel.taal == t, EuTitel.celex.in_(celexen))).all())
    for w in eu:
        uit[w.id] = eunamen.titel(w.wet, t) or vertaald.get(_basis(w)) or w.titel
    return uit


def toon_afkorting(w: Wettekst) -> str | None:
    return wet_kort(w.stelsel_code, w.wet)


@lru_cache(maxsize=8192)
def _eu_titel(celex: str, t: str) -> str | None:
    from ..db import session_factory
    with session_factory()() as db:
        if t == "nl":
            return db.scalar(select(EuHandeling.titel).where(EuHandeling.celex == celex))
        return db.scalar(select(EuTitel.titel).where(EuTitel.celex == celex, EuTitel.taal == t))


def toon_titel(w: Wettekst) -> str:
    """Voor templates: de titel van één wet in de taal van de interface (EU), anders zoals in de bron."""
    if w.stelsel_code != "EU":
        return w.titel
    t = taal()
    if w.taal == t:
        return w.titel
    try:
        return eunamen.titel(w.wet, t) or _eu_titel(_basis(w), t) or w.titel
    except Exception:
        return w.titel


def inhoud(db: Session, w: Wettekst) -> Inhoud:
    bewaard = _CACHE.get(w.id)
    if bewaard and bewaard[0] == w.opgehaald:
        return bewaard[1]
    rijen = db.execute(
        select(WettekstArtikel.nummer, WettekstArtikel.pad).where(WettekstArtikel.wettekst_id == w.id).order_by(WettekstArtikel.volgorde)
    ).all()
    afgeleid = bool(rijen) and not any(p for _n, p in rijen)
    pl = plaatser(db, w.stelsel_code, w.wet) if w.kern and any(not p for _n, p in rijen) else None
    wortel = Deel(w.titel, ())
    per_pad: dict[tuple[str, ...], Deel] = {(): wortel}
    for nummer, pad in rijen:
        if pad:
            delen = tuple(d.strip() for d in pad.split(SCHEIDING) if d.strip())
        else:
            knopen = pl.pad(nummer) if pl else []
            delen = tuple(k.label for k in knopen)
            # De wortelknoop van een andere wet is de wet zelf ("Sale of Goods Act 1979"): niet herhalen.
            if delen and w.wet and delen[0] == w.titel:
                delen = delen[1:]
        if not delen and any(p for _n, p in rijen):
            delen = ("Overige artikelen",)
        ouder = wortel
        for i in range(len(delen)):
            sleutel = delen[: i + 1]
            d = per_pad.get(sleutel)
            if d is None:
                d = per_pad[sleutel] = Deel(delen[i], sleutel)
                ouder.kinderen.append(d)
            ouder = d
        ouder.artikelen.append(nummer)
        for i in range(len(delen) + 1):
            d = per_pad[delen[:i]]
            d.aantal += 1
            d.eerste = d.eerste or nummer
            d.laatste = nummer
    volgorde: list[Deel] = []

    def loop(d: Deel) -> None:
        for k in d.kinderen:
            volgorde.append(k)
            loop(k)

    loop(wortel)
    uit = Inhoud(wortel, per_pad, volgorde, afgeleid)
    if len(_CACHE) >= _CACHE_MAX:
        _CACHE.pop(next(iter(_CACHE)))
    _CACHE[w.id] = (w.opgehaald, uit)
    return uit


def deel(ih: Inhoud, sleutel: str) -> Deel | None:
    pad = tuple(d for d in sleutel.split(SCHEIDING) if d) if sleutel else ()
    return ih.per_pad.get(pad)


def nummers_onder(d: Deel) -> list[str]:
    uit = list(d.artikelen)
    for k in d.kinderen:
        uit.extend(nummers_onder(k))
    return uit


def artikelen(db: Session, w: Wettekst, nummers: list[str]) -> list[WettekstArtikel]:
    if not nummers:
        return []
    uit: list[WettekstArtikel] = []
    for i in range(0, len(nummers), 500):
        uit.extend(db.scalars(select(WettekstArtikel).where(WettekstArtikel.wettekst_id == w.id, WettekstArtikel.nummer.in_(nummers[i:i + 500]))).all())
    return sorted(uit, key=lambda a: a.volgorde)


def buren(ih: Inhoud, d: Deel) -> tuple[Deel | None, Deel | None]:
    """Vorige en volgende afdeling op hetzelfde of een dieper niveau, zoals 'précédent/suivant'."""
    try:
        i = ih.volgorde.index(d)
    except ValueError:
        return None, None
    return (ih.volgorde[i - 1] if i > 0 else None), (ih.volgorde[i + 1] if i + 1 < len(ih.volgorde) else None)


def ref(w: Wettekst, nummer: str) -> Ref:
    return Ref(w.stelsel_code, nummer, w.wet)


def naast(db: Session, wa: WettekstArtikel) -> tuple[WettekstArtikel | None, WettekstArtikel | None]:
    """Vorig en volgend artikel in dezelfde wettekst."""
    q = select(WettekstArtikel).where(WettekstArtikel.wettekst_id == wa.wettekst_id)
    vorig = db.scalars(q.where(WettekstArtikel.volgorde < wa.volgorde).order_by(WettekstArtikel.volgorde.desc())).first()
    volgend = db.scalars(q.where(WettekstArtikel.volgorde > wa.volgorde).order_by(WettekstArtikel.volgorde)).first()
    return vorig, volgend


# --- lezen in de systematiek ----------------------------------------------------------
# De boom van Synoptikon (Systematiek) is de leesingang: elk ingelezen artikel hangt aan de diepste knoop die het
# bevat. Wat de systematiek niet plaatst, blijft via de wet zelf (`inhoud`) leesbaar.


@dataclass
class Plaatsing:
    direct: dict[int, list[tuple[int, str]]]  # knoop-id → [(wettekst-id, nummer)], in wetsvolgorde
    onder: dict[int, int]  # knoop-id → aantal artikelen in de knoop en haar afstammelingen
    los: dict[int, list[str]]  # wettekst-id → nummers zonder plaats
    wortel: dict[int, int]  # wettekst-id → wortelknoop waaronder haar eerste artikel staat
    plek: dict[tuple[int, str], int]  # (wettekst-id, nummer) → knoop-id


_PLAATSING: dict[str, tuple[object, Plaatsing]] = {}


def plaatsing(db: Session, stelsel: str) -> Plaatsing:
    from ..models import Systematiek

    ws = wetten(db, stelsel)
    knopen = db.execute(select(Systematiek.id, Systematiek.parent_id, Systematiek.bereik, Systematiek.wet).where(Systematiek.stelsel_code == stelsel)).all()
    versie = (tuple((w.id, w.opgehaald) for w in ws), hash(tuple(sorted(tuple(k) for k in knopen))))
    sleutel = f"{stelsel}:{taal()}" if stelsel == "EU" else stelsel  # EU: de verdragen per taal
    bewaard = _PLAATSING.get(sleutel)
    if bewaard and bewaard[0] == versie:
        return bewaard[1]
    uit = Plaatsing({}, {}, {}, {}, {})
    plaatsers: dict[str | None, object] = {}
    for w in ws:
        pl = plaatsers.get(w.wet) or plaatsers.setdefault(w.wet, plaatser(db, stelsel, w.wet))
        nummers = db.scalars(select(WettekstArtikel.nummer).where(WettekstArtikel.wettekst_id == w.id).order_by(WettekstArtikel.volgorde)).all()
        for nr in nummers:
            pad = pl.pad(nr)
            if not pad:
                uit.los.setdefault(w.id, []).append(nr)
                continue
            uit.wortel.setdefault(w.id, pad[0].id)
            uit.direct.setdefault(pad[-1].id, []).append((w.id, nr))
            uit.plek[(w.id, nr)] = pad[-1].id
            for k in pad:
                uit.onder[k.id] = uit.onder.get(k.id, 0) + 1
    _PLAATSING[sleutel] = (versie, uit)
    return uit


def artikelen_bij(db: Session, paren: list[tuple[int, str]]) -> list[WettekstArtikel]:
    """De artikelen bij (wettekst-id, nummer)-paren, in de volgorde van de paren."""
    per_wet: dict[int, list[str]] = {}
    for wid, nr in paren:
        per_wet.setdefault(wid, []).append(nr)
    gevonden: dict[tuple[int, str], WettekstArtikel] = {}
    for wid, nrs in per_wet.items():
        for i in range(0, len(nrs), 500):
            for a in db.scalars(select(WettekstArtikel).where(WettekstArtikel.wettekst_id == wid, WettekstArtikel.nummer.in_(nrs[i:i + 500]))):
                gevonden[(wid, a.nummer)] = a
    return [gevonden[p] for p in paren if p in gevonden]


def lees_url(db: Session, r: Ref, wa: WettekstArtikel | None = None) -> str | None:
    """Het artikel in de leesweergave van zijn wet (de afdeling waarin het staat, op het artikel); anders de artikelpagina."""
    if wa is None:
        return r.url
    from urllib.parse import quote

    return f"/stelsels/{wa.wettekst.stelsel_code}/wet/{wa.wettekst_id}?artikel={quote(wa.nummer)}"
