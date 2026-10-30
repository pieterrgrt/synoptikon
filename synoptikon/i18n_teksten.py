"""Alle interfaceteksten die vertaald moeten worden, rechtstreeks uit de code gehaald.

* Templates: elke aanroep `_('…')` en `n_('…', '…', n)` met letterlijke tekst
  (via de Jinja-parser, dus ook in macro's en filters).
* Python: hetzelfde voor `_`, `n_` en `vertaal` (via de AST, dus ook
  aaneengeschakelde regels).
* Waarden die pas bij het tonen door `_()` gaan: labels uit de modellen
  (rechtsfamilies, relatietypen, EU-soorten, rollen …) en de regels van
  de Europese rechtslogica.

`python -m synoptikon.i18n_teksten` toont wat in een catalogus ontbreekt;
`tests/test_i18n.py` eist dat alles in alle talen vertaald is.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

from jinja2 import Environment, nodes

HIER = Path(__file__).parent
_FUNCTIES = {"_", "n_", "vertaal"}


def _uit_templates() -> set[str]:
    env = Environment()
    uit: set[str] = set()
    for pad in sorted((HIER / "templates").glob("*.html")):
        boom = env.parse(pad.read_text(encoding="utf-8"))
        for call in boom.find_all(nodes.Call):
            if isinstance(call.node, nodes.Name) and call.node.name in _FUNCTIES:
                aantal = 2 if call.node.name == "n_" else 1
                for arg in call.args[:aantal]:
                    if isinstance(arg, nodes.Const) and isinstance(arg.value, str):
                        uit.add(arg.value)
    return uit


def _uit_python() -> set[str]:
    uit: set[str] = set()
    for pad in sorted(HIER.rglob("*.py")):
        if pad.name == "i18n_teksten.py":
            continue
        boom = ast.parse(pad.read_text(encoding="utf-8"))
        for knoop in ast.walk(boom):
            if isinstance(knoop, ast.Call) and isinstance(knoop.func, ast.Name) and knoop.func.id in _FUNCTIES:
                aantal = 2 if knoop.func.id == "n_" else 1
                for arg in knoop.args[:aantal]:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        uit.add(arg.value)
    return uit


def _uit_gegevens() -> set[str]:
    from .models import EU_SOORTEN, EU_VARIANTEN, FASEN, KAARTSOORTEN, MARKERINGSOORTEN, OMZETTING_SOORTEN, RECHTSFAMILIES, RELATIE_TYPES, ROLLEN, ZICHTBAAR
    from .routes.bronnen import SOORTEN
    from .services.eu_logica import HARMONISATIE, VARIANT, WERKING

    uit: set[str] = {"Overig", "Nog niet ingedeeld bij een rechtsfamilie"}
    for naam, kenmerk in RECHTSFAMILIES.values():
        uit |= {naam, kenmerk}
    uit |= set(RELATIE_TYPES.values()) | set(EU_VARIANTEN.values()) | set(OMZETTING_SOORTEN.values()) | set(ROLLEN.values())
    uit |= set(ZICHTBAAR.values()) | set(MARKERINGSOORTEN.values())
    uit |= {t for paar in KAARTSOORTEN.values() for t in paar} | set(FASEN.values())
    uit |= {w for paar in EU_SOORTEN.values() for w in paar}
    uit |= set(SOORTEN.values()) | set(SOORTEN)  # ook de sleutels: de systematiek toont b.soort
    uit |= {"eigen", "officieel", "literatuur"}  # herkomst van een bronvertaling
    from .routes.begrippen import KAART_TEKSTEN
    from .seed.regios import REGIOS

    uit |= set(REGIOS.values())

    uit |= set(KAART_TEKSTEN)
    for niveau, grond in HARMONISATIE.values():
        uit |= {niveau, grond}
    uit |= {r.tekst for regels in WERKING.values() for r in regels} | {r.tekst for r in VARIANT.values()}
    # Soorten in het vertaaloverzicht (services/vertalen.py).
    uit |= {"stelsel", "vraag", "rechtsgebied", "tag", "omschrijving", "notitie", "kern", "analyse", "rol",
            "annotatie", "opmerking", "definitie", "relatie", "thema", "omzetting", "concordantie"}
    return uit


def alle() -> set[str]:
    return {t for t in _uit_templates() | _uit_python() | _uit_gegevens() if t.strip()}


def ontbrekend(taal: str) -> list[str]:
    from .i18n import catalogus

    cat = catalogus(taal)
    return sorted(t for t in alle() if not cat.get(t))


if __name__ == "__main__":
    import json

    talen = sys.argv[1:] or ["fr", "de", "it", "en", "es"]
    for t in talen:
        m = ontbrekend(t)
        print(f"{t}: {len(m)} ontbrekend", file=sys.stderr)
    if len(talen) == 1:
        print(json.dumps({t: "" for t in ontbrekend(talen[0])}, ensure_ascii=False, indent=1))
