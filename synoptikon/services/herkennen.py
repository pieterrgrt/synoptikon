"""Identificaties herkennen en ophalen: ECLI en CELEX, vóór Claude.

Een ECLI (`ECLI:<land>:<gerecht>:<jaar>:<nummer>`) en een CELEX-nummer zijn vaste formaten; wat erbij hoort (zaaknaam,
zaaknummer, datum, gerecht, link) is een feit en hoeft niet geraden te worden. Per land:

- `EU`: de Cellar van het Publicatiebureau (SPARQL, zoals `importers/cellar.py`), dezelfde gegevens als EUR-Lex. Ook
  een CELEX-nummer van rechtspraak (sector 6, `62014CJ0594`) gaat zo.
- `NL`: de open data van rechtspraak.nl (`data.rechtspraak.nl/uitspraken/content`): instantie, datum, zaaknummer en de
  inhoudsindicatie.
- andere landen: niet herkend; dat is aan Claude.

`herken_id` kijkt alleen naar de tekst; `zoek` gaat het netwerk op en geeft een resultaat in de vorm van
`Opzoeking.resultaat`, of None als er niets te vinden was (dan neemt Claude het over).
"""
from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date
from urllib.parse import unquote

import httpx

from ..i18n import rechtstaal
from ..importers import cellar
from ..importers.http import client

log = logging.getLogger(__name__)

_ECLI = re.compile(r"\bECLI:([A-Z]{2}):([A-Z0-9]{1,7}):(\d{4}):([A-Z0-9.]{1,25})\b", re.I)
# Sector 6 = rechtspraak; ook sectoren 3 (wetgeving) en 5 (voorbereidend) worden herkend, maar niet opgehaald.
_CELEX = re.compile(r"(?:\bCELEX\s*[:\s]\s*)?\b([1-9CE])(\d{4})([A-Z]{1,2})(\d{4})\b", re.I)
RECHTSPRAAK = "https://data.rechtspraak.nl/uitspraken/content"
RECHTSPRAAK_WEB = "https://uitspraken.rechtspraak.nl/details?id={ecli}"
EURLEX = "https://eur-lex.europa.eu/legal-content/{taal}/TXT/?uri={uri}"
# Cellar werkt met drieletterige taalcodes; EUR-Lex met tweeletterige in de URL.
_CELLAR_TAAL = {"nl": "NLD", "de": "DEU", "fr": "FRA", "it": "ITA", "en": "ENG", "es": "SPA"}
# De naam van het gerecht is een juridische afkorting en volgt dus de rechtstaal, niet de interface.
GERECHTEN_EU: dict[str, dict[str, str]] = {
    "C": dict(nl="HvJ EU", de="EuGH", fr="CJUE", it="CGUE", en="CJEU", es="TJUE"),
    "T": dict(nl="Gerecht EU", de="EuG", fr="Trib. UE", it="Trib. UE", en="General Court", es="TG UE"),
    "F": dict(nl="Ambtenarengerecht EU", de="EuGöD", fr="TFP UE", it="TFP UE", en="CST", es="TFP UE"),
}
_HVJ = {"nl": "HvJ EU", "de": "EuGH", "fr": "CJUE", "it": "CGUE", "en": "CJEU", "es": "TJUE"}
_MAANDEN: dict[str, list[str]] = {
    "nl": ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober",
           "november", "december"],
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
           "November", "Dezember"],
    "fr": ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre",
           "novembre", "décembre"],
    "it": ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre",
           "novembre", "dicembre"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"],
    "es": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
           "noviembre", "diciembre"],
}


@dataclass(frozen=True)
class Id:
    soort: str  # ecli | celex
    waarde: str  # ECLI:EU:C:2015:806, 62014CJ0594
    land: str | None = None  # alleen bij ECLI

    @property
    def bron(self) -> str:
        """Waar het opgehaald wordt (voor het knoptekstje en het logboek)."""
        return "rechtspraak.nl" if self.land == "NL" else "EUR-Lex"


def herken_id(q: str) -> Id | None:
    """Een ECLI of CELEX-nummer in de invoer (ook in een geplakte EUR-Lex-link), anders None."""
    q = unquote(q or "").strip()
    if m := _ECLI.search(q):
        ecli = ":".join(["ECLI", *(x.upper() for x in m.groups())])
        return Id("ecli", ecli, m.group(1).upper())
    # Een CELEX-nummer alleen als het (bijna) de hele invoer is of expliciet CELEX heet: anders is '32016R0679' ruis.
    if m := _CELEX.fullmatch(q) or (_CELEX.search(q) if re.search(r"CELEX|eur-lex", q, re.I) else None):
        sector, jaar, soort, nr = m.groups()
        return Id("celex", f"{sector}{jaar}{soort}{nr}".upper())
    return None


