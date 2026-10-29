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


VIGUEUR = Path("legi/global/code_et_TNC_en_vigueur/code_en_vigueur")


def _map(basis: Path, code: str) -> Path:
    # Eerst de vaste plaats in de dump (rglob over een volledige dump duurt minuten), dan zoeken.
    cijfers = code[8:]
    for p in (basis / VIGUEUR / "LEGI" / "TEXT" / Path(*[cijfers[i:i + 2] for i in range(0, 10, 2)]) / code, basis / code):
        if (p / "texte").exists():
            return p
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
    # Versie = de laatste begindatum van een geldende sectie of geldend artikel: stabiel zolang de tekst niet verandert
    # (de peildatum zelf zou elke dag een nieuwe "versie" geven).
    laatste = ["0000-00-00"]

    def sectie(id_: str, pad: list[str]) -> None:
        f = _bestand(map_, "section_ta", id_)
        if not f.exists():
            return
        root = ET.parse(f).getroot()
        for el in root.find("STRUCTURE_TA") if root.find("STRUCTURE_TA") is not None else []:
            if not _geldig(el, peil) or el.get("etat") in ("ABROGE", "ANNULE", "PERIME", "TRANSFERE"):
                continue
            if (el.get("debut") or "") > laatste[0]:
                laatste[0] = el.get("debut")
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
    versie = laatste[0] if laatste[0] != "0000-00-00" else peil
    return Geparseerd(wet_id=code, titel=titel or TITELS.get(code, code), versie=versie, bron_url=WEB.format(id=code), artikelen=artikelen)


# --- alle codes (bulk en bijwerken) ---------------------------------------------------------

# Gangbare citeerwijze van de codes (Dalloz/Cour de cassation); LEGI zelf geeft alleen de titel. Een code die hier niet
# staat, wordt onder haar titel opgeslagen.
AFKORTINGEN = {
    "Code civil": "C. civ.", "Code de la consommation": "C. consom.", "Code de commerce": "C. com.", "Code du travail": "C. trav.",
    "Code rural et de la pêche maritime": "C. rur.", "Code de procédure civile": "C. proc. civ.", "Code des assurances": "C. assur.",
    "Code pénal": "C. pén.", "Code de procédure pénale": "C. pr. pén.", "Code de la propriété intellectuelle": "CPI",
    "Code monétaire et financier": "C. mon. fin.", "Code de la sécurité sociale": "CSS", "Code général des impôts": "CGI",
    "Code de l'environnement": "C. envir.", "Code de la santé publique": "CSP", "Code de l'urbanisme": "C. urb.",
    "Code de justice administrative": "CJA", "Code de la construction et de l'habitation": "CCH",
    "Code des procédures civiles d'exécution": "CPCE", "Code de l'organisation judiciaire": "COJ",
    "Code général des collectivités territoriales": "CGCT", "Code des relations entre le public et l'administration": "CRPA",
    "Code de l'entrée et du séjour des étrangers et du droit d'asile": "CESEDA", "Code de l'éducation": "C. éduc.",
    "Code de la route": "C. route", "Code des transports": "C. transp.", "Code électoral": "C. élect.",
    "Code de la mutualité": "C. mut.", "Code des douanes": "C. douanes", "Code du sport": "C. sport",
    "Code de la commande publique": "CCP", "Code général de la propriété des personnes publiques": "CGPPP",
}


def afkorting(titel: str) -> str:
    return AFKORTINGEN.get(titel.strip(), titel.strip())


def codes(basis: Path) -> list[tuple[str, str]]:
    """Alle codes in de uitgepakte dump (map `code_en_vigueur`): [(LEGITEXT…, titel)], op id gesorteerd."""
    uit = {}
    vast = Path(basis) / VIGUEUR
    for vigueur in [vast] if vast.is_dir() else Path(basis).rglob("code_en_vigueur"):
        for versie in vigueur.glob("LEGI/TEXT/*/*/*/*/*/LEGITEXT*/texte/version/LEGITEXT*.xml"):
            code = versie.stem
            try:
                meta = ET.parse(versie).getroot().find(".//META_TEXTE_VERSION")
            except ET.ParseError:
                continue
            titel = re.sub(r"\s+", " ", (meta.findtext("TITREFULL") or meta.findtext("TITRE") or code) if meta is not None else code).strip()
            if meta is not None and (meta.findtext("ETAT") or "VIGUEUR") not in ("VIGUEUR", "VIGUEUR_DIFF"):
                continue
            uit[code] = titel
    return sorted(uit.items())
