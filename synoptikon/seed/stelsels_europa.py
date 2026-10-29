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

# NO: geen burgerlijk wetboek; zelfde opzet als DK, de hoofdstukken komen uit de import.
NO = [
    ("NO-FORMUE", "Formuerett (avtaler, kjøp, erstatning)", "", [
        ("NO-AVTL", "Avtaleloven (1918)", "", [], "avtl."),
        ("NO-KJL", "Kjøpsloven (1988)", "", [], "kjl."),
        ("NO-FKJL", "Forbrukerkjøpsloven (2002)", "", [], "fkjl."),
        ("NO-SKL", "Skadeserstatningsloven (1969)", "", [], "skl."),
        ("NO-FORELDL", "Foreldelsesloven (1979)", "", [], "foreldelsesl."),
    ]),
    ("NO-SELSKAP", "Selskapsrett", "", [
        ("NO-ASL", "Aksjeloven (1997)", "", [], "asl."),
    ]),
    ("NO-PROSESS", "Sivilprosess", "", [
        ("NO-TVL", "Tvisteloven (2005)", "", [], "tvl."),
    ]),
    ("NO-OFF", "Statsforfatning og strafferett", "", [
        ("NO-GRL", "Kongeriket Norges Grunnlov (1814)", "", [], "Grl."),
        ("NO-STRL", "Straffeloven (2005)", "", [], "strl."),
    ]),
]

# SE: geen burgerlijk wetboek; zelfde opzet als DK, de hoofdstukken komen uit de import.
SE = [
    ("SE-FORMÖGENHET", "Förmögenhetsrätt (avtal, köp, skadestånd)", "", [
        ("SE-AVTL", "Avtalslagen (1915:218)", "", [], "AvtL"),
        ("SE-KÖPL", "Köplagen (1990:931)", "", [], "KöpL"),
        ("SE-KKL", "Konsumentköplagen (2022:260)", "", [], "KKL"),
        ("SE-SKL", "Skadeståndslagen (1972:207)", "", [], "SkL"),
        ("SE-PRESKL", "Preskriptionslagen (1981:130)", "", [], "PreskL"),
    ]),
    ("SE-ASSOCIATION", "Associationsrätt", "", [
        ("SE-ABL", "Aktiebolagslagen (2005:551)", "", [], "ABL"),
    ]),
    ("SE-PROCESS", "Processrätt", "", [
        ("SE-RB", "Rättegångsbalken (1942:740)", "", [], "RB"),
    ]),
    ("SE-OFF", "Statsrätt och straffrätt", "", [
        ("SE-RF", "Regeringsformen (1974:152)", "", [], "RF"),
        ("SE-BRB", "Brottsbalken (1962:700)", "", [], "BrB"),
    ]),
]

