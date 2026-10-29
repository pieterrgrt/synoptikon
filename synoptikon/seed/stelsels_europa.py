"""Stelsels en systematiek van de Europese stelsels buiten het basisregister (regio "europa").

De bomen geven de hoofdindeling van het burgerlijk wetboek (of wat het privaatrecht draagt) met
artikelbereiken: eerste en laatste paragraaf of artikel per eenheid. Waar ze uit de import zijn gegenereerd
staat dat erbij; de labels zijn ingekort en in de hedendaagse spelling gezet waar de officiële kop nog
de spelling van 1811 heeft ("Zweyter Theil").
"""

# AT: ABGB (gegenereerd uit RIS, stand BGBl. I Nr. 62/2026). Teil › Abteilung › Hauptstück.
AT = [
    ("ABGB", "Allgemeines bürgerliches Gesetzbuch (ABGB, JGS Nr. 946/1811)", "§§ 1–1503", [
        ("ABGB-0", "Einleitung · Von den bürgerlichen Gesetzen überhaupt", "§§ 1–14", []),
        ("ABGB-1", "Erster Teil · Von dem Personenrechte", "§§ 15–284", [
            ("ABGB-1-1", "1. Hauptstück · Rechte, die sich auf persönliche Eigenschaften und Verhältnisse beziehen", "§§ 15–43", []),
            ("ABGB-1-2", "2. Hauptstück · Von dem Eherechte", "§§ 44–100", []),
            ("ABGB-1-3", "3. Hauptstück · Rechte zwischen Eltern und Kindern", "§§ 137–203", []),
            ("ABGB-1-4", "4. Hauptstück · Von der Obsorge einer anderen Person", "§§ 204–230", []),
            ("ABGB-1-5", "5. Hauptstück · Kindesunterhalt", "§§ 231–235", []),
            ("ABGB-1-6", "6. Hauptstück · Vorsorgevollmacht und Erwachsenenvertretung", "§§ 239–276", []),
            ("ABGB-1-7", "7. Hauptstück · Von der Kuratel", "§§ 277–284", []),
        ]),
        ("ABGB-2", "Zweiter Teil · Von dem Sachenrechte", "§§ 285–1341", [
            ("ABGB-2-0", "Von Sachen und ihrer rechtlichen Einteilung", "§§ 285–308", []),
            ("ABGB-2-1", "Erste Abteilung · Von den dinglichen Rechten", "§§ 309–858", [
                ("ABGB-2-1-1", "1. Hauptstück · Von dem Besitze", "§§ 309–352", []),
                ("ABGB-2-1-2", "2. Hauptstück · Von dem Eigentumsrechte", "§§ 353–379", []),
                ("ABGB-2-1-3", "3. Hauptstück · Erwerbung des Eigentums durch Zueignung", "§§ 380–403", []),
                ("ABGB-2-1-4", "4. Hauptstück · Erwerbung des Eigentums durch Zuwachs", "§§ 404–422", []),
                ("ABGB-2-1-5", "5. Hauptstück · Erwerbung des Eigentums durch Übergabe", "§§ 423–446", []),
                ("ABGB-2-1-6", "6. Hauptstück · Von dem Pfandrechte", "§§ 447–471", []),
                ("ABGB-2-1-7", "7. Hauptstück · Von Dienstbarkeiten (Servituten)", "§§ 472–530", []),
                ("ABGB-2-1-8", "8. Hauptstück · Vom Erbrecht allgemein", "§§ 531–551", []),
                ("ABGB-2-1-9", "9. Hauptstück · Gewillkürte Erbfolge", "§§ 552–603", []),
                ("ABGB-2-1-10", "10. Hauptstück · Ersatz- und Nacherbschaft", "§§ 604–617", []),
                ("ABGB-2-1-11", "11. Hauptstück · Vermächtnisse", "§§ 647–694", []),
                ("ABGB-2-1-12", "12. Hauptstück · Einschränkung und Aufhebung des letzten Willens", "§§ 695–726", []),
                ("ABGB-2-1-13", "13. Hauptstück · Gesetzliche Erbfolge", "§§ 727–755", []),
                ("ABGB-2-1-14", "14. Hauptstück · Pflichtteil und Anrechnung auf den Pflichtteil", "§§ 756–792", []),
                ("ABGB-2-1-15", "15. Hauptstück · Erwerb einer Erbschaft", "§§ 797–824", []),
                ("ABGB-2-1-16", "16. Hauptstück · Gemeinschaft des Eigentums und anderer dinglicher Rechte", "§§ 825–858", []),
            ]),
            ("ABGB-2-2", "Zweite Abteilung · Von den persönlichen Sachenrechten", "§§ 859–1341", [
                ("ABGB-2-2-17", "17. Hauptstück · Von Verträgen und Rechtsgeschäften überhaupt", "§§ 859–937", []),
                ("ABGB-2-2-18", "18. Hauptstück · Von Schenkungen", "§§ 938–956", []),
                ("ABGB-2-2-19", "19. Hauptstück · Verwahrungsvertrag", "§§ 957–970c", []),
                ("ABGB-2-2-20", "20. Hauptstück · Leihvertrag", "§§ 971–982", []),
                ("ABGB-2-2-21", "21. Hauptstück · Darlehensvertrag", "§§ 983–1001", []),
                ("ABGB-2-2-22", "22. Hauptstück · Bevollmächtigung und andere Arten der Geschäftsführung", "§§ 1002–1044", []),
                ("ABGB-2-2-23", "23. Hauptstück · Tauschvertrag", "§§ 1045–1052", []),
                ("ABGB-2-2-24", "24. Hauptstück · Kaufvertrag", "§§ 1053–1089", []),
                ("ABGB-2-2-25", "25. Hauptstück · Bestand-, Erbpacht- und Erbzinsverträge", "§§ 1090–1150", []),
                ("ABGB-2-2-26", "26. Hauptstück · Verträge über Dienstleistungen", "§§ 1151–1174", []),
                ("ABGB-2-2-27", "27. Hauptstück · Gesellschaft bürgerlichen Rechts", "§§ 1175–1216e", []),
                ("ABGB-2-2-28", "28. Hauptstück · Ehepakte und Anspruch auf Ausstattung", "§§ 1217–1266", []),
                ("ABGB-2-2-29", "29. Hauptstück · Glücksverträge", "§§ 1267–1292", []),
                ("ABGB-2-2-30", "30. Hauptstück · Schadenersatz und Genugtuung", "§§ 1293–1341", []),
            ]),
        ]),
        ("ABGB-3", "Dritter Teil · Gemeinschaftliche Bestimmungen der Personen- und Sachenrechte", "§§ 1342–1503", [
            ("ABGB-3-1", "1. Hauptstück · Befestigung der Rechte und Verbindlichkeiten", "§§ 1342–1374", []),
            ("ABGB-3-2", "2. Hauptstück · Umänderung der Rechte und Verbindlichkeiten", "§§ 1375–1410", []),
            ("ABGB-3-3", "3. Hauptstück · Aufhebung der Rechte und Verbindlichkeiten", "§§ 1411–1450", []),
            ("ABGB-3-4", "4. Hauptstück · Verjährung und Ersitzung", "§§ 1451–1502", []),
            ("ABGB-3-5", "5. Hauptstück · Inkrafttreten und Übergangsbestimmungen", "§ 1503", []),
        ]),
    ]),
]

