"""Stelsels, systematiekbomen en concordanties voor de voorbeeldinhoud."""

from .systematiek_de import BGB
from .systematiek_fr import CC
from .systematiek_nl import BW

# Seedcodes die niet meer bestaan (de handgeschreven BW-boom is vervangen door
# een uit de officiële XML gegenereerde). Een volgende `seed` verplaatst hun
# bronnen naar de knoop waar het artikelnummer nu valt en verwijdert ze.
VERVALLEN = ["BW-3-11-1", "BW-3-11-2", "BW-7A-BRUIKLEEN", "BW-7A-MAATSCHAP", "BW-7A-VERBRUIKLEEN"]

# code, naam, taal, toelichting, actief
STELSELS = [
    ("NL", "Nederland", "nl", "Burgerlijk Wetboek (1992)", True),
    ("DE", "Duitsland", "de", "Bürgerliches Gesetzbuch (1900; Schuldrechtsmodernisierung 2002)", True),
    ("FR", "Frankrijk", "fr", "Code civil (1804; réforme du droit des contrats 2016/2018)", True),
    ("EU", "Europese Unie", "en", "Primair en secundair Unierecht, HvJ EU; soft law (DCFR, PECL) als vergelijkingsmateriaal", True),
    ("IT", "Italië", "it", "Codice civile (1942)", False),
    ("EN", "Engeland & Wales", "en", "Common law, Sale of Goods Act 1979", False),
]

# Per stelsel: lijst van (code, label, bereik, kinderen). NL, DE en FR staan
# in eigen modules; de EU heeft geen codificatie en dus een eigen indeling.
SYSTEMATIEK = {
    "NL": BW,
    "DE": BGB,
    "FR": CC,
    "EU": [
        ("EU-PRIM", "Primair recht", "", [
            ("EU-VWEU", "VWEU", "", []),
        ]),
        ("EU-SEC", "Secundair recht", "", [
            ("EU-SEC-IPR", "Internationaal privaatrecht (Rome I, Rome II, Brussel I-bis)", "", []),
            ("EU-SEC-CONS", "Consumentenrecht", "", []),
        ]),
        ("EU-HVJ", "Rechtspraak HvJ EU", "", []),
        ("EU-SOFT", "Soft law · DCFR, PECL, UNIDROIT", "", []),
    ],
}

# stelsel, wet, oud, nieuw, datum, grond, toelichting
CONCORDANTIES = [
    ("FR", "C. civ.", "art. 1138", "art. 1196", "2016-10-01", "Ordonnance n° 2016-131 du 10 février 2016", "Transfert solo consensu; oud 1138 sprak van 'obligation de livrer'."),
    ("FR", "C. civ.", "art. 1141", "art. 1198", "2016-10-01", "Ordonnance n° 2016-131 du 10 février 2016", "Conflit entre acquéreurs successifs d'un meuble."),
    ("FR", "C. civ.", "art. 1134", "art. 1103, 1104, 1193", "2016-10-01", "Ordonnance n° 2016-131 du 10 février 2016", "Force obligatoire (1103), bonne foi (1104), mutabilité (1193)."),
    ("FR", "C. civ.", "art. 1382", "art. 1240", "2016-10-01", "Ordonnance n° 2016-131 du 10 février 2016", "Hernummering zonder inhoudelijke wijziging."),
    ("FR", "C. civ.", "art. 1383", "art. 1241", "2016-10-01", "Ordonnance n° 2016-131 du 10 février 2016", None),
    ("FR", "C. civ.", "art. 2279", "art. 2276", "2008-06-19", "Loi n° 2008-561 du 17 juin 2008 portant réforme de la prescription", "'En fait de meubles, la possession vaut titre' verhuisde van 2279 naar 2276."),
    ("FR", "C. civ.", "art. 1112 (versie 2016)", "art. 1112 (versie 2018)", "2018-10-01", "Loi n° 2018-287 du 20 avril 2018 de ratification", "Toevoeging: 'ni la perte de chance d'obtenir ces avantages' (codificatie Manoukian)."),
    ("NL", "BW", "art. 639 BW (oud)", "art. 3:84 BW", "1992-01-01", "Invoering Nieuw BW (Boeken 3, 5, 6)", "Vereisten voor overdracht; 'levering krachtens geldige titel door een beschikkingsbevoegde'."),
    ("NL", "BW", "art. 2014 BW (oud)", "art. 3:86 BW", "1992-01-01", "Invoering Nieuw BW", "'Bezit geldt als volkomen titel' → bescherming verkrijger te goeder trouw om baat."),
    ("NL", "BW", "art. 1401 BW (oud)", "art. 6:162 BW", "1992-01-01", "Invoering Nieuw BW", "Onrechtmatige daad; codificatie Lindenbaum/Cohen-formule."),
    ("NL", "BW", "art. 1374 lid 3 BW (oud)", "art. 6:248 BW", "1992-01-01", "Invoering Nieuw BW", "Goede trouw bij uitvoering → redelijkheid en billijkheid (aanvullend en derogerend)."),
    ("DE", "BGB", "§ 242 (c.i.c. ongeschreven)", "§ 311 Abs. 2, § 241 Abs. 2", "2002-01-01", "Gesetz zur Modernisierung des Schuldrechts (BGBl. I 2001, 3138)", "Culpa in contrahendo gecodificeerd; voorheen gewoonterecht op basis van RGZ 78, 239."),
    ("DE", "BGB", "§ 276 a.F. (positive Vertragsverletzung)", "§ 280 Abs. 1", "2002-01-01", "Schuldrechtsmodernisierung", "Eenheidstatbestand Pflichtverletzung."),
]
