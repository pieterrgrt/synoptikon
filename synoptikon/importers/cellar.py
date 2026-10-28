"""EU: catalogus van het geldende afgeleide recht, uit de Cellar (SPARQL) van het Publicatiebureau.

Drie lagen, elk met één soort query:

1. **Handelingen.** Alle werken met `resource_legal_in-force` waar, sector 3
   (wetgeving), van de typen verordening, richtlijn en kaderbesluit,
   inclusief gedelegeerde en uitvoeringshandelingen (REG_DEL, REG_IMPL,
   DIR_DEL, DIR_IMPL). Titel in het Nederlands, datum, inwerkingtreding
   (Cellar geeft er soms twee: inwerkingtreding en toepassing), einde
   geldigheid, omzettingstermijn (`directive_date_transposition`), EER en ELI.
2. **Repertorium.** De rubrieken van het "Repertorium van de geldende
   wetgeving van de Unie" (concept scheme `dir-eu-legal-act`, notatie in
   paren: 13301420 → 13.30.14.20) en per handeling de rubrieken.
3. **Nationale uitvoeringsmaatregelen.** Werken van het type
   `measure_national_implementing` (CELEX-sector 7) die een geldende
   handeling uitvoeren, voor de lidstaten die Synoptikon als stelsel kent
   (en het VK van vóór de Brexit). Titel en soort akte zoals de lidstaat ze
   gemeld heeft.

Besluiten (DEC, ~27.000 geldende) laten we bewust weg: ze zijn grotendeels
individueel (adressaten) en voor rechtsvergelijking zelden van belang.
Ophalen gebeurt in pagina's; de endpoint geeft hooguit 10.000 rijen per
antwoord.
"""
from __future__ import annotations

import csv
import io
import re
import time
from dataclasses import dataclass
from datetime import date

from .http import client

SPARQL = "https://publications.europa.eu/webapi/rdf/sparql"
_PREFIX = """PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
"""
RT = "http://publications.europa.eu/resource/authority/resource-type/"
LAND = "http://publications.europa.eu/resource/authority/country/"
TAAL_NL = "<http://publications.europa.eu/resource/authority/language/NLD>"

# resource-type → (soort, variant)
TYPEN: dict[str, tuple[str, str]] = {
    "REG": ("verordening", "basis"),
    "REG_IMPL": ("verordening", "uitvoering"),
    "REG_DEL": ("verordening", "gedelegeerd"),
    "REG_FINANC": ("verordening", "basis"),
    "DIR": ("richtlijn", "basis"),
    "DIR_IMPL": ("richtlijn", "uitvoering"),
    "DIR_DEL": ("richtlijn", "gedelegeerd"),
    "DEC_FRAMW": ("kaderbesluit", "basis"),
}

# Cellar-landcode → stelsel in Synoptikon. GBR: omzetting van vóór 1-1-2021.
LANDEN: dict[str, str] = {"NLD": "NL", "BEL": "BE", "FRA": "FR", "ITA": "IT", "ESP": "ES", "DEU": "DE", "GBR": "EN"}

PAGINA = 5000


@dataclass
class Handeling:
    celex: str
    soort: str
    variant: str
    nummer: str | None
    titel: str
    datum: date | None
    in_werking: date | None
    toepassing: date | None
    geldig_tot: date | None
    omzettingstermijn: date | None
    eer: bool
    eli: str | None


@dataclass
class Nim:
    celex: str
    land: str
    nim_id: str
    titel: str
    soort_akte: str | None
    datum: date | None
    vindplaats: str | None


def _query(c, q: str, pogingen: int = 4) -> list[dict[str, str]]:
    """De endpoint geeft af en toe een 500 bij drukte; dan na een korte pauze opnieuw."""
    for i in range(pogingen):
        r = c.post(SPARQL, data={"query": _PREFIX + q}, headers={"Accept": "text/csv"})
        if r.status_code < 500 or i == pogingen - 1:
            r.raise_for_status()
            return list(csv.DictReader(io.StringIO(r.text)))
        time.sleep(5 * (i + 1))
    return []


def _pagina_s(c, q: str) -> list[dict[str, str]]:
    """Voert `q` (met ORDER BY) uit in pagina's van PAGINA rijen."""
    uit: list[dict[str, str]] = []
    offset = 0
    while True:
        rijen = _query(c, f"{q}\nLIMIT {PAGINA} OFFSET {offset}")
        uit.extend(rijen)
        if len(rijen) < PAGINA:
            return uit
        offset += PAGINA


def _datum(s: str | None) -> date | None:
    if not s:
        return None
    try:
        d = date.fromisoformat(s[:10])
    except ValueError:
        return None
    return None if d.year >= 9999 else d