# DK: geen burgerlijk wetboek; de vermogensrechtelijke wetten per rubriek (eigen indeling), de hoofdstukken komen
# uit de import (`systematiek=True` in het register).
DK = [
    ("DK-FORMUE", "Formueret (aftaler, køb, erstatning)", "", [
        ("DK-AFTL", "Aftaleloven (LBK nr 193 af 2016)", "", [], "aftl."),
        ("DK-KBL", "Købeloven (LBK nr 1853 af 2021)", "", [], "kbl."),
        ("DK-FAL", "Forbrugeraftaleloven (LBK nr 1184 af 2025)", "", [], "forbrugeraftalel."),
        ("DK-EAL", "Erstatningsansvarsloven (LBK nr 1080 af 2025)", "", [], "EAL"),
        ("DK-FORLDL", "Forældelsesloven (LBK nr 1238 af 2015)", "", [], "forældelsesl."),
    ]),
    ("DK-SELSKAB", "Selskabsret", "", [
        ("DK-SL", "Selskabsloven (LBK nr 331 af 2025)", "", [], "selskabsl."),
    ]),
    ("DK-PROCES", "Retspleje", "", [
        ("DK-RPL", "Retsplejeloven (LBK nr 1298 af 2025)", "", [], "rpl."),
    ]),
    ("DK-OFF", "Forfatning og strafferet", "", [
        ("DK-GRL", "Danmarks Riges Grundlov (1953)", "§§ 1–89", [], "grl."),
        ("DK-STRFL", "Straffeloven (LBK nr 1294 af 2025)", "", [], "strfl."),
    ]),
]

