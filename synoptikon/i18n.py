"""Talen: de interface in zes talen en vertaalde inhoud.

Twee lagen, bewust gescheiden:

* **Interface** (`_`): vaste teksten uit templates, routes en services. De
  Nederlandse tekst is de sleutel (zoals bij gettext); de vertalingen staan
  per taal in `i18n/<taal>.json`. Ontbreekt een vertaling, dan blijft het
  Nederlands staan. `tests/test_i18n.py` controleert dat elke `_()`-tekst in
  alle talen bestaat.

* **Rechtstaal** (`rechtstaal`): de taal waarin juridische inhoud geleverd wordt —
  welke taalversie van een verdrag, welke afkorting (VWEU of AEUV), en de taal van
  de kaartzijden. Staat los van de interface: wie in Berlijn recht studeert wil de
  Duitse verdragstekst met een Nederlandse interface. Leeg = volg de interface.

* **Inhoud** (`vt`): vragen, analyses, definities, toelichtingen, thema's.
  Die worden in het Nederlands ingevoerd. Vertalingen staan in het
  vertaalgeheugen (`InhoudVertaling`), met als sleutel de hash van de
  Nederlandse tekst. Wijzigt de bron, dan past de hash niet meer en valt de
  weergave terug op het Nederlands: een verouderde vertaling verschijnt nooit
  stilzwijgend. Wetteksten, termen en citeertitels worden nooit vertaald.

De taal van het verzoek staat in een ContextVar, gezet door de middleware
(profiel → cookie → Accept-Language), zodat ook services en
modeleigenschappen zonder request-object vertalen.
"""
from __future__ import annotations

import hashlib
import json
import time
from contextlib import contextmanager
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path

TALEN: dict[str, str] = {
    "nl": "Nederlands",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
    "en": "English",
    "es": "Español",
}
BRONTAAL = "nl"
_HIER = Path(__file__).parent / "i18n"

_taal: ContextVar[str] = ContextVar("taal", default=BRONTAAL)
_origineel: ContextVar[bool] = ContextVar("origineel", default=False)
_rechtstaal: ContextVar[str] = ContextVar("rechtstaal", default="")


def zet_taal(taal: str | None, origineel: bool = False) -> None:
    _taal.set(taal if taal in TALEN else BRONTAAL)
    _origineel.set(origineel)


def taal() -> str:
    return _taal.get()


def toont_origineel() -> bool:
    return _origineel.get()


def zet_rechtstaal(code: str | None) -> None:
    """De taal voor juridische inhoud; leeg of onbekend = volg de interfacetaal."""
    _rechtstaal.set(code if code in TALEN else "")


def rechtstaal() -> str:
    """De taal waarin wetteksten, afkortingen en kaarten geleverd worden."""
    return _rechtstaal.get() or _taal.get()


def eigen_rechtstaal() -> str:
    """De ingestelde rechtstaal zelf, zonder terugval: leeg als ze de interface volgt."""
    return _rechtstaal.get()


@contextmanager
def in_taal(code: str | None):
    """Tijdelijk een andere interfacetaal, om een tekst in de rechtstaal op te bouwen (kaartzijden)."""
    vorige = _taal.get()
    _taal.set(code if code in TALEN else vorige)
    try:
        yield
    finally:
        _taal.set(vorige)


def kies_taal(accept_language: str | None) -> str:
    """Eerste ondersteunde taal uit een Accept-Language-kop."""
    kandidaten = []
    for deel in (accept_language or "").split(","):
        code, _, q = deel.strip().partition(";q=")
        try:
            gewicht = float(q) if q else 1.0
        except ValueError:
            gewicht = 0.0
        kandidaten.append((gewicht, code.split("-")[0].lower()))
    for _gewicht, code in sorted(kandidaten, key=lambda x: -x[0]):
        if code in TALEN:
            return code
    return BRONTAAL


@lru_cache(maxsize=None)
def catalogus(t: str) -> dict[str, str]:
    pad = _HIER / f"{t}.json"
    return json.loads(pad.read_text(encoding="utf-8")) if pad.exists() else {}


def _(tekst: str, **waarden) -> str:
    """Interfacetekst in de taal van het verzoek; `waarden` vullen {plaatshouders} in."""
    t = taal()
    uit = tekst if t == BRONTAAL else (catalogus(t).get(tekst) or tekst)
    return uit.format(**waarden) if waarden else uit


def n_(enkel: str, meer: str, aantal: int, **waarden) -> str:
    """Enkelvoud of meervoud; {n} is het aantal, tenzij `waarden` een opgemaakte n meegeeft."""
    waarden.setdefault("n", aantal)
    return _(enkel if aantal == 1 else meer, **waarden)


# ---------------------------------------------------------------- inhoud

def sleutel(tekst: str) -> str:
    """Hash van een Nederlandse brontekst, ongevoelig voor regeleinden en witruimte aan de randen."""
    return hashlib.sha1(tekst.replace("\r\n", "\n").strip().encode("utf-8")).hexdigest()


class _Geheugen:
    """Vertaalgeheugen in het werkgeheugen: {(hash, taal): tekst}.

    Een paar duizend korte teksten; opnieuw laden na een eigen schrijfactie
    of na een minuut (voor wijzigingen uit de CLI in een ander proces).
    """

    def __init__(self) -> None:
        self.data: dict[tuple[str, str], str] = {}
        self.geladen = 0.0

    def ongeldig(self) -> None:
        self.geladen = 0.0

    def get(self, h: str, t: str) -> str | None:
        if time.monotonic() - self.geladen > 60:
            self._laad()
        return self.data.get((h, t))

    def _laad(self) -> None:
        from sqlalchemy import select

        from .db import session_factory
        from .models import InhoudVertaling

        with session_factory()() as s:
            self.data = {(v.hash, v.taal): v.tekst for v in s.scalars(select(InhoudVertaling))}
        self.geladen = time.monotonic()


geheugen = _Geheugen()


def vt(tekst: str | None) -> str | None:
    """Inhoud in de taal van het verzoek, of de Nederlandse tekst als er (nog) geen geldige vertaling is."""
    t = taal()
    if not tekst or t == BRONTAAL or toont_origineel():
        return tekst
    return geheugen.get(sleutel(tekst), t) or tekst


def is_vertaald(tekst: str | None) -> bool:
    t = taal()
    return bool(tekst) and t != BRONTAAL and geheugen.get(sleutel(tekst), t) is not None
