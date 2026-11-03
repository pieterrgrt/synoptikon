"""Een citatie om te kopiëren ("Citeer"): zoals men in het stelsel citeert, klaar voor een processtuk of scriptie.

Artikelen: `Ref.citeer` ("art. 6:162 lid 2 BW", "§ 823 Abs. 1 BGB", "art. 1240 C. civ."). Uitspraken: de citeertitel
met de ECLI en de andere vindplaatsen ervoor, de roepnaam tussen haakjes achteraan, zoals de Leidraad voor juridische
auteurs dat doet: "HR 18 juni 1982, ECLI:NL:HR:1982:AG4405, NJ 1983/723 (Plas/Valburg)".
"""
from __future__ import annotations

import re

from ..models import Bron
from .artikelen import Ref, ref_uit_bron

_ECLI = re.compile(r"ECLI:[A-Z]{2}:[A-Z0-9]+:\d{4}:[A-Z0-9.]+", re.I)
_ONZEKER = re.compile(r"\s*\((?:niet geverifieerd|not verified)\)", re.I)


def artikel(ref: Ref) -> str:
    return ref.citeer


def _vindplaatsen(b: Bron) -> list[str]:
    """ECLI eerst, dan de rest (NJ, BGHZ, Jur.); "CELEX …" laat men in een citatie weg."""
    delen = [d.strip() for d in re.split(r";\s*", _ONZEKER.sub("", b.vindplaats or "")) if d.strip()]
    ecli = [d for d in delen if _ECLI.fullmatch(d)]
    rest = [d for d in delen if d not in ecli and not d.upper().startswith("CELEX")]
    return ecli + rest


def bron(b: Bron) -> str:
    if b.soort == "wet":
        r = ref_uit_bron(b)
        return r.citeer if r else b.citeertitel
    titel = _ONZEKER.sub("", b.citeertitel).strip()
    if b.soort != "rechtspraak":
        return titel
    vindplaatsen = [v for v in _vindplaatsen(b) if v.casefold() not in titel.casefold()]
    if not vindplaatsen:
        return titel
    m = re.fullmatch(r"(.*?)\s*(\((?:[^()]|\([^()]*\))*\))", titel)  # de roepnaam of partijen tussen haakjes achteraan
    kern, naam = (m.group(1), " " + m.group(2)) if m else (titel, "")
    return f"{kern}, {', '.join(vindplaatsen)}{naam}"
