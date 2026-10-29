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
* FI: Finlex open data (opendata.finlex.fi, Oikeusministeriö), Akoma Ntoso, geconsolideerd (*ajantasa*);
  vrij herbruikbaar (CC BY 4.0). Ook Finland heeft geen burgerlijk wetboek. De oude *kaaret* uit het Zweedse
  Rijkswetboek van 1734 en de rikoslaki hebben een id met achtervoegsel ("1734/4-000", "1889/39-001").
* NO: Lovdata, de gratis dataset "Gjeldende lover" (api.lovdata.no, NLOD 2.0): één tar.bz2 van ±6 MB met
  alle geldende wetten als XHTML, bijgewerkt; geconsolideerd. De pagina's op lovdata.no zelf niet (daar is
  automatisch ophalen niet de bedoeling). Geen burgerlijk wetboek; Christian V's Norske Lov (1687) geldt nog
  in enkele artikelen en is niet opgenomen.
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
    # FI: de wetten die het vermogensrecht dragen (Finlex, jaar/nummer van de oorspronkelijke wet)
    *[Wet("FI", afk, "finlex", id, t, systematiek=True) for afk, id, t in [
        ("PL", "1999/731", "Suomen perustuslaki"),
        ("OikTL", "1929/228", "Oikeustoimilaki (laki varallisuusoikeudellisista oikeustoimista)"),
        ("KL", "1987/355", "Kauppalaki"),
        ("KSL", "1978/38", "Kuluttajansuojalaki"),
        ("VahL", "1974/412", "Vahingonkorvauslaki"),
        ("VanhL", "2003/728", "Laki velan vanhentumisesta"),
        ("OYL", "2006/624", "Osakeyhtiölaki"),
        ("OK", "1734/4-000", "Oikeudenkäymiskaari"),
        ("RL", "1889/39-001", "Rikoslaki"),
    ]],
    # NO: de wetten die het vermogensrecht dragen (Lovdata, datumcode van de wet)
    *[Wet("NO", afk, "lovdata", id, t, systematiek=True) for afk, id, t in [
        ("Grl.", "1814-05-17-0", "Kongeriket Norges Grunnlov"),
        ("avtl.", "1918-05-31-4", "Avtaleloven (lov om avslutning av avtaler, om fuldmagt og om ugyldige viljeserklæringer)"),
        ("kjl.", "1988-05-13-27", "Kjøpsloven (lov om kjøp)"),
        ("fkjl.", "2002-06-21-34", "Forbrukerkjøpsloven (lov om forbrukerkjøp)"),
        ("skl.", "1969-06-13-26", "Skadeserstatningsloven (lov om skadeserstatning)"),
        ("foreldelsesl.", "1979-05-18-18", "Foreldelsesloven (lov om foreldelse av fordringer)"),
        ("asl.", "1997-06-13-44", "Aksjeloven (lov om aksjeselskaper)"),
        ("tvl.", "2005-06-17-90", "Tvisteloven (lov om mekling og rettergang i sivile tvister)"),
        ("strl.", "2005-05-20-28", "Straffeloven (lov om straff)"),
    ]],
]
