"""QC: de gecodificeerde wetten van Québec als XML, uit de open-datadump op Données Québec.

LégisQuébec zelf (legisquebec.gouv.qc.ca) weigert geautomatiseerde verzoeken (CloudFront 403). Het ministerie van
Justitie zet dezelfde geconsolideerde teksten wekelijks als zip op Données Québec, dataset "Lois et règlements
codifiés du Québec" (licentie CC BY-NC-ND 4.0: niet-commercieel, ongewijzigd; Synoptikon toont de tekst ongewijzigd
en alleen voor eigen gebruik). De zip met alle wetten is ±45 MB; we lezen hem met HTTP-range-verzoeken en halen
alleen de inhoudsopgave, het statusbestand en de gevraagde wet op (enkele MB).

In de zip: `Statutes\\{id}\\FR\\{id}_FR.xml` (id: CCQ-1991, C-25.01, P-40.1, C-12) en `Statutes_FR_Status.txt`
met per wet "À jour au 15 octobre 2026"; die datum is de `versie`. Opbouw van het XML: geneste <Group1-Part>,
<Group2-Division> … <GroupN>, elk met een <Heading> (Label "PREMIER", TitleText "DES PERSONNES"), en daarin
<Section> met <Label> (het nummer), <Subsection>/<Paragraph> met <Text>. De Heading noemt het soort eenheid niet
(livre, titre …); per wet geven we die woorden mee.
"""
from __future__ import annotations

import io
import re
import time
import xml.etree.ElementTree as ET
import zipfile
from datetime import date

from . import Artikel, Geparseerd
from .http import client

API = "https://www.donneesquebec.ca/recherche/api/3/action/package_show?id=https-donneesquebec-ca-recherche-dataset-edit-lois-et-reglements-quebec"
WEB = "https://www.legisquebec.gouv.qc.ca/fr/document/lc/{id}"
# De soorten eenheden per niveau, voor de wetten waarvan we ze kennen.
EENHEDEN = {
    "CCQ-1991": ("LIVRE", "TITRE", "CHAPITRE", "SECTION", "§"),
    "C-25.01": ("LIVRE", "TITRE", "CHAPITRE", "SECTION", "§"),
    "C-12": ("PARTIE", "CHAPITRE"),
}
_DEEL = {"Subsection": 0, "Paragraph": 1, "Subparagraph": 2}


def _tekst(el: ET.Element) -> str:
    delen: list[str] = []

    def loop(e: ET.Element) -> None:
        if e.text:
            delen.append(e.text)
        for k in e:
            if k.tag == "Br":
                delen.append(" ")
            elif k.tag not in ("HistoricalNote", "Label", "Note") and k.tag not in _DEEL:
                loop(k)
            if k.tail:
                delen.append(k.tail)

    loop(el)
    return re.sub(r"\s+", " ", "".join(delen)).strip()


def _alineas(sectie: ET.Element) -> list[str]:
    uit: list[str] = []

    def loop(e: ET.Element) -> None:
        for k in e:
            if k.tag in _DEEL:
                label = k.find("Label")
                tekst = " ".join(_tekst(t) for t in k if t.tag in ("Text", "Repealed"))
                regel = " ".join(x for x in ((label.text or "").strip() if label is not None else "", tekst) if x)
                if regel:
                    uit.append("    " * _DEEL[k.tag] + regel)
                loop(k)
            elif k.tag in ("Text", "Repealed") and e is sectie:
                t = _tekst(k)
                if t:
                    uit.append(t)

    loop(sectie)
    return uit


def parse(data: bytes, wet_id: str, bron_url: str | None = None, titel: str | None = None, versie: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    eenheden = EENHEDEN.get(wet_id, ())
    artikelen: list[Artikel] = []

    def loop(el: ET.Element, pad: list[str]) -> None:
        for k in el:
            if k.tag.startswith("Group"):
                h = k.find("Heading")
                kop = ""
                if h is not None:
                    label, t = h.find("Label"), h.find("TitleText")
                    label = _tekst(label) if label is not None else ""
                    if label and len(pad) < len(eenheden):
                        label = f"{eenheden[len(pad)]} {label}"
                    kop = " · ".join(x for x in (label, _tekst(t) if t is not None else "") if x)
                loop(k, [*pad, kop])
            elif k.tag == "Section":
                label = k.find("Label")
                if label is None or not (label.text or "").strip():
                    continue
                artikelen.append(Artikel(nummer=label.text.strip(), tekst="\n\n".join(_alineas(k)) or "(abrogé)",
                                         pad=" › ".join(p for p in pad if p) or None))

    body = root.find("Statute/Body")
    if body is not None:
        loop(body, [])
    if titel is None:
        t = root.find("Statute/Identification/LongTitle")
        titel = _tekst(t) if t is not None else wet_id
    if versie is None:
        d = root.get("date-eev") or ""
        versie = f"{d[:4]}-{d[4:6]}-{d[6:8]}" if len(d) == 8 else date.today().isoformat()
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie, bron_url=bron_url or WEB.format(id=wet_id), artikelen=artikelen,
                      ruw=data, ruw_extensie="xml")


def versie_uit_status(status: str, wet_id: str) -> str | None:
    """`"CCQ-1991", "À jour au 15 octobre 2026", "J", "20261015"` → "2026-10-15"."""
    m = re.search(rf'^"{re.escape(wet_id)}",.*"(\d{{8}})"\s*$', status, re.M)
    return f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:8]}" if m else None


class _OpAfstand(io.RawIOBase):
    """Een bestand op een webserver als leesbaar, doorzoekbaar bestand: elke `read` is een Range-verzoek."""

    def __init__(self, c, url: str) -> None:
        self.c, self.url, self.pos = c, url, 0
        r = c.head(url)
        r.raise_for_status()
        self.lengte = int(r.headers["content-length"])

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = 0) -> int:
        self.pos = {0: offset, 1: self.pos + offset, 2: self.lengte + offset}[whence]
        return self.pos

    def readinto(self, b) -> int:
        if not len(b) or self.pos >= self.lengte:
            return 0
        eind = min(self.lengte, self.pos + len(b)) - 1
        r = self.c.get(self.url, headers={"Range": f"bytes={self.pos}-{eind}"})
        if r.status_code != 206:
            raise ValueError(f"Données Québec: geen Range-antwoord ({r.status_code})")
        time.sleep(0.2)  # beleefd: de zip-lezer doet een handvol verzoeken achter elkaar
        b[: len(r.content)] = r.content
        self.pos += len(r.content)
        return len(r.content)


def haal_op(wet_id: str, titel: str | None = None) -> Geparseerd:
    with client(timeout=180.0) as c:
        r = c.get(API)
        r.raise_for_status()
        bronnen = r.json()["result"]["resources"]
        url = next(b["url"] for b in bronnen if b.get("format") == "XML" and b["url"].endswith("_lois.zip"))
        z = zipfile.ZipFile(io.BufferedReader(_OpAfstand(c, url), buffer_size=1 << 18))
        status = z.read("Statutes_FR_Status.txt").decode("utf-8-sig", "replace")
        data = z.read(f"Statutes\\{wet_id}\\FR\\{wet_id}_FR.xml")
    return parse(data, wet_id, WEB.format(id=wet_id), titel, versie_uit_status(status, wet_id))
