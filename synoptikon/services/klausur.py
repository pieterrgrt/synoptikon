"""Klausurtrainer: een casus oplossen in Gutachtenstil, laten beoordelen, en leren van wat je miste.

De gang van een casus:

1. **Sachverhalt** — zelf geplakt (`maak`), een voorbeeldcasus (`seed/casussen.py`) of door Claude gemaakt op een
   onderwerp en niveau (`genereer`). Bij een gegenereerde casus hoort een verborgen Lösungsskizze (`Casus.skizze`).
2. **Oplossen** — een `CasusPoging`: skizze en uitwerking, tussentijds bewaard (`bewaar`, met een revisienummer zodat
   een ander apparaat niets stil overschrijft). In de Klausurmodus loopt een limiet; is die om, dan is de poging
   ingeleverd (`sluit_als_tijd_om`).
3. **Zelf nakijken, zonder Claude** — `volgorde` controleert of de Anspruchsgrundlagen in de skizze in de gebruikelijke
   volgorde staan, `genoemde_normen` of elke norm die je noemt in de lokale wettekst bestaat, `stijl_telling` telt de
   woorden van Gutachten- en Urteilsstil.
4. **Beoordeling** — Claude leest de normen via de lokale wettekst-tools en vult het schema `BEOORDELING`: per
   Prüfungspunkt de Anspruchsgrundlage, Obersatz, Definition, Subsumtion en Ergebnis, daarnaast Aufbau, Stil,
   Schwerpunktsetzung en de gemiste problemen. Niets daarvan is geverifieerd; de pagina zegt dat.
5. **Leren** — elk Prüfungspunkt wordt een `CasusProbleem`; `kaartvoorstel` maakt er met één tik een voorstel van in de
   leerlijst van het vak (de gewone voorstellenstroom, dus pas na overnemen naar Wunderkammer), en `steeds_gemist`
   telt over alle casussen heen.
"""
from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from markupsafe import Markup
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import md
from ..config import settings
from ..i18n import TALEN, _
from ..models import ANSPRUCHSGRUPPEN, CASUS_NIVEAUS, Casus, CasusPoging, CasusProbleem, Kaart, now
from . import citaties, claude, leren, vakken
from .artikelen import Ref, herken
from .correspondentie import wettekst_artikel

log = logging.getLogger(__name__)

ACHTERGROND = True  # tests zetten dit uit: dan draait Claude in het verzoek zelf
SPELING = timedelta(minutes=2)  # na het einde van de tijd mag het laatste autosave nog binnenkomen
MAX_TEKST = 60000  # tekens per veld

NOTEN = [(16, "sehr gut"), (13, "gut"), (10, "vollbefriedigend"), (7, "befriedigend"), (4, "ausreichend"), (1, "mangelhaft"), (0, "ungenügend")]


def note(punkte: int | None) -> str:
    """De Notenstufe bij 0–18 Punkte."""
    if punkte is None:
        return ""
    return next(naam for grens, naam in NOTEN if punkte >= grens)


# --- normen koppelen aan de lokale tekst -----------------------------------------------------------------------------


class Koppelaar:
    """Maakt van normen in tekst links naar het artikel, als het artikel in de lokale wettekst staat."""

    def __init__(self, db: Session, stelsel: str = "DE") -> None:
        self.db, self.stelsel = db, stelsel
        self._er: dict[tuple, bool] = {}

    def bestaat(self, ref: Ref) -> bool:
        sleutel = (ref.stelsel, ref.wet, ref.nummer)
        if sleutel not in self._er:
            self._er[sleutel] = wettekst_artikel(self.db, ref) is not None
        return self._er[sleutel]

    def md(self, tekst: str | None) -> Markup:
        return md.render(citaties.koppel_md(tekst, self.bestaat, self.stelsel))

    def inline(self, tekst: str | None) -> Markup:
        return md.render_inline(citaties.koppel_md(tekst, self.bestaat, self.stelsel))

    def ref(self, norm: str) -> Ref | None:
        """De eerste verwijzing in een norm zoals Claude of de gebruiker hem schreef ("§§ 280 I, III, 283 BGB")."""
        gevonden = citaties.refs(norm, self.stelsel)
        if gevonden:
            return gevonden[0]
        los = herken(norm) or herken(norm, self.stelsel)
        return los[0] if los else None

    def norm(self, norm: str) -> dict:
        """{"tekst", "url", "gevonden"}: voor de lijst met normen bij een casus of Prüfungspunkt."""
        r = self.ref(norm)
        er = r is not None and self.bestaat(r)
        return {"tekst": norm, "url": r.url if er else None, "gevonden": er}

    def normen(self, lijst: list | None) -> list[dict]:
        return [self.norm(str(n)) for n in (lijst or []) if str(n).strip()]


# --- volgorde van de Anspruchsgrundlagen (deterministisch) ----------------------------------------------------------------

# BGB-paragrafen die als Anspruchsgrundlage voorkomen, per groep. Een keten telt als de 'zwaarste' groep die erin zit:
# "§§ 280 I, 311 II, 241 II" is vertragsähnlich (c.i.c.), "§§ 683 S. 1, 670" ook (GoA), "§§ 990, 989" dinglich.
_VERTRAG = {280, 281, 282, 283, 284, 285, 286, 288, 311, 346, 347, 433, 437, 439, 441, 488, 516, 535, 536, 546, 598, 604, 611,
            631, 634, 635, 637, 651, 662, 667, 670, 675, 765}
