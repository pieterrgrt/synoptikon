"""SE: Riksdagens öppna data, Svensk författningssamling in de geconsolideerde stand van Regeringskansliet (SFST).

`https://data.riksdagen.se/dokument/sfs-1915-218.json` geeft metadata en de tekst als HTML; de ondertitel
("t.o.m. SFS 1994:1513") is de laatst verwerkte wijziging, en dus onze versie. De HTML is geen nette XML
(losse <p>-ankers tussen de leden), dus we knippen op de vaste markeringen:

* <h3 name="K1">1 kap. …</h3>: hoofdstuk (balken en nieuwere wetten); <h3>/<h4> zonder K-naam: kop
  boven één paragraaf (opschrift) of een reeks (een eenheid in het pad);
* <a class="paragraf" name="K1P2"><b>2 §</b></a>: begin van een paragraaf, tot de volgende markering;
* <p>-ankers scheiden de leden (*stycken*), <br /> de regels van een opsomming;
* <h3 name="overgang">: overgangsbepalingen, daar houden we op.

Staat een paragraaf er twee keer (de geldende met "/Upphör att gälla U:…/" en de nieuwe met "/Träder i kraft
I:…/"), dan nemen we de eerste, die nu geldt. Verwijzingen naar de wijzigingswet aan het eind van een lid
(<i>Lag (1994:1513)</i>) vallen weg.

Nummering: begint de paragraafnummering per hoofdstuk opnieuw (de balkar, aktiebolagslagen), dan
"hoofdstuk:paragraaf" ("RB 1:1", "BrB 3:1"); anders alleen de paragraaf ("36 § AvtL").
"""
from __future__ import annotations

import html
import re

from . import Artikel, Geparseerd
from .http import client

URL = "https://data.riksdagen.se/dokument/{id}.json"
WEB = "https://rkrattsbaser.gov.se/sfst?bet={bet}"  # de bron die het document zelf noemt

_TOKEN = re.compile(
    r'<h3 name="overgang"'
    r'|<h3 name="K(?P<kap>[^"]*)"[^>]*>(?P<kaptekst>.*?)</h3>'
    r'|<h[34][^>]*>(?P<kop>.*?)</h[34]>'
    r'|<a class="paragraf" name="(?P<naam>[^"]*)"><b>(?P<par>[^<]*)</b></a>',
    re.S,
)
_STATUS = re.compile(r"/\s*(?:Upphör att gälla|Träder i kraft)\s+[UI]:[^/]*/")


def _schoon(fragment: str) -> str:
    t = re.sub(r"<i>\s*(?:Lag|Förordning|Kungörelse)\s*\([^)]*\)\.?\s*</i>\.?", "", fragment)
    t = re.sub(r"<p>\s*<a name=\"[^\"]*\"></a>\s*</p>", "\n\n", t)
    t = re.sub(r"<br\s*/?>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = _STATUS.sub("", html.unescape(t))
    leden = []
    for lid in re.split(r"\n\s*\n", t):
        regels = [re.sub(r"[ \t\r\xa0]+", " ", r).strip() for r in lid.split("\n")]
        lid = "\n".join(r for r in regels if r)
        if lid:
            leden.append(lid)
    return "\n\n".join(leden)


def _kopnummer(tekst: str) -> str | None:
    m = re.match(r"(\d+(?:\s?[a-zåäö])?)\s*kap\.", tekst)
    return re.sub(r"(\d)\s?([a-zåäö])", r"\1 \2", m.group(1)) if m else None


def parse(data: bytes | dict, id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    import json

    doc = (json.loads(data) if isinstance(data, (bytes, str)) else data)["dokumentstatus"]["dokument"]
    h = doc.get("html") or ""
    begin = h.find("</div>", h.find('class="sfstoc"')) if 'class="sfstoc"' in h else 0
    h = h[max(begin, 0):]

    # (hoofdstuk, nummer, tekst, pad, kop) per paragraaf; koppen tussen paragrafen houden we apart bij
    ruwe: list[tuple[str | None, str, str, list[str], int | None]] = []
    koppen: list[str] = []
    pad: list[str] = []
    hoofdstuk: str | None = None
    kop: int | None = None  # index in `koppen` van de kop die nu geldt
    tokens = list(_TOKEN.finditer(h))
    for i, m in enumerate(tokens):
        if m.group(0).startswith('<h3 name="overgang"'):
            break
        eind = tokens[i + 1].start() if i + 1 < len(tokens) else len(h)
        if m.group("kaptekst") is not None:
            tekst = _schoon(m.group("kaptekst")).replace("\n", " ")
            hoofdstuk, pad, kop = _kopnummer(tekst), [tekst] if tekst else [], None
        elif m.group("kop") is not None:
            tekst = _schoon(m.group("kop")).replace("\n", " ")
            if tekst and tekst != "Innehåll:":
                koppen.append(tekst)
                kop = len(koppen) - 1
        elif m.group("par") is not None:
            nm = re.match(r"(\d+(?:\s?[a-zåäö])?)\s*§", m.group("par").strip())
            if nm:
                nr = re.sub(r"(\d)\s?([a-zåäö])", r"\1 \2", nm.group(1))
                ruwe.append((hoofdstuk, nr, _schoon(h[m.end():eind]), list(pad), kop))

    nummers = [nr for _, nr, _, _, _ in ruwe]
    per_hoofdstuk = any(hs for hs, *_ in ruwe) and len(nummers) > len(set(nummers))
    gebruik: dict[int, int] = {}
    for *_, k in ruwe:
        if k is not None:
            gebruik[k] = gebruik.get(k, 0) + 1
    artikelen: list[Artikel] = []
    gezien: set[str] = set()
    for hoofdstuk, nr, tekst, p, k in ruwe:
        if per_hoofdstuk and hoofdstuk:
            nr = f"{hoofdstuk}:{nr}"
        if nr in gezien:
            continue
        gezien.add(nr)
        opschrift = None
        if k is not None and gebruik[k] == 1:
            opschrift = koppen[k]
        elif k is not None:
            p = [*p, koppen[k]]
        artikelen.append(Artikel(nummer=nr, tekst=tekst or "(upphävd)", opschrift=opschrift, pad=" › ".join(p) or None))

    versie = (doc.get("subtitel") or "").strip() or f"SFS {doc.get('beteckning', id)}"
    if titel is None:
        titel = re.sub(r"\s+", " ", doc.get("titel") or "").strip() or id
    ruw = data if isinstance(data, bytes) else json.dumps(data, ensure_ascii=False).encode()
    return Geparseerd(wet_id=id, titel=titel, versie=versie, bron_url=bron_url or WEB.format(bet=doc.get("beteckning") or id), artikelen=artikelen,
                      ruw=ruw, ruw_extensie="json")


def haal_op(id: str, titel: str | None = None) -> Geparseerd:
    """`id`: SFS-nummer als '1915:218' of dok_id 'sfs-1915-218' (avtalslagen)."""
    if ":" in id:
        jaar, nr = id.split(":", 1)
        id = f"sfs-{jaar}-{nr}"
    with client(timeout=180.0) as c:
        r = c.get(URL.format(id=id))
        r.raise_for_status()
    return parse(r.content, id, None, titel)
