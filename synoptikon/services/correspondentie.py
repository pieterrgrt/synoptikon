"""Gegevens voor de artikelpagina, de themapagina en de knooppagina.

Alles leest uit de database en is per verzoek opgebouwd; de aantallen zijn
klein (honderden thema's, enkele duizenden knopen en bronnen), dus volledige
lijsten in het geheugen zijn eenvoudiger dan slimme SQL op nummerbereiken.
"""
from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..models import AntwoordBron, Bron, Concordantie, Correspondentie, CorrespondentieArtikel, Systematiek, Wettekst, WettekstArtikel
from .artikelen import HOOFDWET, Plaatser, Ref, plaatser, ref_bevat, ref_uit_bron, sleutel

FR_CODE_CIVIL = "LEGITEXT000006070721"


@dataclass
class Tekst:
    """De tekst van een artikel zoals Synoptikon hem kent: uit een bron of een geïmporteerde wet."""

    tekst: str
    opschrift: str | None
    herkomst: str  # "bron" | "wettekst"
    url: str  # interne link
    officieel: str | None = None  # externe link


@dataclass
class Lid:
    """Eén artikel binnen een thema, verrijkt voor weergave."""

    artikel: CorrespondentieArtikel
    pad: list = field(default_factory=list)
    tekst: Tekst | None = None

    @property
    def ref(self) -> Ref:
        return self.artikel.ref


class Context:
    """Per verzoek: plaatsers per stelsel en een index van wetsbronnen."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self._plaatsers: dict[str, Plaatser] = {}
        self._bronnen: dict[tuple, list[Bron]] | None = None

    def plaatser(self, stelsel: str) -> Plaatser:
        if stelsel not in self._plaatsers:
            self._plaatsers[stelsel] = plaatser(self.db, stelsel)
        return self._plaatsers[stelsel]

    def pad(self, ref: Ref) -> list:
        if ref.nummer is None or ref.wet or ref.stelsel not in HOOFDWET:
            return []
        return self.plaatser(ref.stelsel).pad(ref.nummer)

    def bronnen_voor(self, stelsel: str, nummer: str, wet: str | None = None) -> list[Bron]:
        if self._bronnen is None:
            self._bronnen = {}
            for b in self.db.scalars(select(Bron).where(Bron.soort == "wet")).all():
                r = ref_uit_bron(b)
                if r:
                    self._bronnen.setdefault((r.stelsel, r.wet, r.nummer), []).append(b)
        return self._bronnen.get((stelsel, wet, nummer), [])

    def tekst(self, ref: Ref) -> Tekst | None:
        if ref.nummer is None:
            return None
        for b in self.bronnen_voor(ref.stelsel, ref.nummer, ref.wet):
            if b.tekst and b.is_geldig:
                return Tekst(b.tekst, b.titel, "bron", f"/bronnen/{b.id}", b.url)
        wa = wettekst_artikel(self.db, ref)
        if wa:
            return Tekst(wa.tekst, wa.opschrift, "wettekst", f"/wetteksten/{wa.wettekst_id}#{wa.nummer}", wa.wettekst.bron_url)
        return None

    def lid(self, a: CorrespondentieArtikel) -> Lid:
        return Lid(a, self.pad(a.ref), self.tekst(a.ref))


def wettekst_artikel(db: Session, ref: Ref) -> WettekstArtikel | None:
    """Het artikel uit de meest recent geïmporteerde versie van de passende wet."""
    if ref.nummer is None:
        return None
    q = select(WettekstArtikel).join(Wettekst).where(Wettekst.stelsel_code == ref.stelsel, WettekstArtikel.nummer == ref.nummer)
    if ref.stelsel == "DE":
        q = q.where(Wettekst.wet_id == (ref.wet or "bgb").lower())
    elif ref.stelsel == "FR":
        if ref.wet:
            return None
        q = q.where(Wettekst.wet_id == FR_CODE_CIVIL)
    elif ref.wet:
        return None
    return db.scalars(q.order_by(Wettekst.opgehaald.desc())).first()


def alle_correspondenties(db: Session) -> list[Correspondentie]:
    return list(
        db.scalars(select(Correspondentie).options(selectinload(Correspondentie.artikelen)).order_by(Correspondentie.rechtsgebied, Correspondentie.titel)).all()
    )


def thema_s_voor(db: Session, stelsel: str, nummer: str, wet: str | None = None) -> list[tuple[Correspondentie, list[CorrespondentieArtikel]]]:
    """Thema's waarin dit artikel staat, met de leden die het (ook via een bereik) dekken."""
    uit = []
    for c in alle_correspondenties(db):
        eigen = [a for a in c.artikelen if ref_bevat(a.ref, stelsel, nummer, wet)]
        if eigen:
            uit.append((c, eigen))
    return uit