_VERTRAGSAEHNLICH = {122, 179, 677, 678, 681, 683, 684, 687}
_DINGLICH = {861, 862, 888, 894, 985, 987, 988, 989, 990, 991, 992, 993, 994, 996, 1004, 1007, 1147, 1227}
_DELIKT = {823, 824, 825, 826, 829, 831, 832, 833, 834, 836, 837, 838, 839}
_BEREICHERUNG = {812, 813, 816, 817, 822}
_ANDERE_WET = {("StVG", 7): "delikt", ("StVG", 18): "delikt", ("ProdHaftG", 1): "delikt"}
GROEPEN = list(ANSPRUCHSGRUPPEN)


def anspruchsgroep(v: citaties.Vondst) -> str | None:
    """De groep van een aangehaalde Anspruchsgrundlage, of None als de keten er geen bevat."""
    nummers: set[int] = set()
    cic = False
    for e in v.elementen:
        r = e.ref
        if r is None or r.stelsel != "DE":
            continue
        m = re.match(r"\d+", r.nummer)
        if not m:
            continue
        n = int(m.group())
        if r.wet:
            groep = next((g for (w, nr), g in _ANDERE_WET.items() if w.lower() == r.wet.lower() and nr == n), None)
            if groep:
                return groep
            continue
        nummers.add(n)
        if n == 311 and any(d.lid in ("2", "3") for d in e.details):
            cic = True
    if not nummers:
        return None
    if cic or (311 in nummers and 241 in nummers) or nummers & _VERTRAGSAEHNLICH:
        return "vertragsaehnlich"
    for groep, verzameling in (("dinglich", _DINGLICH), ("delikt", _DELIKT), ("bereicherung", _BEREICHERUNG), ("vertrag", _VERTRAG)):
        if nummers & verzameling:
            return groep
    return None


@dataclass
class VolgordeOpmerking:
    regel: int  # regelnummer in de skizze (vanaf 1)
    norm: str
    groep: str
    na_norm: str
    na_groep: str

    @property
    def tekst(self) -> str:
        return _("{norm} ({groep}) staat na {na_norm} ({na_groep}).", norm=self.norm, groep=ANSPRUCHSGRUPPEN[self.groep],
                 na_norm=self.na_norm, na_groep=ANSPRUCHSGRUPPEN[self.na_groep])


_PARTIJEN = re.compile(r"\b([A-ZÄÖÜ][\wÄÖÜäöüß\-]{0,24})\s+gegen\s+(?:den\s+|die\s+|das\s+)?([A-ZÄÖÜ][\wÄÖÜäöüß\-]{0,24})")
_ANSPRUCH = re.compile(r"\b(?:aus|gem\.|gemäß|nach|Anspruch|Ansprüche)\b|^\s*(?:[A-Z]|[IVX]+|\d+)[.)]\s", re.I)


def volgorde(skizze: str) -> list[VolgordeOpmerking]:
    """Waar de skizze afwijkt van Vertrag → vertragsähnlich → dinglich → Delikt → Bereicherung.

    Per paar partijen ("K gegen V") begint de volgorde opnieuw. Alleen regels die een Anspruch aankondigen tellen (een
    koptekst, of "aus/gemäß/nach § …"); wat daaronder als voorwaarde staat ("§ 119 II") is geen Anspruchsgrundlage. Een
    hint, geen oordeel: soms is afwijken juist (bijvoorbeeld als een latere Anspruch voorvraag is voor een eerdere)."""
    uit: list[VolgordeOpmerking] = []
    paar: tuple[str, str] | None = None
    hoogste: dict[tuple | None, tuple[int, str]] = {}
    for i, regel in enumerate((skizze or "").splitlines(), 1):
        if m := _PARTIJEN.search(regel):
            nieuw = (m.group(1), m.group(2))
            if nieuw != paar:
                paar = nieuw
        if not _ANSPRUCH.search(regel):
            continue
        for v in citaties.vind(regel, "DE"):
            groep = anspruchsgroep(v)
            if groep is None:
                continue
            rang = GROEPEN.index(groep)
            norm = v.ruw.strip()
            vorige = hoogste.get(paar)
            if vorige and rang < vorige[0]:
                uit.append(VolgordeOpmerking(i, norm, groep, vorige[1], GROEPEN[vorige[0]]))
            elif vorige is None or rang > vorige[0]:
                hoogste[paar] = (rang, norm)
            break  # één Anspruchsgrundlage per regel
    return uit


@dataclass
class GenoemdeNorm:
    tekst: str
    url: str | None
    gevonden: bool
    aangenomen: bool = False
    onbekend: str | None = None


def genoemde_normen(db: Session, tekst: str, stelsel: str = "DE") -> list[GenoemdeNorm]:
    """Elke norm die in de tekst genoemd wordt, één keer, met of ze in de lokale wettekst staat."""
    k = Koppelaar(db, stelsel)
    uit: list[GenoemdeNorm] = []
    gezien: set = set()
    for v in citaties.vind(tekst or "", stelsel):
        if v.onbekend:
            if v.ruw not in gezien:
                gezien.add(v.ruw)
                uit.append(GenoemdeNorm(v.ruw, None, False, onbekend=v.onbekend))
            continue
        for e in v.elementen:
            r = e.ref
            if r is None or (r.stelsel, r.wet, r.nummer) in gezien:
                continue
            gezien.add((r.stelsel, r.wet, r.nummer))
            er = k.bestaat(r)
            uit.append(GenoemdeNorm(Ref(r.stelsel, r.nummer, r.wet, r.tot).citeer, r.url if er else None, er, v.aangenomen))
    return uit


