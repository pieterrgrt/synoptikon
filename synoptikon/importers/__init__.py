"""Importers voor wetteksten.

Elke importer levert een `Geparseerd`-object (titel, versie, artikelen) uit
een ruwe download of een lokaal bestand. `store.sla_op` schrijft het ruwe
bestand onder data/wetteksten en zet de artikelen in de database. De app
leest daarna uitsluitend uit de database.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Artikel:
    nummer: str
    tekst: str
    opschrift: str | None = None
    pad: str | None = None


@dataclass
class Geparseerd:
    wet_id: str
    titel: str
    versie: str
    bron_url: str | None
    artikelen: list[Artikel] = field(default_factory=list)
    ruw: bytes | None = None
    ruw_extensie: str = "xml"


class ImportOvergeslagen(Exception):
    """De importer kan niet draaien (bijv. geen API-sleutel) en slaat netjes over."""
