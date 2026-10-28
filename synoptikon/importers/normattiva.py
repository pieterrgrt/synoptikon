"""IT: Normattiva, Akoma Ntoso-export van een geconsolideerde akte.

De export (`/do/atto/caricaAKN`) vraagt de publicatiedatum in de Gazzetta
Ufficiale en de codice redazionale; die staan op de aktepagina, die we via de
URN openen (`/uri-res/N2Ls?urn:nir:…`). Normattiva zet een sessiecookie bij
die pagina; zonder cookie komt er een lege export terug.

Twee vormen. Bij de Codice civile is elk artikel een eigen <attachment><doc name="CODICE
CIVILE-art. 1337">. Er is geen boek- of titelstructuur: de plaats in de
systematiek volgt uit het nummer en de seed-boom (bereiken per titel). Het
eerste <p> begint met "Art. 1337." en, als het artikel een opschrift heeft,
"(Trattative e responsabilità precontrattuale)."; de rest zijn de leden.
Normattiva schrijft accenten als apostrof ("e'", "puo'"); dat laten we staan,
het is de officiële weergave.

Bij jongere akten (Codice del consumo) staan de artikelen gewoon in de
<body>, als <article> met <num>, <heading> en leden; het pad volgt dan uit
de omringende <chapter>/<section>-koppen.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date

from ..services.artikelen import _LAT
from . import Artikel, Geparseerd
from .http import client

BASIS = "https://www.normattiva.it"
NS = {"a": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"}

# Rangtelwoorden: "1469 bis", "135-sex-decies", "135-vicies-ter" (eerste deel desnoods met een streepje gesplitst).
_SUFFIX = rf"(?:[\s-]*(?:sex-decies|septies-decies|{_LAT})(?:-(?:{_LAT}))?)?"
_NAAM = re.compile(rf"^(?P<deel>.*?)-art\.\s*(?P<nr>\d+{_SUFFIX})\s*$", re.I)
_KOP = re.compile(rf"^\s*Art\.\s*\d+{_SUFFIX}\s*\.?\s*", re.I)
# "(Trattative e responsabilita' precontrattuale)." vooraan; binnen het opschrift kunnen haakjes voorkomen.
_OPSCHRIFT = re.compile(r"^\(((?:[^()]|\([^()]*\)){2,300}?)\)\.?(?:\s+|$)")
_KOPREGEL = re.compile(r"^(CODICE CIVILE|DISPOSIZIONI\b.*|LIBRO\b.*|TITOLO\b.*|CAPO\b.*|SEZIONE\b.*|PARAGRAFO\b.*)$")
_NOOT = re.compile(r"(?:\s*\(\d+[a-z]?\))+")
# Redactionele aantekeningen in hoofdletters tussen dubbele haken ("((IL D.LGS. … HA CONFERMATO …))").
_AANTEKENING = re.compile(r"\(\((?=[^()]*[A-Z]{4})[^a-z()]*\)\)")


def _nummer(nr: str) -> str:
    """'1469 bis' → '1469-bis', '135-sex-decies' → '135-sexdecies', '135-vicies-ter' → '135-vicies-ter'."""
    nr = re.sub(r"\s+", " ", nr.strip().lower()).replace("sex-decies", "sexdecies").replace("septies-decies", "septiesdecies")
    m = re.fullmatch(r"(\d+)[\s-]*(.*)", nr)
    if not m or not m.group(2):
        return nr
    return f"{m.group(1)}-{re.sub(r'[\s-]+', '-', m.group(2))}"


def _alineas(doc: ET.Element) -> list[str]:
    uit = []
    for p in doc.iterfind(".//a:mainBody//a:p", NS):
        tekst = "".join(p.itertext())
        for blok in re.split(r"\n\s*\n", tekst):
            blok = re.sub(r"\s+", " ", blok).strip()
            if blok:
                uit.append(blok)
    return uit


def parse(data: bytes, wet_id: str, bron_url: str | None = None, deel: str | None = "CODICE CIVILE") -> Geparseerd:
    """`deel`: alleen documenten waarvan de naam zo begint (de preleggi staan in dezelfde export)."""
    root = ET.fromstring(data)
    titel = wet_id
    versie = date.today().isoformat()
    alias = root.find(".//a:act/a:meta//a:FRBRWork/a:FRBRalias[@name='eli']", NS)
    if alias is not None:
        m = re.search(r"CONSOLIDATED/(\d{8})", alias.get("value", ""))
        if m:
            versie = f"{m.group(1)[:4]}-{m.group(1)[4:6]}-{m.group(1)[6:]}"
    artikelen: list[Artikel] = []
    for doc in root.iterfind(".//a:attachment/a:doc", NS):
        m = _NAAM.match(doc.get("name", ""))
        if not m:
            continue
        if deel and m.group("deel").strip().upper() != deel.upper():
            continue
        alineas = _alineas(doc)
        if not alineas:
            continue
        # Alles na de streep is het blok "AGGIORNAMENTO" met wijzigingsnoten.
        for i, a in enumerate(alineas):
            if re.fullmatch(r"-{5,}", a):
                alineas = alineas[:i]
                break
        alineas = [_NOOT.sub("", _AANTEKENING.sub("", a)) for a in alineas]
        # Gewijzigde tekst staat tussen (( … )); de haken zijn markering, geen inhoud.
        alineas = [re.sub(r"\s*\(\s*\)", "", re.sub(r"\(\(\s*|\s*\)\)", "", a)).strip() for a in alineas]
        alineas = [a for a in alineas if re.search(r"\w", a)]
        # Koppen vooraan: "CODICE CIVILE", "LIBRO PRIMO …", "Art. 1337.", dan het opschrift.
        while alineas and (_KOPREGEL.match(alineas[0]) or _KOP.fullmatch(alineas[0])):
            alineas.pop(0)
        if alineas and _KOP.match(alineas[0]):
            alineas[0] = _KOP.sub("", alineas[0])
        opschrift = None
        o = _OPSCHRIFT.match(alineas[0]) if alineas else None
        if o:
            opschrift = o.group(1).strip().rstrip(".")
            alineas[0] = alineas[0][o.end():].strip()
        elif len(alineas) > 1 and len(alineas[0].split()) <= 12 and alineas[0].endswith(".") and alineas[0][:1].isupper():
            # Een gewijzigd opschrift verliest zijn haakjes: "Domicilio dei coniugi …."
            opschrift = alineas.pop(0).rstrip(".")
        alineas = [a for a in alineas if a]
        tekst = "\n\n".join(alineas)
        if re.fullmatch(r"\(?\s*(abrogato|soppresso)\.?\s*\)?\.?", tekst, re.I) or not tekst:
            tekst = tekst or "(abrogato)"
        artikelen.append(Artikel(nummer=_nummer(m.group("nr")), tekst=tekst, opschrift=opschrift))
    if not artikelen:
        artikelen = _body_artikelen(root)
    if deel and deel.upper() == "CODICE CIVILE":
        titel = "Codice civile"
    return Geparseerd(wet_id=wet_id, titel=titel, versie=versie, bron_url=bron_url, artikelen=artikelen, ruw=data, ruw_extensie="xml")


_STRUCTUUR = {"book", "part", "title", "chapter", "section", "subsection"}


def _platte(el: ET.Element | None) -> str:
    """Tekst zonder de wijzigingshaken (( … )) en zonder losse streepjes ("- - Titolo I")."""
    if el is None:
        return ""
    t = re.sub(r"\(\(\s*|\s*\)\)", " ", "".join(el.itertext()))
    t = re.sub(r"(?:^|\s)-(?:\s+-)*(?=\s|$)", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _body_artikelen(root: ET.Element) -> list[Artikel]:
    uit: list[Artikel] = []
    a = "{%s}" % NS["a"]

    def loop(el: ET.Element, pad: list[str]) -> None:
        for k in el:
            naam = k.tag.removeprefix(a)
            if naam in _STRUCTUUR:
                kop = " ".join(x for x in (_platte(k.find(a + "num")), _platte(k.find(a + "heading"))) if x)
                loop(k, [*pad, kop] if kop else pad)
            elif naam == "article":
                m = re.match(rf"Art\.\s*(\d+{_SUFFIX})", _platte(k.find(a + "num")), re.I)
                if not m:
                    continue
                leden = []
                for para in k.iter(a + "paragraph"):
                    nr = _platte(para.find(a + "num"))
                    delen = [_platte(p) for p in para.iter(a + "p")]
                    tekst = " ".join(d for d in delen if d)
                    tekst = re.sub(r"\s*\(\s*\)", "", re.sub(r"\(\(\s*|\s*\)\)", "", tekst)).strip()
                    if tekst:
                        leden.append(f"{nr} {tekst}".strip())
                kop = _platte(k.find(a + "heading")).strip(" ().") or None
                uit.append(Artikel(nummer=_nummer(m.group(1)), tekst="\n\n".join(leden) or "(abrogato)", opschrift=kop, pad=" › ".join(pad) or None))
            elif naam in ("body", "mainBody"):
                loop(k, pad)

    body = root.find(f".//{a}body")
    if body is not None:
        loop(body, [])
    return uit


def haal_op(urn: str, titel: str | None = None, deel: str | None = None) -> Geparseerd:
    """`urn`: bijv. 'urn:nir:stato:regio.decreto:1942-03-16;262' (Codice civile)."""
    pagina_url = f"{BASIS}/uri-res/N2Ls?{urn}"
    with client(timeout=300.0) as c:
        pagina = c.get(pagina_url)
        pagina.raise_for_status()
        m = re.search(r"caricaAKN\?dataGU=(\d{8})&(?:amp;)?codiceRedaz=([0-9A-Z]+)", pagina.text)
        if not m:
            raise ValueError(f"Geen Akoma Ntoso-export gevonden op {pagina_url}")
        vandaag = date.today().strftime("%Y%m%d")
        r = c.get(f"{BASIS}/do/atto/caricaAKN", params={"dataGU": m.group(1), "codiceRedaz": m.group(2), "dataVigenza": vandaag})
        r.raise_for_status()
    g = parse(r.content, urn, pagina_url, deel=deel)
    if titel:
        g.titel = titel
    return g