_GUTACHTEN = re.compile(r"\b(könnte|könnten|müsste|müssten|dürfte|fraglich|zu prüfen|in Betracht|voraussetz\w*|somit|folglich|mithin|demnach|also|daher)\b", re.I)
_URTEIL = re.compile(r"\b(da|weil|denn|nämlich)\b", re.I)


def stijl_telling(tekst: str) -> dict:
    """Een ruwe telling: woorden die bij Gutachtenstil horen (könnte, fraglich, folglich) tegenover die van Urteilsstil
    (da, weil, denn). Geen oordeel; het laat alleen zien welke kant de tekst op helt."""
    return {"gutachten": len(_GUTACHTEN.findall(tekst or "")), "urteil": len(_URTEIL.findall(tekst or "")),
            "woorden": len((tekst or "").split())}


# --- casussen en pogingen ------------------------------------------------------------------------------------------------


def casussen(db: Session, profiel_id: int) -> list[Casus]:
    """Eigen casussen en de voorbeeldcasussen, nieuwste eerst."""
    return list(db.scalars(select(Casus).where((Casus.profiel_id == profiel_id) | Casus.profiel_id.is_(None))
                           .options(selectinload(Casus.pogingen)).order_by(Casus.profiel_id.is_(None), Casus.id.desc())).all())


def van(db: Session, profiel_id: int, cid: int) -> Casus | None:
    c = db.get(Casus, cid)
    return c if c is not None and c.profiel_id in (None, profiel_id) else None


def lees_normen(tekst: str) -> list[str]:
    """"§ 119 BGB; § 122 BGB" of één per regel → lijst."""
    return [n.strip() for n in re.split(r"[;\n]+", tekst or "") if n.strip()][:40]


def maak(db: Session, profiel_id: int, titel: str, sachverhalt: str, fallfrage: str = "", niveau: str = "ag", vak: str = "",
         onderwerp: str = "", normen: str | list = "") -> Casus:
    """Een zelf geplakte casus. Zonder opgegeven normen: de normen die in de tekst zelf staan."""
    sachverhalt = sachverhalt.strip()[:MAX_TEKST]
    lijst = normen if isinstance(normen, list) else lees_normen(normen)
    if not lijst:
        lijst = [r.citeer for r in citaties.refs(f"{sachverhalt}\n{fallfrage}", "DE")][:40]
    c = Casus(profiel_id=profiel_id, titel=(titel.strip() or _titel_uit(sachverhalt))[:200], sachverhalt=sachverhalt,
              fallfrage=fallfrage.strip() or None, niveau=niveau if niveau in CASUS_NIVEAUS else "ag", vak=vak.strip()[:60] or None,
              onderwerp=onderwerp.strip()[:200] or None, normen=lijst, herkomst="eigen", geverifieerd=False)
    db.add(c)
    db.flush()
    return c


def _titel_uit(sachverhalt: str) -> str:
    eerste = re.split(r"(?<=[.!?])\s", sachverhalt.strip(), maxsplit=1)[0]
    return (eerste[:80] + "…") if len(eerste) > 80 else (eerste or "Casus")


def pogingen(db: Session, profiel_id: int, alleen_open: bool = False) -> list[CasusPoging]:
    q = select(CasusPoging).where(CasusPoging.profiel_id == profiel_id).options(selectinload(CasusPoging.casus)).order_by(CasusPoging.id.desc())
    uit = list(db.scalars(q).all())
    for p in uit:
        sluit_als_tijd_om(p)
    return [p for p in uit if p.open] if alleen_open else uit


def poging(db: Session, profiel_id: int, pid: int) -> CasusPoging | None:
    p = db.get(CasusPoging, pid)
    if p is None or p.profiel_id != profiel_id:
        return None
    sluit_als_tijd_om(p)
    return p


def start(db: Session, profiel_id: int, c: Casus, modus: str = "oefenen", limiet: int | None = None) -> CasusPoging:
    """Een nieuwe poging. Klausurmodus: de tijd loopt vanaf nu; zonder opgegeven limiet de standaardtijd van het niveau."""
    modus = "klausur" if modus == "klausur" else "oefenen"
    if modus == "klausur" and not limiet:
        limiet = c.minuten
    p = CasusPoging(casus_id=c.id, profiel_id=profiel_id, modus=modus, limiet=max(1, min(int(limiet), 600)) if limiet else None,
                    begonnen=now(), status="bezig")
    db.add(p)
    db.flush()
    return p


def _nu() -> datetime:
    return now().replace(tzinfo=None)


def rest_seconden(p: CasusPoging) -> int | None:
    """Seconden tot het einde van de tijd (0 als ze om is); None zonder limiet."""
    if p.einde is None:
        return None
    return max(0, int((p.einde.replace(tzinfo=None) - _nu()).total_seconds()))


def sluit_als_tijd_om(p: CasusPoging) -> bool:
    """In de Klausurmodus is na de limiet (plus een korte speling voor het laatste autosave) de poging ingeleverd."""
    if p.open and p.einde is not None and _nu() > p.einde.replace(tzinfo=None) + SPELING:
        p.ingeleverd, p.status = p.einde, "ingeleverd"
        return True
    return False


class Conflict(Exception):
    """Elders is een nieuwere versie bewaard."""


