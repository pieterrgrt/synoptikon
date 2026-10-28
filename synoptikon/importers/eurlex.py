"""EU: teksten uit de Cellar van het Publicatiebureau (dezelfde documenten als EUR-Lex).

EUR-Lex zelf weigert geautomatiseerde toegang; de Cellar geeft per CELEX-nummer en taal het document via content
negotiation: `http://publications.europa.eu/resource/celex/{celex}` met `Accept: application/xhtml+xml` (of
`text/html` voor oudere handelingen) en `Accept-Language: deu`. Voor een geldende handeling nemen we de nieuwste
geconsolideerde versie (CELEX `0…-JJJJMMDD`) als die er is, anders de oorspronkelijke tekst. De verdragen staan in het
Publicatieblad in delen; het volledige document heeft het CELEX-nummer met `/TXT` (12016E/TXT = VWEU met protocollen,
bijlagen en verklaringen).

Drie opmaakvormen, alle drie herkend:
- geconsolideerd: `title-article-norm`, `stitle-article-norm`, `norm`, `title-division-1/2`;
- Publicatieblad (sinds ca. 2014): `oj-ti-art`, `oj-sti-art`, `oj-normal`, `oj-ti-section-1/2`;
- ouder: `ti-art`, `sti-art`, `normal`, `ti-section-1/2`, of helemaal geen klassen (alleen alinea's, "Artikel 1").

Alles wordt eerst een platte lijst blokken (titel, afdeling, artikel, opschrift, tekst); daaruit volgen de artikelen.
De preambule (overwegingen) wordt een eigen blok, net als bijlagen, protocollen en verklaringen, zodat de hele tekst
leesbaar is. Artikelen in een protocol krijgen het protocol in hun nummer ("Protokoll 3 Art. 12").
"""
from __future__ import annotations

import html as htmllib
import re
import xml.etree.ElementTree as ET
from datetime import date
from html.parser import HTMLParser

from . import Artikel, Geparseerd
from .http import client

CELLAR = "http://publications.europa.eu/resource/celex/{celex}"
EURLEX = "https://eur-lex.europa.eu/legal-content/{taal}/TXT/?uri=CELEX:{celex}"
TAAL3 = dict(nl="nld", de="deu", fr="fra", it="ita", en="eng", es="spa")

_ART_RE = re.compile(r"^(?:Artikel|Article|Artículo|Articolo|Artigo|Art\.)\s+(\d+\s?(?:[a-z]{0,3}|bis|ter|quater)|[IVXL]+(?:\.-\d+)?|premier|1er|primo|unique|único|unico)"
                     r"\s*(?:[.:–—-]\s*(.*))?$", re.I)
_EERSTE = {"premier": "1", "1er": "1", "primo": "1", "unique": "1", "único": "1", "unico": "1"}
_PROTOCOL = re.compile(r"^(PROTOKOLL|PROTOCOL|PROTOCOLE|PROTOCOLLO|PROTOCOLO)\s*\(?\s*(?:Nr\.|No|N[°o]\.?|n[°o.]|n\.)\s*(\d+)\s*\)?", re.I)
_BIJLAGE = re.compile(r"^(ANHANG|ANHÄNGE|ANNEX|ANNEXES|ANNEXE|BIJLAGE|BIJLAGEN|ALLEGATO|ALLEGATI|ANEXO|ANEXOS|ERKLÄRUNGEN|DECLARATIONS|"
                      r"VERKLARINGEN|DICHIARAZIONI|DECLARACIONES|ÜBEREINSTIMMUNGSTABELLEN|TABLES OF EQUIVALENCES|CONCORDANTIETABELLEN|"
                      r"TABLEAUX DE CORRESPONDANCE|TAVOLE DI CONCORDANZA|TABLAS DE CORRESPONDENCIAS|ENTSPRECHUNGSTABELLE|CORRELATION TABLE|"
                      r"CONCORDANTIETABEL|TABLEAU DE CORRESPONDANCE|TAVOLA DI CONCORDANZA|TABLA DE CORRESPONDENCIAS)\b", re.I)
