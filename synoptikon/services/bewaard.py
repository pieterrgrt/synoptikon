"""Wat jij zelf hebt bewaard: je wetsartikelen en uitspraken, per vak.

De bibliotheek (`services/bibliotheek.py`) laat zien wat Synoptikon aan wetteksten binnen heeft — honderdduizenden
artikelen, waarvan jij de meeste nooit zag. Dit is het omgekeerde: alleen wat jij hebt aangeraakt. Dat zit op drie
plekken en stond nergens bij elkaar:

* een **kaart** die naar een artikel wijst (`Kaart.stelsel_code/wet/nummer`), met het vak van zijn leerlijst;
* een zelf bewaarde **wetsbron** (`Bron` met soort 'wet'), bijvoorbeeld uit een opzoeking — die hangt niet aan
  een profiel (zo zit `Bron` in Synoptikon: één gedeelde verzameling) en komt daarom onder 'Zonder vak';
* een **markering** die je in een artikel zette (`Markering`), met het vak waarvoor je hem maakte.

Hetzelfde artikel kan uit alle drie komen en in meer dan één vak zitten; het wordt één regel, die zegt waar het
vandaan komt. Groeperen gaat op vak, want zo studeer je; wat geen vak heeft komt onderaan.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..i18n import _
from ..models import Bron, Kaart, Leerlijst, Markering
from .artikelen import Ref, ref_uit_bron
from .correspondentie import thema_s_voor, wettekst_artikel

ZONDER_VAK = ""


@dataclass
class Artikel:
    """Eén wetsartikel dat jij hebt bewaard."""

    stelsel: str
    wet: str | None
    nummer: str
    kaarten: int = 0
    bron_id: int | None = None       # zelf bewaard als Bron (dan is er eigen tekst)
    markeringen: int = 0
    opschrift: str | None = None
    heeft_tekst: bool = False        # staat de wettekst erbij, of alleen de verwijzing
    vakken: set[str] = field(default_factory=set)

    @property
    def ref(self) -> Ref:
        return Ref(self.stelsel, self.nummer, self.wet)

    @property
    def citeer(self) -> str:
        return self.ref.citeer

    @property
    def url(self) -> str:
        return f"/artikelen/{self.stelsel}/{self.nummer}"

    @property
    def herkomst(self) -> list[str]:
        """Waarom dit artikel in je lijst staat — in je eigen woorden leesbaar."""
        uit = []
        if self.kaarten:
            uit.append(_("{n} kaarten", n=self.kaarten) if self.kaarten > 1 else _("1 kaart"))
        if self.bron_id:
            uit.append(_("zelf bewaard"))
        if self.markeringen:
            uit.append(_("{n} markeringen", n=self.markeringen) if self.markeringen > 1 else _("1 markering"))
        return uit


@dataclass
class Uitspraak:
    """Een bewaarde uitspraak; hoort bij punt 6 van de backlog: artikelen en rechtspraak naast elkaar."""

    bron_id: int
    stelsel: str
    citeertitel: str
    vindplaats: str | None
    kaarten: int = 0
    vakken: set[str] = field(default_factory=set)
    tekst: str = ""
    over: list[Artikel] = field(default_factory=list)  # bewaarde artikelen (uit dit vak) die de uitspraak noemt

    @property
    def url(self) -> str:
        return f"/bronnen/{self.bron_id}"


@dataclass
class Groep:
    vak: str
    artikelen: list[Artikel] = field(default_factory=list)
    uitspraken: list[Uitspraak] = field(default_factory=list)
    themas: list[tuple[str, list[Artikel]]] = field(default_factory=list)  # thema → bewaarde artikelen die erin staan (≥ 2)

    @property
    def naam(self) -> str:
        return self.vak or _("Zonder vak")

    @property
    def leeg(self) -> bool:
        return not (self.artikelen or self.uitspraken)


@dataclass
class Overzicht:
    groepen: list[Groep] = field(default_factory=list)
    artikelen: int = 0
    uitspraken: int = 0
    stelsels: list[str] = field(default_factory=list)

    @property
    def leeg(self) -> bool:
        return not self.groepen


def overzicht(db: Session, profiel_id: int, vak: str | None = None) -> Overzicht:
    """Alles wat dit profiel aan artikelen en uitspraken bewaarde, per vak. `vak` filtert op één vak."""
    artikelen: dict[tuple[str, str | None, str], Artikel] = {}
    uitspraken: dict[int, Uitspraak] = {}

    def haal(stelsel: str, wet: str | None, nummer: str) -> Artikel:
        sleutel = (stelsel, wet or None, nummer)
        if sleutel not in artikelen:
            artikelen[sleutel] = Artikel(stelsel=stelsel, wet=wet or None, nummer=nummer)
        return artikelen[sleutel]

    # 1. kaarten die naar een artikel wijzen, met het vak van hun leerlijst
    # Een arrestkaart heeft geen artikelnummer maar wel een bron: die hoort er ook bij.
    kaarten = db.scalars(
        select(Kaart).join(Leerlijst)
        .where(Leerlijst.profiel_id == profiel_id, Kaart.nummer.is_not(None) | Kaart.bron_id.is_not(None))
        .options(selectinload(Kaart.lijst), selectinload(Kaart.bron))).all()
    for k in kaarten:
        vak_van_kaart = (k.lijst.vak or ZONDER_VAK) if k.lijst else ZONDER_VAK
        if k.stelsel_code and k.nummer:
            a = haal(k.stelsel_code, k.wet, k.nummer)
            a.kaarten += 1
            a.vakken.add(vak_van_kaart)
        if k.bron_id and k.bron is not None and k.bron.soort == "rechtspraak":
            u = uitspraken.setdefault(k.bron_id, Uitspraak(
                bron_id=k.bron_id, stelsel=k.bron.stelsel_code, citeertitel=k.bron.citeertitel,
                vindplaats=k.bron.vindplaats, tekst=" ".join(x for x in (k.bron.tekst, k.bron.opmerking) if x)))
            u.kaarten += 1
            u.vakken.add(vak_van_kaart)

    # 2. zelf bewaarde wetsbronnen: die hebben geen vak, maar wel eigen tekst
    for b in db.scalars(select(Bron).where(Bron.soort == "wet").order_by(Bron.id)).all():
        if (r := ref_uit_bron(b)) and r.nummer:
            a = haal(r.stelsel, r.wet, r.nummer)
            a.bron_id = a.bron_id or b.id
            a.heeft_tekst = a.heeft_tekst or bool(b.tekst)
            if not a.vakken:   # een bewaarde wetsbron hangt niet aan een vak
                a.vakken.add(ZONDER_VAK)

    # 3. markeringen in een artikel (die in een uitspraak horen bij de uitspraak)
    for m in db.scalars(select(Markering).where(Markering.profiel_id == profiel_id,
                                                Markering.bron_id.is_(None),
                                                Markering.stelsel_code.is_not(None),
                                                Markering.nummer.is_not(None))).all():
        a = haal(m.stelsel_code, m.wet, m.nummer)
        a.markeringen += 1
        a.vakken.add(m.vak or ZONDER_VAK)

    # De wettekst erbij zoeken: staat het artikel in de kast, of heb je alleen de verwijzing?
    for a in artikelen.values():
        if wa := wettekst_artikel(db, a.ref):
            a.heeft_tekst = True
            a.opschrift = a.opschrift or wa.opschrift

    uit = Overzicht(artikelen=len(artikelen), uitspraken=len(uitspraken),
                    stelsels=sorted({a.stelsel for a in artikelen.values()}))

    # Vakken in de orde van de leerlijsten (zo staat /leren ook), 'zonder vak' altijd onderaan.
    orde = [l.vak for l in db.scalars(select(Leerlijst).where(Leerlijst.profiel_id == profiel_id)
                                      .order_by(Leerlijst.id)).all() if l.vak]
    vakken = sorted({v for a in artikelen.values() for v in a.vakken} | {v for u in uitspraken.values() for v in u.vakken},
                    key=lambda v: (v == ZONDER_VAK, orde.index(v) if v in orde else len(orde), v))
    for v in vakken:
        if vak is not None and v != vak:
            continue
        g = Groep(vak=v)
        g.artikelen = sorted((a for a in artikelen.values() if v in a.vakken),
                             key=lambda a: (a.stelsel, a.wet or "", _sorteer(a.nummer)))
        g.uitspraken = sorted((u for u in uitspraken.values() if v in u.vakken), key=lambda u: u.citeertitel)
        if not g.leeg:
            _samenhang(db, g)
            uit.groepen.append(g)
    return uit


def noemt(tekst: str, a: Artikel) -> bool:
    """Noemt deze tekst het artikel? '§ 929', 'Art. 6:162', 'article 1240', 'Artikel 101 AEUV' — met grens na het nummer,
    zodat § 92 niet in § 929 zit. Zonder wet in de tekst telt het nummer alleen (de uitspraak hoort bij hetzelfde vak)."""
    nr = re.escape(a.nummer)
    return bool(re.search(rf"(?:§§?|\bArt(?:ikel|icle|ículo|icolo)?s?\.?|\bart\.)\s*{nr}(?![\w:.-]*\d)", tekst or "", re.I))


def _samenhang(db: Session, g: Groep) -> None:
    """Welke bewaarde uitspraak noemt welk bewaard artikel, en welke artikelen staan samen in een thema van de
    correspondentietabel. Alleen binnen het vak: daar studeer je ze samen."""
    for u in g.uitspraken:
        u.over = [a for a in g.artikelen if a.stelsel == u.stelsel and noemt(u.tekst, a)]
    per_thema: dict[str, list[Artikel]] = {}
    for a in g.artikelen:
        for c, _leden in thema_s_voor(db, a.stelsel, a.nummer, a.wet):
            per_thema.setdefault(c.titel, []).append(a)
    g.themas = sorted(((t, xs) for t, xs in per_thema.items() if len(xs) >= 2), key=lambda x: (-len(x[1]), x[0]))


def _sorteer(nummer: str) -> tuple:
    """§ 929 na § 90, niet ervoor: cijfergroepen als getal, de rest als tekst."""
    return tuple((0, int(d)) if d.isdigit() else (1, d) for d in re.findall(r"\d+|\D+", nummer or ""))
