"""Bewaking van schijf en geheugen tijdens lange imports: liever netjes stoppen dan de server volschrijven.

Schijf: minstens `SYNOPTIKON_MIN_VRIJ_GB` (standaard 4) vrij op de schijf van de datamap, het archief en de LEGI-map.
Geheugen: in de container telt de cgroup-grens (memory.max), en die delen we met de webapp. Gemeten wordt het anonieme
geheugen (memory.stat `anon`), niet memory.current: dat telt ook de paginacache mee, die bij het lezen van de LEGI-dump
vanzelf groeit en door de kernel wordt vrijgegeven. Zonder cgroup-grens: de eigen RSS tegen
`SYNOPTIKON_MAX_GEHEUGEN_MB` (standaard 1024).
"""
from __future__ import annotations

import gc
import os
import shutil
from pathlib import Path

from ..config import settings

_CGROUP = Path("/sys/fs/cgroup")
GRENS = 0.85  # deel van memory.max


class Stop(Exception):
    """Te weinig schijf of geheugen, of de tijd is op: de lopende ronde stopt na de huidige wet."""


def vrij_gb(pad: Path) -> float:
    p = Path(pad)
    while not p.exists() and p != p.parent:
        p = p.parent
    return shutil.disk_usage(p).free / 1e9


def mappen() -> list[Path]:
    return [settings.data_dir, settings.archief_dir, settings.legi_dir]


def controleer_schijf() -> None:
    for m in mappen():
        vrij = vrij_gb(m)
        if vrij < settings.min_vrij_gb:
            raise Stop(f"nog {vrij:.1f} GB vrij op de schijf van {m} (minimum {settings.min_vrij_gb:g} GB, SYNOPTIKON_MIN_VRIJ_GB)")


def _cgroup() -> tuple[int, int] | None:
    """(anon, max) in bytes, of None zonder cgroup-v2-grens."""
    try:
        grens = (_CGROUP / "memory.max").read_text().strip()
        if grens == "max":
            return None
        for regel in (_CGROUP / "memory.stat").read_text().splitlines():
            if regel.startswith("anon "):
                return int(regel.split()[1]), int(grens)
    except (OSError, ValueError):
        return None
    return None


def _rss() -> int:
    try:
        return int(Path("/proc/self/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
    except (OSError, ValueError, IndexError):
        return 0


def geheugen_te_vol() -> str | None:
    cg = _cgroup()
    if cg:
        anon, grens = cg
        if anon > GRENS * grens:
            return f"geheugen {anon / 1e6:.0f} van {grens / 1e6:.0f} MB in gebruik (container)"
        return None
    maximum = int(os.environ.get("SYNOPTIKON_MAX_GEHEUGEN_MB") or 1024) * 1e6
    if _rss() > maximum:
        return f"eigen geheugen {_rss() / 1e6:.0f} MB boven {maximum / 1e6:.0f} MB (SYNOPTIKON_MAX_GEHEUGEN_MB)"
    return None


def controleer_geheugen() -> None:
    if geheugen_te_vol():
        gc.collect()
        reden = geheugen_te_vol()
        if reden:
            raise Stop(reden)


def controleer() -> None:
    controleer_schijf()
    controleer_geheugen()
