"""Uitbreidingen per bestand in plaats van in gedeelde lijsten.

Een nieuw stelsel of een nieuwe regio voegt eigen modules toe (`importers/register_<regio>.py`,
`seed/stelsels_<regio>.py`, `services/regels_<regio>.py`) in plaats van het register, de stelsellijst en de
citeerregels te bewerken. `modules()` vindt ze, op naam gesorteerd.
"""
from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType


def modules(pakket: str, prefix: str) -> list[ModuleType]:
    mod = importlib.import_module(pakket)
    namen = sorted(m.name for m in pkgutil.iter_modules(mod.__path__) if m.name.startswith(prefix))
    return [importlib.import_module(f"{pakket}.{n}") for n in namen]


def importer(naam: str) -> ModuleType:
    """De importermodule `synoptikon.importers.<naam>` (met `haal_op(id, titel=…)` en `parse(data, id)`)."""
    return importlib.import_module(f"synoptikon.importers.{naam}")
