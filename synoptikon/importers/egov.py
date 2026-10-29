"""JP: e-Gov 法令検索, API v2 (`laws.e-gov.go.jp/api/2`), standaard-XML van het 法令標準XMLスキーマ.

`/law_data/{law_id}?response_format=xml` geeft de geldende stand (current enforced) met in <revision_info> de
datum van inwerkingtreding van de laatste wijziging; die datum is de versie. De wettekst zelf staat in
<law_full_text><Law>: MainProvision › Part (編) › Chapter (章) › Section (節) › Subsection (款) › Division (目)
› Article. Een artikel heeft <ArticleCaption> ("（目的）", het opschrift), <ArticleTitle> ("第七百九条") en
Paragraphs (項) met Items (号) en Subitems; het nummer staat als attribuut (`Num="709"`, `"12_2"` voor
第十二条の二, `"38:84"` voor een geschrapt bereik). We nummeren als in de citeerwijze: 709, 12の2.
Ruby (<Rt>) en de 附則 (SupplProvision, overgangsrecht met eigen nummering) vallen weg.

Bekende ids: 129AC0000000089 (民法), 132AC0000000048 (商法), 417AC0000000086 (会社法),
408AC0000000109 (民事訴訟法), 140AC0000000045 (刑法), 321CONSTITUTION (日本国憲法),
412AC0000000061 (消費者契約法), 418AC0000000078 (法の適用に関する通則法).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from . import Artikel, Geparseerd
from .http import client

URL = "https://laws.e-gov.go.jp/api/2/law_data/{id}?response_format=xml"
WEB = "https://laws.e-gov.go.jp/law/{id}"
_STRUCTUUR = {"Part", "Chapter", "Section", "Subsection", "Division"}


def _tekst(el: ET.Element | None) -> str:
    """Tekst zonder ruby-lezing; de Japanse spatie blijft (in 号 scheidt die handeling en gevolg)."""
    if el is None:
        return ""
    delen: list[str] = []

    def loop(e: ET.Element) -> None:
        if e.tag == "Rt":
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
    return re.sub(r"[^\S\u3000]+", " ", "".join(delen)).strip(" \n\t")  # de Japanse spatie (　) blijft staan


def _kop(el: ET.Element) -> str:
    """"第三編　債権" → "第三編 債権"."""
    return _tekst(el.find(el.tag + "Title")).replace("　", " ")


def _nummer(num: str) -> str:
    """"709" → "709", "12_2" → "12の2", "38:84" → "38" (geschrapt bereik: het eerste artikel)."""
    return num.split(":")[0].replace("_", "の")


def _zinnen(el: ET.Element | None) -> str:
    """De zinnen van een ParagraphSentence, ItemSentence …, zonder spatie ertussen (zoals in het Japans);
    kolommen (定義規定: begrip en omschrijving) met een Japanse spatie."""
    if el is None:
        return ""
    kolommen = el.findall("Column")
    if kolommen:
        return "\u3000".join(_zinnen(k) for k in kolommen)
    zinnen = el.findall("Sentence")
    return "".join(_tekst(z) for z in zinnen) if zinnen else _tekst(el)


def _onderdelen(el: ET.Element, diepte: int, uit: list[str]) -> None:
    """Items (号) en Subitems, ingesprongen onder hun lid."""
    for k in el:
        if k.tag == "Item" or re.fullmatch(r"Subitem\d+", k.tag):
            titel = _tekst(k.find(k.tag + "Title"))
            zin = _zinnen(k.find(k.tag + "Sentence"))
            uit.append(("    " * diepte) + f"{titel} {zin}".strip())
            _onderdelen(k, diepte + 1, uit)


def _leden(art: ET.Element) -> list[str]:
    uit: list[str] = []
    for para in art.findall("Paragraph"):
        num = _tekst(para.find("ParagraphNum"))
        zin = _zinnen(para.find("ParagraphSentence"))
        regels = [f"{num} {zin}".strip() if num else zin]
        _onderdelen(para, 1, regels)
        uit.append("\n".join(r for r in regels if r))
    return [u for u in uit if u]


def parse(data: bytes, wet_id: str, bron_url: str | None = None, titel: str | None = None, versie: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    law = root.find(".//Law") if root.tag != "Law" else root
    if law is None:
        raise ValueError(f"Geen <Law> in de e-Gov-XML van {wet_id}")
    if versie is None:
        rev = root.find("revision_info")
        datum = (rev.findtext("amendment_enforcement_date") if rev is not None else None) or ""
        if not datum and rev is not None:
            m = re.search(r"_(\d{4})(\d{2})(\d{2})_", rev.findtext("law_revision_id") or "")
            datum = "-".join(m.groups()) if m else ""
        versie = datum or law.get("Year", "onbekend")
    artikelen: list[Artikel] = []

    def loop(el: ET.Element, pad: list[str]) -> None:
        for k in el:
            if k.tag in _STRUCTUUR:
                loop(k, [*pad, _kop(k)])
            elif k.tag == "Article":
                opschrift = _tekst(k.find("ArticleCaption")).strip("（）() ") or None
                leden = _leden(k)
                artikelen.append(Artikel(nummer=_nummer(k.get("Num", "")), tekst="\n\n".join(leden) or "削除",
                                         opschrift=opschrift, pad=" › ".join(pad) or None))

    hoofd = law.find("LawBody/MainProvision")
    if hoofd is not None:
        loop(hoofd, [])
    if titel is None:
        titel = _tekst(law.find("LawBody/LawTitle")) or wet_id
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie, bron_url=bron_url or WEB.format(id=wet_id),
                      artikelen=[a for a in artikelen if a.nummer], ruw=data, ruw_extensie="xml")


def haal_op(id: str, titel: str | None = None) -> Geparseerd:
    """`id`: de law_id van e-Gov, bijv. '129AC0000000089' (民法)."""
    with client(timeout=180.0) as c:
        r = c.get(URL.format(id=id))
        r.raise_for_status()
    return parse(r.content, id, WEB.format(id=id), titel)
