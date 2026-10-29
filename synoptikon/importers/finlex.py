"""FI: Finlex open data (Oikeusministeriö), Akoma Ntoso via de open API, geconsolideerd (*ajantasainen*).

`https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/{jaar}/{nr}` geeft de
geldende stand van een wet als een lijst <akomaNtoso>-documenten: Fins en Zweeds, en soms meer dan één
Finse stand (een wijziging die al is verwerkt naast een die later in werking treedt). We nemen de Finse
met de jongste consolidatie (ELI-alias `…/ajantasa/{datum}/fin`).

Structuur: (part ›) chapter › section, met <num>"5 luku"</num>/<heading>; <crossHeading> tussen de
paragrafen van een hoofdstuk is een kop boven de volgende paragrafen (een eenheid in het pad). Een section
heeft <num>"3 a §"</num>, een eventuele <heading> (opschrift) en <subsection>-leden (*momentit*, niet
genummerd) met <intro> en <paragraph>-opsommingen ("1)"). Auteursnoten (noteAuthorial) en de
inwerkingtredingsbepalingen van wijzigingswetten vallen weg.

Nummering: begint de paragraafnummering per hoofdstuk opnieuw (de *kaaret*, KSL, OYL), dan is het nummer
"hoofdstuk:paragraaf" zoals men in Finland citeert ("RL 21:1", "KSL 7 a:14 a"); anders alleen de paragraaf
("OikTL 36 §").

Versie: "ajantasa 2026-09-04 (835/2026)": datum van de consolidatie en de laatst verwerkte wijzigingswet.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from . import Artikel, Geparseerd
from .http import client

URL = "https://opendata.finlex.fi/finlex/avoindata/v1/akn/fi/act/statute-consolidated/{id}"
WEB = "https://www.finlex.fi/fi/lainsaadanto/{id}"
NS = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
_STRUCTUUR = {"part", "title", "chapter"}


def _naam(el: ET.Element) -> str:
    return el.tag.removeprefix(NS)


def _weg(el: ET.Element) -> bool:
    if _naam(el) == "ref" and el.get("href", "").startswith("#entryIntoForce") and (el.text or "").strip().startswith("("):
        return True  # "(17.12.1982/956)" achter een kop of lid: de wijzigingswet, geen tekst
    return el.get("name") in ("noteAuthorial", "amendmentEntryIntoForceAndApplianceProvisions") or _naam(el) in ("authorialNote", "num", "heading")


def _tekst(el: ET.Element | None) -> str:
    if el is None:
        return ""
    delen: list[str] = []

    def loop(e: ET.Element) -> None:
        if e.text:
            delen.append(e.text)
        for k in e:
            if not _weg(k):
                loop(k)
            if k.tail:
                delen.append(k.tail)

    loop(el)
    return re.sub(r"\s+", " ", "".join(delen)).strip()


def _kind(el: ET.Element, naam: str) -> ET.Element | None:
    return el.find(NS + naam)


def _kop(el: ET.Element) -> str:
    return " ".join(t for t in (_tekst(_kind(el, "num")) if _kind(el, "num") is not None else "",
                                _tekst(_kind(el, "heading")) if _kind(el, "heading") is not None else "") if t)


def _num(el: ET.Element) -> str:
    n = _kind(el, "num")
    return re.sub(r"\s+", " ", "".join(n.itertext())).strip() if n is not None else ""


def _regels(el: ET.Element, inspring: str = "") -> list[str]:
    """Tekstregels van een lid: inleiding, opsomming ("1) …", met subparagraphs), slot."""
    uit: list[str] = []
    for k in el:
        if _weg(k):
            continue
        n = _naam(k)
        if n in ("content", "intro", "wrapUp"):
            t = _tekst(k)
            if t:
                uit.append(inspring + t)
        elif n in ("paragraph", "subparagraph", "point", "list"):
            sub = _regels(k, inspring)
            if _num(k) and sub:
                sub[0] = f"{inspring}{_num(k)} {sub[0].removeprefix(inspring)}"
            uit.extend(sub)
    return uit


def _paragraaf(sec: ET.Element) -> str:
    leden = [_regels(s) for s in sec.findall(NS + "subsection")]
    if not leden:
        leden = [_regels(sec)]
    return "\n\n".join("\n".join(lid) for lid in leden if lid)


def _sectienummer(sec: ET.Element) -> str | None:
    m = re.match(r"(\d+(?:\s?[a-zäö](?![a-zäö]))?)\s*§", _num(sec))
    return re.sub(r"(\d)\s?([a-zäö])", r"\1 \2", m.group(1)) if m else None


def _hoofdstuknummer(ch: ET.Element) -> str | None:
    m = re.match(r"(\d+(?:\s?[a-zäö](?![a-zäö]))?)\s*luku", _num(ch))
    return re.sub(r"(\d)\s?([a-zäö])", r"\1 \2", m.group(1)) if m else None


def _kies(data: bytes) -> tuple[bytes, ET.Element]:
    """De Finse stand met de jongste consolidatie, als bytes (voor `ruw`) en als element."""
    stukken = [b"<akomaNtoso" + s for s in re.split(rb"<akomaNtoso", data)[1:]]
    stukken = [re.sub(rb"</Results>\s*</AknXmlList>\s*$", b"", s) for s in stukken] or [data]
    beste: tuple[str, bytes, ET.Element] | None = None
    for s in stukken:
        el = ET.fromstring(s)
        expr = el.find(f".//{NS}FRBRExpression")
        taal = expr.find(NS + "FRBRlanguage").get("language") if expr is not None else "fin"
        if taal != "fin":
            continue
        alias = expr.find(NS + "FRBRalias").get("value", "") if expr is not None else ""
        if beste is None or alias > beste[0]:
            beste = (alias, s, el)
    if beste is None:
        raise ValueError("geen Finse tekst in de Finlex-respons")
    return beste[1], beste[2]


def parse(data: bytes, id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    ruw, root = _kies(data)
    body = root.find(f".//{NS}body")
    secties: list[tuple[str | None, ET.Element, list[str]]] = []  # (hoofdstuk, section, pad)

    def loop(el: ET.Element, pad: list[str], hoofdstuk: str | None) -> None:
        kruis: str | None = None
        for k in el:
            if _weg(k):
                continue
            n = _naam(k)
            if n in _STRUCTUUR:
                kop = _kop(k)
                loop(k, [*pad, kop] if kop else pad, _hoofdstuknummer(k) if n == "chapter" else hoofdstuk)
                kruis = None
            elif n == "crossHeading":
                kruis = _tekst(k) or None
            elif n == "section":
                secties.append((hoofdstuk, k, [*pad, kruis] if kruis else pad))
            elif n == "hcontainer" and k.get("name") == "statuteProvisionsWrapper":
                loop(k, pad, hoofdstuk)

    loop(body if body is not None else root, [], None)
    nummers = [_sectienummer(s) for _, s, _ in secties]
    per_hoofdstuk = any(h for h, _, _ in secties) and len([n for n in nummers if n]) > len(set(n for n in nummers if n))
    artikelen: list[Artikel] = []
    gezien: set[str] = set()
    for (hoofdstuk, sec, pad), nr in zip(secties, nummers):
        if nr is None:
            continue
        if per_hoofdstuk and hoofdstuk:
            nr = f"{hoofdstuk}:{nr}"
        if nr in gezien:
            continue
        gezien.add(nr)
        kop = _kind(sec, "heading")
        artikelen.append(Artikel(nummer=nr, tekst=_paragraaf(sec) or "(kumottu)", opschrift=_tekst(kop) or None if kop is not None else None,
                                 pad=" › ".join(pad) or None))
    expr = root.find(f".//{NS}FRBRExpression")
    alias = expr.find(NS + "FRBRalias").get("value", "") if expr is not None else ""
    datum = re.search(r"/ajantasa/(\d{4}-\d{2}-\d{2})", alias)
    vnr = expr.find(NS + "FRBRversionNumber") if expr is not None else None
    wijz = ""
    if vnr is not None and re.fullmatch(r"\d{8}", vnr.get("value", "")):
        v = vnr.get("value")
        wijz = f" ({int(v[4:])}/{v[:4]})"
    if titel is None:
        titel = _tekst(root.find(f".//{NS}docTitle")) or id
    return Geparseerd(wet_id=id, titel=titel, versie=f"ajantasa {datum.group(1) if datum else '?'}{wijz}",
                      bron_url=bron_url or WEB.format(id=id), artikelen=artikelen, ruw=ruw, ruw_extensie="xml")


def haal_op(id: str, titel: str | None = None) -> Geparseerd:
    """`id`: jaar/nummer, bijv. '1929/228' (oikeustoimilaki 228/1929)."""
    id = id.strip("/")
    with client(timeout=180.0) as c:
        r = c.get(URL.format(id=id))
        r.raise_for_status()
    return parse(r.content, id, WEB.format(id=id), titel)
