"""TR: mevzuat.gov.tr, de officiële databank van het Turkse presidentschap (Mevzuat Bilgi Sistemi).

https://www.mevzuat.gov.tr/anasayfa/MevzuatFihristDetayIframe?MevzuatTur=1&MevzuatNo={nr}&MevzuatTertip=5 geeft de
geconsolideerde tekst van een wet als Word-HTML (de pagina die de site zelf in een iframe toont). Id = het
wetsnummer (`4721` Türk Medeni Kanunu, `6098` Türk Borçlar Kanunu), of `tur.nr.tertip` voor een ander soort
regeling (`1.5.6102`). robots.txt beperkt alleen Googlebot.

Opbouw, zonder bruikbare klassen (elke wet heeft eigen Word-stijlen), dus op de tekst:

* een structuurkop staat op een eigen regel ("BİRİNCİ KISIM", "İKİNCİ KİTAP", "ÜÇÜNCÜ BÖLÜM", "BİRİNCİ AYIRIM"),
  met de titel op de regel erna ("Genel Hükümler");
* een artikel begint met "MADDE 1-" ("GEÇİCİ MADDE 2 –", "EK MADDE 1-"); de kantkoppen (kenar başlıkları,
  "A. Sözleşmenin kurulması", "I. İrade açıklaması", "1. Genel olarak") staan direct erboven, na een lege regel;
* achteraan een tabel met de inwerkingtreding van de wijzigingen en de voetnoten.

De versie is de laatste datum van inwerkingtreding uit die tabel, of anders de laatste datum in de
wijzigingsnoten in de tekst ("(Değişik: 13/2/2011-6111/213 md.)"): zo blijft ze gelijk zolang de tekst niet wijzigt.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser

from . import Artikel, Geparseerd
from .http import client

URL = "https://www.mevzuat.gov.tr/anasayfa/MevzuatFihristDetayIframe?MevzuatTur={tur}&MevzuatNo={nr}&MevzuatTertip={tertip}"
WEB = "https://www.mevzuat.gov.tr/mevzuat?MevzuatNo={nr}&MevzuatTur={tur}&MevzuatTertip={tertip}"

_BLOK = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "td", "li", "div"}
_STRUCTUUR = re.compile(r"^(?:[A-ZÇĞİÖŞÜ]+\s+){1,2}(KİTAP|KISIM|BÖLÜM|AYIRIM|KESİM)\b\s*(.*)$")
_NIVEAU = {"KİTAP": 1, "KISIM": 2, "BÖLÜM": 3, "AYIRIM": 4, "KESİM": 5}
_MADDE = re.compile(r"^(GEÇİCİ\s+|EK\s+)?MADDE\s+(\d+(?:/[A-Z])?)\s*[-–—]\s*(.*)$", re.S)
_EINDE = re.compile(r"SAYILI\s+(?:KANUNA|KANUN\s+HÜKMÜNDE).*(?:EK\s+VE\s+DEĞİŞİKLİK|İŞLENEMEYEN)")
_NOOT = re.compile(r"\((?:Değişik|Ek|Mülga|İptal|Yeniden düzenleme)[^:()]*:\s*(\d{1,2})/(\d{1,2})/(\d{4})")
_DATUM = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
# Kantkoppen: A. · I. · 1. · a. · aa. — het niveau volgt uit de nummering.
# "I." en "V." zijn Romeins (de letterreeks komt zelden zo ver).
_KANT = [(re.compile(r"^[IVXL]+\.\s"), 2), (re.compile(r"^[A-ZÇĞİÖŞÜ]\.\s"), 1), (re.compile(r"^\d+\.\s"), 3),
         (re.compile(r"^[a-zçğıöşü]\.\s"), 4), (re.compile(r"^[a-zçğıöşü]{2}\.\s"), 5)]


class _Blokken(HTMLParser):
    """De tekst van de body als reeks blokken; een lege string is een lege regel."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blokken: list[str] = []
        self._buf: list[str] = []
        self._body = False

    def _spoel(self, leeg: bool = True) -> None:
        t = re.sub(r"\s+", " ", "".join(self._buf).replace("\xa0", " ")).strip()
        self._buf = []
        if self._body and (t or leeg):
            self.blokken.append(t)

    def handle_starttag(self, tag, attrs):
        if tag == "body":
            self._body = True
        elif tag in _BLOK or tag == "br":
            if "".join(self._buf).strip():
                self._spoel()
            self._buf = []

    def handle_endtag(self, tag):
        if tag in _BLOK:
            self._spoel(leeg=tag in ("p", "h1", "h2", "h3", "h4", "h5", "h6"))  # een lege alinea is een lege regel

    def handle_data(self, data):
        if self._body:
            self._buf.append(data)


def _kantniveau(t: str) -> int:
    for patroon, n in _KANT:
        if patroon.match(t):
            return n
    return 6


def _is_kop(t: str) -> bool:
    return len(t) <= 140 and not t.endswith((".", ":", ";", ",")) and not t.startswith("(")


