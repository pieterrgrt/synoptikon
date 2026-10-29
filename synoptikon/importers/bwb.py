"""NL: wetten.overheid.nl, BWB-XML ("toestand").

Download: wetten.overheid.nl kent geen directe XML-URL meer (het oude
`xml.php?regelingID=` geeft 404). `https://wetten.overheid.nl/BWBR0005291/`
verwijst door naar de geldende versie (`/BWBR0005291/2025-07-01`); een POST
van het exportformulier naar `/BWBR0005291/2025-07-01/0` levert de toestand
als XML. Het BW is per boek een eigen regeling:

    Boek 1 BWBR0002656   Boek 4 BWBR0002761   Boek 7  BWBR0005290
    Boek 2 BWBR0003045   Boek 5 BWBR0005288   Boek 7A BWBR0006000
    Boek 3 BWBR0005291   Boek 6 BWBR0005289   Boek 8  BWBR0005034
                                              Boek 10 BWBR0030068

De artikelnummers worden als "3:84" opgeslagen zodra het boeknummer uit de
structuur bekend is (Boek 7A als "7A:1576").
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date

from . import Artikel, Geparseerd
from .http import client

BASIS = "https://wetten.overheid.nl"

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
    # meta-data (jci-verwijzingen e.d.) zit in de elementen zelf en zou anders in de tekst belanden.
    for ouder in root.iter():
        for kind in [k for k in ouder if k.tag == "meta-data"]:
            ouder.remove(kind)

    titel = _tekst(root.find(".//citeertitel")) or _tekst(root.find(".//intitule")) or wet_id
    versie = root.get("inwerkingtreding") or root.get("inwerkingtredingsdatum") or root.get("geldigheidsdatum") or ""
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
                loop(kind, pad + [stuk.strip()], nr.upper() if tag == "boek" and nr else boek)
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
    with client() as c:
        pagina = c.get(f"{BASIS}/{wet_id}/")
        pagina.raise_for_status()
        pad = pagina.url.path.rstrip("/")
        if pad.count("/") == 2:  # /BWBR…/datum → /BWBR…/datum/0
            pad += "/0"
        r = c.post(
            BASIS + pad,
            data={"hiddenBWBId": wet_id, "hfExportOnderdeelID": pad, "exportopties": "rbXml", "exportopties2": "rbZonderAfbeeldingen", "btnExporteerOK": "Exporteer"},
        )
        r.raise_for_status()
        if not r.content.lstrip().startswith(b"<?xml"):
            raise ValueError(f"wetten.overheid.nl gaf geen XML voor {wet_id} ({r.headers.get('content-type')})")
    return parse(r.content, wet_id, f"{BASIS}{pad}")


# --- alle geldende regelingen (bulk en bijwerken) ---------------------------------------------
#
# De lijst komt uit de SRU-zoekdienst van het BWB (zoekservice.overheid.nl, open, geen sleutel): per regeling de
# geldende toestand met haar begindatum en de URL van de XML in de repository van officiële overheidspublicaties. Die
# toestand-XML is hetzelfde formaat als de export van wetten.overheid.nl, maar statisch (één verzoek, ETag), en de
# begindatum = de versie die `parse` uit de wortel leest. Een wet waarvan de datum niet veranderde, hoeft dus niet
# opnieuw te worden opgehaald. De citeerafkorting (Awb, Wft) staat bovenaan het WTI-bestand; dat kan tientallen MB
# zijn, dus alleen de eerste kilobytes.

SRU = "https://zoekservice.overheid.nl/sru/Search"
REPOSITORY = "https://repository.officiele-overheidspublicaties.nl/bwb"
SOORTEN = ("wet", "rijkswet", "AMvB", "rijksAMvB")
_SRU_NS = {"sru": "http://docs.oasis-open.org/ns/search-ws/sruResponse", "dcterms": "http://purl.org/dc/terms/",
           "overheidbwb": "http://standaarden.overheid.nl/bwb/terms/"}


@dataclass(frozen=True)
class Regeling:
    id: str
    titel: str
    soort: str
    versie: str  # begindatum van de geldende toestand
    url: str  # toestand-XML in de repository


def parse_sru(xml_bytes: bytes) -> tuple[list[Regeling], int | None]:
    """Eén pagina van de SRU-respons: de regelingen en de volgende startpositie (None = klaar)."""
    root = ET.fromstring(xml_bytes)
    uit = []
    for rec in root.iterfind(".//sru:record", _SRU_NS):
        def veld(pad: str) -> str:
            el = rec.find(pad, _SRU_NS)
            return (el.text or "").strip() if el is not None else ""
        bwb_id = veld(".//dcterms:identifier")
        url = veld(".//overheidbwb:locatie_toestand")
        if bwb_id and url:
            uit.append(Regeling(bwb_id, veld(".//dcterms:title"), veld(".//dcterms:type"),
                                veld(".//overheidbwb:geldigheidsperiode_startdatum")[:10], url))
    volgende = root.find("sru:nextRecordPosition", _SRU_NS)
    tekst = (volgende.text or "").strip() if volgende is not None else ""
    return uit, int(tekst) if tekst.isdigit() else None


def geldende(c=None, peildatum: date | None = None, soorten: tuple[str, ...] = SOORTEN, per_pagina: int = 500) -> list[Regeling]:
    """Alle regelingen van deze soorten die op de peildatum gelden (±4.400 voor wet, rijkswet, AMvB, rijksAMvB)."""
    eigen = c is None
    c = c or client(timeout=120.0)
    peil = (peildatum or date.today()).isoformat()
    gezien: dict[str, Regeling] = {}
    try:
        for soort in soorten:
            start: int | None = 1
            while start:
                r = c.get(SRU, params={"operation": "searchRetrieve", "version": "2.0", "x-connection": "BWB", "startRecord": start,
                                       "maximumRecords": per_pagina, "query": f"overheidbwb.geldigheidsdatum=={peil} and dcterms.type=={soort}"})
                r.raise_for_status()
                pagina, start = parse_sru(r.content)
                for reg in pagina:
                    gezien.setdefault(reg.id, reg)
                if not pagina:
                    break
    finally:
        if eigen:
            c.close()
    return sorted(gezien.values(), key=lambda x: x.id)


def haal_toestand(url: str, wet_id: str, c=None) -> Geparseerd:
    eigen = c is None
    c = c or client(timeout=120.0)
    try:
        r = c.get(url)
        r.raise_for_status()
    finally:
        if eigen:
            c.close()
    return parse(r.content, wet_id, f"{BASIS}/{wet_id}/")


def afkorting(wet_id: str, c=None) -> str | None:
    """Officiële afkorting uit de kop van het WTI-bestand, of None."""
    eigen = c is None
    c = c or client(timeout=60.0)
    kop = b""
    try:
        with c.stream("GET", f"{REPOSITORY}/{wet_id}/{wet_id}.WTI") as r:
            if r.status_code != 200:
                return None
            for stuk in r.iter_bytes():
                kop += stuk
                if b"</afkortingen>" in kop or b"<citeertitel" in kop or len(kop) > 16384:
                    break
    except Exception:  # alleen een gemak; de wet zelf komt er ook zonder
        return None
    finally:
        if eigen:
            c.close()
    m = re.search(rb"<afkorting>([^<]{1,60})</afkorting>", kop)
    return m.group(1).decode("utf-8", "replace").strip() if m else None
