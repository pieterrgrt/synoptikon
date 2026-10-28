"""ES: Agencia Estatal BOE, open-data-API voor geconsolideerde wetgeving.

https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/{id}/texto
geeft de hele tekst als XML: een reeks <bloque>-elementen, elk met één of
meer <version>s (de laatste is de geldende). Een blok van het type
`encabezado` is een kop (Libro, Título, Capítulo, Sección); een blok van het
type `precepto` is een artikel. Het pad van een artikel is de stapel koppen
erboven. Noten (`nota_pie`) en wijzigingsverwijzingen (`refPost`) horen niet
bij de tekst.

Bekende id's: BOE-A-1889-4763 (Código Civil), BOE-A-1885-6627 (Código de
Comercio), BOE-A-2007-20555 (TRLGDCU), BOE-A-2000-323 (LEC).
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date

from . import Artikel, Geparseerd
from .http import client

URL = "https://www.boe.es/datosabiertos/api/legislacion-consolidada/id/{id}/texto"
WEB = "https://www.boe.es/buscar/act.php?id={id}"

# Kopniveaus naar klasse van de eerste <p>; lager getal = hoger niveau.
_NIVEAU = {"libro": 1, "titulo": 2, "capitulo": 3, "seccion": 4, "subseccion": 5}
# "Artículo 1902.", "Artículo 94 bis.", in oudere teksten "Artículo 1º." of "Art. 50."
_ART = re.compile(r"^Art(?:[íi]culo|\.)\s*(\d+)(?:º|°|o(?=\.))?(?:\s+(bis|ter|quater|quinquies|sexies|septies|octies|nonies|novies|decies)\b)?\.?\s*(.*)$", re.I)
_OVERSLAAN = {"nota_pie", "nota_pie_2", "refPost", "firma_rey", "firma_ministro"}


def _tekst(el: ET.Element) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def _kop(versie: ET.Element) -> tuple[int, str] | None:
    ps = list(versie.iter("p"))
    if not ps:
        return None
    klasse = (ps[0].get("class") or "").split("_")[0]
    niveau = _NIVEAU.get(klasse)
    if niveau is None:
        return None
    delen = [_tekst(p) for p in ps if (p.get("class") or "").split("_")[0] == klasse]
    return niveau, " ".join(d for d in delen if d)


def parse(data: bytes, wet_id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    stapel: list[tuple[int, str]] = []
    artikelen: list[Artikel] = []
    laatste = ""
    for blok in root.iter("bloque"):
        versies = blok.findall("version")
        if not versies:
            continue
        v = versies[-1]
        laatste = max(laatste, v.get("fecha_vigencia") or "")
        soort = blok.get("tipo")
        if soort == "encabezado":
            kop = _kop(v)
            if kop:
                stapel = [k for k in stapel if k[0] < kop[0]] + [kop]
            continue
        if soort != "precepto":
            continue
        kop_p = next((p for p in v.iter("p") if p.get("class") == "articulo"), None)
        m = _ART.match(_tekst(kop_p)) if kop_p is not None else None
        if not m:
            continue
        nummer = m.group(1) + (f" {m.group(2).lower()}" if m.group(2) else "")
        opschrift = m.group(3).strip(" .") or None
        alineas = [_tekst(p) for p in v.iter("p") if p is not kop_p and p.get("class") not in _OVERSLAAN]
        alineas = [a for a in alineas if a]
        if not alineas and not opschrift:
            continue
        artikelen.append(Artikel(nummer=nummer, tekst="\n\n".join(alineas) or "(sin contenido)", opschrift=opschrift,
                                 pad=" › ".join(k[1] for k in stapel) or None))
    # Het afkondigingsbesluit gaat soms vooraf met eigen artikelen 1º–4º; het wetboek zelf (later) wint.
    per_nummer = {a.nummer: a for a in artikelen}
    artikelen = [a for a in artikelen if per_nummer[a.nummer] is a]
    versie = f"{laatste[:4]}-{laatste[4:6]}-{laatste[6:8]}" if len(laatste) == 8 else date.today().isoformat()
    return Geparseerd(wet_id=wet_id, titel=titel or wet_id, versie=versie, bron_url=bron_url or WEB.format(id=wet_id),
                      artikelen=artikelen, ruw=data, ruw_extensie="xml")


def haal_op(wet_id: str, titel: str | None = None) -> Geparseerd:
    with client(timeout=300.0, headers={"Accept": "application/xml", "User-Agent": "Synoptikon/0.1"}) as c:
        r = c.get(URL.format(id=wet_id))
        r.raise_for_status()
    return parse(r.content, wet_id, WEB.format(id=wet_id), titel)
