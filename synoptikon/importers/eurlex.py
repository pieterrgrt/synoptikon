"""EU: EUR-Lex, HTML op CELEX-nummer.

https://eur-lex.europa.eu/legal-content/{TAAL}/TXT/HTML/?uri=CELEX:{celex}
Nieuwere documenten hebben <div class="eli-subdivision" id="art_12">; oudere
alleen <p class="ti-art">Artikel 12</p> gevolgd door <p class="sti-art"> en
<p class="normal">. Beide vormen worden herkend. De parser is bewust
pragmatisch: EU-teksten dienen hier als vergelijkingsmateriaal, niet als
authentieke publicatie; de link naar EUR-Lex blijft erbij.
"""
from __future__ import annotations

import re
from datetime import date
from html.parser import HTMLParser

from . import Artikel, Geparseerd
from .http import client

URL = "https://eur-lex.europa.eu/legal-content/{taal}/TXT/HTML/?uri=CELEX:{celex}"

_ART_RE = re.compile(r"^(Artikel|Article|Artículo|Articolo|Artigo)\s+(\d+[a-z]?)\b", re.IGNORECASE)


class _Parser(HTMLParser):
    """Zet de HTML om in een lijst (klasse, id, tekst) per blok-element."""

    BLOK = {"p", "div", "h1", "h2", "h3", "h4", "td", "li", "table"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blokken: list[tuple[str, str, str]] = []
        self._stapel: list[tuple[str, str, list[str]]] = []
        self.titel = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        if tag in self.BLOK:
            self._stapel.append((a.get("class", ""), a.get("id", ""), []))

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in self.BLOK and self._stapel:
            klasse, id_, delen = self._stapel.pop()
            tekst = re.sub(r"\s+", " ", "".join(delen)).strip()
            if tekst:
                self.blokken.append((klasse, id_, tekst))
            if self._stapel and tag != "div":
                # Tekst van geneste blokken niet dubbel tellen bij de ouder.
                pass

    def handle_data(self, data):
        if self._in_title:
            self.titel += data
        if self._stapel:
            # Alleen aan het binnenste blok toevoegen.
            self._stapel[-1][2].append(data)


def parse(html: str, celex: str, bron_url: str | None = None) -> Geparseerd:
    p = _Parser()
    p.feed(html)
    titel = re.sub(r"\s+", " ", p.titel).strip() or celex
    titel = re.sub(r"\s*[-–]\s*EUR-Lex.*$", "", titel)

    artikelen: list[Artikel] = []
    huidig: Artikel | None = None
    pad: list[str] = []
    buffer: list[str] = []

    def sluit():
        nonlocal huidig, buffer
        if huidig is not None:
            huidig.tekst = "\n\n".join(buffer).strip() or huidig.tekst
            artikelen.append(huidig)
        huidig, buffer = None, []

    for klasse, id_, tekst in p.blokken:
        klassen = klasse.split()
        m = _ART_RE.match(tekst)
        if ("ti-art" in klassen or re.fullmatch(r"art_\d+[a-z]?", id_ or "")) and m:
            sluit()
            huidig = Artikel(nummer=m.group(2), tekst="", pad=" › ".join(pad) or None)
            rest = tekst[m.end():].strip(" -–—")
            if rest:
                huidig.opschrift = rest
            continue
        if "ti-section-1" in klassen or "ti-section-2" in klassen or ("title-division-1" in klassen):
            if "ti-section-1" in klassen or "title-division-1" in klassen:
                pad = [tekst]
            else:
                pad = pad[:1] + [tekst]
            continue
        if huidig is not None:
            if "sti-art" in klassen and not huidig.opschrift:
                huidig.opschrift = tekst
            elif "normal" in klassen or klasse == "" or "norm" in klassen or "ti-grseq-1" in klassen:
                buffer.append(tekst)
        if "doc-ti" in klassen and not artikelen and huidig is None and len(tekst) > len(titel) and len(tekst) < 400:
            titel = tekst
    sluit()
    # Ontdubbel: geneste divs kunnen hetzelfde artikel tweemaal opleveren.
    gezien: set[str] = set()
    uniek = []
    for a in artikelen:
        if a.nummer not in gezien:
            gezien.add(a.nummer)
            uniek.append(a)
    return Geparseerd(wet_id=celex, titel=titel, versie=date.today().isoformat(), bron_url=bron_url, artikelen=uniek, ruw=html.encode(), ruw_extensie="html")


def haal_op(celex: str, taal: str = "NL") -> Geparseerd:
    url = URL.format(taal=taal.upper(), celex=celex)
    with client() as c:
        r = c.get(url)
        r.raise_for_status()
    return parse(r.text, celex, url)