def bewaar(p: CasusPoging, skizze: str | None, uitwerking: str | None, revisie: int | None = None) -> int:
    """Tussentijds bewaren. `revisie`: het nummer waarop de afzender verder schreef; is de poging intussen elders bewaard,
    dan `Conflict` (de afzender moet eerst herladen). Geeft het nieuwe revisienummer."""
    if not p.open:
        raise ValueError(_("Deze poging is al ingeleverd."))
    if revisie is not None and revisie != p.revisie:
        raise Conflict()
    if skizze is not None:
        p.skizze = skizze[:MAX_TEKST]
    if uitwerking is not None:
        p.uitwerking = uitwerking[:MAX_TEKST]
    p.bewaard = now()
    p.revisie += 1
    return p.revisie


def lever_in(p: CasusPoging) -> None:
    if p.open:
        p.ingeleverd, p.status = now(), "ingeleverd"


def duur_minuten(p: CasusPoging) -> int:
    eind = (p.ingeleverd or now()).replace(tzinfo=None)
    return max(0, int((eind - p.begonnen.replace(tzinfo=None)).total_seconds() // 60))


# --- Claude: genereren, beoordelen, Musterlösung -------------------------------------------------------------------------

_PUNT = {
    "type": "object",
    "properties": {
        "niveau": {"type": "integer", "description": "1 = Anspruch (A.), 2 = Voraussetzung (I.), 3 = onderpunt (1.)"},
        "titel": {"type": "string"},
        "groep": {"type": "string", "enum": [*GROEPEN, "overig"]},
        "normen": {"type": "array", "items": {"type": "string"}},
        "inhoud": {"type": "string"},
        "probleem": {"type": "boolean", "description": "true als hier een Schwerpunkt of klassiek probleem ligt"},
    },
    "required": ["niveau", "titel", "groep", "normen", "inhoud", "probleem"],
    "additionalProperties": False,
}

GENEREER = {
    "type": "object",
    "properties": {
        "titel": {"type": "string"},
        "sachverhalt": {"type": "string"},
        "fallfrage": {"type": "string"},
        "normen": {"type": "array", "items": {"type": "string"}},
        "skizze": {"type": "array", "items": _PUNT},
    },
    "required": ["titel", "sachverhalt", "fallfrage", "normen", "skizze"],
    "additionalProperties": False,
}

_ONDERDEEL = {"type": "string", "enum": ["gut", "mangelhaft", "fehlt", "entfaellt"]}

BEOORDELING = {
    "type": "object",
    "properties": {
        "punkte": {"type": "integer", "description": "0 tot en met 18 Punkte"},
        "gesamturteil": {"type": "string"},
        "staerken": {"type": "array", "items": {"type": "string"}},
        "schwaechen": {"type": "array", "items": {"type": "string"}},
        "aufbau": {
            "type": "object",
            "properties": {"urteil": {"type": "string", "enum": ["richtig", "teilweise", "falsch"]}, "kommentar": {"type": "string"}},
            "required": ["urteil", "kommentar"],
            "additionalProperties": False,
        },
        "stil": {
            "type": "object",
            "properties": {
                "urteil": {"type": "string", "enum": ["gutachtenstil", "gemischt", "urteilsstil"]},
                "kommentar": {"type": "string"},
                "beispiele": {"type": "array", "items": {
                    "type": "object",
                    "properties": {"zitat": {"type": "string"}, "problem": {"type": "string"}, "besser": {"type": "string"}},
                    "required": ["zitat", "problem", "besser"],
                    "additionalProperties": False,
                }},
            },
            "required": ["urteil", "kommentar", "beispiele"],
            "additionalProperties": False,
        },
        "schwerpunkte": {
            "type": "object",
            "properties": {"urteil": {"type": "string", "enum": ["angemessen", "teilweise", "verfehlt"]}, "kommentar": {"type": "string"}},
            "required": ["urteil", "kommentar"],
            "additionalProperties": False,
        },
        "pruefungspunkte": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "titel": {"type": "string"},
                "normen": {"type": "array", "items": {"type": "string"}},
                "erwartet": {"type": "string"},
                "status": {"type": "string", "enum": ["gezien", "deels", "gemist", "fout"]},
                "anspruchsgrundlage": {"type": "string", "enum": ["richtig", "falsch", "fehlt", "entfaellt"]},
                "obersatz": _ONDERDEEL, "definition": _ONDERDEEL, "subsumtion": _ONDERDEEL, "ergebnis": _ONDERDEEL,
                "kommentar": {"type": "string"},
                "probleem": {"type": "boolean"},
                "leervraag": {"type": "string"},
                "leerantwoord": {"type": "string"},
            },
            "required": ["titel", "normen", "erwartet", "status", "anspruchsgrundlage", "obersatz", "definition", "subsumtion", "ergebnis",
                         "kommentar", "probleem", "leervraag", "leerantwoord"],
            "additionalProperties": False,
        }},
        "fehlende_probleme": {"type": "array", "items": {
            "type": "object",
            "properties": {"titel": {"type": "string"}, "normen": {"type": "array", "items": {"type": "string"}}, "erklaerung": {"type": "string"},
                           "leervraag": {"type": "string"}, "leerantwoord": {"type": "string"}},
            "required": ["titel", "normen", "erklaerung", "leervraag", "leerantwoord"],
            "additionalProperties": False,
        }},
        "skizze": {"type": "array", "items": _PUNT},
    },
    "required": ["punkte", "gesamturteil", "staerken", "schwaechen", "aufbau", "stil", "schwerpunkte", "pruefungspunkte",
                 "fehlende_probleme", "skizze"],
    "additionalProperties": False,
}

MUSTER = {
    "type": "object",
    "properties": {"musterloesung": {"type": "string"}},
    "required": ["musterloesung"],
    "additionalProperties": False,
}

