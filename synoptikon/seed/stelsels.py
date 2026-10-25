"""Stelsels, systematiekbomen en concordanties voor de voorbeeldinhoud."""

from .systematiek_au import AU
from .systematiek_be import BE, OUD_BW
from .systematiek_ch import CH
from .systematiek_de import BGB
from .systematiek_en import EN
from .systematiek_es import CC_ES
from .systematiek_fr import CC
from .systematiek_it import CC as CC_IT
from .systematiek_nl import BW
from .systematiek_us import US

# Seedcodes die niet meer bestaan (de handgeschreven BW-boom is vervangen door
# een uit de officiële XML gegenereerde). Een volgende `seed` verplaatst hun
# bronnen naar de knoop waar het artikelnummer nu valt en verwijdert ze.
VERVALLEN = ["BGB-4-1-6-3", "BW-3-11-1", "BW-3-11-2", "BW-7A-BRUIKLEEN", "BW-7A-MAATSCHAP", "BW-7A-VERBRUIKLEEN"]

# code, naam, taal, toelichting, actief, rechtsfamilie. De volgorde groepeert per
# rechtsfamilie (models.RECHTSFAMILIES); binnen een familie het moederstelsel eerst.
STELSELS = [
    ("NL", "Nederland", "nl", "Burgerlijk Wetboek (1992); Code civil-erfgoed met Duitse invloed in het NBW", True, "romaans"),
    ("BE", "België", "nl", "Burgerlijk Wetboek (2019, boek voor boek ingevoerd); voor de rest het oud BW (Code Napoléon 1804)", True, "romaans"),
    ("FR", "Frankrijk", "fr", "Code civil (1804; réforme du droit des contrats 2016/2018)", True, "romaans"),
    ("IT", "Italië", "it", "Codice civile (1942): één wetboek voor burgerlijk en handelsrecht", True, "romaans"),
    ("ES", "Spanje", "es", "Código Civil (1889), naast de forale burgerlijke rechten (Catalonië, Aragón, Navarra …)", True, "romaans"),
    ("DE", "Duitsland", "de", "Bürgerliches Gesetzbuch (1900; Schuldrechtsmodernisierung 2002)", True, "germaans"),
    ("CH", "Zwitserland", "de", "Zivilgesetzbuch (1907) en Obligationenrecht (1911): monistisch privaatrecht", True, "germaans"),
    ("EN", "Engeland & Wales", "en", "Common law en equity; statutes vullen aan (Sale of Goods Act 1979, Consumer Rights Act 2015)", True, "common_law"),
    ("US", "Verenigde Staten", "en", "Statelijk common law; UCC en Restatements als gemeenschappelijke kern; Louisiana gemengd", True, "common_law"),
    ("AU", "Australië", "en", "Common law (Engelse receptie); federale Australian Consumer Law, verder statelijk recht", True, "common_law"),
    ("EU", "Europese Unie", "en", "Primair en secundair Unierecht, HvJ EU; soft law (DCFR, PECL) als vergelijkingsmateriaal", True, "supranationaal"),
]

