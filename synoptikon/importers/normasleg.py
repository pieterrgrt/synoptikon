"""BR: Normas.leg.br van het Congresso Nacional, de bijgewerkte federale wetten (licentie CC BY 4.0).

Planalto (planalto.gov.br/ccivil_03) verbreekt de verbinding van buiten Brazilië; Normas.leg.br heeft een open API
(`/v3/api-docs`, robots.txt staat alles toe). `GET /api/public/normas?urn={urn}&tipo_documento=maior-detalhe` geeft de
metadata als schema.org-JSON; daarin wijst `encoding[]` met `version: "Current"` (de "Compilação Monovigente" van de
Câmara dos Deputados) naar `/api/public/binario/{id}/texto`, een HTML-export uit Word. id = de LexML-URN:
urn:lex:br:federal:lei:2002-01-10;10406 (Código Civil), …:lei:1990-09-11;8078 (CDC), …:lei:2015-03-16;13105 (CPC),
…:constituicao:1988-10-05;1988, …:decreto.lei:1940-12-07;2848 (Código Penal), …:decreto.lei:1942-09-04;4657 (LINDB).

De HTML is een reeks <p>: koppen ("TÍTULO I" met de titel op de volgende regel), artikelen ("Art. 1.022. …",
"Art. 4º-A …") en daarna de leden (§, incisos, alíneas). Wijzigingsnoten tussen haakjes aan het eind ("(Inciso
acrescido pela Lei nº 14.181, de 2021)") vallen weg; ingesloten afbeeldingen ook. `versie` is de opslagdatum van het
Word-document (`o:LastSaved`), de stand van de compilatie.
"""
from __future__ import annotations

import html as htmllib
import re
from datetime import date

from . import Artikel, Geparseerd
from .http import client

API = "https://normas.leg.br/api/public/normas?urn={urn}&tipo_documento=maior-detalhe"
WEB = "https://normas.leg.br/?urn={urn}"
_NIVEAUS = {"PARTE": 0, "LIVRO": 1, "TÍTULO": 2, "CAPÍTULO": 3, "SEÇÃO": 4, "SUBSEÇÃO": 5}
_KOP = re.compile(r"^(PARTE|LIVRO|T[ÍI]TULO|CAP[ÍI]TULO|SE[ÇC][ÃA]O|SUBSE[ÇC][ÃA]O)\b\s*(.*)$", re.I)
_ART = re.compile(r"^Art\.\s*(\d+(?:\.\d{3})*)\s*[º°o]?\s*(?:-\s*([A-Z]{1,2}))?\s*[.\-–]?\s*(.*)$", re.S)
_NOOT = re.compile(r"\s*\((?:[^()]|\([^()]*\))*?\b(?:acrescid|alterad|revogad|inclu[íi]d|renumerad|vide|vig[êe]ncia|reda[çc][ãa]o|"
                   r"vetad|suprimid|declarad|transformad|convers[ãa]o|regulament)(?:[^()]|\([^()]*\))*\)\s*$", re.I)
_P = re.compile(r"<(p|h\d)\b[^>]*>(.*?)</\1>", re.S | re.I)


def _schoon(fragment: str) -> str:
    t = re.sub(r"<br\s*/?>", " ", fragment, flags=re.I)
    t = htmllib.unescape(re.sub(r"<[^>]+>", "", t)).replace("\xa0", " ")
    return re.sub(r"\s+", " ", t).strip()


def _zonder_noten(t: str) -> str:
    while True:
        m = _NOOT.search(t)
        if not m:
            return t
        t = t[: m.start()].rstrip()


def parse(data: bytes | str, wet_id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    h = data.decode("utf-8", "replace") if isinstance(data, bytes) else data
    h = re.sub(r"<img\b[^>]*>", "", h)
    artikelen: list[Artikel] = []
    koppen: dict[int, str] = {}
    open_kop: int | None = None  # niveau van een kop waarvan de titel nog op de volgende regel komt
    art: Artikel | None = None
    regels: list[str] = []
    begonnen = False

    def sluit() -> None:
        nonlocal art, regels
        if art is not None:
            art.tekst = "\n\n".join(r for r in regels if r) or "(revogado)"
            artikelen.append(art)
        art, regels = None, []

    for _, inner in _P.findall(h):
        t = _schoon(inner)
        if not t:
            continue
        if begonnen and re.match(r"^Bras[íi]lia\s*,", t):  # ondertekening: einde van de wet
            break
        m = _KOP.match(t)
        if m and (not m.group(2) or not re.match(r"^[a-zà-ú]", m.group(2))):
            sluit()
            begonnen = True
            soort = m.group(1).upper().replace("TITULO", "TÍTULO").replace("CAPITULO", "CAPÍTULO").replace("SECAO", "SEÇÃO")
            niveau = _NIVEAUS.get(soort, 5)
            koppen = {n: k for n, k in koppen.items() if n < niveau}
            koppen[niveau] = _zonder_noten(t)
            open_kop = niveau
            continue
        m = _ART.match(t)
        if m:
            sluit()
            begonnen, open_kop = True, None
            nummer = m.group(1).replace(".", "") + (f"-{m.group(2)}" if m.group(2) else "")
            art = Artikel(nummer=nummer, tekst="", pad=" › ".join(koppen[n] for n in sorted(koppen)) or None)
            rest = _zonder_noten(m.group(3))
            regels = [rest] if rest and not re.fullmatch(r"\(?revogad[oa]\)?\.?", rest, re.I) else []
            continue
        if open_kop is not None and art is None:  # de titel van de kop
            koppen[open_kop] += " · " + _zonder_noten(t)
            open_kop = None
            continue
        if art is not None:
            regels.append(_zonder_noten(t))
    sluit()
    if titel is None:
        titel = next((t for _, x in _P.findall(h[:20000]) if re.match(r"(LEI|DECRETO|CONSTITUI|EMENDA)", t := _schoon(x))), wet_id)
    m = re.search(r"<o:LastSaved>(\d{4}-\d\d-\d\d)", h)
    versie = m.group(1) if m else date.today().isoformat()
    ruw = re.sub(r'src="data:[^"]*"', 'src=""', h).encode("utf-8")
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie, bron_url=bron_url or WEB.format(urn=wet_id), artikelen=artikelen,
                      ruw=ruw, ruw_extensie="html")


def tekst_url(meta: dict) -> str:
    """De bijgewerkte tekst uit de metadata; de API geeft het pad zonder /public."""
    enc = next(e for e in meta.get("encoding", []) if e.get("version") == "Current" and e.get("contentUrl"))
    return enc["contentUrl"].replace("/api/binario/", "/api/public/binario/")


def haal_op(wet_id: str, titel: str | None = None) -> Geparseerd:
    with client(timeout=180.0) as c:
        r = c.get(API.format(urn=wet_id))
        r.raise_for_status()
        r = c.get(tekst_url(r.json()))
        r.raise_for_status()
    return parse(r.content, wet_id, WEB.format(urn=wet_id), titel)
