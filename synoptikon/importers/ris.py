"""AT: Rechtsinformationssystem des Bundes (RIS), geltende Fassung van een bundeswet.

De OGD-API van het BKA (data.bka.gv.at/ris/api/v2.6/Bundesrecht) levert elke paragraaf als eigen document, met
in de metadata een `GesamteRechtsvorschriftUrl`: de hele wet in de geldende stand op één pagina
(`ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=…`). Die ene pagina halen we op in
plaats van honderden losse paragrafen (ABGB: ±1400). De robots.txt van het RIS sluit alleen de map
/GeltendeFassung/ (de RTF- en pdf-downloads) uit, niet deze pagina; crawl-delay 2.

Opbouw: per paragraaf een <div class="documentContent"> met het nummer in de <h2> ("§ 1295", "Art. 7") en de
tekst in een TextContainer. Koppen (<h4 class="UeberschrG1|UeberschrG2|UeberschrArt">) staan boven de eerste
paragraaf van hun eenheid; hun niveau is niet aan de klasse af te lezen, wel aan het woord ("Theil",
"Abtheilung", "Hauptstück", "Abschnitt", "I.", "a)"). Een kop zonder zo'n woord direct na een andere kop is
een vervolgregel ("Zweyter Theil / des / bürgerlichen Gesetzbuches."). <h4 class="UeberschrPara"> is het
opschrift van de paragraaf. Alles in <span class="sr-only"> (de voorleesversie, "Absatz eins,") valt weg.

Aan het eind van een wet staan de overgangsbepalingen van wijzigingswetten als "Art. 10 § 1"; die passen niet
in de paragraafnummering en laten we weg: alleen de soort (§ of Art.) die het vaakst voorkomt blijft.

Versie: de laatste wijziging in de lijst "Änderung" ("BGBl. I Nr. 109/2025"), dus stabiel zolang de tekst niet
verandert. Bekende Gesetzesnummern: 10001622 (ABGB), 10001702 (UGB), 10002462 (KSchG), 10001699 (ZPO),
10002296 (StGB), 10000138 (B-VG), 10002426 (IPRG).
"""
from __future__ import annotations

import html as htmllib
import re
from collections import Counter

from . import Artikel, Geparseerd
from .http import client

URL = "https://ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer={nr}"

# Niveau van een kop naar het eerste woord; hoe lager, hoe hoger in de boom.
_NIVEAU = [
    (re.compile(r"^(?:\S+\s+)?(?:Th?eil|Buch)\b|^Einleitung\b", re.I), 1),
    (re.compile(r"^(?:\S+\s+)?Abth?eilung\b", re.I), 2),
    (re.compile(r"^(?:\S+\s+){0,3}Hauptstück\b", re.I), 3),
    (re.compile(r"^(?:\S+\s+)?Abschnitt\b|^Abschnitt\s", re.I), 4),
    (re.compile(r"^(?:\S+\s+)?Unterabschnitt\b|^Artikel\s+[IVXLC\d]+\b", re.I), 5),
    (re.compile(r"^(?:[IVXLC]+\.|[A-Z]\.)\s"), 6),
    (re.compile(r"^(?:\d+\.|[a-z]\)|\d+\))\s"), 7),
]
_ONDERSTE = 8


def _niveau(kop: str) -> int | None:
    for patroon, n in _NIVEAU:
        if patroon.search(kop):
            return n
    return None


def _schoon(s: str) -> str:
    s = re.sub(r'<span class="sr-only">.*?</span>', "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", htmllib.unescape(s).replace("\xa0", " ")).strip()