def _nummer(celex: str, titel: str) -> str | None:
    """Het eigen nummer uit de titel, in de citeervorm van die tijd: '2016/679', '593/2008', '93/13'.

    Een titel noemt vaak ook andere handelingen ("tot wijziging van Verordening (EG) nr. 300/2008");
    het eigen nummer is het eerste dat jaar én volgnummer uit het CELEX-nummer bevat.
    """
    m = re.fullmatch(r"3(\d{4})[A-Z](\d{4})(?:\(\d+\))?", celex)
    if not m:
        return None
    jaar, volg = m.group(1), int(m.group(2))
    for a, b in re.findall(r"\b(\d{1,4})/(\d{1,4})\b", titel):
        delen = {a, b}
        if (jaar in delen or jaar[2:] in delen) and str(volg) in delen:
            return f"{a}/{b}"
    return f"{jaar}/{volg}"


# Per eigenschap een aparte, lichte query: alles in één query met zeven OPTIONALs
# laat de endpoint vastlopen (500). (eigenschap, aggregaat)
_EIGENSCHAPPEN = {
    "datum": ("cdm:work_date_document", "MIN"),
    "in": ("cdm:resource_legal_date_entry-into-force", "MIN"),
    "tot": ("cdm:resource_legal_date_end-of-validity", "MIN"),
    "omz": ("cdm:directive_date_transposition", "MIN"),
    "eer": ("cdm:resource_legal_eea", "MAX"),
    "eli": ("cdm:resource_legal_eli", "SAMPLE"),
}


def _basis(rt: str) -> str:
    return (f'?w cdm:resource_legal_in-force "true"^^xsd:boolean ; cdm:work_has_resource-type <{RT}{rt}> ; '
            f'cdm:resource_legal_id_celex ?c . FILTER(STRSTARTS(STR(?c), "3"))')


def handelingen(c) -> list[Handeling]:
    uit: dict[str, Handeling] = {}
    for rt, (soort, variant) in TYPEN.items():
        titels = _pagina_s(c, f"""
SELECT ?c (SAMPLE(?t) AS ?titel) WHERE {{
  {_basis(rt)}
  OPTIONAL {{ ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language {TAAL_NL} ; cdm:expression_title ?t }}
}} GROUP BY ?c ORDER BY ?c""")
        waarden: dict[str, dict[str, str]] = {}
        for naam, (eig, agg) in _EIGENSCHAPPEN.items():
            if naam == "omz" and soort == "verordening":
                continue
            for r in _pagina_s(c, f"SELECT ?c ({agg}(?v) AS ?x) WHERE {{ {_basis(rt)} ?w {eig} ?v }} GROUP BY ?c ORDER BY ?c"):
                waarden.setdefault(r["c"], {})[naam] = r["x"]
        for r in titels:
            celex = r["c"]
            if celex in uit and uit[celex].variant != "basis":
                continue  # één werk kan twee typen dragen (REG en REG_IMPL): het specifieke wint
            w = waarden.get(celex, {})
            titel = re.sub(r"\s+", " ", r.get("titel") or "").strip() or celex
            # Cellar kent meer data van inwerkingtreding (ook van latere wijzigingen); alleen de eerste is betrouwbaar.
            in_werking, toepassing = _datum(w.get("in")), None
            uit[celex] = Handeling(
                celex=celex, soort=soort, variant=variant, nummer=_nummer(celex, titel), titel=titel,
                datum=_datum(w.get("datum")), in_werking=in_werking, toepassing=toepassing,
                geldig_tot=_datum(w.get("tot")), omzettingstermijn=_datum(w.get("omz")),
                eer=(w.get("eer") or "").lower() in ("1", "true"), eli=w.get("eli") or None,
            )
    return list(uit.values())


# Taalcodes van de interface → Publications Office-taal (ISO 639-2/B in de authority-tabel).
TALEN_CELLAR = {"fr": "FRA", "de": "DEU", "it": "ITA", "en": "ENG", "es": "SPA"}


def titels(c, taal: str) -> dict[str, str]:
    """celex → officiële titel in één taal (fr, de, it, en, es) voor alle geldende handelingen van de gekozen typen."""
    lang = f"<http://publications.europa.eu/resource/authority/language/{TALEN_CELLAR[taal]}>"
    uit: dict[str, str] = {}
    for rt in TYPEN:
        for r in _pagina_s(c, f"""
SELECT ?c (SAMPLE(?t) AS ?titel) WHERE {{
  {_basis(rt)}
  ?e cdm:expression_belongs_to_work ?w ; cdm:expression_uses_language {lang} ; cdm:expression_title ?t
}} GROUP BY ?c ORDER BY ?c"""):
            titel = re.sub(r"\s+", " ", r.get("titel") or "").strip()
            if titel:
                uit[r["c"]] = titel
    return uit