def per_stelsel(ctx: Context, c: Correspondentie, codes: list[str], behalve: CorrespondentieArtikel | None = None) -> "OrderedDict[str, list[Lid]]":
    kolommen: OrderedDict[str, list[Lid]] = OrderedDict((code, []) for code in codes)
    for a in c.artikelen:
        if a is behalve:
            continue
        kolommen.setdefault(a.stelsel_code, []).append(ctx.lid(a))
    return kolommen


def concordanties_voor(db: Session, stelsel: str, nummer: str) -> list[Concordantie]:
    patroon = re.compile(rf"(?<![\d:\-]){re.escape(nummer)}(?![\d\-a-z])")
    return [c for c in db.scalars(select(Concordantie).where(Concordantie.stelsel_code == stelsel)).all() if patroon.search(c.oud) or (c.nieuw and patroon.search(c.nieuw))]


def gebruik(ctx: Context, ref: Ref) -> list[AntwoordBron]:
    """Koppelingen bron → vraag voor dit artikel (via de wetsbronnen)."""
    uit: list[AntwoordBron] = []
    for b in ctx.bronnen_voor(ref.stelsel, ref.nummer, ref.wet) if ref.nummer else []:
        uit.extend(b.antwoorden)
    return uit


# --- knopen ---------------------------------------------------------------------


@dataclass
class Tegenhanger:
    """Een plaats in een ander stelsel waar artikelen uit een knoop naartoe wijzen."""

    pad: list
    thema_s: list[Correspondentie] = field(default_factory=list)
    leden: list[Lid] = field(default_factory=list)


def leden_in_knoop(ctx: Context, knoop: Systematiek) -> list[tuple[Correspondentie, CorrespondentieArtikel]]:
    """Correspondentieleden van dit stelsel waarvan het artikel onder deze knoop valt."""
    pl = ctx.plaatser(knoop.stelsel_code)
    uit = []
    for c in alle_correspondenties(ctx.db):
        for a in c.artikelen:
            if a.stelsel_code == knoop.stelsel_code and a.wet is None and a.nummer and knoop in pl.pad(a.nummer):
                uit.append((c, a))
    return uit


def tegenhangers(ctx: Context, knoop: Systematiek, codes: list[str]) -> "OrderedDict[str, list[Tegenhanger]]":
    """Per ander stelsel: de diepste knopen waarin de corresponderende artikelen staan.

    Zo zie je dat BW Boek 3 Titel 4 Afdeling 2 in DE uiteenvalt over het
    Sachenrecht (§§ 929 ff.) en het Schuldrecht (§ 433, § 812), en in FR in
    het contractenrecht (art. 1196) terechtkomt.
    """
    gezien: set[tuple[int, int]] = set()
    uit: OrderedDict[str, OrderedDict] = OrderedDict((code, OrderedDict()) for code in codes if code != knoop.stelsel_code)
    for c, _eigen in leden_in_knoop(ctx, knoop):
        for a in c.artikelen:
            if a.stelsel_code == knoop.stelsel_code or a.stelsel_code not in uit or (c.id, a.id) in gezien:
                continue
            gezien.add((c.id, a.id))
            lid = ctx.lid(a)
            sleutel_ = lid.pad[-1].id if lid.pad else ("los", a.wet or "", a.nummer is None)
            t = uit[a.stelsel_code].setdefault(sleutel_, Tegenhanger(lid.pad))
            if c not in t.thema_s:
                t.thema_s.append(c)
            t.leden.append(lid)
    resultaat: OrderedDict[str, list[Tegenhanger]] = OrderedDict()
    for code, groepen in uit.items():
        lijst = list(groepen.values())
        lijst.sort(key=lambda t: _padsleutel(code, t))
        resultaat[code] = lijst
    return resultaat


def _padsleutel(stelsel: str, t: Tegenhanger) -> tuple:
    nummers = [l.artikel.nummer for l in t.leden if l.artikel.nummer and not l.artikel.wet]
    sleutels = [sleutel(stelsel, n) for n in nummers]
    sleutels = [s for s in sleutels if s is not None]
    return (0 if t.pad else 1, min(sleutels) if sleutels else ())


def tellingen(ctx: Context, stelsel: str) -> dict[int, int]:
    """Aantal thema's per knoop (inclusief onderliggende knopen), voor de boomweergave."""
    pl = ctx.plaatser(stelsel)
    per_knoop: dict[int, set[int]] = {}
    for c in alle_correspondenties(ctx.db):
        for a in c.artikelen:
            if a.stelsel_code == stelsel and a.wet is None and a.nummer:
                for k in pl.pad(a.nummer):
                    per_knoop.setdefault(k.id, set()).add(c.id)
    return {k: len(v) for k, v in per_knoop.items()}
