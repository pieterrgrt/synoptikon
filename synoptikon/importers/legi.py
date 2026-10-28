"""FR: LEGI, de open-databank van de DILA (de inhoud van Légifrance), lokaal uitgepakt.

Légifrance zelf zit achter Cloudflare en de PISTE-API vraagt een sleutel;
de LEGI-dump is vrij (licence ouverte). `scripts/legi_ophalen.sh` haalt de
volledige dump plus de dagelijkse aanvullingen en pakt alleen de gevraagde
codes uit. Per code staat er dan een map `…/LEGITEXT000006070721/` met:

* `texte/struct/LEGITEXT….xml`: de bovenste secties (LIEN_SECTION_TA, niv 1);
* `section_ta/…/LEGISCTA….xml`: per sectie haar titel, subsecties en
  artikelen (LIEN_ART), elk met een geldigheidsperiode (debut–fin);
* `article/…/LEGIARTI….xml`: één versie van één artikel, met de tekst in
  BLOC_TEXTUEL/CONTENU.

We lopen de boom af en nemen per sectie en per artikel de versie die op de
peildatum geldt (debut ≤ datum < fin). Zo volgen de volgorde en het pad uit
de officiële structuur en komen ingetrokken en toekomstige versies niet mee.
"""
from __future__ import annotations

import html as htmllib
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from . import Artikel, Geparseerd

WEB = "https://www.legifrance.gouv.fr/codes/texte_lc/{id}"

TITELS = {
    "LEGITEXT000006070721": "Code civil",
    "LEGITEXT000006069565": "Code de la consommation",
    "LEGITEXT000005634379": "Code de commerce",
}


def _map(basis: Path, code: str) -> Path:
    for p in basis.rglob(code):
        if p.is_dir() and (p / "texte").exists():
            return p
    raise FileNotFoundError(f"{code} niet gevonden onder {basis}; eerst scripts/legi_ophalen.sh draaien")


def _geldig(el: ET.Element, peil: str) -> bool:
    return (el.get("debut") or "0000") <= peil < (el.get("fin") or "2999-01-01")


def _bestand(map_: Path, soort: str, id_: str) -> Path:
    """LEGIARTI000006437044 → article/LEGI/ARTI/00/00/06/43/70/LEGIARTI000006437044.xml (paren van cijfers 0–9)."""
    cijfers = id_[8:]
    delen = [cijfers[i:i + 2] for i in range(0, 10, 2)]
    return map_.joinpath(soort, "LEGI", id_[4:8], *delen, f"{id_}.xml")


def _tekst(contenu: ET.Element | None) -> str:
    if contenu is None:
        return ""
    ruw = ET.tostring(contenu, encoding="unicode", method="html")
    ruw = re.sub(r"<br\s*/?>|</p>|<p[^>]*>|</?div[^>]*>|</tr>", "\n", ruw)
    ruw = re.sub(r"<[^>]+>", " ", ruw)
    delen = [re.sub(r"\s+", " ", htmllib.unescape(d)).strip() for d in ruw.split("\n")]
    return "\n\n".join(d for d in delen if d)


def _kop(titel: str) -> str:
    """'Titre III : Des sources d'obligations' blijft zo; dubbele spaties en een slotpunt weg."""
    return re.sub(r"\s+", " ", titel).strip().rstrip(".")


def parse_map(basis: Path, code: str, peildatum: date | None = None, titel: str | None = None) -> Geparseerd:
    peil = (peildatum or date.today()).isoformat()
    map_ = _map(Path(basis), code)
    struct = ET.parse(next((map_ / "texte" / "struct").glob("*.xml"))).getroot()
    artikelen: list[Artikel] = []
    gezien: set[str] = set()

    def sectie(id_: str, pad: list[str]) -> None:
        f = _bestand(map_, "section_ta", id_)
        if not f.exists():
            return
        root = ET.parse(f).getroot()
        for el in root.find("STRUCTURE_TA") if root.find("STRUCTURE_TA") is not None else []:
            if not _geldig(el, peil) or el.get("etat") in ("ABROGE", "ANNULE", "PERIME", "TRANSFERE"):
                continue
            if el.tag == "LIEN_SECTION_TA":
                sectie(el.get("id"), [*pad, _kop(el.text or "")])
            elif el.tag == "LIEN_ART":
                nummer = (el.get("num") or "").strip()
                if not nummer or nummer in gezien:
                    continue
                af = _bestand(map_, "article", el.get("id"))
                if not af.exists():
                    continue
                art = ET.parse(af).getroot()
                gezien.add(nummer)
                artikelen.append(Artikel(nummer=nummer, tekst=_tekst(art.find("BLOC_TEXTUEL/CONTENU")) or "(sans texte)", pad=" › ".join(pad) or None))

    for el in struct.iter("LIEN_SECTION_TA"):
        if el.get("niv") == "1" and _geldig(el, peil):
            sectie(el.get("id"), [_kop(el.text or "")])
    return Geparseerd(wet_id=code, titel=titel or TITELS.get(code, code), versie=peil, bron_url=WEB.format(id=code), artikelen=artikelen)