_RANG = {  # niveau van een afdelingskop, naar het kernwoord
    1: r"teil|part|partie|deel|parte",
    2: r"titel|title|titre|titolo|título|titulo",
    3: r"kapitel|chapter|chapitre|hoofdstuk|capo|capitolo|capítulo|capitulo",
    4: r"abschnitt|section|afdeling|sezione|sección|seccion",
    5: r"unterabschnitt|subsection|sous-section|onderafdeling|sottosezione|subsección",
}
PREAMBULE = dict(nl="Preambule", de="Präambel", fr="Préambule", it="Preambolo", en="Preamble", es="Preámbulo")

_KLASSE = {
    "art": {"ti-art", "oj-ti-art", "title-article-norm"},
    "sti": {"sti-art", "oj-sti-art", "stitle-article-norm"},
    "sec1": {"ti-section-1", "oj-ti-section-1", "title-division-1"},
    "sec2": {"ti-section-2", "oj-ti-section-2", "title-division-2"},
    "doc": {"doc-ti", "oj-doc-ti", "title-doc-first", "title-doc-last", "title-annex-1", "title-annex-2", "oj-ti-annex"},
}
_WEG = {"modref", "arrow", "disclaimer", "reference", "hd-date", "hd-lg", "hd-ti", "hd-oj", "oj-hd-date", "oj-hd-lg", "oj-hd-ti",
        "oj-hd-oj", "doc-end", "oj-doc-end", "separator", "oj-separator", "hd-modifiers", "linkToTop"}
_BLAD = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "li", "dt", "dd", "caption"}
_MARKERING = re.compile(r"[▼►◄]\s?(?:[A-Z]\d*)?\s?")


def _schoon(t: str) -> str:
    t = _MARKERING.sub(" ", t)
    return re.sub(r"\s+", " ", t.replace("\xa0", " ")).strip()


def _soort(klassen: set[str]) -> str:
    if klassen & _WEG or any("note" in k for k in klassen):
        return "weg"
    for soort, namen in _KLASSE.items():
        if klassen & namen:
            return soort
    return "tekst"


# --- HTML → blokken -----------------------------------------------------------------

