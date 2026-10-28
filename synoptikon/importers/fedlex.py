"""CH: Fedlex, Akoma Ntoso-XML van de systematische rechtsverzameling (SR).

De XML-bestanden staan in de filestore onder het ELI van de akte en de
datum van de stand (`…/eli/cc/24/233_245_233/20260701/de/xml/…xml`). Welke
standen er zijn en welk bestand erbij hoort, staat in de SPARQL-endpoint van
Fedlex; we nemen de laatste stand die vandaag geldt (Fedlex publiceert ook
standen die pas later in werking treden).

Structuur: book › part › title › chapter › (level met fedlex:role="marginal")
› article. De `marginal`-levels zijn de Zwitserse randtitels ("A. Inhalt des
Eigentums › I. Im Allgemeinen"): die vormen samen het opschrift van het
artikel, niet het pad in de systematiek. Voetnoten (<authorialNote>) zijn
wijzigingsgeschiedenis en worden weggelaten. Leden krijgen hun nummer
voorop, zoals in de officiële weergave ("1 Wer Eigentümer …").

Bekende ELI's: cc/24/233_245_233 (ZGB, SR 210), cc/27/317_321_377 (OR, SR 220),
cc/1988/1776_1776_1776 (IPRG, SR 291), cc/1993/3122_3122_3122 (PrHG, SR 221.112.944).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date

from . import Artikel, Geparseerd
from .http import client

SPARQL = "https://fedlex.data.admin.ch/sparqlendpoint"
WEB = "https://www.fedlex.admin.ch/eli/{eli}/{taal}"
A = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
_STRUCTUUR = {"book", "part", "title", "subtitle", "chapter", "subchapter", "section", "subsection"}

_QUERY = """PREFIX jolux: <http://data.legilux.public.lu/resource/ontology/jolux#>
SELECT ?d ?f WHERE {{
  ?c jolux:isMemberOf <https://fedlex.data.admin.ch/eli/{eli}> ; jolux:dateApplicability ?d ;
     jolux:isRealizedBy ?e . ?e jolux:isEmbodiedBy ?m . ?m jolux:isExemplifiedBy ?f .
  FILTER(CONTAINS(STR(?f), "/{taal}/xml/"))
}} ORDER BY DESC(?d)"""


def _tekst(el: ET.Element | None) -> str:
    """Tekst zonder voetnoten."""
    if el is None:
        return ""
    delen: list[str] = []

    def loop(e: ET.Element) -> None:
        if e.tag == A + "authorialNote":
            if e.tail:
                delen.append(e.tail)
            return
        if e.text:
            delen.append(e.text)
        for k in e:
            loop(k)
        if e.tail and e is not el:
            delen.append(e.tail)

    loop(el)
    return re.sub(r"\s+", " ", "".join(delen)).strip()


def _kop(el: ET.Element) -> str:
    num = _tekst(el.find(A + "num")).rstrip(": ")
    heading = _tekst(el.find(A + "heading"))
    return f"{num} {heading}".strip() if heading else num


def _nummer(art: ET.Element) -> str | None:
    m = re.match(r"Art\.\s*(\d+\s*[a-z]{0,3}(?:\s?(?:bis|ter|quater|quinquies|sexies|septies|octies|novies|decies))?)", _tekst(art.find(A + "num")))
    return re.sub(r"\s+", "", m.group(1)) if m else None


def _leden(art: ET.Element) -> list[str]:
    uit = []
    for para in art.iter(A + "paragraph"):
        num = _tekst(para.find(A + "num"))
        inhoud = para.find(A + "content")
        delen = []
        if inhoud is not None:
            for k in inhoud:
                if k.tag == A + "blockList":
                    intro = _tekst(k.find(A + "listIntroduction"))
                    if intro:
                        delen.append(intro)
                    for item in k.iter(A + "item"):
                        delen.append(f"{_tekst(item.find(A + 'num'))} {_tekst(item.find(A + 'p'))}".strip())
                else:
                    t = _tekst(k)
                    if t:
                        delen.append(t)
        tekst = "\n".join(delen)
        if tekst:
            uit.append(f"{num} {tekst}".strip() if num else tekst)
    if not uit:
        t = _tekst(art.find(A + "content"))
        if t:
            uit.append(t)
    return uit


def parse(data: bytes, wet_id: str, bron_url: str | None = None, titel: str | None = None, versie: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    artikelen: list[Artikel] = []

    def loop(el: ET.Element, pad: list[str], rand: list[str]) -> None:
        for k in el:
            naam = k.tag.removeprefix(A)
            if naam in _STRUCTUUR:
                loop(k, [*pad, _kop(k)], [])
            elif naam == "level":
                kop = _tekst(k.find(A + "heading"))
                loop(k, pad, [*rand, kop] if kop else rand)
            elif naam == "article":
                nr = _nummer(k)
                if nr is None:
                    continue
                leden = _leden(k)
                opschrift = " › ".join(rand) or _tekst(k.find(A + "heading")) or None
                artikelen.append(Artikel(nummer=nr, tekst="\n\n".join(leden) or "(aufgehoben)", opschrift=opschrift, pad=" › ".join(pad) or None))
            elif naam in ("body", "mainBody", "act"):
                loop(k, pad, rand)

    body = root.find(f".//{A}body")
    loop(body if body is not None else root, [], [])
    if titel is None:
        t = root.find(f".//{A}docTitle")
        titel = _tekst(t) if t is not None else wet_id
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie or date.today().isoformat(), bron_url=bron_url,
                      artikelen=artikelen, ruw=data, ruw_extensie="xml")


def haal_op(eli: str, titel: str | None = None, taal: str = "de") -> Geparseerd:
    """`eli`: bijv. 'cc/24/233_245_233' (ZGB)."""
    eli = eli.strip("/").removeprefix("eli/")
    vandaag = date.today().isoformat()
    with client(timeout=300.0) as c:
        r = c.post(SPARQL, data={"query": _QUERY.format(eli=eli, taal=taal)}, headers={"Accept": "application/sparql-results+json", "User-Agent": "Synoptikon/0.1"})
        r.raise_for_status()
        standen = [(b["d"]["value"][:10], b["f"]["value"]) for b in r.json()["results"]["bindings"]]
        geldig = [s for s in standen if s[0] <= vandaag] or standen
        if not geldig:
            raise ValueError(f"Geen XML-stand gevonden voor eli/{eli}")
        datum, url = max(geldig)
        x = c.get(url)
        x.raise_for_status()
    return parse(x.content, f"eli/{eli}", WEB.format(eli=eli, taal=taal), titel, datum)
