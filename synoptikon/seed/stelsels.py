"""Stelsels, systematiekbomen en concordanties voor de voorbeeldinhoud."""

# code, naam, taal, toelichting, actief
STELSELS = [
    ("NL", "Nederland", "nl", "Burgerlijk Wetboek (1992)", True),
    ("DE", "Duitsland", "de", "Bürgerliches Gesetzbuch (1900; Schuldrechtsmodernisierung 2002)", True),
    ("FR", "Frankrijk", "fr", "Code civil (1804; réforme du droit des contrats 2016/2018)", True),
    ("EU", "Europese Unie", "en", "Primair en secundair Unierecht, HvJ EU; soft law (DCFR, PECL) als vergelijkingsmateriaal", True),
    ("IT", "Italië", "it", "Codice civile (1942)", False),
    ("EN", "Engeland & Wales", "en", "Common law, Sale of Goods Act 1979", False),
]

# Per stelsel: lijst van (code, label, bereik, kinderen)
SYSTEMATIEK = {
    "NL": [
        ("BW-3", "Boek 3 · Vermogensrecht in het algemeen", "art. 3:1–3:326", [
            ("BW-3-1", "Titel 1 · Algemene bepalingen", "art. 3:1–3:31", []),
            ("BW-3-2", "Titel 2 · Rechtshandelingen", "art. 3:32–3:59", []),
            ("BW-3-4", "Titel 4 · Verkrijging en verlies van goederen", "art. 3:80–3:106", [
                ("BW-3-4-1", "Afdeling 1 · Algemene bepalingen", "art. 3:80–3:82", []),
                ("BW-3-4-2", "Afdeling 2 · Overdracht van goederen en afstand van beperkte rechten", "art. 3:83–3:98", []),
                ("BW-3-4-3", "Afdeling 3 · Verkrijging en verlies door verjaring", "art. 3:99–3:106", []),
            ]),
            ("BW-3-5", "Titel 5 · Bezit en houderschap", "art. 3:107–3:125", []),
            ("BW-3-9", "Titel 9 · Rechten van pand en hypotheek", "art. 3:227–3:275", []),
        ]),
        ("BW-5", "Boek 5 · Zakelijke rechten", "art. 5:1–5:147", [
            ("BW-5-1", "Titel 1 · Eigendom in het algemeen", "art. 5:1–5:19", []),
            ("BW-5-2", "Titel 2 · Eigendom van roerende zaken", "art. 5:4–5:19", []),
        ]),
        ("BW-6", "Boek 6 · Algemeen gedeelte van het verbintenissenrecht", "art. 6:1–6:279", [
            ("BW-6-1", "Titel 1 · Verbintenissen in het algemeen", "art. 6:1–6:160", [
                ("BW-6-1-1", "Afdeling 1 · Algemene bepalingen", "art. 6:1–6:5", []),
                ("BW-6-1-10", "Afdeling 10 · Wettelijke verplichtingen tot schadevergoeding", "art. 6:95–6:110", []),
            ]),
            ("BW-6-3", "Titel 3 · Onrechtmatige daad", "art. 6:162–6:197", [
                ("BW-6-3-1", "Afdeling 1 · Algemene bepalingen", "art. 6:162–6:168", []),
            ]),
            ("BW-6-4", "Titel 4 · Verbintenissen uit andere bron dan onrechtmatige daad of overeenkomst", "art. 6:198–6:212", [
                ("BW-6-4-3", "Afdeling 3 · Ongerechtvaardigde verrijking", "art. 6:212", []),
            ]),
            ("BW-6-5", "Titel 5 · Overeenkomsten in het algemeen", "art. 6:213–6:279", [
                ("BW-6-5-2", "Afdeling 2 · Het tot stand komen van overeenkomsten", "art. 6:217–6:230", []),
                ("BW-6-5-4", "Afdeling 4 · Rechtsgevolgen van overeenkomsten", "art. 6:248–6:260", []),
            ]),
        ]),
        ("BW-7", "Boek 7 · Bijzondere overeenkomsten", "", [
            ("BW-7-1", "Titel 1 · Koop en ruil", "art. 7:1–7:50", []),
        ]),
    ],
    "DE": [
        ("BGB-1", "Buch 1 · Allgemeiner Teil", "§§ 1–240", [
            ("BGB-1-3", "Abschnitt 3 · Rechtsgeschäfte", "§§ 104–185", [
                ("BGB-1-3-3", "Titel 3 · Vertrag", "§§ 145–157", []),
            ]),
        ]),
        ("BGB-2", "Buch 2 · Recht der Schuldverhältnisse", "§§ 241–853", [
            ("BGB-2-1", "Abschnitt 1 · Inhalt der Schuldverhältnisse", "§§ 241–304", [
                ("BGB-2-1-1", "Titel 1 · Verpflichtung zur Leistung", "§§ 241–292", []),
            ]),
            ("BGB-2-3", "Abschnitt 3 · Schuldverhältnisse aus Verträgen", "§§ 311–361", [
                ("BGB-2-3-1", "Titel 1 · Begründung, Inhalt und Beendigung", "§§ 311–319", []),
            ]),
            ("BGB-2-8", "Abschnitt 8 · Einzelne Schuldverhältnisse", "§§ 433–853", [
                ("BGB-2-8-1", "Titel 1 · Kauf, Tausch", "§§ 433–480", []),
                ("BGB-2-8-26", "Titel 26 · Ungerechtfertigte Bereicherung", "§§ 812–822", []),
                ("BGB-2-8-27", "Titel 27 · Unerlaubte Handlungen", "§§ 823–853", []),
            ]),
        ]),
        ("BGB-3", "Buch 3 · Sachenrecht", "§§ 854–1296", [
            ("BGB-3-1", "Abschnitt 1 · Besitz", "§§ 854–872", []),
            ("BGB-3-3", "Abschnitt 3 · Eigentum", "§§ 903–1011", [
                ("BGB-3-3-1", "Titel 1 · Inhalt des Eigentums", "§§ 903–924", []),
                ("BGB-3-3-3", "Titel 3 · Erwerb und Verlust des Eigentums an beweglichen Sachen", "§§ 929–984", [
                    ("BGB-3-3-3-1", "Untertitel 1 · Übertragung", "§§ 929–936", []),
                    ("BGB-3-3-3-2", "Untertitel 2 · Ersitzung", "§§ 937–945", []),
                ]),
                ("BGB-3-3-4", "Titel 4 · Ansprüche aus dem Eigentum", "§§ 985–1007", []),
            ]),
        ]),
    ],
    "FR": [
        ("CC-II", "Livre II · Des biens et des différentes modifications de la propriété", "art. 516–710-1", [
            ("CC-II-II", "Titre II · De la propriété", "art. 544–577", []),
        ]),
        ("CC-III", "Livre III · Des différentes manières dont on acquiert la propriété", "art. 711–2278", [
            ("CC-III-III", "Titre III · Des sources d'obligations", "art. 1100–1303-4", [
                ("CC-III-III-I", "Sous-titre Ier · Le contrat", "art. 1101–1231-7", [
                    ("CC-III-III-I-1", "Chapitre Ier · Dispositions liminaires", "art. 1101–1111-1", []),
                    ("CC-III-III-I-2", "Chapitre II · La formation du contrat", "art. 1112–1187", [
                        ("CC-III-III-I-2-1", "Section 1 · La conclusion du contrat", "art. 1112–1127-6", [
                            ("CC-III-III-I-2-1-1", "Sous-section 1 · Les négociations", "art. 1112–1112-2", []),
                        ]),
                    ]),
                    ("CC-III-III-I-4", "Chapitre IV · Les effets du contrat", "art. 1193–1231-7", [
                        ("CC-III-III-I-4-1", "Section 1 · Les effets du contrat entre les parties", "art. 1193–1198", [
                            ("CC-III-III-I-4-1-2", "Sous-section 2 · L'effet translatif", "art. 1196–1198", []),
                        ]),
                    ]),
                ]),
                ("CC-III-III-II", "Sous-titre II · La responsabilité extracontractuelle", "art. 1240–1252", []),
            ]),
            ("CC-III-VI", "Titre VI · De la vente", "art. 1582–1701-1", [
                ("CC-III-VI-I", "Chapitre Ier · De la nature et de la forme de la vente", "art. 1582–1593", []),
                ("CC-III-VI-IV", "Chapitre IV · Des obligations du vendeur", "art. 1602–1649", []),
            ]),
            ("CC-III-XX", "Titre XX · De la prescription extinctive", "art. 2219–2254", []),
            ("CC-III-XXI", "Titre XXI · De la possession et de la prescription acquisitive", "art. 2255–2278", [
                ("CC-III-XXI-III", "Chapitre III · De la prescription acquisitive", "art. 2258–2277", [
                    ("CC-III-XXI-III-3", "Section 3 · De la prescription acquisitive en matière mobilière", "art. 2276–2277", []),
                ]),
            ]),
        ]),
    ],
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
