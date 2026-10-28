"""BE: boeken van het nieuwe Burgerlijk Wetboek, uit de spiegel van het Belgisch Staatsblad.

Justel (de geconsolideerde databank van de FOD Justitie) weigert
geautomatiseerde toegang; etaamb.openjustice.be is een openbare spiegel van
het Staatsblad en geeft de tekst *zoals bekendgemaakt*. Dat betekent: geen
consolidatie. Wijzigingen na de bekendmaking zijn niet verwerkt; de versie
heet daarom "bekendmaking JJJJ-MM-DD" en de link naar Justel staat erbij.

De tekst staat in <div class="document_text"> als losse alinea's; de wet
"houdende boek 5" bevat het boek tussen aanhalingstekens in een van haar
eigen artikelen. We lezen de tekst als één stroom en knippen op koppen
("Boek 5.", "Titel 2.", "Ondertitel 1.", "Hoofdstuk 3.", "Afdeling 4.",
"Onderafdeling 1.") en artikelen met een samengesteld nummer ("Art. 5.69.",
"Artikel 2.3.16."). Artikelen van de invoeringswet zelf ("Art. 3.") sluiten
het vorige artikel af maar worden niet opgenomen. Het opschrift van een
artikel staat op dezelfde regel als het nummer, gescheiden door een
regelovergang (in de spiegel: drie of meer spaties).
"""
from __future__ import annotations

import html as htmllib
import re

from . import Artikel, Geparseerd
from .http import client

URL = "https://etaamb.openjustice.be/nl/{slug}.html"
JUSTEL = "https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=nl&la=N&table_name=wet&cn={cn}"

_NIVEAUS = ["Boek", "Titel", "Ondertitel", "Hoofdstuk", "Afdeling", "Onderafdeling"]
_MARKER = re.compile(
    r"(?:^|\n|\s{3}|[\"“])\s*(?:(?P<kop>Boek|Titel|Ondertitel|Hoofdstuk|Afdeling|Onderafdeling)\s+(?P<kopnr>\d+(?:/\d+)?(?:bis|ter)?)\.\s*"
    r"|(?P<art>Art(?:ikel|\.))\s*(?P<nr>\d+(?:\.\d+)+(?:/\d+)?(?:bis|ter|quater)?)\.\s*"
    r"|(?P<eind>Art(?:ikel|\.))\s*\d+(?:bis|ter)?\.\s)"
)


def _platte_tekst(pagina: str) -> tuple[str, str]:
    m = re.search(r'<div class="document_text">(.*?)<div class="etaamb_description">', pagina, re.S)
    ruw = m.group(1) if m else pagina
    titel = re.search(r'<span class="p_title">(.*?)</span>', ruw, re.S)
    ruw = re.sub(r"</p>|<br\s*/?>|<p[^>]*>|<span class=\"p_(?:section|chapitre|article)\">", "\n", ruw)
    ruw = re.sub(r"<[^>]+>", "", ruw)
    tekst = htmllib.unescape(ruw).replace("\xa0", " ")
    return tekst, re.sub(r"\s+", " ", htmllib.unescape(titel.group(1))).strip() if titel else ""


def _regel(s: str) -> tuple[str, str]:
    """Eerste 'regel' (tot een regelovergang of drie spaties) en de rest."""
    m = re.search(r"\n|\s{3,}", s)
    if not m:
        return s.strip(), ""
    return s[: m.start()].strip(), s[m.end():]


def _alineas(s: str) -> str:
    delen = [re.sub(r"\s+", " ", d).strip() for d in s.split("\n")]
    return "\n\n".join(d for d in delen if d).strip(" \"”")


def parse(pagina: str, wet_id: str, bron_url: str | None = None, titel: str | None = None, versie: str | None = None) -> Geparseerd:
    tekst, paginatitel = _platte_tekst(pagina)
    markers = list(_MARKER.finditer(tekst))
    stapel: list[tuple[int, str]] = []
    artikelen: list[Artikel] = []
    for i, m in enumerate(markers):
        einde = markers[i + 1].start() if i + 1 < len(markers) else len(tekst)
        stuk = tekst[m.end():einde]
        if m.group("kop"):
            niveau = _NIVEAUS.index(m.group("kop"))
            naam, _ = _regel(stuk)
            naam = naam.strip(" \"“”")
            stapel = [k for k in stapel if k[0] < niveau] + [(niveau, f"{m.group('kop')} {m.group('kopnr')} {naam}".strip())]
        elif m.group("art"):
            opschrift, rest = _regel(stuk)
            if not rest.strip():  # artikel zonder opschrift
                opschrift, rest = None, stuk
            artikelen.append(Artikel(nummer=m.group("nr"), tekst=_alineas(rest) or "(geen tekst)", opschrift=opschrift or None,
                                     pad=" › ".join(k[1] for k in stapel) or None))
        # een artikel van de invoeringswet ("Art. 3.") sluit alleen af
    if not versie:
        d = re.search(r"<dt>pub\.</dt>\s*<dd class=\"date\">(\d\d)/(\d\d)/(\d{4})", pagina)
        versie = f"bekendmaking {d.group(3)}-{d.group(2)}-{d.group(1)}" if d else "bekendmaking"
    return Geparseerd(wet_id=wet_id, titel=titel or paginatitel or wet_id, versie=versie, bron_url=bron_url,
                      artikelen=artikelen, ruw=pagina.encode(), ruw_extensie="html")


def haal_op(slug: str, titel: str | None = None) -> Geparseerd:
    """`slug`: het etaamb-adres zonder .html, bijv. 'wet-van-28-april-2022_n2022032058'."""
    url = URL.format(slug=slug)
    with client(timeout=120.0) as c:
        r = c.get(url)
        r.raise_for_status()
    return parse(r.text, slug, url, titel)