def verbinding():
    return client(timeout=25.0, headers={"User-Agent": "Synoptikon/0.1 (persoonlijke rechtsvergelijkingsapp)"})


def zoek(i: Id, c=None, taal: str | None = None) -> dict | None:
    """Haalt de feiten op; None als de bron niets (of niets bruikbaars) geeft. Netwerkfouten zijn ook 'niets'.

    `taal` is de rechtstaal: in die taal worden de titel van een EU-arrest, de naam van het gerecht en de
    EUR-Lex-link opgehaald. Standaard de rechtstaal van het verzoek."""
    eigen = c is None
    taal = taal or rechtstaal()
    c = c or verbinding()
    try:
        if i.land == "NL":
            return _rechtspraak(i, c)
        if i.land == "EU" or (i.soort == "celex" and i.waarde[0] == "6"):
            return _cellar(i, c, taal)
        return None
    except (httpx.HTTPError, ET.ParseError, ValueError) as e:
        log.warning("herkennen %s: %s: %s", i.waarde, type(e).__name__, e)
        return None
    finally:
        if eigen:
            c.close()


def _datum(d: date, taal: str = "nl") -> str:
    """De datum zoals ze in een citaat staat: '10 december 2015', '10. Dezember 2015', '10 de diciembre de 2015'."""
    maand = _MAANDEN.get(taal, _MAANDEN["nl"])[d.month - 1]
    if taal == "de":
        return f"{d.day}. {maand} {d.year}"
    if taal == "es":
        return f"{d.day} de {maand} de {d.year}"
    return f"{d.day} {maand} {d.year}"


# --- EU: Cellar --------------------------------------------------------------------------------------------------


def _cellar_vraag(i: Id, taal: str = "nl") -> str:
    sleutel = ("cdm:case-law_ecli", "?e") if i.soort == "ecli" else ("cdm:resource_legal_id_celex", "?c")
    return f"""SELECT ?ecli ?celex ?datum ?titel WHERE {{
  ?w {sleutel[0]} {sleutel[1]} . FILTER(STR({sleutel[1]}) = "{i.waarde}")
  OPTIONAL {{ ?w cdm:case-law_ecli ?ecli }}
  OPTIONAL {{ ?w cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?w cdm:work_date_document ?datum }}
  OPTIONAL {{ ?x cdm:expression_belongs_to_work ?w ; cdm:expression_title ?titel ;
             cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/{_CELLAR_TAAL.get(taal, "NLD")}> }}
}} LIMIT 4"""


def _cellar(i: Id, c, taal: str = "nl") -> dict | None:
    rijen = cellar._query(c, _cellar_vraag(i, taal))
    rij = next((r for r in rijen if r.get("titel")), rijen[0] if rijen else None)
    if rij is None:
        return None
    ecli = rij.get("ecli") or (i.waarde if i.soort == "ecli" else "")
    celex = rij.get("celex") or (i.waarde if i.soort == "celex" else "")
    datum = cellar._datum(rij.get("datum"))
    # De titel is '#'-gescheiden: 'Arrest van het Hof (Zesde kamer) van 10 december 2015.#Partijen.#Verzoek …#Zaak C-594/14.'
    delen = [d.strip() for d in (rij.get("titel") or "").split("#") if d.strip()]
    zaak = next((m.group(1) for d in reversed(delen) if (m := re.search(r"\b((?:C|T|F)[-‑]\d+/\d+(?: \w+)?)\.?$", d))), "")
    partijen = delen[1].rstrip(".") if len(delen) > 2 else ""
    land_gerecht = (ecli.split(":") + ["", "", ""])[2] if ecli else ""
    gerecht = (GERECHTEN_EU.get(land_gerecht) or {}).get(taal) \
        or (_HVJ.get(taal, "HvJ EU") if celex[3:5].upper() == "CJ" else "EU")
    citeer = ", ".join(x for x in [f"{gerecht} {_datum(datum, taal)}" if datum else gerecht, zaak] if x)
    if partijen:
        citeer += f" ({partijen})"
    if not (zaak or partijen or datum):
        return None  # alleen een ID zonder metadata: geen feiten, dus ook geen antwoord
    uri = f"ecli:{ecli}" if ecli else f"CELEX:{celex}"
    return dict(soort="uitspraak", stelsel="EU", citeer=citeer, titel=partijen or citeer,
                vindplaats=ecli or celex, celex=celex, url=EURLEX.format(taal=taal.upper(), uri=uri),
                plaats=delen[0].rstrip(".") if delen else "", tekst="", tekst_herkomst="geen",
                toelichting=" ".join(d.rstrip(".") + "." for d in delen[2:-1]),
                artikelverwijzing="", zekerheid="hoog", bron="cellar")


