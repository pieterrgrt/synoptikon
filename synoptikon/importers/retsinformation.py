"""DK: Retsinformation (Civilstyrelsen), LexDania-XML via ELI.

`https://www.retsinformation.dk/eli/lta/{jaar}/{nr}/xml` geeft een akte als XML. Denemarken consolideert
door een *lovbekendtgørelse* (LBK) uit te vaardigen: een nieuwe akte met een eigen nummer, die de wet met
alle wijzigingen tot dan toe bevat. Het register wijst dus naar de laatste LBK; wijzigingswetten van ná die
LBK (in de metadata onder <Change>) zijn niet verwerkt tot de volgende LBK verschijnt. Staat de akte niet
meer op "Valid", dan is er een nieuwere LBK en geven we een waarschuwing in de titel.

Structuur: Bog › Afsnit › Kapitel (› Afdeling), elk met <Explicatus> ("Kapitel 5") en <Rubrica> (de kop);
<ParagrafGruppe> met een <Rubrica> boven één paragraaf is het opschrift, boven meer paragrafen een eenheid
in het pad (Købeloven heeft geen hoofdstukken, alleen zulke koppen); <Paragraf> met
<Explicatus>"§ 4 a."</Explicatus> en <Stk>-leden ("Stk. 2."), opsommingen als <Indentatio>. Voetnoten
(<Nota>) vallen weg; inleiding, ondertekening en ikrafttredingsbepalingen van wijzigingswetten (<Ikraft>)
ook, want die hebben hun eigen §-nummering.

Versie: "LBK nr 1853 af 2021-09-24" (de akte zelf), stabiel tot een nieuwe LBK.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from . import Artikel, Geparseerd
from .http import client

URL = "https://www.retsinformation.dk/eli/{eli}/xml"
WEB = "https://www.retsinformation.dk/eli/{eli}"
_STRUCTUUR = {"Bog", "Del", "Afsnit", "Underafsnit", "Kapitel", "Afdeling", "Underafdeling"}
_WEG = {"Nota", "Ikraft", "Signature", "Indledning", "IkraftCentreretParagraf", "TitelGruppe", "Meta"}


def _tekst(el: ET.Element | None) -> str:
    if el is None:
        return ""
    delen: list[str] = []

    def loop(e: ET.Element) -> None:
        if e.tag in _WEG:
            return
        if e.text and e.text.strip():
            delen.append(e.text)
        for k in e:
            loop(k)
            if k.tail and k.tail.strip():
                delen.append(k.tail)

    loop(el)
    return re.sub(r"\s+", " ", " ".join(delen)).strip()


def _kop(el: ET.Element) -> str:
    return " ".join(t for t in (_tekst(el.find("Explicatus")), _tekst(el.find("Rubrica"))) if t)


def _leden(par: ET.Element) -> str:
    uit = []
    for stk in par.findall("Stk"):
        regels: list[str] = []
        nr = _tekst(stk.find("Explicatus"))
        for k in stk:
            if k.tag != "Exitus":
                continue
            if k.find("Index") is not None:
                for ind in k.iter("Indentatio"):
                    regels.append(f"{_tekst(ind.find('Explicatus'))} {' '.join(_tekst(e) for e in ind.findall('Exitus'))}".strip())
            else:
                t = _tekst(k)
                if t:
                    regels.append(t)
        tekst = "\n".join(regels)
        if tekst or nr:
            uit.append(f"{nr} {tekst}".strip())
    return "\n\n".join(uit)


def _nummer(par: ET.Element) -> str | None:
    m = re.match(r"§\s*(\d+(?:\s?[a-zæøå](?![a-zæøå]))?)", _tekst(par.find("Explicatus")))
    return re.sub(r"(\d)\s?([a-zæøå])", r"\1 \2", m.group(1)) if m else None


def parse(data: bytes, eli: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    artikelen: list[Artikel] = []
    gezien: set[str] = set()

    def loop(el: ET.Element, pad: list[str], groep: str | None) -> None:
        for k in el:
            if k.tag in _WEG:
                continue
            if k.tag in _STRUCTUUR:
                kop = _kop(k)
                loop(k, [*pad, kop] if kop else pad, None)
            elif k.tag == "ParagrafGruppe":
                kop = _tekst(k.find("Rubrica")) or None
                if kop and len(k.findall("Paragraf")) > 1:  # kop boven een reeks paragrafen: een eenheid in het pad
                    loop(k, [*pad, kop], None)
                else:
                    loop(k, pad, kop)
            elif k.tag == "Paragraf":
                nr = _nummer(k)
                if nr is None or nr in gezien:
                    continue
                gezien.add(nr)
                opschrift = _tekst(k.find("Rubrica")) or groep
                artikelen.append(Artikel(nummer=nr, tekst=_leden(k) or "(ophævet)", opschrift=opschrift, pad=" › ".join(pad) or None))
            elif k.tag in ("DokumentIndhold", "Dokument"):
                loop(k, pad, groep)

    inhoud = root.find("DokumentIndhold")
    loop(inhoud if inhoud is not None else root, [], None)
    meta = root.find("Meta")
    nummer, datum = _tekst(meta.find("Number")), _tekst(meta.find("DiesSigni"))
    soort = _tekst(meta.find("DocumentType")).split(" ")[0] or "LOV"
    if titel is None:
        titel = _tekst(meta.find("PopularTitle")) or _tekst(meta.find("DocumentTitle")) or eli
    if _tekst(meta.find("Status")) not in ("", "Valid"):
        titel = f"{titel} (historisk: er is een nieuwere lovbekendtgørelse)"
    return Geparseerd(wet_id=eli, titel=titel, versie=f"{soort} nr {nummer} af {datum}", bron_url=bron_url or WEB.format(eli=eli),
                      artikelen=artikelen, ruw=data, ruw_extensie="xml")


def haal_op(eli: str, titel: str | None = None) -> Geparseerd:
    """`eli`: bijv. 'lta/2021/1853' (Købeloven, LBK nr 1853 af 24/09/2021)."""
    eli = eli.strip("/").removeprefix("eli/")
    with client(timeout=180.0) as c:
        r = c.get(URL.format(eli=eli))
        r.raise_for_status()
    return parse(r.content, eli, WEB.format(eli=eli), titel)
