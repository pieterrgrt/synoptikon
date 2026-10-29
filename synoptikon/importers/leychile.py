"""CL: Ley Chile van de Biblioteca del Congreso Nacional (BCN), geconsolideerde wetten als XML.

`https://www.leychile.cl/Consulta/obtxml?opt=7&idNorma={id}` geeft de geldende tekst van één norm in het
uitwisselingsschema van de BCN (EsquemaIntercambioNorma-v1-0, open data; geen robots.txt). id = het idNorma:
1974 Código de Comercio, 1984 Código Penal, 22740 Código de Procedimiento Civil, 61438 Ley 19.496 (consument),
242302 Constitución. Het Código Civil is artikel 2 van DFL 1 (2000), idNorma 172986: `haal_op("172986/2")` houdt
alleen de deelboom onder dat artikel.

Opbouw: geneste <EstructuraFuncional tipoParte="Libro|Título|Párrafo|Enumeración|Capítulo|Artículo|…">, elk met
<Texto> en <Metadatos> (<NombreParte>: het artikelnummer, "1184 (DEL ART. 2)" of "58 BIS"; <TituloParte>: de kop
als die er is). De tekst is in vaste regelbreedte gezet: een alinea begint met vijf spaties, andere regels lopen
door; wijzigingsnoten staan in een rechterkolom ("L. 19.585", "Art. 1º, Nº 91") en vallen weg. De norm zelf
draagt fechaVersion "2222-02-02" (geldend); `versie` is daarom de jongste fechaVersion van de onderdelen.

Bijlagen (tabellen, formulieren) zitten er als base64-pdf in (<DataCodificada>, bij het Código de Procedimiento
Civil 55 MB); die laten we uit het bewaarde ruwe bestand weg.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date

from . import Artikel, Geparseerd
from .http import client

URL = "https://www.leychile.cl/Consulta/obtxml?opt=7&idNorma={id}"
WEB = "https://www.bcn.cl/leychile/navegar?idNorma={id}"
NS = "{http://www.leychile.cl/esquemas}"
_KOPPEN = {"Libro", "Título", "Párrafo", "Enumeración", "Capítulo", "Otros"}
_BIJLAGE = re.compile(rb"(<(?:\w+:)?DataCodificada\b[^>]*>)[^<]*")
_NOOT = re.compile(r"\S\s{4,}\S.*$")  # tekst, dan een gat van vier of meer spaties, dan een randnoot


def _regels(tekst: str) -> list[str]:
    """Vaste regelbreedte → alinea's: randnoten weg, doorlopende regels aan elkaar."""
    alineas: list[str] = []
    for regel in tekst.replace("\xa0", " ").split("\n"):
        if not regel.strip():
            continue
        if len(regel) - len(regel.lstrip()) >= 20:  # alleen een randnoot op deze regel
            continue
        m = _NOOT.search(regel)
        if m:
            regel = regel[: m.start() + 1]
        if regel.startswith("   ") or not alineas:
            alineas.append(regel.strip())
        else:
            alineas[-1] += " " + regel.strip()
    return [re.sub(r"\s+", " ", a) for a in alineas]


def _nummer(naam: str) -> str:
    """ "1184 (DEL ART. 2)" → "1184"; "58 BIS" → "58 bis"."""
    return re.sub(r"\s*-\s*", "-", re.sub(r"\s*\(DEL ART\.?.*\)$", "", naam.strip())).lower()


def _kop(e: ET.Element) -> str:
    t = e.find(f"{NS}Metadatos/{NS}TituloParte")
    if t is not None and t.get("presente") == "si" and (t.text or "").strip():
        kop = re.sub(r"\s+", " ", t.text).strip()
    else:
        kop = " ".join(_regels(e.findtext(f"{NS}Texto") or ""))
    for w in ("TITULO", "TÍTULO", "LIBRO", "CAPITULO", "CAPÍTULO", "PARRAFO", "PÁRRAFO"):  # "T I T U L O I"
        kop = re.sub(r"\b" + " ".join(w) + r"\b", w, kop)
    # "LIBRO PRIMERO DE LAS PERSONAS" → "LIBRO PRIMERO · DE LAS PERSONAS", zoals de andere importers
    return re.sub(r"^((?:LIBRO|T[IÍ]TULO|CAP[IÍ]TULO|P[AÁ]RRAFO)\s+\S+)\s+", r"\1 · ", kop, flags=re.I)


def parse(data: bytes, wet_id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    norma, _, deel = wet_id.partition("/")
    artikelen: list[Artikel] = []
    datums: list[str] = []

    def kinderen(e: ET.Element) -> list[ET.Element]:
        return e.findall(f"{NS}EstructurasFuncionales/{NS}EstructuraFuncional")

    def loop(e: ET.Element, pad: list[str]) -> None:
        for k in kinderen(e):
            soort = k.get("tipoParte")
            if (k.get("fechaVersion") or "") < "2222":
                datums.append(k.get("fechaVersion") or "")
            if soort == "Artículo":
                nummer = _nummer(k.findtext(f"{NS}Metadatos/{NS}NombreParte") or "")
                if nummer:
                    if k.get("transitorio") == "transitorio" and "transitorio" not in nummer:
                        nummer += " transitorio"
                    alineas = _regels(k.findtext(f"{NS}Texto") or "")
                    if alineas:  # "Art. 1184. La mitad …": het nummer staat al apart
                        alineas[0] = re.sub(r"^(?:Artículo|Art\.)\s*[\dº°]+\s*(?:bis|ter|quáter)?[º°]?\s*[.\-–]*\s*", "", alineas[0], flags=re.I)
                    tekst = "\n\n".join(a for a in alineas if a) or ("(derogado)" if k.get("derogado") == "derogado" else "")
                    artikelen.append(Artikel(nummer=nummer, tekst=tekst, pad=" › ".join(p for p in pad if p) or None))
                loop(k, pad)  # het Código Civil hangt onder artikel 2 van DFL 1
            elif soort in _KOPPEN:
                loop(k, [*pad, _kop(k)])
            else:  # "Doble Articulado": een wet in een artikel
                loop(k, pad)

    start: ET.Element | None = root
    if deel:  # alleen de deelboom onder dat artikel, zonder het artikel zelf
        start = next((k for k in kinderen(root) if k.get("tipoParte") == "Artículo"
                      and _nummer(k.findtext(f"{NS}Metadatos/{NS}NombreParte") or "") == deel), None)
    if start is not None:
        loop(start, [])
    if titel is None:
        titel = (root.findtext(f"{NS}Metadatos/{NS}NombresUsoComun/{NS}NombreUsoComun")
                 or root.findtext(f"{NS}Metadatos/{NS}TituloNorma") or wet_id).strip()
    versie = max(datums) if datums else date.today().isoformat()
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie, bron_url=bron_url or WEB.format(id=norma), artikelen=artikelen,
                      ruw=_BIJLAGE.sub(rb"\1", data), ruw_extensie="xml")


def haal_op(wet_id: str, titel: str | None = None) -> Geparseerd:
    norma = wet_id.partition("/")[0]
    with client(timeout=180.0) as c:
        r = c.get(URL.format(id=norma))
        r.raise_for_status()
    return parse(r.content, wet_id, WEB.format(id=norma), titel)
