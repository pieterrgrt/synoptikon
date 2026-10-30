"""GR: lawspot.gr, de volledige tekst van een wet op één pagina.

https://www.lawspot.gr/nomikes-plirofories/nomothesia/{slug}, bijv. astikos-kodikas, syntagma-tis-ellados,
nomos-2251-1994. Griekenland heeft geen open, machineleesbare geconsolideerde bron (het Staatsblad, search.et.gr,
geeft alleen de oorspronkelijke ΦΕΚ als pdf); lawspot houdt de codificaties en de belangrijkste wetten bij, met de
wijzigingen verwerkt, en staat crawlers toe (robots.txt). Een paar wetten (ΚΠολΔ, ΚΠΔ) zet lawspot achter een
login; die halen we niet op.

Opbouw: geneste <div class="chapter"> met een <h3 class="chapter__title"> (ΒΙΒΛΙΟ, ΚΕΦΑΛΑΙΟ, …) en daarin
<article class="legislation__article"> met kop "Άρθρο 914 - Αστικός Κώδικας - Έννοια" en <div class="body"> met de
tekst. Het pad volgt uit de nesting van de hoofdstukken.
"""
from __future__ import annotations

import re
from datetime import date
from html.parser import HTMLParser

from . import Artikel, Geparseerd
from .http import client

URL = "https://www.lawspot.gr/nomikes-plirofories/nomothesia/{slug}"


class _Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.artikelen: list[Artikel] = []
        self.titel = ""
        self.versie: str | None = None
        self._divs: list[bool] = []  # per open <div>: is het een hoofdstuk?
        self._hoofdstukken: list[str] = []
        self._in: str | None = None  # "h3" | "kop" | "body" | "h1"
        self._buf: list[str] = []
        self._alineas: list[str] = []
        self._kop = ""
        self._in_artikel = False
        self._tekst_na_versie = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        klassen = set((a.get("class") or "").split())
        if tag == "div":
            hoofdstuk = "chapter" in klassen
            self._divs.append(hoofdstuk)
            if hoofdstuk:
                self._hoofdstukken.append("")
            if "body" in klassen and self._in_artikel:
                self._in, self._alineas, self._buf = "body", [], []
        elif tag == "h3" and "chapter__title" in klassen:
            self._in, self._buf = "h3", []
        elif tag == "h1" and "post__title" in klassen:
            self._in, self._buf = "h1", []
        elif tag == "article" and "legislation__article" in klassen:
            self._in_artikel, self._kop = True, ""
        elif tag == "a" and "inner" in klassen and self._in_artikel and not self._kop:
            self._in, self._buf = "kop", []
        elif self._in == "body" and tag in ("p", "li", "tr", "br"):
            self._spoel()

    def _spoel(self) -> None:
        t = re.sub(r"\s+", " ", "".join(self._buf).replace("\xa0", " ")).strip()
        if t:
            self._alineas.append(t)
        self._buf = []

    def handle_endtag(self, tag):
        if tag == "h3" and self._in == "h3":
            if self._hoofdstukken:
                self._hoofdstukken[-1] = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            self._in = None
        elif tag == "h1" and self._in == "h1":
            self.titel = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            self._in = None
        elif tag == "a" and self._in == "kop":
            self._kop = re.sub(r"\s+", " ", "".join(self._buf)).strip()
            self._in = None
        elif tag == "div" and self._divs:
            if self._in == "body" and self._divs[-1] is False:
                self._spoel()
                self._in = "einde"
            if self._divs.pop() and self._hoofdstukken:
                self._hoofdstukken.pop()
        elif tag in ("p", "li", "tr") and self._in == "body":
            self._spoel()
        elif tag == "article" and self._in_artikel:
            self._sluit_artikel()

    def _sluit_artikel(self) -> None:
        self._in_artikel = False
        if self._in == "body":
            self._spoel()
        self._in = None
        delen = [d.strip() for d in self._kop.split(" - ")]
        m = re.match(r"^Άρθρο\s+(.+)$", delen[0]) if delen else None
        if not m:
            return
        nummer = re.sub(r"\s+", "", m.group(1))
        opschrift = delen[2] if len(delen) >= 3 else None
        pad = " › ".join(h for h in self._hoofdstukken if h) or None
        self.artikelen.append(Artikel(nummer=nummer, tekst="\n\n".join(self._alineas) or "—", opschrift=opschrift, pad=pad))

    def handle_data(self, data):
        if self._in in ("h3", "h1", "kop", "body"):
            self._buf.append(data)
        elif self.versie is None and "Τελευταία Τροποποίηση" in data:
            self._tekst_na_versie = True
        elif self._tekst_na_versie and (m := re.search(r"(\d{2})\.(\d{2})\.(\d{4})", data)):
            self.versie = f"{m.group(3)}-{m.group(2)}-{m.group(1)}"
            self._tekst_na_versie = False


def parse(html: str, wet_id: str, bron_url: str | None = None) -> Geparseerd:
    p = _Parser()
    p.feed(html)
    p.close()
    return Geparseerd(wet_id=wet_id, titel=p.titel or wet_id, versie=p.versie or date.today().isoformat(), bron_url=bron_url,
                      artikelen=p.artikelen, ruw=html.encode("utf-8"), ruw_extensie="html")


def haal_op(slug: str) -> Geparseerd:
    url = URL.format(slug=slug)
    with client() as c:
        r = c.get(url, follow_redirects=True)
        r.raise_for_status()
    g = parse(r.text, slug, url)
    if not g.artikelen:
        raise ValueError(f"lawspot: geen artikelen op {url} (achter een login?)")
    return g