_BASIS = """Je werkt voor Pieter, rechtenstudent aan de Humboldt-Universität zu Berlin met een Nederlandse juridische
achtergrond. Hij bereidt zich voor op de Klausur Zivilrecht Ia (BGB Allgemeiner Teil en Allgemeines Schuldrecht) en
oefent het oplossen van casussen in Gutachtenstil.

Wetteksten: lees elke norm die je noemt met artikel_lezen in de lokaal geïmporteerde officiële tekst; citeer nooit een
wettekst uit je geheugen. Een norm die artikel_lezen niet vindt, noem je niet als vaststaand. Schrijf normen in de
Duitse citeerwijze met de wet erbij ("§ 280 Abs. 1 BGB", "§§ 280 Abs. 1, 3, 283 BGB").

Taal: Duitse vaktermen, Obersätze, definities en de tekst van een Sachverhalt of Musterlösung in het Duits; uitleg en
commentaar in het {taal}. Lege velden als lege string of lege lijst."""

_GENEREER = _BASIS + """

Opdracht: schrijf een casus voor een {niveau}.
- De Sachverhalt in het Duits, zoals in een Duitse Klausur: neutraal verteld, met alle feiten die de oplossing nodig
  heeft en zonder juridische kwalificaties. Personen met een letter (K, V, M). Sluit af met de Fallfrage(n) in het
  veld `fallfrage`, niet in de Sachverhalt zelf.
- Omvang en moeilijkheid passen bij het niveau: een AG-Fall heeft één of twee Schwerpunkte en is in een uur te
  doen; een Klausur van 2 uur drie tot vier; een Klausur van 5 uur meerdere Ansprüche tussen meerdere partijen.
- `normen`: alle normen die de oplossing raakt, elk met artikel_lezen gecontroleerd.
- `skizze`: de Lösungsskizze als platte lijst in de volgorde van de oplossing. `niveau` 1 is een Anspruch ("A. Anspruch K
  gegen V aus § 433 Abs. 1 S. 1 BGB"), 2 een Voraussetzung of stap ("I. Anspruch entstanden"), 3 een onderpunt. Zet de
  Ansprüche in de volgorde Vertrag, vertragsähnlich, dinglich, Delikt, Bereicherung en geef bij elk punt de `groep`.
  `inhoud`: wat hier in één of twee zinnen te zeggen is, met het resultaat. `probleem` is true waar een Schwerpunkt ligt.
- De oplossing moet volgen uit de wet en de heersende leer; vermijd casussen waarvan de uitkomst omstreden is zonder
  dat de Streitstand zelf het onderwerp is."""

_BEOORDEEL = _BASIS + """

Opdracht: beoordeel de uitwerking van een casus zoals een Korrekturassistent dat doet, streng en concreet.
- Stel eerst voor jezelf vast wat een goede oplossing bevat. Is er een Lösungsskizze meegegeven, dan is die de
  maatstaf (en blijft `skizze` leeg); zo niet, maak er zelf een en geef die terug in `skizze` (zelfde vorm: `niveau` 1
  Anspruch, 2 Voraussetzung, 3 onderpunt).
- `pruefungspunkte`: één regel per Prüfungspunkt van de goede oplossing, in haar volgorde. `status`: gezien (behandeld
  en juist), deels (aangeraakt maar onvolledig of oppervlakkig), gemist (niet behandeld), fout (behandeld maar onjuist).
  `anspruchsgrundlage`, `obersatz`, `definition`, `subsumtion`, `ergebnis`: gut, mangelhaft, fehlt, of entfaellt als
  het onderdeel op dit punt niet aan de orde is. `kommentar`: wat er concreet aan schort en hoe het beter kan.
  `probleem`: true als hier een Schwerpunkt ligt. Bij elk punt dat niet 'gezien' is: een `leervraag` en `leerantwoord`
  voor een leerkaart (één ding, het antwoord hooguit 80 woorden, met de norm).
- `fehlende_probleme`: problemen die de uitwerking helemaal niet zag en die niet al als Prüfungspunkt staan.
- `aufbau`: klopt de volgorde van de Anspruchsgrundlagen (Vertrag, vertragsähnlich, dinglich, Delikt, Bereicherung)
  en de opbouw per Anspruch (entstanden, nicht untergegangen, durchsetzbar)?
- `stil`: Gutachtenstil of Urteilsstil; geef tot drie citaten uit de uitwerking waar de stijl misgaat, met een betere
  formulering. Urteilsstil is goed waar een punt onproblematisch is; reken dat niet aan.
- `schwerpunkte`: is de ruimte verdeeld naar het gewicht van de problemen?
- `punkte`: 0 tot 18 op de Duitse schaal (4 = ausreichend, 9 = befriedigend, 13 = gut). Een lege of zeer korte
  uitwerking krijgt weinig punten, ook als de skizze goed is.
- Beoordeel wat er staat, niet wat de schrijver bedoeld kan hebben. Is alleen een skizze ingeleverd, beoordeel dan de
  skizze en zeg dat in `gesamturteil`."""

_MUSTER = _BASIS + """

Opdracht: schrijf de Musterlösung van de casus, volledig in het Duits en in Gutachtenstil, zoals in een Duitse
Fallsammlung: per Anspruch een kop, dan Obersatz, Voraussetzungen met Definition en Subsumtion, en het Ergebnis.
Onproblematische punten kort (Urteilsstil mag daar), Schwerpunkte uitgewerkt, bij een Streitstand de standpunten met
argumenten en een Stellungnahme. Markdown met koppen (`##`, `###`). Volg de meegegeven Lösungsskizze als die er is.
Noem bij rechtspraak alleen vindplaatsen waarvan je zeker bent; anders "st. Rspr." of "h.M." zonder vindplaats."""