def _versie(blokken: list[str], einde: int) -> str | None:
    datums = [(int(j), int(m), int(d)) for b in blokken[einde:] for d, m, j in _DATUM.findall(b)]
    if not datums:
        datums = [(int(j), int(m), int(d)) for b in blokken[:einde] for d, m, j in _NOOT.findall(b)]
    if not datums:
        return None
    j, m, d = max(datums)
    return f"{j:04d}-{m:02d}-{d:02d}"


def parse(data: bytes, wet_id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    p = _Blokken()
    p.feed(data.decode("utf-8", "replace"))
    p.close()
    blokken = p.blokken
    einde = next((i for i, b in enumerate(blokken) if _EINDE.search(b)), len(blokken))
    eerste = next((b for b in blokken if b), "")

    artikelen: list[Artikel] = []
    structuur: list[tuple[int, str]] = []
    kant: list[tuple[int, str]] = []
    huidig: dict | None = None
    wachtend: list[str] = []  # na een lege regel: kantkoppen van het volgende artikel, of nog tekst
    na_leeg = False
    i = 0

    def sluit() -> None:
        nonlocal huidig
        if huidig is not None:
            tekst = "\n\n".join(huidig["alineas"]).strip()
            artikelen.append(Artikel(nummer=huidig["nummer"], tekst=tekst or "—", opschrift=huidig["opschrift"], pad=huidig["pad"]))
        huidig = None

    while i < einde:
        b = blokken[i]
        i += 1
        if not b:
            na_leeg = True
            if huidig is None:  # de kop van de wet (nummer, datums) is geen kantkop
                wachtend = []
            continue
        if re.fullmatch(r"\[\d+\]\s.*", b, re.S) and huidig is None and not artikelen:
            continue
        m = _STRUCTUUR.match(b)
        if m and b.split()[0].isupper():
            if huidig is not None:
                huidig["alineas"].extend(wachtend)
            sluit()
            wachtend, na_leeg = [], False
            naam = m.group(2).strip()
            if not naam:  # titel op de volgende niet-lege regel
                while i < einde and not blokken[i]:
                    i += 1
                if i < einde and not _MADDE.match(blokken[i]) and _is_kop(blokken[i]):
                    naam = blokken[i]
                    i += 1
            niveau = _NIVEAU[m.group(1)]
            kop = f"{b.split(m.group(1))[0]}{m.group(1)}".strip() + (f" · {naam}" if naam else "")
            structuur = [s for s in structuur if s[0] < niveau] + [(niveau, kop)]
            kant = []
            continue
        m = _MADDE.match(b)
        if m:
            koppen = [w for w in wachtend if _is_kop(w)]
            if huidig is not None:
                huidig["alineas"].extend(w for w in wachtend if not _is_kop(w))
            sluit()
            for k in koppen:
                n = _kantniveau(k)
                kant = [x for x in kant if x[0] < n] + [(n, k)]
            opschrift = koppen[-1] if koppen else None
            boven = [x[1] for x in kant if not opschrift or x[1] != opschrift]
            soort = {"GEÇİCİ": "Geçici ", "EK": "Ek "}.get((m.group(1) or "").strip(), "")
            huidig = {"nummer": soort + m.group(2), "opschrift": opschrift, "alineas": [m.group(3).strip()] if m.group(3).strip() else [],
                      "pad": " › ".join([s[1] for s in structuur] + boven) or None}
            wachtend, na_leeg = [], False
            continue
        if huidig is None:
            wachtend.append(b)
            continue
        if na_leeg or wachtend:
            wachtend.append(b)
            # Een tweede alinea na een lege regel die geen kop kan zijn: alles was nog tekst van het artikel.
            if not _is_kop(b):
                huidig["alineas"].extend(wachtend)
                wachtend = []
            na_leeg = False
            continue
        huidig["alineas"].append(b)
    if huidig is not None:
        huidig["alineas"].extend(wachtend)
    sluit()

    # Een tweede artikel met hetzelfde nummer (bijv. de geïntegreerde invoeringswet) wint niet.
    gezien: set[str] = set()
    uniek = []
    for a in artikelen:
        if a.nummer not in gezien:
            gezien.add(a.nummer)
            uniek.append(a)
    tur, nr, tertip = _id(wet_id)
    return Geparseerd(wet_id=wet_id, titel=titel or eerste.title() or wet_id, versie=_versie(blokken, einde) or "onbekend",
                      bron_url=bron_url or WEB.format(nr=nr, tur=tur, tertip=tertip), artikelen=uniek, ruw=data, ruw_extensie="html")


def _id(wet_id: str) -> tuple[str, str, str]:
    delen = wet_id.split(".")
    return (delen[0], delen[2], delen[1]) if len(delen) == 3 else ("1", wet_id, "5")


def haal_op(wet_id: str, titel: str | None = None) -> Geparseerd:
    tur, nr, tertip = _id(wet_id)
    with client(timeout=120.0) as c:
        r = c.get(URL.format(tur=tur, nr=nr, tertip=tertip))
        r.raise_for_status()
    g = parse(r.content, wet_id, WEB.format(nr=nr, tur=tur, tertip=tertip), titel)
    if not g.artikelen:
        raise ValueError(f"mevzuat.gov.tr: geen artikelen voor {wet_id}")
    return g
