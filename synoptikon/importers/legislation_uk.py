"""EN: legislation.gov.uk, Crown Legislation Markup Language (CLML).

`https://www.legislation.gov.uk/{type}/{jaar}/{nr}/data.xml` geeft de
geconsolideerde ("latest available revised") tekst. Een section is een
<P1> (met <Pnumber>), meestal binnen een <P1group> met het opschrift als
<Title>. Part en Cross-heading (<Pblock>) vormen het pad. Schedules laten we
weg: ze hebben een eigen nummering ("Sch 2 para 1") die niet in de
section-reeks past. <Commentary> (de redactionele voetnoten) en de
verwijzingen ernaar vallen weg; ingevoegde tekst (<Addition>, <Substitution>)
blijft staan, want dat is de geldende tekst.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date

from . import Artikel, Geparseerd
from .http import client

URL = "https://www.legislation.gov.uk/{id}/data.xml"
WEB = "https://www.legislation.gov.uk/{id}"
L = "{http://www.legislation.gov.uk/namespaces/legislation}"
_WEG = {L + "Commentary", L + "CommentaryRef", L + "Commentaries", L + "Footnote", L + "FootnoteRef"}
_BLOK = {L + "P2", L + "P3", L + "P4", L + "P2group", L + "ListItem", L + "Text"}


def _tekst(el: ET.Element) -> str:
    delen: list[str] = []

    def loop(e: ET.Element) -> None:
        if e.tag in _WEG:
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


def _alineas(p1: ET.Element) -> list[str]:
    """Één alinea per subsection, met "(1)" voorop; dieper geneste paragrafen op eigen regels."""
    uit: list[str] = []

    def loop(e: ET.Element, diepte: int) -> None:
        for k in e:
            if k.tag in (L + "P2", L + "P3", L + "P4"):
                nr = k.find(L + "Pnumber")
                kop = f"({_tekst(nr)}) " if nr is not None else ""
                tekst = " ".join(_tekst(t) for t in k.iter(L + "Text") if _directe_tekst(t, k))
                if tekst or kop:
                    uit.append(("    " * (diepte - 1)) + kop + tekst)
                loop(k, diepte + 1)
            elif k.tag == L + "Text" and diepte == 1:
                t = _tekst(k)
                if t:
                    uit.append(t)
            elif k.tag not in _WEG and k.tag != L + "Pnumber":
                loop(k, diepte)

    loop(p1, 1)
    return uit


def _directe_tekst(t: ET.Element, ouder: ET.Element) -> bool:
    """Hoort <Text> direct bij deze P2/P3 (en niet bij een geneste P3)?"""
    for k in ouder:
        if k.tag.endswith("para"):
            return t in list(k)
    return False


def parse(data: bytes, wet_id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    body = root.find(f".//{L}Body")
    artikelen: list[Artikel] = []

    def loop(el: ET.Element, pad: list[str], opschrift: str | None) -> None:
        for k in el:
            naam = k.tag.removeprefix(L)
            if naam in ("Part", "Chapter", "Pblock"):
                nr = k.find(L + "Number")
                kop = " ".join(x for x in (_tekst(nr) if nr is not None else "", _tekst(k.find(L + "Title")) if k.find(L + "Title") is not None else "") if x)
                loop(k, [*pad, kop] if kop else pad, None)
            elif naam == "P1group":
                t = k.find(L + "Title")
                loop(k, pad, _tekst(t).rstrip(".") if t is not None else None)
            elif naam == "P1":
                nr = k.find(L + "Pnumber")
                if nr is None:
                    continue
                artikelen.append(Artikel(nummer=_tekst(nr), tekst="\n\n".join(_alineas(k)) or "(repealed)", opschrift=opschrift,
                                         pad=" › ".join(pad) or None))
    if body is not None:
        loop(body, [], None)
    if titel is None:
        t = root.find(f".//{L}PrimaryPrelims/{L}Title")
        titel = _tekst(t) if t is not None else wet_id
    versie = date.today().isoformat()
    m = re.search(rb'RestrictStartDate="(\d{4}-\d\d-\d\d)"', data[:3000])
    if m:
        versie = m.group(1).decode()
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie, bron_url=bron_url or WEB.format(id=wet_id), artikelen=artikelen, ruw=data, ruw_extensie="xml")


def haal_op(wet_id: str, titel: str | None = None) -> Geparseerd:
    """`wet_id`: bijv. 'ukpga/1979/54' (Sale of Goods Act 1979)."""
    wet_id = wet_id.strip("/")
    with client(timeout=180.0) as c:
        r = c.get(URL.format(id=wet_id))
        r.raise_for_status()
    return parse(r.content, wet_id, WEB.format(id=wet_id), titel)
