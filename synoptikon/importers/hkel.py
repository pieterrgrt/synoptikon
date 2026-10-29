"""HK: Hong Kong e-Legislation (DoJ), de open data op data.gov.hk in het HKLM-XML-schema.

De website zelf (elegislation.gov.hk) sluit in robots.txt alles af behalve voor zoekmachines; de open data staan
als zip per reeks chapters (Cap. 1–300, 301–600, 601 en verder, en de instruments zoals de Basic Law) op
resource.data.one.gov.hk, honderden MB per zip. We lezen alleen wat nodig is met HTTP-Range-verzoeken: het einde
van de zip (de inhoudsopgave) en het ene XML-bestand van de wet, samen een handvol verzoeken. Geconsolideerd:
de "current version", per wet met de datum van de stand (<dc:date>, ook in de bestandsnaam); die is de versie.

Opbouw: <main> › <part> (met <num> en <heading>) › <division> › <crossHeading> (een tussenkop vóór de
sections die erop volgen) › <section> met <num value="14">, <heading> (het opschrift) en <subsection> ›
<paragraph> › <subparagraph>. De Basic Law (A101) is anders: opgemaakte tabellen met <p><b>Article 18</b></p> en
de alinea's als <p>, Chapter en Section als tabelrij; die lezen we regel voor regel (`_vrij`), zonder de annexes.
<sourceNote>, <editorialNote> en <referenceNote> (de wijzigingsgeschiedenis) vallen weg, de <schedule>s ook.
"""
from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ET
import zipfile

from . import Artikel, Geparseerd
from .http import client

ZIP = "https://resource.data.one.gov.hk/doj/data/hkel_c_{deel}_en.zip"
WEB = "https://www.elegislation.gov.hk/hk/{id}"
N = "{http://www.xml.gov.hk/schemas/hklm/1.0}"
_WEG = {N + t for t in ("sourceNote", "editorialNote", "referenceNote", "commencementNote", "schedule", "num", "heading")}
_INDELING = {N + t for t in ("part", "division", "subdivision", "chapter")}
_EENHEID = {N + "section", N + "article"}
_HOUDER = {N + t for t in ("content", "leadIn", "continued", "text")}
_BLOK = {N + t for t in ("subsection", "paragraph", "subparagraph", "subsubparagraph", "def", "proviso")}


def _deel(id: str) -> str:
    """"cap26" → "leg_cap_1_cap_300", "cap622" → "leg_cap_601_cap_end", "A101" → "instruments"."""
    m = re.fullmatch(r"cap(\d+)[A-Z]*", id)
    if not m:
        return "instruments"
    nr = int(m.group(1))
    return "leg_cap_1_cap_300" if nr <= 300 else "leg_cap_301_cap_600" if nr <= 600 else "leg_cap_601_cap_end"


def _ruw(el: ET.Element) -> str:
    """De tekst van een element met de witruimte zoals in de bron, zonder de noten."""
    delen = [el.text or ""]
    for k in el:
        if k.tag not in _WEG:
            delen.append(_ruw(k))
        delen.append(k.tail or "")
    return "".join(delen)


def _tekst(el: ET.Element | None) -> str:
    return re.sub(r"\s+", " ", _ruw(el)).strip() if el is not None else ""


def _kop(el: ET.Element) -> str:
    """"Part I" + "Formation of the Contract" → "Part I Formation of the Contract"."""
    return " ".join(t for t in (_tekst(el.find(N + "num")), _tekst(el.find(N + "heading"))) if t)


def _leden(eenheid: ET.Element) -> list[str]:
    """Één alinea per subsection, met "(1)" voorop; paragraphs, definities en subparagraphs ingesprongen eronder."""
    leden: list[list[str]] = []

    def regel(tekst: str, inspring: int, nieuw: bool) -> None:
        if tekst:
            if nieuw or not leden:
                leden.append([])
            leden[-1].append("    " * inspring + tekst)

    def loop(el: ET.Element, inspring: int, nieuw: bool) -> None:
        delen = [el.text or ""]
        for k in el:
            if k.tag in _BLOK:
                regel(re.sub(r"\s+", " ", "".join(delen)).strip(), inspring, nieuw)
                delen, nieuw = [""], False
                if k.tag == N + "subsection":
                    loop(k, 0, True)
                else:
                    loop(k, inspring + 1, False)
            elif k.tag == N + "num":
                if el is not eenheid:
                    delen.append(f" {_ruw(k)} ")
            elif k.tag in _HOUDER:
                delen.append(f" {_ruw(k)} ")
            elif k.tag not in _WEG:
                delen.append(_ruw(k))  # <term>, <ref>, <shortTitle> …: midden in de zin
            delen.append(k.tail or "")
        regel(re.sub(r"\s+", " ", "".join(delen)).strip(), inspring, nieuw)

    loop(eenheid, 0, True)
    return ["\n".join(lid) for lid in leden if lid]


