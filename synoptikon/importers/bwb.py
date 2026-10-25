"""NL: wetten.overheid.nl, BWB-XML ("toestand").

Download: https://wetten.overheid.nl/xml.php?regelingID=BWBR0005291 geeft de
geldende toestand als XML. Het BW is per boek een eigen regeling:
Boek 3 = BWBR0005291, Boek 5 = BWBR0005288, Boek 6 = BWBR0005289,
Boek 7 = BWBR0005290. De artikelnummers worden als "3:84" opgeslagen zodra
het boeknummer uit de structuur bekend is.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date

from . import Artikel, Geparseerd
from .http import client

URL = "https://wetten.overheid.nl/xml.php?regelingID={id}"

_STRUCTUUR = ("boek", "deel", "titeldeel", "hoofdstuk", "afdeling", "paragraaf", "sub-paragraaf")


def _tekst(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def _kop(el: ET.Element) -> tuple[str, str, str]:
    kop = el.find("kop")
    if kop is None:
        return "", "", ""
    return _tekst(kop.find("label")), _tekst(kop.find("nr")), _tekst(kop.find("titel"))


def _artikel_tekst(art: ET.Element) -> str:
    """Leden worden genummerde alinea's; losse alinea's blijven alinea's."""
    regels: list[str] = []
    leden = art.findall("lid")
    if leden:
        for lid in leden:
            nr = _tekst(lid.find("lidnr"))
            alinea = " ".join(_tekst(al) for al in lid.findall("al") if _tekst(al))
            lijst = _lijst(lid)
            regels.append((f"{nr}. " if nr else "") + alinea + (("\n" + lijst) if lijst else ""))
    else:
        for al in art.findall("al"):
            if _tekst(al):
                regels.append(_tekst(al))
        lijst = _lijst(art)
        if lijst:
            regels.append(lijst)
    return "\n\n".join(r for r in regels if r.strip())


def _lijst(parent: ET.Element) -> str:
    items = []
    for li in parent.findall("lijst/li"):
        nr = _tekst(li.find("li.nr"))
        items.append(f"{nr} " + " ".join(_tekst(al) for al in li.findall("al")))
    return "\n".join(items)


def parse(xml_bytes: bytes, wet_id: str, bron_url: str | None = None) -> Geparseerd:
    root = ET.fromstring(xml_bytes)
    # Namespaces strippen vereenvoudigt het zoeken aanzienlijk.
    for el in root.iter():
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]

    titel = _tekst(root.find(".//citeertitel")) or _tekst(root.find(".//intitule")) or wet_id
    versie = root.get("inwerkingtredingsdatum") or root.get("geldigheidsdatum") or ""
    meta = root.find(".//meta-data")
    if not versie and meta is not None:
        versie = _tekst(meta.find(".//inwerkingtredingsdatum")) or _tekst(meta.find(".//geldigheidsdatum"))
    versie = versie[:10] or date.today().isoformat()

    artikelen: list[Artikel] = []
    volgorde = 0

    def loop(el: ET.Element, pad: list[str], boek: str | None):
        nonlocal volgorde
        for kind in el:
            tag = kind.tag
            if tag in _STRUCTUUR:
                label, nr, kop_titel = _kop(kind)
                stuk = " ".join(x for x in (label, nr) if x) + (f" {kop_titel}" if kop_titel else "")
                loop(kind, pad + [stuk.strip()], nr if tag == "boek" and nr else boek)
            elif tag == "artikel":
                _label, nr, kop_titel = _kop(kind)
                if not nr:
                    continue
                nummer = f"{boek}:{nr}" if boek else nr
                tekst = _artikel_tekst(kind)
                if kind.get("status") == "vervallen" or not tekst:
                    tekst = tekst or "[Vervallen]"
                volgorde += 1
                artikelen.append(Artikel(nummer=nummer, tekst=tekst, opschrift=kop_titel or None, pad=" › ".join(pad) or None))
            else:
                loop(kind, pad, boek)

    wettekst = root.find(".//wettekst")
    loop(wettekst if wettekst is not None else root, [], None)
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie, bron_url=bron_url, artikelen=artikelen, ruw=xml_bytes, ruw_extensie="xml")


def haal_op(wet_id: str) -> Geparseerd:
    url = URL.format(id=wet_id)
    with client() as c:
        r = c.get(url)
        r.raise_for_status()
    return parse(r.content, wet_id, url)
