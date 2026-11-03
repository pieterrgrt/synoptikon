"""Arresten op hun roepnaam: "Kelderluik", "Haviltex", "Costa/ENEL" → de ECLI.

Juristen noemen een arrest bij zijn naam, niet bij zijn nummer. Elke ECLI hieronder is op 03-11-2026 nagekeken bij de
bron (rechtspraak.nl of de Cellar van EUR-Lex): datum en zaak kloppen. Zet er alleen iets bij dat zo is nagekeken;
een verkeerd nummer is erger dan geen nummer. De EU-arresten uit `eu_logica` (Van Gend & Loos, Costa/ENEL, Francovich …)
komen er vanzelf bij.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Roepnaam:
    naam: str
    ecli: str


# naam (en andere schrijfwijzen) → ECLI
_LIJST: list[tuple[tuple[str, ...], str]] = [
    # Hoge Raad
    (("Kelderluik",), "ECLI:NL:HR:1965:AB7079"),
    (("Lindenbaum/Cohen", "Lindenbaum-Cohen"), "ECLI:NL:HR:1919:AG1776"),
    (("Haviltex",), "ECLI:NL:HR:1981:AG4158"),
    (("Plas/Valburg", "Plas-Valburg"), "ECLI:NL:HR:1982:AG4405"),
    (("Baris/Riezenkamp", "Baris-Riezenkamp"), "ECLI:NL:HR:1957:AG2023"),
    (("CBB/JPO",), "ECLI:NL:HR:2005:AT7337"),
    (("Beklamel",), "ECLI:NL:HR:1989:AB9521"),
    (("Wilnis",), "ECLI:NL:HR:2010:BN6236"),
    (("Urgenda", "Staat/Urgenda"), "ECLI:NL:HR:2019:2007"),
    # Hof van Justitie
    (("Cassis de Dijon", "Rewe-Zentral"), "ECLI:EU:C:1979:42"),
    (("Dassonville",), "ECLI:EU:C:1974:82"),
    (("Keck", "Keck en Mithouard"), "ECLI:EU:C:1993:905"),
    (("Simmenthal",), "ECLI:EU:C:1978:49"),
    (("Factortame",), "ECLI:EU:C:1990:257"),
    (("Überseering", "Ueberseering"), "ECLI:EU:C:2002:632"),
    (("Daily Mail",), "ECLI:EU:C:1988:456"),
    (("Cartesio",), "ECLI:EU:C:2008:723"),
    (("Polbud",), "ECLI:EU:C:2017:804"),
    (("Google Spain",), "ECLI:EU:C:2014:317"),
    (("Schrems II",), "ECLI:EU:C:2020:559"),
    (("Centros",), "ECLI:EU:C:1999:126"),
    (("Inspire Art",), "ECLI:EU:C:2003:512"),
    (("Tacconi",), "ECLI:EU:C:2002:499"),
    (("Kornhaas",), "ECLI:EU:C:2015:806"),
    (("Sevic",), "ECLI:EU:C:2005:762"),
    (("VALE",), "ECLI:EU:C:2012:440"),
    (("Köbler", "Koebler"), "ECLI:EU:C:2003:513"),
    (("Brasserie du Pêcheur", "Brasserie du Pecheur"), "ECLI:EU:C:1996:79"),
    (("Mangold",), "ECLI:EU:C:2005:709"),
    (("Kadi",), "ECLI:EU:C:2008:461"),
]


def _sleutel(s: str) -> str:
    s = re.sub(r"[-‑–]?\s*(?:arrest|urteil|arrêt|judgment|zaak)\s*$", "", s.strip(), flags=re.I)
    s = re.sub(r"^(?:arrest|urteil|arrêt|zaak)\s+", "", s, flags=re.I)
    return re.sub(r"\s*[/\-–]\s*", "/", re.sub(r"\s+", " ", s)).casefold()


def _index() -> dict[str, Roepnaam]:
    from . import eu_logica

    uit: dict[str, Roepnaam] = {}
    for namen, ecli in _LIJST:
        for n in namen:
            uit[_sleutel(n)] = Roepnaam(namen[0], ecli)
    for waarde in vars(eu_logica).values():
        if isinstance(waarde, tuple) and len(waarde) == 2 and isinstance(waarde[0], str) and waarde[0].startswith("HvJ "):
            m = re.match(r"HvJ (.+?), .+?, (ECLI:EU:C:\d{4}:\d+)$", waarde[0])
            if m and not m.group(1).startswith("Commissie/"):  # "Commissie/Frankrijk" is geen roepnaam: daar zijn er honderden van
                uit.setdefault(_sleutel(m.group(1)), Roepnaam(m.group(1), m.group(2)))
    return uit


_INDEX: dict[str, Roepnaam] | None = None


def zoek(q: str) -> Roepnaam | None:
    """De roepnaam als de invoer (bijna) alleen dat is: "Kelderluik", "Kelderluik-arrest", "arrest Haviltex"."""
    global _INDEX
    if _INDEX is None:
        _INDEX = _index()
    if not q or len(q) > 60:
        return None
    return _INDEX.get(_sleutel(q))
