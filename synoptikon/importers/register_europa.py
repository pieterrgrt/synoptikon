"""Register van de Europese stelsels die niet in het basisregister staan (regio "europa").

Per stelsel alleen de kern: grondwet, burgerlijk wetboek, handels- en consumentenrecht, burgerlijke
rechtsvordering, strafwetboek en IPR, voor zover er een open, machineleesbare bron is.

Bronnen per stelsel en waarom:

* AT: RIS (Bundeskanzleramt), geltende Fassung van de hele wet op één pagina, de URL die de OGD-API
  (data.bka.gv.at) zelf als `GesamteRechtsvorschriftUrl` geeft; geconsolideerd.
"""
from __future__ import annotations

from .register import Wet

WETTEN: list[Wet] = [
    # AT: ABGB en de wetten eromheen (RIS, Gesetzesnummer)
    Wet("AT", None, "ris", "10001622", "Allgemeines bürgerliches Gesetzbuch"),
    *[Wet("AT", afk, "ris", nr, t, systematiek=True) for afk, nr, t in [
        ("B-VG", "10000138", "Bundes-Verfassungsgesetz"),
        ("UGB", "10001702", "Unternehmensgesetzbuch"),
        ("KSchG", "10002462", "Konsumentenschutzgesetz"),
        ("ZPO", "10001699", "Zivilprozessordnung"),
        ("IPRG", "10002426", "Bundesgesetz über das internationale Privatrecht (IPR-Gesetz)"),
        ("StGB", "10002296", "Strafgesetzbuch"),
    ]],
]