# PL: Kodeks cywilny (1964), boeken en titels. Gegenereerd uit de oorspronkelijke tekst (ELI-API van de Sejm,
# DU/1964/93/text.html), met de huidige stand van de titels: later ingevoegde titels met een superscript
# (XVIII¹ Leasing, XXXVI¹ Papiery wartościowe …) vallen binnen de bereiken van hun buren.
PL = [
    ("KC-I", "Księga pierwsza · Część ogólna", "art. 1–125", [
        ("KC-I-1", "Tytuł I · Przepisy wstępne", "art. 1–7", []),
        ("KC-I-2", "Tytuł II · Osoby", "art. 8–43", []),
        ("KC-I-3", "Tytuł III · Mienie", "art. 44–55", []),
        ("KC-I-4", "Tytuł IV · Czynności prawne", "art. 56–109", []),
        ("KC-I-5", "Tytuł V · Terminy", "art. 110–116", []),
        ("KC-I-6", "Tytuł VI · Przedawnienie roszczeń", "art. 117–125", []),
    ]),
    ("KC-II", "Księga druga · Własność i inne prawa rzeczowe", "art. 140–352", [
        ("KC-II-1", "Tytuł I · Własność", "art. 140–231", []),
        ("KC-II-2", "Tytuł II · Użytkowanie wieczyste", "art. 232–243", []),
        ("KC-II-3", "Tytuł III · Prawa rzeczowe ograniczone", "art. 244–335", []),
        ("KC-II-4", "Tytuł IV · Posiadanie", "art. 336–352", []),
    ]),
    ("KC-III", "Księga trzecia · Zobowiązania", "art. 353–921", [
        ("KC-III-1", "Tytuł I · Przepisy ogólne", "art. 353–365", []),
        ("KC-III-2", "Tytuł II · Wielość dłużników albo wierzycieli", "art. 366–383", []),
        ("KC-III-3", "Tytuł III · Ogólne przepisy o zobowiązaniach umownych", "art. 384–396", []),
        ("KC-III-5", "Tytuł V · Bezpodstawne wzbogacenie", "art. 405–414", []),
        ("KC-III-6", "Tytuł VI · Czyny niedozwolone", "art. 415–449", []),
        ("KC-III-7", "Tytuł VII · Wykonanie zobowiązań i skutki ich niewykonania", "art. 450–497", []),
        ("KC-III-8", "Tytuł VIII · Potrącenie, odnowienie, zwolnienie z długu", "art. 498–508", []),
        ("KC-III-9", "Tytuł IX · Zmiana wierzyciela lub dłużnika", "art. 509–526", []),
        ("KC-III-10", "Tytuł X · Ochrona wierzyciela w razie niewypłacalności dłużnika", "art. 527–534", []),
        ("KC-III-11", "Tytuł XI · Sprzedaż", "art. 535–602", []),
        ("KC-III-12", "Tytuł XII · Zamiana", "art. 603–604", []),
        ("KC-III-13", "Tytuł XIII · Dostawa", "art. 605–612", []),
        ("KC-III-14", "Tytuł XIV · Kontraktacja", "art. 613–626", []),
        ("KC-III-15", "Tytuł XV · Umowa o dzieło", "art. 627–646", []),
        ("KC-III-16", "Tytuł XVI · Umowa o roboty budowlane", "art. 647–658", []),
        ("KC-III-17", "Tytuł XVII · Najem i dzierżawa (met XVIII¹ Leasing)", "art. 659–709", []),
        ("KC-III-18", "Tytuł XVIII · Użyczenie", "art. 710–719", []),
        ("KC-III-19", "Tytuł XIX · Pożyczka", "art. 720–724", []),
        ("KC-III-20", "Tytuł XX · Umowa rachunku bankowego", "art. 725–733", []),
        ("KC-III-21", "Tytuł XXI · Zlecenie", "art. 734–751", []),
        ("KC-III-22", "Tytuł XXII · Prowadzenie cudzych spraw bez zlecenia", "art. 752–757", []),
        ("KC-III-23", "Tytuł XXIII · Umowa agencyjna", "art. 758–764", []),
        ("KC-III-24", "Tytuł XXIV · Umowa komisu", "art. 765–773", []),
        ("KC-III-25", "Tytuł XXV · Umowa przewozu", "art. 774–793", []),
        ("KC-III-26", "Tytuł XXVI · Umowa spedycji", "art. 794–804", []),
        ("KC-III-27", "Tytuł XXVII · Umowa ubezpieczenia", "art. 805–834", []),
        ("KC-III-28", "Tytuł XXVIII · Przechowanie", "art. 835–845", []),
        ("KC-III-29", "Tytuł XXIX · Odpowiedzialność utrzymujących hotele i podobne zakłady", "art. 846–852", []),
        ("KC-III-30", "Tytuł XXX · Umowa składu", "art. 853–859", []),
        ("KC-III-31", "Tytuł XXXI · Spółka", "art. 860–875", []),
        ("KC-III-32", "Tytuł XXXII · Poręczenie", "art. 876–887", []),
        ("KC-III-33", "Tytuł XXXIII · Darowizna", "art. 888–902", []),
        ("KC-III-34", "Tytuł XXXIV · Renta i dożywocie", "art. 903–916", []),
        ("KC-III-35", "Tytuł XXXV · Ugoda", "art. 917–918", []),
        ("KC-III-36", "Tytuł XXXVI · Przyrzeczenie publiczne (met XXXVI¹ Papiery wartościowe)", "art. 919–921", []),
    ]),
    ("KC-IV", "Księga czwarta · Spadki", "art. 922–1088", [
        ("KC-IV-1", "Tytuł I · Przepisy ogólne", "art. 922–930", []),
        ("KC-IV-2", "Tytuł II · Dziedziczenie ustawowe", "art. 931–940", []),
        ("KC-IV-3", "Tytuł III · Rozrządzenia na wypadek śmierci", "art. 941–990", []),
        ("KC-IV-4", "Tytuł IV · Zachowek", "art. 991–1011", []),
        ("KC-IV-5", "Tytuł V · Przyjęcie i odrzucenie spadku", "art. 1012–1024", []),
        ("KC-IV-6", "Tytuł VI · Stwierdzenie nabycia spadku i ochrona spadkobiercy", "art. 1025–1029", []),
        ("KC-IV-7", "Tytuł VII · Odpowiedzialność za długi spadkowe", "art. 1030–1034", []),
        ("KC-IV-8", "Tytuł VIII · Wspólność majątku spadkowego i dział spadku", "art. 1035–1046", []),
        ("KC-IV-9", "Tytuł IX · Umowy dotyczące spadku", "art. 1047–1088", []),
    ]),
]