# FI: geen burgerlijk wetboek; zelfde opzet als DK, de hoofdstukken komen uit de import.
FI = [
    ("FI-VARALL", "Varallisuusoikeus (oikeustoimet, kauppa, vahingonkorvaus)", "", [
        ("FI-OIKTL", "Oikeustoimilaki (228/1929)", "", [], "OikTL"),
        ("FI-KL", "Kauppalaki (355/1987)", "", [], "KL"),
        ("FI-KSL", "Kuluttajansuojalaki (38/1978)", "", [], "KSL"),
        ("FI-VAHL", "Vahingonkorvauslaki (412/1974)", "", [], "VahL"),
        ("FI-VANHL", "Laki velan vanhentumisesta (728/2003)", "", [], "VanhL"),
    ]),
    ("FI-YHTIÖ", "Yhtiöoikeus", "", [
        ("FI-OYL", "Osakeyhtiölaki (624/2006)", "", [], "OYL"),
    ]),
    ("FI-PROSESSI", "Prosessioikeus", "", [
        ("FI-OK", "Oikeudenkäymiskaari (4/1734)", "", [], "OK"),
    ]),
    ("FI-JULK", "Valtiosääntö ja rikosoikeus", "", [
        ("FI-PL", "Suomen perustuslaki (731/1999)", "", [], "PL"),
        ("FI-RL", "Rikoslaki (39/1889)", "", [], "RL"),
    ]),
]

# code, naam, taal, toelichting, actief, rechtsfamilie (zelfde vorm als seed/stelsels.py)
STELSELS = [
    ("DK", "Denemarken", "da", "Geen burgerlijk wetboek: losse vermogensrechtelijke wetten (Aftaleloven 1917, Købeloven 1906), deels in Scandinavische samenwerking tot stand gekomen; Danske Lov (1683) geldt nog in enkele artikelen", True, "nordisch"),
    ("FI", "Finland", "fi", "Geen burgerlijk wetboek: losse vermogensrechtelijke wetten in Scandinavische samenwerking (Oikeustoimilaki 1929, Kauppalaki 1987); het Zweedse Rijkswetboek van 1734 leeft voort in de procesrechtelijke 'kaari'", True, "nordisch"),
    ("AT", "Oostenrijk", "de", "Allgemeines bürgerliches Gesetzbuch (1811): natuurrechtelijke codificatie, gemoderniseerd door de Teilnovellen (1914–1916) en latere hervormingen", True, "germaans"),
]

SYSTEMATIEK = {
    "AT": AT,
    "DK": DK,
    "FI": FI,
}