def _lokaal(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def _tekst_van(el: ET.Element) -> str:
    delen = []

    def loop(e: ET.Element) -> None:
        klassen = set((e.get("class") or "").split())
        if klassen & _WEG or any("note" in k for k in klassen):
            if e.tail:
                delen.append(e.tail)
            return
        if e.text:
            delen.append(e.text)
        for k in e:
            loop(k)
            if _lokaal(k.tag) in ("td", "th", "div", "p", "br"):
                delen.append(" ")
        if e.tail and e is not el:
            delen.append(e.tail)

    loop(el)
    return _schoon("".join(delen))


def _blokken_xhtml(bron: str) -> list[tuple[str, str]] | None:
    bron = re.sub(r"<!DOCTYPE[^>]*>", "", bron, count=1)
    bron = re.sub(r"&(?!amp;|lt;|gt;|quot;|apos;|#)(\w+);", lambda m: htmllib.unescape(m.group(0)), bron)
    try:
        wortel = ET.fromstring(bron.encode("utf-8"))
    except ET.ParseError:
        return None
    uit: list[tuple[str, str]] = []

    def heeft_blokken(e: ET.Element) -> bool:
        return any(_lokaal(k.tag) in _BLAD or _lokaal(k.tag) == "table" for k in e.iter() if k is not e)

    def is_blad(e: ET.Element, tag: str, klassen: set[str]) -> bool:
        if tag == "div" and "grid-container" in klassen:
            return True
        if tag in _BLAD:
            return not any(_lokaal(k.tag) == "table" for k in e)
        return tag == "div" and "inline-element" not in klassen and not heeft_blokken(e)

    def voeg_toe(soort: str, t: str) -> None:
        if t and soort != "weg":
            uit.append((soort, t))

    def blad(e: ET.Element, klassen: set[str]) -> None:
        # Een alinea met een blok-soort uit een kind (<td><p class="dlist-term">) telt als die soort.
        soort = _soort(klassen)
        if soort == "tekst" and _lokaal(e.tag) == "tr":
            eerste = next((k for k in e.iter() if k is not e and (k.get("class") or "")), None)
            soort = _soort(set((eerste.get("class") or "").split())) if eerste is not None else "tekst"
            soort = "tekst" if soort == "weg" else soort
        voeg_toe(soort, _tekst_van(e))

    def loop(e: ET.Element) -> None:
        """Een container: blokken erin apart, losse tekst ertussen ("(1)" + inline-div) als eigen alinea."""
        los: list[str] = [e.text or ""]

        def spoel() -> None:
            voeg_toe("tekst", _schoon("".join(los)))
            los.clear()

        for k in e:
            tag = _lokaal(k.tag)
            klassen = set((k.get("class") or "").split())
            if tag in ("script", "style", "head", "title") or klassen & _WEG or any("note" in x for x in klassen):
                los.append(k.tail or "")
                continue
            if is_blad(k, tag, klassen):
                spoel()
                blad(k, klassen)
            elif tag in ("div", "table", "tbody", "thead", "ul", "ol", "dl", "section", "article", "body", "center") or heeft_blokken(k):
                spoel()
                loop(k)
            else:
                los.append(_tekst_van(k) + " ")
                los.append(k.tail or "")
                continue
            los.append(k.tail or "")
        spoel()

    body = next((e for e in wortel.iter() if _lokaal(e.tag) == "body"), wortel)
    loop(body)
    return uit


class _Alineas(HTMLParser):
    """Oudere HTML zonder geldige XML: elke <p>, <td>-rij of kop wordt een blok."""

    BLOK = {"p", "h1", "h2", "h3", "h4", "tr", "li", "div"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.blokken: list[tuple[str, str]] = []
        self._stapel: list[tuple[str, set[str], list[str]]] = []
        self._weg = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "head"):
            self._weg += 1
        if tag in self.BLOK:
            if self._stapel:  # genest blok: de ouder sluit hier af
                self._sluit()
            self._stapel.append((tag, set((a.get("class") or "").split()), []))
        elif tag in ("td", "th", "br") and self._stapel:
            self._stapel[-1][2].append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head"):
            self._weg = max(0, self._weg - 1)
        if tag in self.BLOK and self._stapel:
            self._sluit()

    def _sluit(self) -> None:
        _, klassen, delen = self._stapel.pop()
        t = _schoon("".join(delen))
        soort = _soort(klassen)
        if t and soort != "weg":
            self.blokken.append((soort, t))

    def handle_data(self, data):
        if self._stapel and not self._weg:
            self._stapel[-1][2].append(data)


def blokken(bron: str) -> list[tuple[str, str]]:
    # Zeer grote documenten (tarieflijsten, bijlagen van tientallen MB) streamend: een ElementTree-boom kost het
    # tienvoudige aan geheugen.
    xml = (bron.lstrip().startswith("<?xml") or "xmlns" in bron[:2000]) and len(bron) < 15_000_000
    b = _blokken_xhtml(bron) if xml else None
    if b is None:
        p = _Alineas()
        p.feed(bron)
        p.close()
        b = p.blokken
        # Oude documenten: de tekst staat in #TexteOnly; de kop ervoor (bannier, OJ-verwijzing) laten we weg.
        start = next((i for i, (_, t) in enumerate(b) if t == "*****" or re.match(r"^(VERORDNUNG|RICHTLINIE|RAHMENBESCHLUSS|REGULATION|"
                     r"DIRECTIVE|COUNCIL|VERORDENING|RICHTLIJN|RÈGLEMENT|REGOLAMENTO|DIRETTIVA|REGLAMENTO|DIRECTIVA)\b", t)), None)
        if start is not None:
            b = b[start:]
    return b


# --- blokken → artikelen ------------------------------------------------------------

def _rang(kop: str) -> int:
    woorden = kop.lower().split()[:3]
    for rang, patroon in _RANG.items():
        if any(re.fullmatch(patroon, w) for w in woorden):
            return rang
    return 6


def _kort(protocol: re.Match) -> str:
    return f"{protocol.group(1).capitalize()} {protocol.group(2)}"


def _bijlage_naam(kop: str) -> str:
    kop = re.sub(r"\s*\(\*?\d*\)\s*$", "", kop.strip()).rstrip(".")
    return kop if not kop.isupper() else kop.capitalize() if " " not in kop else " ".join(
        w if re.fullmatch(r"[IVXL]+|\d+\w?", w) else w.capitalize() for w in kop.split())


def parse(bron: str, celex: str, bron_url: str | None = None, taal: str = "de", versie: str | None = None) -> Geparseerd:
    pre = PREAMBULE.get(taal, PREAMBULE["de"])
    titel_delen: list[str] = []
    artikelen: list[Artikel] = []
    preambule: list[str] = []
    huidig: Artikel | None = None
    buffer: list[str] = []
    niveaus: dict[int, str] = {}
    open_kop: int | None = None  # rang van de laatste afdelingskop, voor de titel eronder (sec2)
    deel, deel_kort = "", ""  # protocol of bijlage waarin we zitten
    in_bijlage = False
    gezien = False  # al een artikel gehad
    begonnen = False  # de titel is voorbij

    def pad() -> str | None:
        return " › ".join(([deel] if deel else []) + [niveaus[k] for k in sorted(niveaus)]) or None

    def sluit() -> None:
        nonlocal huidig, buffer
        if huidig is not None:
            huidig.tekst = "\n\n".join(buffer).strip() or "—"
            artikelen.append(huidig)
        huidig, buffer = None, []

    def begin(nummer: str, opschrift: str | None = None) -> None:
        nonlocal huidig
        sluit()
        huidig = Artikel(nummer=nummer, tekst="", opschrift=opschrift, pad=pad())

    bl = blokken(bron)
    # Met opmaakklassen herkennen we koppen alleen aan hun klasse; zonder (oude teksten) aan de woorden.
    klassen = any(soort != "tekst" for soort, _ in bl)
    in_inhoud = False
    for soort, t in bl:
        if not begonnen:
            if soort == "doc":
                titel_delen.append(t)
                continue
            if klassen and not titel_delen and soort == "tekst":
                continue  # kop boven de titel (geconsolideerde tekst: titel en rectificaties nog eens)
            if not klassen and not titel_delen and t.isupper() and len(t) < 300:
                titel_delen.append(t)  # oude opmaak: de titel is de eerste alinea in hoofdletters
                continue
        begonnen = True
        if not gezien and t in ("Inhalt", "Inhoud", "Contents", "Sommaire", "Indice", "Índice", "INHALT", "INHOUD", "SOMMAIRE"):
            in_inhoud = True  # inhoudsopgave (verdragen): regels met een paginanummer
            continue
        if in_inhoud:
            if re.search(r"\s\d{1,4}$", t):
                continue
            in_inhoud = False
        m_art = _ART_RE.match(t) if len(t) < 120 else None
        is_art = m_art is not None and (soort == "art" or (not klassen and soort == "tekst" and len(t) < 40 and not in_bijlage))
        if soort == "doc" or (not klassen and soort == "tekst" and not is_art and (_PROTOCOL.match(t) or (_BIJLAGE.match(t) and t.isupper() and len(t) < 120))):
            if (prot := _PROTOCOL.match(t)) and len(t) < 80:
                deel, deel_kort, niveaus, in_bijlage = t, _kort(prot), {}, False
                begin(deel_kort)
                continue
            if _BIJLAGE.match(t) and len(t) < 120:
                deel, deel_kort, niveaus, in_bijlage = "", "", {}, True
                begin(_bijlage_naam(t))
                deel = huidig.nummer
                continue
            if huidig is not None and not buffer and huidig.nummer in (deel_kort, deel):
                # tweede regel van een protocol- of bijlagekop: "ÜBER DIE ROLLE DER NATIONALEN PARLAMENTE …"
                huidig.opschrift = f"{huidig.opschrift} {t}" if huidig.opschrift else t
                if deel_kort and len(deel) < 200:
                    deel = f"{deel} {t}"
                continue
            soort = "tekst"
        if is_art:
            if not gezien and preambule:
                artikelen.append(Artikel(nummer=pre, tekst="\n\n".join(preambule)))
                preambule = []
            gezien = True
            nr = re.sub(r"\s+", "", m_art.group(1))
            nr = _EERSTE.get(nr.lower(), nr)
            begin(f"{deel_kort} Art. {nr}" if deel_kort else nr, (m_art.group(2) or "").strip(" -–—") or None)
            continue
        if soort in ("sec1", "sec2") and not in_bijlage:
            if soort == "sec2" and open_kop is not None:
                niveaus[open_kop] = f"{niveaus[open_kop]} {t}"
                open_kop = None
            else:
                r = _rang(t)
                niveaus = {k: v for k, v in niveaus.items() if k < r}
                niveaus[r] = t
                open_kop = r if soort == "sec1" else None
            if huidig is not None and (buffer or huidig.nummer != deel_kort):
                sluit()
            continue
        if huidig is not None and not huidig.opschrift and not buffer and (
                soort == "sti" or (soort == "tekst" and len(t) < 150 and not re.search(r"[.:;,]$", t)
                                   and not re.match(r"^(\(?\d|[a-z]\)|\(?[ivx]+\)|[-—–•])", t))):
            huidig.opschrift = t  # oudere consolidaties: het opschrift is een gewone alinea
            continue
        if huidig is None:
            if not gezien:
                preambule.append(t)
                continue
            begin(deel_kort or pre)
        buffer.append(t)
    sluit()
    if preambule:  # handeling zonder artikelen: alles als één blok
        artikelen.insert(0, Artikel(nummer=pre, tekst="\n\n".join(preambule)))
    titel = " ".join(titel_delen)[:300] or celex
    return Geparseerd(wet_id=celex, titel=titel, versie=versie or date.today().isoformat(), bron_url=bron_url, artikelen=artikelen,
                      ruw=None, ruw_extensie="html")


# --- ophalen ------------------------------------------------------------------------

def download(celex: str, taal: str = "de", c=None) -> str | None:
    """Het document uit de Cellar, of None als het in deze taal niet bestaat."""
    url = CELLAR.format(celex=celex.replace("/", "%2F"))
    eigen = c is None
    c = c or client()
    try:
        for accept in ("application/xhtml+xml", "text/html"):
            r = c.get(url, headers={"Accept": accept, "Accept-Language": TAAL3.get(taal, taal)}, follow_redirects=True, timeout=180)
            if r.status_code == 200 and r.content:
                return r.content.decode("utf-8", "replace")
            # 300: de Cellar heeft meerdere manifestaties en kiest niet; behandelen als "niet in deze vorm".
            if r.status_code not in (300, 404, 406):
                r.raise_for_status()
        return None
    finally:
        if eigen:
            c.close()


def versie_van(celex: str) -> str:
    m = re.search(r"-(\d{4})(\d{2})(\d{2})$", celex)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else date.today().isoformat()


def haal_op(celex: str, taal: str = "de", tekst_celex: str | None = None) -> Geparseerd:
    """Eén handeling: `tekst_celex` is de geconsolideerde versie als die er is (anders `celex` zelf)."""
    taal = taal.lower()
    bron_celex = tekst_celex or (f"{celex}/TXT" if celex.startswith("1") and len(celex) == 6 else celex)
    doc = download(bron_celex, taal)
    if doc is None:
        raise LookupError(f"{bron_celex} bestaat niet in het {taal}")
    versie = versie_van(bron_celex) + (" (konsolidiert)" if bron_celex.startswith("0") else "")
    return parse(doc, celex, EURLEX.format(taal=taal.upper(), celex=bron_celex.split("/")[0]), taal=taal, versie=versie)