# PT: Código Civil (1966), boeken en titels, met de hand uit de officiële indeling.
PT = [
    ("CC-PT-I", "Livro I · Parte geral", "art. 1–396", [
        ("CC-PT-I-1", "Título I · Das leis, sua interpretação e aplicação", "art. 1–65", []),
        ("CC-PT-I-2", "Título II · Das relações jurídicas", "art. 66–396", []),
    ]),
    ("CC-PT-II", "Livro II · Direito das obrigações", "art. 397–1250", [
        ("CC-PT-II-1", "Título I · Das obrigações em geral", "art. 397–873", []),
        ("CC-PT-II-2", "Título II · Dos contratos em especial", "art. 874–1250", []),
    ]),
    ("CC-PT-III", "Livro III · Direito das coisas", "art. 1251–1575", [
        ("CC-PT-III-1", "Título I · Da posse", "art. 1251–1301", []),
        ("CC-PT-III-2", "Título II · Do direito de propriedade", "art. 1302–1438", []),
        ("CC-PT-III-3", "Título III · Do usufruto, uso e habitação", "art. 1439–1490", []),
        ("CC-PT-III-4", "Título IV · Da enfiteuse (revogado)", "art. 1491–1523", []),
        ("CC-PT-III-5", "Título V · Do direito de superfície", "art. 1524–1542", []),
        ("CC-PT-III-6", "Título VI · Das servidões prediais", "art. 1543–1575", []),
    ]),
    ("CC-PT-IV", "Livro IV · Direito da família", "art. 1576–2023", []),
    ("CC-PT-V", "Livro V · Direito das sucessões", "art. 2024–2334", []),
]

# CZ, HU, RO: nog zonder importer; hoofdindeling van het burgerlijk wetboek met de hand uit de officiële indeling.
# De eindnummers van de Hongaarse boeken (3:405, 4:243 …) na een eerste import controleren.
CZ = [
    ("OZ-1", "Část první · Obecná část", "§§ 1–654", []),
    ("OZ-2", "Část druhá · Rodinné právo", "§§ 655–975", []),
    ("OZ-3", "Část třetí · Absolutní majetková práva", "§§ 976–1720", []),
    ("OZ-4", "Část čtvrtá · Relativní majetková práva", "§§ 1721–3014", []),
    ("OZ-5", "Část pátá · Ustanovení společná, přechodná a závěrečná", "§§ 3015–3081", []),
]

HU = [
    ("PTK-1", "Első könyv · Bevezető rendelkezések", "1:1–1:6", []),
    ("PTK-2", "Második könyv · Az ember mint jogalany", "2:1–2:54", []),
    ("PTK-3", "Harmadik könyv · Jogi személy", "3:1–3:405", []),
    ("PTK-4", "Negyedik könyv · Családjog", "4:1–4:243", []),
    ("PTK-5", "Ötödik könyv · Dologi jog", "5:1–5:187", []),
    ("PTK-6", "Hatodik könyv · Kötelmi jog", "6:1–6:593", []),
    ("PTK-7", "Hetedik könyv · Öröklési jog", "7:1–7:102", []),
    ("PTK-8", "Nyolcadik könyv · Záró rendelkezések", "8:1–8:6", []),
]