# --- NL: rechtspraak.nl ------------------------------------------------------------------------------------------


def _lokaal(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _rechtspraak(i: Id, c) -> dict | None:
    r = c.get(RECHTSPRAAK, params={"id": i.waarde})
    if r.status_code != 200:
        return None
    wortel = ET.fromstring(r.content)
    meta: dict[str, str] = {}
    inhoud = ""
    for el in wortel.iter():
        naam = _lokaal(el.tag)
        if naam in ("creator", "date", "zaaknummer", "identifier", "title") and naam not in meta and (el.text or "").strip():
            meta[naam] = el.text.strip()
        elif naam == "inhoudsindicatie" and not inhoud:
            inhoud = re.sub(r"\s+", " ", " ".join(el.itertext())).strip()
    if meta.get("identifier", "").upper() != i.waarde:
        return None
    try:
        datum = date.fromisoformat(meta["date"][:10])
    except (KeyError, ValueError):
        datum = None
    instantie = meta.get("creator", "")
    kort = "HR" if instantie == "Hoge Raad" else instantie
    citeer = ", ".join(x for x in [f"{kort} {_datum(datum)}" if datum else kort, meta.get("zaaknummer", ""), i.waarde] if x)
    return dict(soort="uitspraak", stelsel="NL", citeer=citeer, titel=citeer, vindplaats=i.waarde,
                url=RECHTSPRAAK_WEB.format(ecli=i.waarde),
                plaats=", ".join(x for x in [instantie, _datum(datum) if datum else "", meta.get("zaaknummer", "")] if x),
                tekst="", tekst_herkomst="geen", toelichting=inhoud, artikelverwijzing="", zekerheid="hoog", bron="rechtspraak")


# --- bestaande bronnen omzetten naar de rechtstaal -----------------------------------------------------------------


@dataclass
class Hertaald:
    bekeken: int = 0
    omgezet: int = 0
    overgeslagen: int = 0   # zelf nagekeken, of geen ECLI/CELEX om op te halen
    mislukt: int = 0        # wel een ID, maar de bron gaf niets


def hertaal(db, taal: str, doen: bool = False, maximum: int | None = None) -> Hertaald:
    """Haalt uitspraken die in een andere taal zijn opgeslagen opnieuw op in `taal`.

    Voor wie zijn rechtstaal omzet: de arresten die al in de kast staan zijn dan nog Nederlands. Er wordt niets
    vertaald — de uitspraak wordt opnieuw bij de bron opgehaald in de gevraagde taal, dus met de officiële
    zaaknaam en de juiste afkorting van het gerecht ('EuGH', niet 'HvJ EU').

    Wat je zelf hebt nagekeken (bron 'eigen') blijft staan: eigen bewerkingen winnen.
    """
    from sqlalchemy import or_, select as _select

    from ..models import Bron
    from .opzoeken import OPMERKING

    u = Hertaald()
    rijen = db.scalars(_select(Bron).where(Bron.soort == "rechtspraak", or_(Bron.taal.is_(None), Bron.taal != taal))
                       .order_by(Bron.id)).all()
    c = verbinding()
    try:
        for b in rijen:
            if maximum is not None and u.omgezet >= maximum:
                break
            u.bekeken += 1
            if (b.opmerking or "").startswith(OPMERKING["eigen"]):
                u.overgeslagen += 1
                continue
            i = herken_id(b.vindplaats or "") or herken_id(b.citeertitel or "")
            if i is None or i.land == "NL":  # een Nederlandse uitspraak citeer je niet in het Duits
                u.overgeslagen += 1
                continue
            r = zoek(i, c, taal=taal)
            if not r:
                u.mislukt += 1
                continue
            u.omgezet += 1
            if not doen:
                continue
            b.citeertitel = (r.get("citeer") or b.citeertitel)[:200]
            b.titel = (r.get("titel") or None) and r["titel"][:300]
            b.url = r.get("url") or b.url
            b.taal = taal
            if r.get("bron") in OPMERKING:
                b.opmerking = OPMERKING[r["bron"]] + (r.get("toelichting") or "")
    finally:
        c.close()
    if doen:
        db.commit()
    return u
