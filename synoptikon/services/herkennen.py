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

from ..importers import cellar
from ..importers.http import client

log = logging.getLogger(__name__)

_ECLI = re.compile(r"\bECLI:([A-Z]{2}):([A-Z0-9]{1,7}):(\d{4}):([A-Z0-9.]{1,25})\b", re.I)
# Sector 6 = rechtspraak; ook sectoren 3 (wetgeving) en 5 (voorbereidend) worden herkend, maar niet opgehaald.
_CELEX = re.compile(r"(?:\bCELEX\s*[:\s]\s*)?\b([1-9CE])(\d{4})([A-Z]{1,2})(\d{4})\b", re.I)
RECHTSPRAAK = "https://data.rechtspraak.nl/uitspraken/content"
RECHTSPRAAK_WEB = "https://uitspraken.rechtspraak.nl/details?id={ecli}"
EURLEX = "https://eur-lex.europa.eu/legal-content/NL/TXT/?uri={uri}"
GERECHTEN_EU = {"C": "HvJ EU", "T": "Gerecht EU", "F": "Ambtenarengerecht EU"}
_MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus", "september", "oktober",
            "november", "december"]


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


def zoek(i: Id, c=None) -> dict | None:
    """Haalt de feiten op; None als de bron niets (of niets bruikbaars) geeft. Netwerkfouten zijn ook 'niets'."""
    eigen = c is None
    c = c or verbinding()
    try:
        if i.land == "NL":
            return _rechtspraak(i, c)
        if i.land == "EU" or (i.soort == "celex" and i.waarde[0] == "6"):
            return _cellar(i, c)
        return None
    except (httpx.HTTPError, ET.ParseError, ValueError) as e:
        log.warning("herkennen %s: %s: %s", i.waarde, type(e).__name__, e)
        return None
    finally:
        if eigen:
            c.close()


def _datum_nl(d: date) -> str:
    return f"{d.day} {_MAANDEN[d.month - 1]} {d.year}"


# --- EU: Cellar --------------------------------------------------------------------------------------------------


def _cellar_vraag(i: Id) -> str:
    sleutel = ("cdm:case-law_ecli", "?e") if i.soort == "ecli" else ("cdm:resource_legal_id_celex", "?c")
    return f"""SELECT ?ecli ?celex ?datum ?titel WHERE {{
  ?w {sleutel[0]} {sleutel[1]} . FILTER(STR({sleutel[1]}) = "{i.waarde}")
  OPTIONAL {{ ?w cdm:case-law_ecli ?ecli }}
  OPTIONAL {{ ?w cdm:resource_legal_id_celex ?celex }}
  OPTIONAL {{ ?w cdm:work_date_document ?datum }}
  OPTIONAL {{ ?x cdm:expression_belongs_to_work ?w ; cdm:expression_title ?titel ;
             cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/NLD> }}
}} LIMIT 4"""


def _cellar(i: Id, c) -> dict | None:
    rijen = cellar._query(c, _cellar_vraag(i))
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
    gerecht = GERECHTEN_EU.get(land_gerecht) or ("HvJ EU" if celex[3:5].upper() == "CJ" else "EU")
    citeer = ", ".join(x for x in [f"{gerecht} {_datum_nl(datum)}" if datum else gerecht, zaak] if x)
    if partijen:
        citeer += f" ({partijen})"
    if not (zaak or partijen or datum):
        return None  # alleen een ID zonder metadata: geen feiten, dus ook geen antwoord
    uri = f"ecli:{ecli}" if ecli else f"CELEX:{celex}"
    return dict(soort="uitspraak", stelsel="EU", citeer=citeer, titel=partijen or citeer,
                vindplaats=ecli or celex, celex=celex, url=EURLEX.format(uri=uri),
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
    citeer = ", ".join(x for x in [f"{kort} {_datum_nl(datum)}" if datum else kort, meta.get("zaaknummer", ""), i.waarde] if x)
    return dict(soort="uitspraak", stelsel="NL", citeer=citeer, titel=citeer, vindplaats=i.waarde,
                url=RECHTSPRAAK_WEB.format(ecli=i.waarde),
                plaats=", ".join(x for x in [instantie, _datum_nl(datum) if datum else "", meta.get("zaaknummer", "")] if x),
                tekst="", tekst_herkomst="geen", toelichting=inhoud, artikelverwijzing="", zekerheid="hoog", bron="rechtspraak")
