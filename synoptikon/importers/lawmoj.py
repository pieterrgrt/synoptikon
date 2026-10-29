"""TW: 全國法規資料庫 (law.moj.gov.tw) van het ministerie van Justitie, de geldende tekst van een wet op één pagina.

https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={pcode}, bijv. B0000001 (民法). De open-databestanden onder
/api/ geven alleen alle wetten tegelijk (een zip van tientallen MB) en vallen onder `Disallow: /` in robots.txt;
LawAll.aspx is daar uitdrukkelijk toegestaan. Geconsolideerd: de pagina toont de geldende stand, met de datum van
de laatste wijziging (修正日期, anders 公布日期) in de jaartelling van de Republiek (民國 104 年 = 2015); die
datum is de versie.

Opbouw: in <div class="law-reg-content"> koppen <div class="h3 char-N"> (N = diepte: 編, 章, 節, 款) en per
artikel een rij met <a name="7-1">第 7-1 條</a> en regels <div class="line-0000 show-number"> (een nieuw lid)
of <div class="line-0004"> (een onderdeel, ingesprongen). Artikelen hebben geen opschrift. We nummeren als de
bron: 184, 7-1 (第七條之一).
"""
from __future__ import annotations

import html
import re

from . import Artikel, Geparseerd
from .http import client

URL = "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode={id}"

_TITEL = re.compile(r'id="hlLawName"[^>]*>(.*?)</a>', re.S)
_DATUM = re.compile(r"<th>(修正|公布)日期：</th>\s*<td>\s*民國\s*(\d+)\s*年\s*(\d+)\s*月\s*(\d+)\s*日", re.S)
_DEEL = re.compile(
    r'<div class="h3 char-(\d)">(.*?)</div>'
    r'|<div class="col-no">\s*<a [^>]*name="([0-9-]+)"[^>]*>.*?</a></div>\s*<div class="col-data"><div class="law-article">(.*?)</div>\s*</div></div>',
    re.S,
)
_REGEL = re.compile(r'<div class="line-(\d{4})( show-number)?">(.*?)</div>', re.S)


def _schoon(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def _kop(s: str) -> str:
    """"第 一 章 總則" → "第一章 總則", "第 四 章之一 農育權" → "第四章之一 農育權"."""
    return re.sub(r"^第\s*(\S+?)\s*([編章節款目](?:之\S+?)?)\s+", r"第\1\2 ", _schoon(s))


def _tekst(blok: str) -> str:
    leden: list[list[str]] = []
    for inspring, nieuw, regel in _REGEL.findall(blok):
        regel = _schoon(regel)
        if not regel:
            continue
        if nieuw or not leden:
            leden.append([])
        leden[-1].append(("    " if inspring != "0000" else "") + regel)
    return "\n\n".join("\n".join(lid) for lid in leden)


def parse(data: bytes, pcode: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    s = data.decode("utf-8")
    m = _DATUM.search(s)
    if not m:
        raise ValueError(f"Geen 修正日期/公布日期 op de pagina van {pcode}")
    versie = f"{int(m.group(2)) + 1911}-{int(m.group(3)):02d}-{int(m.group(4)):02d}"
    if titel is None:
        t = _TITEL.search(s)
        titel = _schoon(t.group(1)) if t else pcode
    begin = s.find('class="law-reg-content"')
    artikelen: list[Artikel] = []
    koppen: dict[int, str] = {}
    for diepte, kop, nummer, blok in _DEEL.findall(s[begin:] if begin >= 0 else s):
        if diepte:
            d = int(diepte)
            koppen = {k: v for k, v in koppen.items() if k < d}
            koppen[d] = _kop(kop)
        else:
            pad = " › ".join(v for _, v in sorted(koppen.items())) or None
            artikelen.append(Artikel(nummer=nummer, tekst=_tekst(blok) or "（刪除）", pad=pad))
    return Geparseerd(wet_id=pcode, titel=titel, versie=versie, bron_url=bron_url or URL.format(id=pcode),
                      artikelen=artikelen, ruw=data, ruw_extensie="html")


def haal_op(id: str, titel: str | None = None) -> Geparseerd:
    """`id`: de pcode, bijv. 'B0000001' (民法)."""
    with client(timeout=120.0) as c:
        r = c.get(URL.format(id=id))
        r.raise_for_status()
    return parse(r.content, id, URL.format(id=id), titel)