def _tekst(blok: str) -> str:
    """Leden op een eigen alinea, opsommingen op een eigen regel ("1. …")."""
    s = re.sub(r'<span class="sr-only">.*?</span>', "", blok, flags=re.S)
    s = re.sub(r"<h[345][^>]*>.*?</h[345]>", "", s, flags=re.S)
    s = re.sub(r"</div>|</li>|</p>|<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    regels = [re.sub(r"\s+", " ", r).strip() for r in htmllib.unescape(s).replace("\xa0", " ").split("\n")]
    regels = [r for r in regels if r]
    uit: list[str] = []
    for r in regels:
        if uit and re.fullmatch(r"(?:\d+[a-z]?\.|[a-z]{1,2}\)|lit\. [a-z]+\)|[–-])", uit[-1]):
            uit[-1] = f"{uit[-1]} {r}"
        else:
            uit.append(r)
    tekst = ""
    for r in uit:
        if not tekst:
            tekst = r
        elif re.match(r"\(\d+[a-z]?\)", r):
            tekst += "\n\n" + r
        else:
            tekst += "\n" + r
    return tekst


def _versie(pagina: str) -> str | None:
    m = re.search(r'AenderungContainer.*?</div>\s*</div>\s*</div>', pagina, re.S)
    stuk = _schoon(m.group(0)) if m else ""
    nrs = re.findall(r"BGBl\.\s*(I\s+)?Nr\.\s*(\d+)/(\d{4})", stuk)
    if not nrs:
        m = re.search(r"StF:\s*(BGBl\.[^<(]*?Nr\.\s*\d+/\d{4}|JGS Nr\.\s*\d+/\d{4}|RGBl\. Nr\.\s*\d+/\d{4})", pagina)
        return m.group(1).strip() if m else None
    deel, nr, jaar = nrs[-1]
    return f"BGBl. {'I ' if deel else ''}Nr. {nr}/{jaar}"


def parse(pagina: str, wet_id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    blokken = re.split(r'<div class="documentContent">', pagina)[1:]
    ruw: list[tuple[str, str, str | None, str]] = []  # soort, nummer, opschrift, pad
    pad: list[tuple[int, str]] = []
    langtitel = None
    for blok in blokken:
        m = re.search(r'<h2 class="onlyScreenreader">(.*?)</h2>', blok, re.S)
        label = _schoon(m.group(1)) if m else ""
        if langtitel is None:
            lt = re.search(r'LangtitelContainer[^>]*>\s*<h3>[^<]*</h3>(.*?)(?:<br|</div>)', blok, re.S)
            if lt:
                langtitel = _schoon(lt.group(1))
        tc = re.search(r'TextContainer[^>]*>(.*)', blok, re.S)
        if not tc:
            continue
        inhoud = tc.group(1)
        opschrift = None
        vorige_kop = False
        for k in re.finditer(r'<h4 class="(Ueberschr\w*)[^"]*"[^>]*>(.*?)</h4>', inhoud, re.S):
            klasse, kop = k.group(1), _schoon(k.group(2))
            if not kop:
                continue
            if klasse == "UeberschrPara":
                opschrift = kop.rstrip(".")
                continue
            n = _niveau(kop)
            if n is None and vorige_kop and pad and klasse != "UeberschrArt":
                pad[-1] = (pad[-1][0], f"{pad[-1][1]} {kop}")
                continue
            n = n or _ONDERSTE
            while pad and pad[-1][0] >= n:
                pad.pop()
            pad.append((n, kop))
            vorige_kop = klasse != "UeberschrArt"
        nm = re.fullmatch(r"(§|Art\.)\s*(\d+[a-z]{0,3})", label)
        if not nm:
            continue
        ruw.append((nm.group(1), nm.group(2), opschrift, " › ".join(p for _, p in pad) or None, _tekst(inhoud)))
    soort = Counter(r[0] for r in ruw).most_common(1)[0][0] if ruw else "§"
    artikelen, gezien = [], set()
    for s, nr, opschrift, p, tekst in ruw:
        if s != soort or nr in gezien:
            continue
        gezien.add(nr)
        artikelen.append(Artikel(nummer=nr, tekst=tekst or "(aufgehoben)", opschrift=opschrift, pad=p))
    if titel is None:
        titel = langtitel or wet_id
    return Geparseerd(wet_id=wet_id, titel=titel, versie=_versie(pagina) or "onbekend", bron_url=bron_url or URL.format(nr=wet_id),
                      artikelen=artikelen, ruw=pagina.encode("utf-8"), ruw_extensie="html", stijl="Art" if soort == "Art." else None)


def haal_op(nr: str, titel: str | None = None) -> Geparseerd:
    """`nr`: de Gesetzesnummer, bijv. '10001622' (ABGB)."""
    with client(timeout=300.0) as c:
        r = c.get(URL.format(nr=nr))
        r.raise_for_status()
    return parse(r.text, nr, URL.format(nr=nr), titel)
