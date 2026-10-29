"""CA: Justice Laws Website van het Department of Justice, geconsolideerde federale wetten als XML.

`https://laws-lois.justice.gc.ca/eng/XML/{id}.xml` (id = het geconsolideerde nummer: C-46 Criminal Code, D-3.4
Divorce Act, B-3 Bankruptcy and Insolvency Act, C-44 CBCA, I-15 Interest Act). Dezelfde bestanden staan als bulk op
GitHub (justicecanada/laws-lois-xml); beide onder de Open Government Licence – Canada. Geen robots.txt.

Opbouw: <Body> met afwisselend <Heading level="1|2|3"> (Label + TitleText; samen het pad) en <Section> met
<MarginalNote> (het opschrift), <Label> (het nummer, ook "83.01") en daaronder <Text>, <Subsection>, <Paragraph>,
<Definition>. Historische noten (<HistoricalNote>) vallen weg; de bijlagen (<Schedule>) ook, want die hebben geen
section-nummering. `versie` is `lims:pit-date`, de stand van de consolidatie.

De Constitution Acts staan niet als XML op de site, alleen als HTML ("Const", één pagina met de Constitution Act,
1867 en de Canada Act 1982 met de Constitution Act, 1982). `haal_op("Const/1867")` en `haal_op("Const/1982")`
lezen die pagina en houden alleen het gevraagde deel.

Wetten zijn tweetalig; we nemen de Engelse tekst (de Franse staat onder /fra/XML/, met hetzelfde formaat).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date
from html.parser import HTMLParser

from . import Artikel, Geparseerd
from .http import client

URL = "https://laws-lois.justice.gc.ca/eng/XML/{id}.xml"
WEB = "https://laws-lois.justice.gc.ca/eng/acts/{id}/"
CONST = "https://laws-lois.justice.gc.ca/eng/Const/FullText.html"
LIMS = "{http://justice.gc.ca/lims}"
_WEG = {"HistoricalNote", "MarginalNote", "Label", "FootnoteRef", "Footnote"}
# Onderdelen met een eigen regel; hoe dieper, hoe meer ingesprongen.
_DEEL = {"Subsection": 0, "Definition": 0, "Paragraph": 1, "Subparagraph": 2, "Clause": 3, "Subclause": 4}


def _tekst(el: ET.Element) -> str:
    """Lopende tekst zonder noten; geneste onderdelen (Paragraph …) horen er niet bij."""
    delen: list[str] = []

    def loop(e: ET.Element) -> None:
        if e.text:
            delen.append(e.text)
        for k in e:
            if k.tag not in _WEG and k.tag not in _DEEL:
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
                tekst = " ".join(_tekst(t) for t in k if t.tag in ("Text", "Repealed", "ContinuedParagraph", "ContinuedSectionSubsection"))
                regel = " ".join(x for x in ((label.text or "").strip() if label is not None else "", tekst) if x)
                if regel:
                    uit.append("    " * _DEEL[k.tag] + regel)
                loop(k)
            elif k.tag in ("Text", "Repealed") and e is sectie:
                t = _tekst(k)
                if t:
                    uit.append(t)
            elif k.tag in ("ContinuedSectionSubsection", "ContinuedParagraph") and e is sectie:
                t = " ".join(_tekst(x) for x in k.iter("Text"))
                if t:
                    uit.append(t)

    loop(sectie)
    return uit


def parse(data: bytes, wet_id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    body = root.find("Body")
    artikelen: list[Artikel] = []
    koppen: dict[int, str] = {}
    for el in body if body is not None else []:
        if el.tag == "Heading":
            niveau = int(el.get("level") or 1)
            label, t = el.find("Label"), el.find("TitleText")
            kop = " · ".join(x for x in (_tekst(label) if label is not None else "", _tekst(t) if t is not None else "") if x)
            koppen = {n: k for n, k in koppen.items() if n < niveau}
            if kop:
                koppen[niveau] = kop
        elif el.tag == "Section":
            label = el.find("Label")
            if label is None or not (label.text or "").strip():
                continue
            noot = el.find("MarginalNote")
            artikelen.append(Artikel(nummer=label.text.strip(), tekst="\n\n".join(_alineas(el)) or "(repealed)",
                                     opschrift=_tekst(noot) if noot is not None else None,
                                     pad=" › ".join(koppen[n] for n in sorted(koppen)) or None))
    if titel is None:
        t = next((x for x in (root.find("Identification/ShortTitle"), root.find("Identification/LongTitle")) if x is not None), None)
        titel = _tekst(t) if t is not None else wet_id
    versie = root.get(LIMS + "pit-date") or root.get(LIMS + "lastAmendedDate") or date.today().isoformat()
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie, bron_url=bron_url or WEB.format(id=wet_id), artikelen=artikelen,
                      ruw=data, ruw_extensie="xml")


class _Const(HTMLParser):
    """De HTML van de Constitution Acts: <h2>CONSTITUTION ACT, 1867|1982</h2>, koppen <h2 class="Part">/<h3>/<h4>
    met een span HTitleText, en per section een <a class="sectionLabel"> met het nummer; de MarginalNote gaat eraan
    vooraf. Eindnoten (<a href="#end…">) en de lijst "Endnotes" vallen weg."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.delen: dict[str, list[Artikel]] = {}
        self.versie: str | None = None
        self._deel: str | None = None
        self._koppen: dict[int, str] = {}
        self._in: str | None = None  # "akte" | "kop" | "noot" | "label" | "tekst" | "datum"
        self._niveau = 0
        self._buf: list[str] = []
        self._noot: str | None = None
        self._art: Artikel | None = None
        self._regels: list[str] = []
        self._weg = 0  # diepte binnen een eindnootverwijzing

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        klasse = a.get("class") or ""
        if self._weg:
            self._weg += 1
            return
        if tag == "a" and (a.get("href") or "").startswith("#end"):
            self._weg = 1
        elif tag == "h2" and klasse in ("", "Title-of-Act"):
            self._sluit()
            self._in, self._buf = "akte", []
        elif tag in ("h2", "h3", "h4") and klasse in ("Part", "Subheading"):
            self._sluit()
            self._in, self._buf, self._niveau = "kop", [], int(tag[1])
        elif tag == "h2" and "scheduleLabel" in klasse:
            self._sluit()
            self._deel = None
        elif tag == "p" and klasse == "MarginalNote":
            self._sluit()
            self._in, self._buf = "noot", []
        elif tag == "span" and klasse == "sectionLabel" and self._deel:
            self._sluit()
            self._in, self._buf = "label", []
        elif self._art is not None and self._in == "tekst" and (tag in ("p", "li") or klasse.startswith("listItemBlock")):
            self._spoel()
        elif tag == "div" and klasse.startswith("listItemText") and self._in == "tekst":
            self._buf.append(" ")
        elif tag == "span" and klasse == "wb-invisible" and self._in == "noot":
            self._weg = 1
        elif tag == "span" and self._in == "kop":
            self._buf.append(" · " if "".join(self._buf).strip() else "")
        elif tag == "time" and a.get("property") == "dateModified":
            self._in, self._buf = "datum", []

    def handle_endtag(self, tag):
        if self._weg:
            self._weg -= 1
            return
        if tag == "h2" and self._in == "akte":
            t = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            m = re.search(r"^CONSTITUTION ACT, (\d{4})", t)
            self._deel = m.group(1) if m else None
            if self._deel:
                self.delen.setdefault(self._deel, [])
            self._koppen, self._in = {}, None
        elif tag in ("h2", "h3", "h4") and self._in == "kop":
            t = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            self._koppen = {n: k for n, k in self._koppen.items() if n < self._niveau}
            if t:
                self._koppen[self._niveau] = t
            self._in = None
        elif tag == "p" and self._in == "noot":
            self._noot = re.sub(r"\s+", " ", "".join(self._buf)).strip() or None
            self._in = None
        elif tag == "span" and self._in == "label":
            nummer = re.sub(r"\s+", "", "".join(self._buf))
            self._art = Artikel(nummer=nummer, tekst="", opschrift=self._noot,
                                pad=" › ".join(self._koppen[n] for n in sorted(self._koppen)) or None)
            self._noot, self._regels, self._buf, self._in = None, [], [], "tekst"
        elif tag in ("p", "li") and self._in == "tekst":
            self._spoel()
        elif tag == "time" and self._in == "datum":
            m = re.search(r"\d{4}-\d\d-\d\d", "".join(self._buf))
            self.versie, self._in = (m.group(0) if m else None), None
        elif tag == "main":
            self._sluit()

    def _spoel(self) -> None:
        t = re.sub(r"\s+", " ", "".join(self._buf).replace("\xa0", " ")).strip()
        if t:
            self._regels.append(t)
        self._buf = []

    def _sluit(self) -> None:
        if self._art is not None and self._deel and self._art.nummer:
            self._spoel()
            self._art.tekst = "\n\n".join(self._regels) or "(repealed)"
            self.delen[self._deel].append(self._art)
        self._art, self._regels = None, []
        if self._in == "tekst":
            self._in = None

    def handle_data(self, data):
        if self._weg:
            return
        if self._in:
            self._buf.append(data)


def parse_const(html: str, deel: str) -> Geparseerd:
    p = _Const()
    p.feed(html)
    p.close()
    p._sluit()
    artikelen = p.delen.get(deel, [])
    gezien: dict[str, Artikel] = {}
    for a in artikelen:  # een section kan in meer stukken staan (bijv. de bevoegdheidslijst van s 91): samenvoegen
        if a.nummer in gezien:
            gezien[a.nummer].tekst += "\n\n" + a.tekst
        else:
            gezien[a.nummer] = a
    return Geparseerd(wet_id=f"Const/{deel}", titel=f"Constitution Act, {deel}", versie=p.versie or date.today().isoformat(),
                      bron_url=CONST, artikelen=list(gezien.values()), ruw=html.encode("utf-8"), ruw_extensie="html")


def haal_op(wet_id: str, titel: str | None = None) -> Geparseerd:
    with client(timeout=180.0) as c:
        if wet_id.startswith("Const/"):
            r = c.get(CONST)
            r.raise_for_status()
            g = parse_const(r.text, wet_id.split("/", 1)[1])
            g.titel = titel or g.titel
            return g
        r = c.get(URL.format(id=wet_id))
        r.raise_for_status()
    return parse(r.content, wet_id, WEB.format(id=wet_id), titel)
