"""DE: gesetze-im-internet.de, XML-download (zip met één XML).

Download: https://www.gesetze-im-internet.de/{kurz}/xml.zip, bijv. bgb, hgb, zpo.
Elke <norm> is óf een gliederingseenheid (Buch, Abschnitt, Titel) óf een
paragraaf met <enbez>§ 929</enbez>. De gliederingseenheid in de metadata van
een paragraaf geeft het directe ouderniveau; het volledige pad bouwen we op
uit de gliederingskennzahl (3 cijfers per niveau).
"""
from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ET
import zipfile
from datetime import date

from . import Artikel, Geparseerd
from .http import client

URL = "https://www.gesetze-im-internet.de/{kurz}/xml.zip"


def _tekst(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return re.sub(r"[ \t]+", " ", "".join(el.itertext())).strip()


def _inhoud(norm: ET.Element) -> str:
    content = norm.find("textdaten/text/Content")
    if content is None:
        return ""
    alineas = []
    for p in content:
        t = _tekst(p)
        if t:
            alineas.append(t)
    if not alineas:
        t = _tekst(content)
        return t
    return "\n\n".join(alineas)


def parse(xml_bytes: bytes, wet_id: str, bron_url: str | None = None) -> Geparseerd:
    root = ET.fromstring(xml_bytes)
    builddate = root.get("builddate") or ""
    versie = f"{builddate[:4]}-{builddate[4:6]}-{builddate[6:8]}" if len(builddate) >= 8 else date.today().isoformat()

    titel = wet_id
    eerste = root.find("norm")
    if eerste is not None:
        titel = _tekst(eerste.find("metadaten/kurzue")) or _tekst(eerste.find("metadaten/jurabk")) or _tekst(eerste.find("metadaten/langue")) or wet_id
        stand = eerste.find("metadaten/standangabe/standkommentar")
        if stand is not None and _tekst(stand):
            versie = f"{versie} ({_tekst(stand)})"

    # Gliederungskennzahl → label, om het pad op te bouwen.
    gliederung: dict[str, str] = {}
    for norm in root.findall("norm"):
        g = norm.find("metadaten/gliederungseinheit")
        if g is not None and norm.find("metadaten/enbez") is None:
            kz = _tekst(g.find("gliederungskennzahl"))
            bez = _tekst(g.find("gliederungsbez"))
            gt = _tekst(g.find("gliederungstitel"))
            if kz:
                gliederung[kz] = f"{bez} {gt}".strip()

    def pad_voor(kz: str) -> str | None:
        delen = [gliederung.get(kz[:i]) for i in range(3, len(kz) + 1, 3)]
        delen = [d for d in delen if d]
        return " › ".join(delen) if delen else None

    artikelen: list[Artikel] = []
    for norm in root.findall("norm"):
        enbez = _tekst(norm.find("metadaten/enbez"))
        if not enbez or not (enbez.startswith("§") or enbez.lower().startswith("art")):
            continue
        g = norm.find("metadaten/gliederungseinheit")
        kz = _tekst(g.find("gliederungskennzahl")) if g is not None else ""
        nummer = enbez.replace("§", "").strip()
        tekst = _inhoud(norm) or "[weggefallen]"
        artikelen.append(Artikel(nummer=nummer, tekst=tekst, opschrift=_tekst(norm.find("metadaten/titel")) or None, pad=pad_voor(kz) if kz else None))
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie, bron_url=bron_url, artikelen=artikelen, ruw=xml_bytes, ruw_extensie="xml")


def parse_zip(zip_bytes: bytes, wet_id: str, bron_url: str | None = None) -> Geparseerd:
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        namen = [n for n in z.namelist() if n.lower().endswith(".xml")]
        if not namen:
            raise ValueError("Geen XML in het zipbestand")
        xml_bytes = z.read(namen[0])
    return parse(xml_bytes, wet_id, bron_url)


def haal_op(kurz: str) -> Geparseerd:
    url = URL.format(kurz=kurz.lower())
    with client() as c:
        r = c.get(url)
        r.raise_for_status()
    return parse_zip(r.content, kurz.lower(), url)
