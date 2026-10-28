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

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Wettekst, WettekstArtikel
from .artikelen import Ref, plaatser

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


def wetten(db: Session, stelsel: str) -> list[Wettekst]:
    """De meest recente versie van elke geïmporteerde wet van een stelsel; de hoofdcodificatie eerst."""
    alle = db.scalars(select(Wettekst).where(Wettekst.stelsel_code == stelsel).order_by(Wettekst.opgehaald.desc())).all()
    gezien, uit = set(), []
    for w in alle:
        if w.wet_id not in gezien:
            gezien.add(w.wet_id)
            uit.append(w)
    return sorted(uit, key=lambda w: (w.wet is not None, w.id))


def inhoud(db: Session, w: Wettekst) -> Inhoud:
    bewaard = _CACHE.get(w.id)
    if bewaard and bewaard[0] == w.opgehaald:
        return bewaard[1]
    rijen = db.execute(
        select(WettekstArtikel.nummer, WettekstArtikel.pad).where(WettekstArtikel.wettekst_id == w.id).order_by(WettekstArtikel.volgorde)
    ).all()
    afgeleid = bool(rijen) and not any(p for _n, p in rijen)
    pl = plaatser(db, w.stelsel_code, w.wet) if any(not p for _n, p in rijen) else None
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
    bewaard = _PLAATSING.get(stelsel)
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
    _PLAATSING[stelsel] = (versie, uit)
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