def repertorium_labels(c) -> list[tuple[str, str, str]]:
    """(code, taal, label) van alle rubrieken in fr, de, it, en en es."""
    rijen = _query(c, """
SELECT ?d ?l (LANG(?l) AS ?t) WHERE {
  ?d skos:inScheme <http://publications.europa.eu/resource/authority/dir-eu-legal-act> ; skos:prefLabel ?l .
  FILTER(LANG(?l) IN ("fr", "de", "it", "en", "es"))
} LIMIT 20000""")
    uit: dict[tuple[str, str], str] = {}
    for r in rijen:
        if not re.search(r"/\d+$", r["d"]):
            continue
        # CSV verliest de taaltag van de literal; daarom staat de taal in een eigen kolom.
        uit.setdefault((_rep_code(r["d"]), (r.get("t") or "").lower()), (r.get("l") or "").strip())
    return [(code, taal, label) for (code, taal), label in uit.items() if label and taal]


def _rep_code(uri: str) -> str:
    cijfers = uri.rsplit("/", 1)[-1]
    return ".".join(cijfers[i:i + 2] for i in range(0, len(cijfers), 2))


def repertorium(c) -> list[tuple[str, str, str | None]]:
    """(code, label, oudercode) van alle rubrieken, in het Nederlands."""
    rijen = _query(c, """
SELECT ?d ?l ?b WHERE {
  ?d skos:inScheme <http://publications.europa.eu/resource/authority/dir-eu-legal-act> .
  OPTIONAL { ?d skos:prefLabel ?l FILTER(lang(?l) = "nl") }
  OPTIONAL { ?d skos:broader ?b }
} LIMIT 10000""")
    uit: dict[str, tuple[str, str, str | None]] = {}
    for r in rijen:
        if not re.search(r"/\d+$", r["d"]):
            continue
        code = _rep_code(r["d"])
        ouder = _rep_code(r["b"]) if r.get("b") and re.search(r"/\d+$", r["b"]) else None
        label = (r.get("l") or "").strip()
        if code not in uit or (label and uit[code][1] == code):  # één rij per rubriek; een rij met label wint
            uit[code] = (code, label or code, ouder)
    return list(uit.values())


def rubrieken(c) -> dict[str, list[str]]:
    """celex → repertoriumcodes, voor alle geldende handelingen van de gekozen typen (per type, anders 500)."""
    uit: dict[str, list[str]] = {}
    for rt in TYPEN:
        for r in _pagina_s(c, f"SELECT ?c ?d WHERE {{ {_basis(rt)} ?w cdm:resource_legal_is_about_concept_directory-code ?d }} ORDER BY ?c ?d"):
            code = _rep_code(r["d"])
            lijst = uit.setdefault(r["c"], [])
            if code not in lijst:
                lijst.append(code)
    return uit


_NIM_EIGENSCHAPPEN = {
    "titel": "cdm:work_title",
    "soort": "cdm:measure_national_implementing_type_act",
    "datum": "cdm:measure_national_implementing_date_official_journal",
    "nummer": "cdm:measure_national_implementing_number_official_journal",
    "pagina": "cdm:measure_national_implementing_page_official_journal",
}


def nims(c, landen: list[str] | None = None) -> list[Nim]:
    """Per land en per eigenschap een aparte query (één grote query geeft een 500)."""
    uit = []
    for land in landen or list(LANDEN):
        basis = (f'?m cdm:measure_national_implementing_implements_resource_legal ?w ; '
                 f'cdm:measure_national_implementing_implemented_by_country <{LAND}{land}> ; cdm:resource_legal_id_celex ?n . '
                 f'?w cdm:resource_legal_in-force "true"^^xsd:boolean ; cdm:resource_legal_id_celex ?c . FILTER(STRSTARTS(STR(?c), "3"))')
        paren = _pagina_s(c, f"SELECT DISTINCT ?c ?n WHERE {{ {basis} }} ORDER BY ?c ?n")
        waarden: dict[str, dict[str, str]] = {}
        for naam, eig in _NIM_EIGENSCHAPPEN.items():
            for r in _pagina_s(c, f"SELECT ?n (SAMPLE(?v) AS ?x) WHERE {{ {basis} ?m {eig} ?v }} GROUP BY ?n ORDER BY ?n"):
                waarden.setdefault(r["n"], {})[naam] = r["x"]
        for r in paren:
            w = waarden.get(r["n"], {})
            vindplaats = ", ".join(x for x in (f"nr. {w['nummer']}" if w.get("nummer") else "", f"p. {w['pagina']}" if w.get("pagina") else "") if x) or None
            uit.append(Nim(celex=r["c"], land=land, nim_id=r["n"], titel=re.sub(r"\s+", " ", w.get("titel") or "").strip() or r["n"],
                           soort_akte=w.get("soort") or None, datum=_datum(w.get("datum")), vindplaats=vindplaats))
    return uit


def verbinding():
    return client(timeout=600.0, headers={"User-Agent": "Synoptikon/0.1 (persoonlijke rechtsvergelijkingsapp)"})
