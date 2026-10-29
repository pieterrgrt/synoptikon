"""PT: Procuradoria-Geral Distrital de Lisboa (Ministério Público), "Legislação", versão actualizada.

Het Diário da República (diariodarepublica.pt) heeft wel geconsolideerde wetgeving, maar alleen in een
JavaScript-toepassing zonder open API. De PGDL, een openbare instelling, houdt de geconsolideerde stand van
de belangrijkste codes bij als gewone HTML: `lei_mostra_articulado.php?nid=775&tabela=leis&ficha=1` is het
Código Civil, 100 artikelen per pagina (`ficha=101`, `201`, …). Geen officiële bron, wel geconsolideerd.

Opbouw per pagina: koppen in <td class=txt_11_b_l> ("LIVRO I<br>PARTE GERAL<br>TÍTULO I<br>…"), daarna per
artikel een kop "Artigo 405.º<br> (Liberdade contratual)" en de tekst in <td … class=txt_base_n_l>, met <BR>
tussen de nummers ("1. …"). De lijst van wijzigingen en eerdere versies onder elk artikel valt weg.

Nummering: "405.º" → "405", "1305.º-A" → "1305-A".

Versie: de laatste wijzigingswet uit de lijst bovenaan ("Lei n.º 29/2026, de 23/06"), dus stabiel tot de
volgende wijziging.
"""
from __future__ import annotations

import html
import math
import re
import time

from . import Artikel, Geparseerd
from .http import client

URL = "https://www.pgdlisboa.pt/leis/lei_mostra_articulado.php?nid={nid}&tabela=leis&ficha={ficha}&pagina={pagina}&so_miolo="
PER_PAGINA = 100

_TOKEN = re.compile(
    r"<td class=txt_11_b_l[^>]*>(?P<kop>.*?)</td>"
    r"|Artigo\s+(?P<nr>\d+)\.?º(?:-(?P<letter>[A-Z]+))?\s*<br>\s*(?P<opschrift>[^<]*)</td>"
    r".*?class=txt_base_n_l>(?P<tekst>.*?)</td>",
    re.S | re.I,
)
_NIVEAUS = (("LIVRO", 1), ("PARTE", 1), ("TÍTULO", 2), ("CAPÍTULO", 3), ("SECÇÃO", 4), ("SUBSECÇÃO", 5), ("DIVISÃO", 6), ("SUBDIVISÃO", 7))


def _schoon(fragment: str) -> str:
    t = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    regels = [re.sub(r"[ \t\r\xa0]+", " ", r).strip() for r in t.split("\n")]
    return "\n".join(r for r in regels if r)


def _mooi(regel: str) -> str:
    """"TÍTULO II" → "Título II", "PARTE GERAL" → "Parte geral"; gemengde schrijfwijze blijft staan."""
    if not regel.isupper():
        return regel
    woorden = regel.lower().split(" ")
    return " ".join(w.upper() if re.fullmatch(r"[ivxlc]+(-[a-z])?", w) else (w.capitalize() if i == 0 else w) for i, w in enumerate(woorden))


def _niveau(regel: str) -> int | None:
    if re.fullmatch(r"PARTE (GERAL|ESPECIAL)", regel):  # "LIVRO I / PARTE GERAL": de titel van het boek
        return None
    for woord, n in _NIVEAUS:
        if re.match(rf"{woord}\b", regel):
            return n
    return None


def _koppen(blok: str) -> list[tuple[int, str]]:
    """"LIVRO I / PARTE GERAL / TÍTULO I / Das leis…" → [(1, "Livro I · Parte geral"), (2, "Título I · Das leis…")]."""
    uit: list[tuple[int, str, bool]] = []  # (niveau, kop, heeft al een titel)
    for regel in _schoon(blok).split("\n"):
        mooi = _mooi(regel)
        n = _niveau(regel)
        if n is not None:
            uit.append((n, mooi, False))
        elif uit and not uit[-1][2]:
            uit[-1] = (uit[-1][0], f"{uit[-1][1]} · {mooi}", True)
    return [(n, k) for n, k, _ in uit]


def parse_pagina(h: str, pad: list[tuple[int, str]]) -> list[Artikel]:
    """Artikelen van één pagina; `pad` (niveau, kop) loopt door over de pagina's heen."""
    artikelen: list[Artikel] = []
    for m in _TOKEN.finditer(h):
        if m.group("kop") is not None:
            for n, kop in _koppen(m.group("kop")):
                pad[:] = [p for p in pad if p[0] < n] + [(n, kop)]
            continue
        nr = m.group("nr") + (f"-{m.group('letter')}" if m.group("letter") else "")
        opschrift = re.sub(r"\s+", " ", m.group("opschrift") or "").strip().removeprefix("(").removesuffix(")") or None
        tekst = _schoon(m.group("tekst"))
        artikelen.append(Artikel(nummer=nr, tekst=tekst or "(Revogado)", opschrift=opschrift, pad=" › ".join(k for _, k in pad) or None))
    return artikelen


def _meta(h: str) -> tuple[str | None, str | None, int]:
    titel = re.search(r'color:#0554e7;font-weight:bold;font-family:tahoma">\s*(?:&nbsp;)*\s*([^<]+)<span', h)
    wijz = re.search(r"Contém as seguintes alterações:.*?-\s*<a\s+href=\s*\"lei_mostra_articulado\.php\?nid=\d+&tabela=leis[^\"]*\">([^<]+)</a>", h, re.S)
    aantal = re.search(r"Nº de artigos\s*:\s*(?:&nbsp;)*\s*<i>\s*(\d+)", h)
    return (html.unescape(titel.group(1)).strip() if titel else None, wijz.group(1).strip() if wijz else None,
            int(aantal.group(1)) if aantal else 0)


def parse(data: bytes | list[bytes], id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    """`data`: één pagina of de pagina's van een wet op volgorde (ISO-8859-1)."""
    paginas = [data] if isinstance(data, bytes) else data
    teksten = [p.decode("latin-1") for p in paginas]
    pad: list[tuple[int, str]] = []
    artikelen: list[Artikel] = []
    gezien: set[str] = set()
    for h in teksten:
        for a in parse_pagina(h, pad):
            if a.nummer not in gezien:
                gezien.add(a.nummer)
                artikelen.append(a)
    t, wijz, _ = _meta(teksten[0])
    if titel is None:
        titel = (t.capitalize() if t and t.isupper() else t) or id
    ruw = "\n".join(m.group(0) for h in teksten for m in _TOKEN.finditer(h)).encode()
    return Geparseerd(wet_id=id, titel=titel, versie=wijz or "versão original", bron_url=bron_url or URL.format(nid=id, ficha=1, pagina=1),
                      artikelen=artikelen, ruw=ruw, ruw_extensie="html")


def haal_op(id: str, titel: str | None = None) -> Geparseerd:
    """`id`: de `nid` van de PGDL, bijv. '775' (Código Civil). Eén pagina per 100 artikelen, met een pauze ertussen."""
    paginas: list[bytes] = []
    with client(timeout=120.0) as c:
        r = c.get(URL.format(nid=id, ficha=1, pagina=1))
        r.raise_for_status()
        paginas.append(r.content)
        aantal = _meta(r.content.decode("latin-1"))[2]
        for p in range(2, math.ceil(aantal / PER_PAGINA) + 1):
            time.sleep(1.5)
            r = c.get(URL.format(nid=id, ficha=(p - 1) * PER_PAGINA + 1, pagina=p))
            r.raise_for_status()
            paginas.append(r.content)
    return parse(paginas, id, URL.format(nid=id, ficha=1, pagina=1), titel)
