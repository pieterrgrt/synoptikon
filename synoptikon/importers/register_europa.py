"""Register van de Europese stelsels die niet in het basisregister staan (regio "europa").

Per stelsel alleen de kern: grondwet, burgerlijk wetboek, handels- en consumentenrecht, burgerlijke
rechtsvordering, strafwetboek en IPR, voor zover er een open, machineleesbare bron is.

Bronnen per stelsel en waarom:

* AT: RIS (Bundeskanzleramt), geltende Fassung van de hele wet op één pagina, de URL die de OGD-API
  (data.bka.gv.at) zelf als `GesamteRechtsvorschriftUrl` geeft; geconsolideerd.
* DK: Retsinformation, LexDania-XML via ELI. Geconsolideerd per lovbekendtgørelse (LBK): het register wijst
  naar de laatste LBK; wijzigingswetten van daarna zijn pas verwerkt in de volgende LBK, en dan moet de id
  hier mee. Denemarken heeft geen burgerlijk wetboek (Danske Lov 1683 geldt nog in enkele artikelen); het
  vermogensrecht staat in losse wetten, dus geen hoofdwet.
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
    # DK: de wetten die het vermogensrecht dragen (Retsinformation, ELI van de laatste LBK)
    *[Wet("DK", afk, "retsinformation", eli, t, systematiek=True) for afk, eli, t in [
        ("grl.", "lta/1953/169", "Danmarks Riges Grundlov"),
        ("aftl.", "lta/2016/193", "Aftaleloven (lov om aftaler og andre retshandler på formuerettens område)"),
        ("kbl.", "lta/2021/1853", "Købeloven (lov om køb)"),
        ("forbrugeraftalel.", "lta/2025/1184", "Forbrugeraftaleloven (lov om forbrugeraftaler)"),
        ("EAL", "lta/2025/1080", "Erstatningsansvarsloven (lov om erstatningsansvar)"),
        ("forældelsesl.", "lta/2015/1238", "Forældelsesloven (lov om forældelse af fordringer)"),
        ("selskabsl.", "lta/2025/331", "Selskabsloven (lov om aktie- og anpartsselskaber)"),
        ("rpl.", "lta/2025/1298", "Retsplejeloven (lov om rettens pleje)"),
        ("strfl.", "lta/2025/1294", "Straffeloven"),
    ]],
]