def _taalnaam(taal: str | None) -> str:
    return {"nl": "Nederlands", "de": "Duits", "fr": "Frans", "it": "Italiaans", "en": "Engels", "es": "Spaans"}.get(taal or "nl", "Nederlands") \
        if (taal or "nl") in TALEN else "Nederlands"


def _skizze_tekst(skizze: list | None) -> str:
    regels = []
    for p in skizze or []:
        if not isinstance(p, dict):
            continue
        inspring = "  " * (max(1, min(int(p.get("niveau") or 1), 4)) - 1)
        normen = ", ".join(p.get("normen") or [])
        regels.append(f"{inspring}- {p.get('titel', '')}" + (f" [{normen}]" if normen else "") + (" (Schwerpunkt)" if p.get("probleem") else "")
                      + (f": {p.get('inhoud')}" if p.get("inhoud") else ""))
    return "\n".join(regels)


def _schoon_skizze(skizze) -> list[dict]:
    uit = []
    for p in skizze or []:
        if isinstance(p, dict) and str(p.get("titel") or "").strip():
            uit.append({"niveau": max(1, min(int(p.get("niveau") or 1), 4)), "titel": str(p["titel"]).strip()[:300],
                        "groep": p.get("groep") if p.get("groep") in GROEPEN else "overig",
                        "normen": [str(n)[:120] for n in (p.get("normen") or [])][:12], "inhoud": str(p.get("inhoud") or "").strip(),
                        "probleem": bool(p.get("probleem"))})
    return uit


def _in_thread(functie, rij_id: int, taal: str, db: Session) -> None:
    """Op de achtergrond met een eigen sessie; zonder `ACHTERGROND` (tests) meteen, in de sessie van de aanroeper."""
    if ACHTERGROND:
        threading.Thread(target=functie, args=(rij_id, taal), daemon=True).start()
    else:
        functie(rij_id, taal, db)


def _sessie(db: Session | None):
    from ..db import session_factory

    return (db, False) if db is not None else (session_factory()(), True)


def genereer(db: Session, profiel_id: int, onderwerp: str, niveau: str = "ag", vak: str = "", normen: str = "", aanwijzing: str = "",
             taal: str = "nl") -> Casus:
    """Laat Claude een casus schrijven. De casus staat meteen in de lijst (status wacht) en wordt op de achtergrond gevuld."""
    niveau = niveau if niveau in CASUS_NIVEAUS else "ag"
    delen = [f"Onderwerp: {onderwerp.strip()}"]
    if lees_normen(normen):
        delen.append("Deze normen moeten erin voorkomen: " + "; ".join(lees_normen(normen)))
    if aanwijzing.strip():
        delen.append(f"Extra aanwijzing: {aanwijzing.strip()}")
    c = Casus(profiel_id=profiel_id, titel=onderwerp.strip()[:200] or "Casus", sachverhalt="", niveau=niveau, vak=vak.strip()[:60] or None,
              onderwerp=onderwerp.strip()[:200] or None, herkomst="claude", geverifieerd=False, status="wacht", opdracht="\n".join(delen),
              normen=lees_normen(normen))
    db.add(c)
    db.commit()
    _in_thread(_genereer, c.id, taal, db)
    return c


def _genereer(cid: int, taal: str = "nl", db: Session | None = None) -> None:
    db, eigen = _sessie(db)
    try:
        c = db.get(Casus, cid)
        if c is None:
            return
        c.status = "bezig"
        db.commit()
        try:
            r, usd = claude.loop(db, "casus", _GENEREER.format(taal=_taalnaam(taal), niveau=CASUS_NIVEAUS[c.niveau][0]), c.opdracht or c.titel,
                                 GENEREER, effort="high", max_rondes=20, max_zoekacties=0)
            c = db.get(Casus, cid)
            if not str(r.get("sachverhalt") or "").strip():
                raise claude.ClaudeFout(_("Claude gaf geen Sachverhalt."))
            c.titel = str(r.get("titel") or c.titel).strip()[:200]
            c.sachverhalt, c.fallfrage = str(r["sachverhalt"]).strip(), str(r.get("fallfrage") or "").strip() or None
            c.normen = [str(n)[:120] for n in (r.get("normen") or [])][:40] or c.normen
            c.skizze = _schoon_skizze(r.get("skizze"))
            c.model, c.usd, c.status, c.fout = settings.claude_model, (c.usd or 0) + usd, "klaar", None
        except Exception as e:  # ClaudeFout of de API zelf: de casus blijft staan met de melding
            log.exception("casus %s genereren", cid)
            db.rollback()
            c = db.get(Casus, cid)
            c.status, c.fout = "fout", str(e)[:2000] or type(e).__name__
        db.commit()
    finally:
        if eigen:
            db.close()


def _beoordeel_prompt(p: CasusPoging) -> str:
    c = p.casus
    delen = [f"Niveau: {CASUS_NIVEAUS.get(c.niveau, (c.niveau,))[0]}", f"<sachverhalt>\n{c.sachverhalt}\n</sachverhalt>"]
    if c.fallfrage:
        delen.append(f"<fallfrage>\n{c.fallfrage}\n</fallfrage>")
    if c.normen:
        delen.append("Normen die de casus raakt: " + "; ".join(c.normen))
    if c.skizze:
        delen.append(f"<loesungsskizze>\n{_skizze_tekst(c.skizze)}\n</loesungsskizze>")
    else:
        delen.append("Er is geen Lösungsskizze: maak er zelf een en geef die terug in `skizze`.")
    delen.append(f"Modus: {'Klausur' if p.modus == 'klausur' else 'oefenen'}; gewerkt: {duur_minuten(p)} minuten"
                 + (f" van {p.limiet}" if p.limiet else "") + ".")
    delen.append(f"<skizze_van_de_student>\n{p.skizze.strip() or '(leeg)'}\n</skizze_van_de_student>")
    delen.append(f"<uitwerking_van_de_student>\n{p.uitwerking.strip() or '(leeg)'}\n</uitwerking_van_de_student>")
    return "\n\n".join(delen)


