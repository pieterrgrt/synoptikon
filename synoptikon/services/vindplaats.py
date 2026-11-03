"""Het soort vindplaats afleiden uit de vindplaats zelf: "ECLI:NL:HR:1982:AG4405" → ECLI, "NJW 2011, 1881" → NJW.

Zo hoeft niemand het type in te vullen, en is een bron zonder vindplaats te vinden (`/bronnen?zonder=vindplaats`)."""
from __future__ import annotations

import re

_PATRONEN = [
    ("ECLI", r"\bECLI:[A-Z]{2}:"),
    ("CELEX", r"\bCELEX\b|\b[0-9]\d{4}[A-Z]{1,2}\d{4}\b"),
    ("BWB", r"\bBWBR\d{7}\b"),
    ("LEGIARTI", r"\bLEGI(?:ARTI|TEXT)\d+"),
    ("NJW", r"\bNJW\s+\d{4}"),
    ("BGHZ", r"\bBGHZ\s+\d+"),
    ("BVerfGE", r"\bBVerfGE\s+\d+"),
    ("RGZ", r"\bRGZ\s+\d+"),
    ("NJ", r"\bNJ\s+\d{4}[/,]"),
    ("pourvoi", r"\bn°\s*\d{2}-\d{2}\.\d{3}|\bpourvoi\b"),
    ("Bull.", r"\bBull\.\s*civ\."),
    ("neutral citation", r"\[\d{4}\]\s+(?:UKSC|UKHL|UKPC|EWCA|EWHC)\b"),
    ("law reports", r"\[\d{4}\]\s+(?:AC|QB|KB|Ch|WLR|All ER|Fam)\b"),
    ("ISBN", r"\bISBN\b"),
    ("UNTS", r"\bUNTS\b"),
]


def soort(vindplaats: str | None) -> str | None:
    """Het eerste soort dat in de vindplaats voorkomt (de ECLI gaat voor NJ: "ECLI:…; NJ 1983/723" is een ECLI)."""
    if not vindplaats:
        return None
    for naam, patroon in _PATRONEN:
        if re.search(patroon, vindplaats):
            return naam
    return None