def parse(data: bytes, id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    meta = root.find(N + "meta")
    versie = (meta.findtext("{http://purl.org/dc/elements/1.1/}date") if meta is not None else None) or "onbekend"
    if titel is None:
        kort = next((e for e in (root.find(f".//{N}shortTitle"), root.find(f".//{N}docTitle")) if e is not None), None)
        titel = _tekst(kort) if kort is not None else (meta.findtext(N + "docName") if meta is not None else id)
        titel = titel.split("(Adopted")[0].strip()  # de docTitle van de Basic Law loopt door in de aanneming
    artikelen: list[Artikel] = []

    def loop(el: ET.Element, pad: list[str]) -> None:
        tussenkop: str | None = None
        for k in el:
            if k.tag in _INDELING:
                tussenkop = None
                loop(k, [*pad, _kop(k)])
            elif k.tag == N + "crossHeading":
                tussenkop = _tekst(k)
            elif k.tag in _EENHEID:
                nr = (k.find(N + "num").get("value") if k.find(N + "num") is not None else None) or k.get("name", "").lstrip("s")
                tekst = "\n\n".join(_leden(k)) or ("(Repealed)" if k.get("reason") == "repealed" else "")
                artikelen.append(Artikel(nummer=nr, tekst=tekst, opschrift=_tekst(k.find(N + "heading")) or None,
                                         pad=" › ".join([*pad, *([tussenkop] if tussenkop else [])]) or None))

    hoofd = root.find(N + "main")
    stijl = None
    if hoofd is not None:
        loop(hoofd, [])
        if not artikelen:
            artikelen, stijl = _vrij(hoofd), "Art"
    return Geparseerd(wet_id=id, titel=titel, versie=versie, bron_url=bron_url or WEB.format(id=id),
                      artikelen=[a for a in artikelen if a.nummer], ruw=data, ruw_extensie="xml", stijl=stijl)


def _vrij(hoofd: ET.Element) -> list[Artikel]:
    """De Basic Law: <p>-regels, "Article 18" opent een artikel, een tabelrij "Chapter IV … Political Structure" of
    "Section 1 … The Chief Executive" (zonder <p>) is een kop."""
    artikelen: list[Artikel] = []
    pad: list[str] = []
    leden: list[str] = []

    def af() -> None:
        if artikelen and leden:
            artikelen[-1].tekst = "\n\n".join(leden)

    def loop(el: ET.Element) -> None:
        naam = el.tag.rsplit("}", 1)[-1]
        if naam == "annex" or el.tag in _WEG:
            return
        if naam == "p":
            t = _tekst(el)
            m = re.fullmatch(r"Article (\d+)", t)
            if m:
                af()
                leden.clear()
                artikelen.append(Artikel(nummer=m.group(1), tekst="", pad=" › ".join(pad) or None))
            elif t and artikelen:
                leden.append(t)
            return
        if naam == "tr" and not any(k.tag.rsplit("}", 1)[-1] == "p" for k in el.iter()):
            t = " ".join(x for x in (_tekst(td) for td in el) if x)
            if re.match(r"Chapter [IVX]+\b", t):
                pad[:] = [t]
            elif re.match(r"Section \d+\b", t):
                pad[1:] = [t]
            return
        for k in el:
            loop(k)

    loop(hoofd)
    af()
    return artikelen


class _Bereik(io.RawIOBase):
    """Een bestand op afstand, gelezen met Range-verzoeken (64 kB of meer per keer), voor `zipfile`."""

    def __init__(self, c, url: str) -> None:
        r = c.head(url)
        r.raise_for_status()
        self.c, self.url, self.pos, self.lengte = c, url, 0, int(r.headers["content-length"])
        self._buf = (0, b"")

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, off: int, whence: int = 0) -> int:
        self.pos = off if whence == 0 else self.pos + off if whence == 1 else self.lengte + off
        return self.pos

    def read(self, n: int = -1) -> bytes:
        if n < 0:
            n = self.lengte - self.pos
        b0, b = self._buf
        if not (b0 <= self.pos and self.pos + n <= b0 + len(b)):
            eind = min(self.lengte, self.pos + max(n, 65536)) - 1
            r = self.c.get(self.url, headers={"Range": f"bytes={self.pos}-{eind}"})
            if r.status_code != 206:
                raise RuntimeError(f"Geen Range-antwoord van {self.url} ({r.status_code})")
            self._buf = b0, b = self.pos, r.content
        uit = b[self.pos - b0:self.pos - b0 + n]
        self.pos += len(uit)
        return uit


def haal_op(id: str, titel: str | None = None) -> Geparseerd:
    """`id`: 'cap26' (Sale of Goods Ordinance), 'cap622' (Companies Ordinance) of 'A101' (Basic Law)."""
    naam = id[3:] if id.startswith("cap") else id
    voorvoegsel = f"cap_{naam}_en_c" if id.startswith("cap") else f"{naam}_en_c"
    url = ZIP.format(deel=_deel(id))
    with client(timeout=180.0) as c:
        z = zipfile.ZipFile(_Bereik(c, url))
        lid = next((n for n in z.namelist() if re.split(r"[\\/]", n)[0] == voorvoegsel), None)
        if lid is None:
            raise ValueError(f"{id} niet gevonden in {url}")
        data = z.read(lid)
    return parse(data, id, WEB.format(id=naam if id.startswith("cap") else id), titel)