RO = [
    ("NCC-0", "Titlul preliminar", "art. 1–24", []),
    ("NCC-1", "Cartea I · Despre persoane", "art. 25–257", []),
    ("NCC-2", "Cartea a II-a · Despre familie", "art. 258–534", []),
    ("NCC-3", "Cartea a III-a · Despre bunuri", "art. 535–952", []),
    ("NCC-4", "Cartea a IV-a · Despre moștenire și liberalități", "art. 953–1163", []),
    ("NCC-5", "Cartea a V-a · Despre obligații", "art. 1164–2499", []),
    ("NCC-6", "Cartea a VI-a · Despre prescripția extinctivă, decădere și calculul termenelor", "art. 2500–2556", []),
    ("NCC-7", "Cartea a VII-a · Dispoziții de drept internațional privat", "art. 2557–2664", []),
]

# code, naam, taal, toelichting, actief, rechtsfamilie (zelfde vorm als seed/stelsels.py)
STELSELS = [
    ("DK", "Denemarken", "da", "Geen burgerlijk wetboek: losse vermogensrechtelijke wetten (Aftaleloven 1917, Købeloven 1906), deels in Scandinavische samenwerking tot stand gekomen; Danske Lov (1683) geldt nog in enkele artikelen", True, "nordisch"),
    ("FI", "Finland", "fi", "Geen burgerlijk wetboek: losse vermogensrechtelijke wetten in Scandinavische samenwerking (Oikeustoimilaki 1929, Kauppalaki 1987); het Zweedse Rijkswetboek van 1734 leeft voort in de procesrechtelijke 'kaari'", True, "nordisch"),
    ("NO", "Noorwegen", "no", "Geen burgerlijk wetboek: losse vermogensrechtelijke wetten, grotendeels in Scandinavische samenwerking (Avtaleloven 1918); Christian V's Norske Lov (1687) geldt nog in enkele artikelen", True, "nordisch"),
    ("SE", "Zweden", "sv", "Geen burgerlijk wetboek: losse vermogensrechtelijke wetten in Scandinavische samenwerking (Avtalslagen 1915, Köplagen 1990); van het Rijkswetboek van 1734 leven de balkar voort", True, "nordisch"),
    ("PL", "Polen", "pl", "Kodeks cywilny (1964): pandektensysteem met een algemeen deel, voortbouwend op het Kodeks zobowiązań (1933); nog geen wettekst, want de ELI-API van de Sejm geeft de geconsolideerde tekst alleen als PDF", True, "germaans"),
    ("PT", "Portugal", "pt", "Código Civil (1966, Antunes Varela): pandektensysteem naar Duits voorbeeld binnen de Romaanse traditie, opvolger van het Código de Seabra (1867); tekst via de PGDL (geconsolideerd, geen officiële bron)", True, "romaans"),
    ("CZ", "Tsjechië", "cs", "Občanský zákoník (zákon č. 89/2012 Sb.): hercodificatie naar het voorbeeld van het ABGB en de Duitstalige traditie, na het socialistische wetboek van 1964; nog geen wettekst (e-Sbírka nog niet aangesloten)", True, "germaans"),
    ("HU", "Hongarije", "hu", "Polgári Törvénykönyv (2013. évi V. törvény): monistisch wetboek met het handelsrecht erin, naar Duits en Nederlands voorbeeld, nummering per boek (6:519); nog geen wettekst", True, "germaans"),
    ("RO", "Roemenië", "ro", "Noul Cod civil (Legea nr. 287/2009, 2011): monistisch wetboek naar het voorbeeld van de Code civil du Québec, opvolger van de Franse codificatie van 1864; nog geen wettekst", True, "romaans"),
    ("AT", "Oostenrijk", "de", "Allgemeines bürgerliches Gesetzbuch (1811): natuurrechtelijke codificatie, gemoderniseerd door de Teilnovellen (1914–1916) en latere hervormingen", True, "germaans"),
]

SYSTEMATIEK = {
    "AT": AT,
    "DK": DK,
    "FI": FI,
    "NO": NO,
    "SE": SE,
    "PL": PL,
    "PT": PT,
    "CZ": CZ,
    "HU": HU,
    "RO": RO,
}
