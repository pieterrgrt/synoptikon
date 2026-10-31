#!/usr/bin/env python3
"""Bouwt de wereldkaart voor het bibliotheekoverzicht: landcontouren als SVG-paden, één keer, offline.

Bron: Natural Earth (publiek domein, 1:110m voor landen, 1:50m voor de onderdelen die we apart nodig hebben).
De paden worden geprojecteerd met Equal Earth (Šavrič, Patterson & Jenny 2018): oppervlaktegetrouw, dus een land
ziet er even groot uit als het is, en rustiger dan Mercator — Groenland hoort niet groter dan Afrika te lijken.

Drie stelsels zijn geen land:

* `EU` is supranationaal. Het krijgt de vorm van de 27 lidstaten samen, als één pad; op de kaart komt dat als
  aparte laag onder de nationale tinten, want EU-recht geldt daar naast het nationale recht.
* `QC` (Québec) is een provincie: die komt uit de admin-1-laag, want CA en QC zijn twee stelsels op één landmassa.
* `EN` (Engeland & Wales) is een deel van het Verenigd Koninkrijk: dat komt uit de subunits-laag.

Hongkong is wél een land met een eigen ISO-code, maar op 1:110m te klein om een eigen vorm te krijgen; dat komt
daarom ook uit de 50m-subunits, met de oppervlakte-ondergrens uit.

Gebruik:  python3 -I scripts/bouw_wereldkaart.py [--data /tmp/natural-earth] [--uit synoptikon/static/kaart/wereld.json]
Het downloaden gebeurt één keer; daarna wordt wat in --data staat hergebruikt.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.request
from pathlib import Path

BRON = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/{naam}.geojson"
LANDEN = "ne_110m_admin_0_countries"
PROVINCIES = "ne_50m_admin_1_states_provinces"
SUBUNITS = "ne_50m_admin_0_map_subunits"

EU_LIDSTATEN = ("AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT",
                "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE")

# Equal Earth
A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
_WORTEL3_2 = math.sqrt(3) / 2


def _equal_earth(lon: float, lat: float) -> tuple[float, float]:
    """Graden → kaarteenheden, y naar boven positief (zoals de projectie zelf is opgeschreven)."""
    lam, phi = math.radians(lon), math.radians(lat)
    theta = math.asin(max(-1.0, min(1.0, _WORTEL3_2 * math.sin(phi))))
    t2 = theta * theta
    # y = A1θ + A2θ³ + A3θ⁹ + A4θ¹¹; x gebruikt dy/dθ.
    y = theta * (A1 + A2 * t2 + t2 * t2 * t2 * t2 * (A3 + A4 * t2))
    afgeleide = A1 + 3 * A2 * t2 + t2 * t2 * t2 * t2 * (9 * A3 + 11 * A4 * t2)
    x = lam * math.cos(theta) / (_WORTEL3_2 * afgeleide)
    return x, y


# Het kader is een eigenschap van de projectie, niet van de data: zo staat de kaart altijd gelijk.
_HOEKEN = [_equal_earth(lon, lat) for lon in (-180.0, 0.0, 180.0) for lat in (-90.0, 0.0, 90.0)]
X0 = min(x for x, _ in _HOEKEN)
BREEDTE = max(x for x, _ in _HOEKEN) - X0
Y1 = max(y for _, y in _HOEKEN)
HOOGTE = Y1 - min(y for _, y in _HOEKEN)


def projecteer(lon: float, lat: float) -> tuple[float, float]:
    """Graden → SVG-coördinaten: oorsprong linksboven, y naar beneden, kader (0,0)-(BREEDTE,HOOGTE)."""
    x, y = _equal_earth(lon, lat)
    return x - X0, Y1 - y


def vereenvoudig(punten: list[tuple[float, float]], tol: float) -> list[tuple[float, float]]:
    """Douglas-Peucker, iteratief (een ring kan duizenden punten hebben)."""
    if len(punten) < 3:
        return punten
    houden = [False] * len(punten)
    houden[0] = houden[-1] = True
    stapel = [(0, len(punten) - 1)]
    while stapel:
        begin, eind = stapel.pop()
        if eind <= begin + 1:
            continue
        (x1, y1), (x2, y2) = punten[begin], punten[eind]
        dx, dy = x2 - x1, y2 - y1
        lengte = math.hypot(dx, dy)
        verst, afstand = -1, -1.0
        for i in range(begin + 1, eind):
            x0, y0 = punten[i]
            d = abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / lengte if lengte else math.hypot(x0 - x1, y0 - y1)
            if d > afstand:
                verst, afstand = i, d
        if afstand > tol and verst > 0:
            houden[verst] = True
            stapel += [(begin, verst), (verst, eind)]
    return [p for p, h in zip(punten, houden) if h]


def ringen_van(geometrie: dict) -> list[list[tuple[float, float]]]:
    """Alle buitenringen van een (Multi)Polygon; gaten laten we weg (op deze schaal zijn ze onzichtbaar)."""
    soort, coords = geometrie.get("type"), geometrie.get("coordinates") or []
    stukken = [coords] if soort == "Polygon" else coords if soort == "MultiPolygon" else []
    return [[(float(x), float(y)) for x, y, *_ in ring] for stuk in stukken for ring in stuk[:1]]


def pad_van(geometrie: dict, tol: float, min_opp: float) -> str:
    """Eén SVG-pad (meerdere subpaden) voor een land, geprojecteerd en vereenvoudigd."""
    delen = []
    for ring in ringen_van(geometrie):
        punten = [projecteer(lon, lat) for lon, lat in ring]
        # Een ring die de datumlijn oversteekt wordt een streep over de hele kaart; die stukken laten we weg.
        if max(x for x, _ in punten) - min(x for x, _ in punten) > BREEDTE * 0.7:
            continue
        punten = vereenvoudig(punten, tol)
        if len(punten) < 3:
            continue
        opp = abs(sum(punten[i][0] * punten[i - 1][1] - punten[i - 1][0] * punten[i][1]
                      for i in range(len(punten)))) / 2
        if opp < min_opp:
            continue
        delen.append(punten)
    return " ".join(_subpad(p) for p in delen)


def _subpad(punten: list[tuple[float, float]]) -> str:
    uit = [f"M{punten[0][0]:.3f} {punten[0][1]:.3f}"]
    uit += [f"L{x:.3f} {y:.3f}" for x, y in punten[1:]]
    return "".join(uit) + "Z"


def haal(naam: str, map_: Path) -> dict:
    map_.mkdir(parents=True, exist_ok=True)
    bestand = map_ / f"{naam}.geojson"
    if not bestand.exists():
        print(f"ophalen {naam} …", file=sys.stderr)
        urllib.request.urlretrieve(BRON.format(naam=naam), bestand)  # noqa: S310 (vaste https-bron)
    return json.loads(bestand.read_text(encoding="utf-8"))


def _code(eigenschappen: dict) -> str | None:
    """De ISO-alpha-2 van een land; Natural Earth zet '-99' als er geen is."""
    for sleutel in ("ISO_A2_EH", "ISO_A2", "WB_A2"):
        code = (eigenschappen.get(sleutel) or "").strip().upper()
        if len(code) == 2 and code != "-9":
            return code
    return None


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="/tmp/natural-earth", help="map voor de gedownloade bronbestanden")
    p.add_argument("--uit", default="synoptikon/static/kaart/wereld.json")
    p.add_argument("--tol", type=float, default=0.004, help="vereenvoudiging in kaarteenheden")
    p.add_argument("--min-opp", type=float, default=0.00004, help="kleinste eiland dat nog meedoet")
    a = p.parse_args(argv)
    data = Path(a.data)

    landen: dict[str, str] = {}
    for f in haal(LANDEN, data)["features"]:
        code = _code(f.get("properties") or {})
        pad = pad_van(f.get("geometry") or {}, a.tol, a.min_opp)
        if code and pad:
            landen[code] = (landen.get(code, "") + " " + pad).strip()

    # Québec apart: CA en QC zijn twee stelsels op één landmassa.
    for f in haal(PROVINCIES, data)["features"]:
        e = f.get("properties") or {}
        if (e.get("iso_3166_2") or "") == "CA-QC":
            if pad := pad_van(f.get("geometry") or {}, a.tol, a.min_opp):
                landen["QC"] = pad

    # Uit de subunits: Engeland & Wales als één vorm ('EN'), en Hongkong, dat op 110m wegvalt.
    # Voor zulke kleine gebieden geen oppervlakte-ondergrens en een fijnere vereenvoudiging.
    uit_subunits: dict[str, tuple[str, ...]] = {"EN": ("ENG", "WLS"), "HK": ("HKG",)}
    stukken: dict[str, list[str]] = {}
    for f in haal(SUBUNITS, data)["features"]:
        su = (f.get("properties") or {}).get("SU_A3") or ""
        for code, wil in uit_subunits.items():
            if su in wil:
                if pad := pad_van(f.get("geometry") or {}, a.tol / 4, 0.0):
                    stukken.setdefault(code, []).append(pad)
    for code, delen in stukken.items():
        landen[code] = " ".join(delen)

    # De EU als de lidstaten samen: EU-recht geldt daar naast het nationale recht.
    if eu := [landen[c] for c in EU_LIDSTATEN if c in landen]:
        landen["EU"] = " ".join(eu)

    uit = dict(breedte=round(BREEDTE, 3), hoogte=round(HOOGTE, 3),
               bron="Natural Earth (publiek domein), projectie Equal Earth", landen=landen)
    doel = Path(a.uit)
    doel.parent.mkdir(parents=True, exist_ok=True)
    doel.write_text(json.dumps(uit, separators=(",", ":"), sort_keys=True) + "\n", encoding="utf-8")
    print(f"{doel}: {len(landen)} vormen, {doel.stat().st_size // 1024} kB, kader "
          f"{uit['breedte']}×{uit['hoogte']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