def beoordeel(db: Session, p: CasusPoging, taal: str = "nl") -> None:
    """Start de beoordeling door Claude (levert eerst in als dat nog niet gebeurd is)."""
    if not (p.skizze.strip() or p.uitwerking.strip()):
        raise ValueError(_("Er is nog niets geschreven om te beoordelen."))
    lever_in(p)
    p.status, p.fout = "wacht", None
    db.commit()
    _in_thread(_beoordeel, p.id, taal, db)


def _beoordeel(pid: int, taal: str = "nl", db: Session | None = None) -> None:
    db, eigen = _sessie(db)
    try:
        p = db.get(CasusPoging, pid)
        if p is None:
            return
        p.status = "beoordelen"
        db.commit()
        try:
            r, usd = claude.loop(db, "klausur", _BEOORDEEL.format(taal=_taalnaam(taal)), _beoordeel_prompt(p), BEOORDELING,
                                 effort="high", max_rondes=20, max_zoekacties=0)
            p = db.get(CasusPoging, pid)
            verwerk_beoordeling(db, p, r)
            p.model, p.usd, p.status, p.fout = settings.claude_model, (p.usd or 0) + usd, "beoordeeld", None
        except Exception as e:
            log.exception("poging %s beoordelen", pid)
            db.rollback()
            p = db.get(CasusPoging, pid)
            p.status, p.fout = "fout", str(e)[:2000] or type(e).__name__
        db.commit()
    finally:
        if eigen:
            db.close()


_STATUS = {"gezien", "deels", "gemist", "fout"}


def verwerk_beoordeling(db: Session, p: CasusPoging, r: dict) -> None:
    """Slaat de beoordeling op en zet elk Prüfungspunkt en elk gemist probleem als `CasusProbleem` klaar."""
    try:
        punkte = max(0, min(18, int(r.get("punkte"))))
    except (TypeError, ValueError):
        punkte = None
    r = {**r, "punkte": punkte}
    eigen_skizze = _schoon_skizze(r.pop("skizze", None))
    if eigen_skizze and not p.casus.skizze:
        p.casus.skizze = eigen_skizze
    p.beoordeling = r
    for oud in list(p.problemen):
        if oud.kaart_id is None:
            db.delete(oud)
    db.flush()
    k = Koppelaar(db)

    def voeg_toe(titel, normen, status, uitleg, vraag, antwoord):
        normen = [str(n)[:120] for n in (normen or []) if str(n).strip()][:12]
        ref = next((x for x in (k.ref(n) for n in normen) if x is not None), None)
        db.add(CasusProbleem(poging_id=p.id, profiel_id=p.profiel_id, titel=str(titel or "").strip()[:300] or "?", normen=normen,
                             stelsel_code=ref.stelsel if ref else None, wet=ref.wet if ref else None, nummer=ref.nummer if ref else None,
                             detail=ref.detail if ref else None, status=status if status in _STATUS else "gemist",
                             uitleg=str(uitleg or "").strip() or None, leervraag=str(vraag or "").strip() or None,
                             leerantwoord=str(antwoord or "").strip() or None))

    for pp in r.get("pruefungspunkte") or []:
        if isinstance(pp, dict):
            voeg_toe(pp.get("titel"), pp.get("normen"), pp.get("status"), pp.get("kommentar") or pp.get("erwartet"), pp.get("leervraag"),
                     pp.get("leerantwoord"))
    for fp in r.get("fehlende_probleme") or []:
        if isinstance(fp, dict):
            voeg_toe(fp.get("titel"), fp.get("normen"), "gemist", fp.get("erklaerung"), fp.get("leervraag"), fp.get("leerantwoord"))
    db.flush()


def muster(db: Session, c: Casus, taal: str = "nl") -> None:
    """Laat Claude de Musterlösung schrijven (op de achtergrond; de pagina toont de stand)."""
    c.muster_status, c.muster_fout = "wacht", None
    db.commit()
    _in_thread(_muster, c.id, taal, db)


def _muster(cid: int, taal: str = "nl", db: Session | None = None) -> None:
    db, eigen = _sessie(db)
    try:
        c = db.get(Casus, cid)
        if c is None:
            return
        c.muster_status = "bezig"
        db.commit()
        try:
            prompt = f"<sachverhalt>\n{c.sachverhalt}\n</sachverhalt>" + (f"\n\n<fallfrage>\n{c.fallfrage}\n</fallfrage>" if c.fallfrage else "")
            if c.skizze:
                prompt += f"\n\n<loesungsskizze>\n{_skizze_tekst(c.skizze)}\n</loesungsskizze>"
            r, usd = claude.loop(db, "muster", _MUSTER.format(taal=_taalnaam(taal)), prompt, MUSTER, effort="high", max_rondes=20,
                                 max_zoekacties=0, max_tokens=48000)
            c = db.get(Casus, cid)
            tekst = str(r.get("musterloesung") or "").strip()
            if not tekst:
                raise claude.ClaudeFout(_("Claude gaf geen Musterlösung."))
            c.musterloesung, c.muster_status, c.muster_fout = tekst, "klaar", None
            c.usd = (c.usd or 0) + usd
            c.model = c.model or settings.claude_model
        except Exception as e:
            log.exception("casus %s musterlösung", cid)
            db.rollback()
            c = db.get(Casus, cid)
            c.muster_status, c.muster_fout = "fout", str(e)[:2000] or type(e).__name__
        db.commit()
    finally:
        if eigen:
            db.close()