# Per stelsel: lijst van (code, label, bereik, kinderen[, wet]). Een knoop met
# een wet (en alles eronder) hoort bij die wet in plaats van bij de
# hoofdcodificatie: zo hebben het OR, de UCC en de Sale of Goods Act een eigen
# boom. De codificaties staan in eigen modules; de EU heeft geen codificatie
# en dus een indeling naar instrument.
SYSTEMATIEK = {
    "NL": BW,
    "BE": [*BE, *OUD_BW],
    "FR": CC,
    "IT": CC_IT,
    "ES": CC_ES,
    "DE": BGB,
    "CH": CH,
    "EN": EN,
    "US": US,
    "AU": AU,
    "EU": [
        ("EU-PRIM", "Primair recht", "", [
            ("EU-VWEU", "Verdrag betreffende de werking van de Europese Unie (VWEU)", "art. 1–358", [
                ("EU-VWEU-1", "Eerste deel · Beginselen", "art. 1–17", []),
                ("EU-VWEU-2", "Tweede deel · Non-discriminatie en burgerschap van de Unie", "art. 18–25", []),
                ("EU-VWEU-3", "Derde deel · Beleid en intern optreden van de Unie", "art. 26–197", []),
                ("EU-VWEU-4", "Vierde deel · Associatie van de landen en gebieden overzee", "art. 198–204", []),
                ("EU-VWEU-5", "Vijfde deel · Extern optreden van de Unie", "art. 205–222", []),
                ("EU-VWEU-6", "Zesde deel · Institutionele en financiële bepalingen", "art. 223–334", []),
                ("EU-VWEU-7", "Zevende deel · Algemene en slotbepalingen", "art. 335–358", []),
            ], "VWEU"),
            ("EU-HANDVEST", "Handvest van de grondrechten van de EU", "", [], "Handvest"),
        ]),
        ("EU-SEC", "Secundair recht", "", [
            ("EU-SEC-IPR", "Internationaal privaatrecht (Rome I, Rome II, Brussel I-bis)", "", [
                ("EU-ROME1", "Rome I · Verordening (EG) nr. 593/2008 (overeenkomsten)", "art. 1–29", [], "Rome I"),
                ("EU-ROME2", "Rome II · Verordening (EG) nr. 864/2007 (niet-contractuele verbintenissen)", "art. 1–32", [], "Rome II"),
                ("EU-BRUSSEL1BIS", "Brussel I-bis · Verordening (EU) nr. 1215/2012 (bevoegdheid en erkenning)", "art. 1–81", [], "Brussel I-bis"),
                ("EU-ERFRECHT", "Erfrechtverordening · Verordening (EU) nr. 650/2012", "art. 1–84", [], "Erfrechtverordening"),
                ("EU-INSOLV", "Insolventieverordening · Verordening (EU) 2015/848", "art. 1–92", [], "Insolventieverordening"),
            ]),
            ("EU-SEC-CONS", "Consumentenrecht en overeenkomstenrecht", "", [
                ("EU-RL85374", "Richtlijn 85/374/EEG · productaansprakelijkheid", "", [], "Richtlijn 85/374"),
                ("EU-RL9313", "Richtlijn 93/13/EEG · oneerlijke bedingen in consumentenovereenkomsten", "", [], "Richtlijn 93/13"),
                ("EU-RL201183", "Richtlijn 2011/83/EU · consumentenrechten", "", [], "Richtlijn 2011/83"),
                ("EU-RL20117", "Richtlijn 2011/7/EU · betalingsachterstand bij handelstransacties", "", [], "Richtlijn 2011/7"),
                ("EU-RL2019770", "Richtlijn (EU) 2019/770 · digitale inhoud en digitale diensten", "", [], "Richtlijn 2019/770"),
                ("EU-RL2019771", "Richtlijn (EU) 2019/771 · verkoop van goederen", "", [], "Richtlijn 2019/771"),
            ]),
        ]),
        ("EU-HVJ", "Rechtspraak HvJ EU", "", []),
        ("EU-SOFT", "Eenvormig recht en soft law · CISG, PECL, DCFR, UNIDROIT", "", [
            ("EU-CISG", "Weens Koopverdrag (CISG, 1980)", "art. 1–101", [
                ("EU-CISG-1", "Deel I · Toepassingsgebied en algemene bepalingen", "art. 1–13", []),
                ("EU-CISG-2", "Deel II · Totstandkoming van de overeenkomst", "art. 14–24", []),
                ("EU-CISG-3", "Deel III · Koop van roerende zaken", "art. 25–88", []),
                ("EU-CISG-4", "Deel IV · Slotbepalingen", "art. 89–101", []),
            ], "CISG"),
            ("EU-PECL", "Principles of European Contract Law (Lando-commissie)", "", [], "PECL"),
            ("EU-DCFR", "Draft Common Frame of Reference (2009)", "", [], "DCFR"),
            ("EU-PICC", "UNIDROIT Principles of International Commercial Contracts (2016)", "", [], "UNIDROIT PICC"),
        ]),
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