# --- leren: kaartvoorstel en wat je steeds mist ----------------------------------------------------------------------------


def kaartvoorstel(db: Session, pr: CasusProbleem) -> Kaart | None:
    """Maakt van een probleem een kaartvoorstel in de leerlijst van het vak. Bestaat de kaart al, dan die.

    Met een leervraag en -antwoord een vrije kaart; anders, als de norm in de lokale tekst staat, een artikelkaart. Het is
    een voorstel (`status="voorstel"`): pas wat je op /leren/voorstellen overneemt, gaat naar Wunderkammer."""
    if pr.kaart_id and pr.kaart is not None:
        return pr.kaart
    c = pr.poging.casus
    ref = Ref(pr.stelsel_code, pr.nummer, pr.wet or None) if pr.stelsel_code and pr.nummer else None
    vak = c.vak or (vakken.afleiden(ref.stelsel, ref.wet, ref.nummer) if ref else None) or vakken.laatste(db, pr.profiel_id) or "ZR Ia"
    lijst = vakken.lijst_voor(db, pr.profiel_id, vak)
    velden = dict(status="voorstel", actief=False, herkomst=f"Klausur/{c.titel}"[:300])
    if pr.leervraag and pr.leerantwoord:
        norm = f"\n\n{', '.join(pr.normen)}" if pr.normen and not any(n in pr.leerantwoord for n in pr.normen) else ""
        kaarten = leren.maak_kaarten(db, lijst, ["vrij"], vraag=pr.leervraag, antwoord=pr.leerantwoord + norm, **velden)
    elif ref is not None and wettekst_artikel(db, ref) is not None:
        kaarten = leren.maak_kaarten(db, lijst, ["artikel"], ref=ref, notitie=pr.uitleg or "", **velden)
    else:
        kaarten = leren.maak_kaarten(db, lijst, ["vrij"], vraag=pr.titel, antwoord=pr.uitleg or ", ".join(pr.normen or []) or "?", **velden)
    if not kaarten:  # dezelfde kaart stond er al (zelfde vraag of zelfde artikel)
        sleutel = (pr.leervraag or pr.titel).strip().lower()
        bestaand = next((k for k in lijst.kaarten if (k.soort == "vrij" and (k.vraag or "").strip().lower() == sleutel)
                         or (ref is not None and k.soort == "artikel" and (k.stelsel_code, k.wet or None, k.nummer) == (ref.stelsel, ref.wet, ref.nummer))), None)
        pr.kaart = bestaand
        return bestaand
    pr.kaart = kaarten[0]
    db.flush()
    return kaarten[0]


@dataclass
class Gemist:
    """Eén probleem over alle casussen heen: hoe vaak het aan de orde was en hoe vaak het misging."""

    sleutel: str
    titel: str
    ref: Ref | None
    keren: int = 0
    gemist: int = 0
    deels: int = 0
    laatst: datetime | None = None
    titels: list[str] = field(default_factory=list)
    casussen: dict[int, str] = field(default_factory=dict)  # casus-id → titel (waar het misging)
    pogingen: dict[int, int] = field(default_factory=dict)  # casus-id → laatste poging waar het misging
    probleem_id: int | None = None  # het meest recente gemiste probleem (voor het kaartvoorstel)
    kaart_id: int | None = None

    @property
    def score(self) -> float:
        return self.gemist + 0.5 * self.deels

    @property
    def steeds(self) -> bool:
        """In meer dan één casus misgegaan."""
        return len(self.casussen) >= 2


def steeds_gemist(db: Session, profiel_id: int) -> list[Gemist]:
    """De problemen die niet (helemaal) goed gingen, gegroepeerd op hoofdnorm (anders op titel), zwaarste eerst."""
    rijen = db.scalars(select(CasusProbleem).where(CasusProbleem.profiel_id == profiel_id)
                       .options(selectinload(CasusProbleem.poging).selectinload(CasusPoging.casus)).order_by(CasusProbleem.id)).all()
    groepen: dict[str, Gemist] = {}
    for pr in rijen:
        ref = Ref(pr.stelsel_code, pr.nummer, pr.wet or None) if pr.stelsel_code and pr.nummer else None
        sleutel = f"{ref.stelsel}|{ref.wet or ''}|{ref.nummer}" if ref else "t|" + re.sub(r"\W+", " ", pr.titel.lower()).strip()
        g = groepen.setdefault(sleutel, Gemist(sleutel, pr.titel, ref))
        g.keren += 1
        if pr.kaart_id:
            g.kaart_id = pr.kaart_id
        if pr.status == "gezien":
            continue
        g.gemist += pr.status in ("gemist", "fout")
        g.deels += pr.status == "deels"
        g.laatst = pr.aangemaakt
        g.probleem_id = pr.id
        if pr.titel not in g.titels:
            g.titels.append(pr.titel)
        g.casussen[pr.poging.casus_id] = pr.poging.casus.titel
        g.pogingen[pr.poging.casus_id] = pr.poging_id
    return sorted((g for g in groepen.values() if g.score > 0), key=lambda g: (-len(g.casussen), -g.score, g.titel))
