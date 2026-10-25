"""Systematiek van ZGB en OR: Teil › Abteilung › Titel › Abschnitt.

Zwitserland heeft twee gelijkwaardige wetboeken: het ZGB (personen-,
familie-, erf- en zakenrecht) en het OR (verbintenissen-, vennootschaps- en
waardepapierenrecht, formeel het vijfde deel van het ZGB maar met eigen
nummering). Het ZGB is hier de hoofdwet; de OR-knopen dragen wet "OR".

Gegenereerd uit de Akoma-Ntoso-XML van Fedlex (ZGB stand 1-7-2026, OR stand
1-10-2026); bereiken zijn het eerste en laatste artikel per eenheid.
Schlusstitel en Übergangsbestimmungen zijn weggelaten.
"""

CH = [
    ('CH-ZGB', 'Schweizerisches Zivilgesetzbuch (ZGB, SR 210)', 'Art. 1–977', [
        ('ZGB-0', 'Einleitung', 'Art. 1–10', []),
        ('ZGB-1', 'Erster Teil · Das Personenrecht', 'Art. 11–89c', [
            ('ZGB-1-1', 'Erster Titel · Die natürlichen Personen', 'Art. 11–50', [
                ('ZGB-1-1-1', 'Erster Abschnitt · Das Recht der Persönlichkeit', 'Art. 11–38', []),
                ('ZGB-1-1-2', 'Zweiter Abschnitt · Die Beurkundung des Personenstandes', 'Art. 39–50', []),
            ]),
            ('ZGB-1-2', 'Zweiter Titel · Die juristischen Personen', 'Art. 52–89a', [
                ('ZGB-1-2-1', 'Erster Abschnitt · Allgemeine Bestimmungen', 'Art. 52–59', []),
                ('ZGB-1-2-2', 'Zweiter Abschnitt · Die Vereine', 'Art. 60–79', []),
                ('ZGB-1-2-3', 'Dritter Abschnitt · Die Stiftungen', 'Art. 80–89a', []),
            ]),
            ('ZGB-1-3', 'Zweiter Titelbis · Die Sammelvermögen', 'Art. 89b–89c', []),
        ]),
        ('ZGB-2', 'Zweiter Teil · Das Familienrecht', 'Art. 90–456', [
            ('ZGB-2-1', 'Erste Abteilung · Das Eherecht', 'Art. 90–251', [
                ('ZGB-2-1-1', 'Dritter Titel · Die Eheschliessung', 'Art. 90–110', [
                    ('ZGB-2-1-1-1', 'Erster Abschnitt · Das Verlöbnis', 'Art. 90–93', []),
                    ('ZGB-2-1-1-2', 'Zweiter Abschnitt · Die Ehevoraussetzungen', 'Art. 94–96', []),
                    ('ZGB-2-1-1-3', 'Dritter Abschnitt · Vorbereitung der Eheschliessung und Trauung', 'Art. 97–103', []),
                    ('ZGB-2-1-1-4', 'Vierter Abschnitt · Die Eheungültigkeit', 'Art. 104–110', []),
                ]),
                ('ZGB-2-1-2', 'Vierter Titel · Die Ehescheidung und die Ehetrennung', 'Art. 111–150', [
                    ('ZGB-2-1-2-1', 'Erster Abschnitt · Die Scheidungsvoraussetzungen', 'Art. 111–116', []),
                    ('ZGB-2-1-2-2', 'Zweiter Abschnitt · Die Ehetrennung', 'Art. 117–118', []),
                    ('ZGB-2-1-2-3', 'Dritter Abschnitt · Die Scheidungsfolgen', 'Art. 119–150', []),
                ]),
                ('ZGB-2-1-3', 'Fünfter Titel · Die Wirkungen der Ehe im Allgemeinen', 'Art. 159–180', []),
                ('ZGB-2-1-4', 'Sechster Titel · Das Güterrecht der Ehegatten', 'Art. 181–251', [
                    ('ZGB-2-1-4-1', 'Erster Abschnitt · Allgemeine Vorschriften', 'Art. 181–195a', []),
                    ('ZGB-2-1-4-2', 'Zweiter Abschnitt · Der ordentliche Güterstand der Errungenschaftsbeteiligung', 'Art. 196–220', []),
                    ('ZGB-2-1-4-3', 'Dritter Abschnitt · Die Gütergemeinschaft', 'Art. 221–246', []),
                    ('ZGB-2-1-4-4', 'Vierter Abschnitt · Die Gütertrennung', 'Art. 247–251', []),
                ]),
            ]),
            ('ZGB-2-2', 'Zweite Abteilung · Die Verwandtschaft', 'Art. 252–359', [
                ('ZGB-2-2-1', 'Siebenter Titel · Die Entstehung des Kindesverhältnisses', 'Art. 252–269c', [
                    ('ZGB-2-2-1-1', 'Erster Abschnitt · Allgemeine Bestimmungen', 'Art. 252–254', []),
                    ('ZGB-2-2-1-2', 'Zweiter Abschnitt · Die Elternschaft des Ehemannes oder der Ehefrau', 'Art. 255–259', []),
                    ('ZGB-2-2-1-3', 'Dritter Abschnitt · Anerkennung und Vaterschaftsurteil', 'Art. 260–263', []),
                    ('ZGB-2-2-1-4', 'Vierter Abschnitt · Die Adoption', 'Art. 264–269c', []),
                ]),
                ('ZGB-2-2-2', 'Achter Titel · Die Wirkungen des Kindesverhältnisses', 'Art. 270–327c', [
                    ('ZGB-2-2-2-1', 'Erster Abschnitt · Die Gemeinschaft der Eltern und Kinder', 'Art. 270–275a', []),
                    ('ZGB-2-2-2-2', 'Zweiter Abschnitt · Die Unterhaltspflicht der Eltern', 'Art. 276–295', []),
                    ('ZGB-2-2-2-3', 'Dritter Abschnitt · Die elterliche Sorge', 'Art. 296–317', []),
                    ('ZGB-2-2-2-4', 'Vierter Abschnitt · Das Kindesvermögen', 'Art. 318–327', []),
                    ('ZGB-2-2-2-5', 'Fünfter Abschnitt · Minderjährige unter Vormundschaft', 'Art. 327a–327c', []),
                ]),
                ('ZGB-2-2-3', 'Neunter Titel · Die Familiengemeinschaft', 'Art. 328–359', [
                    ('ZGB-2-2-3-1', 'Erster Abschnitt · Die Unterstützungspflicht', 'Art. 328–330', []),
                    ('ZGB-2-2-3-2', 'Zweiter Abschnitt · Die Hausgewalt', 'Art. 331–334bis', []),
                    ('ZGB-2-2-3-3', 'Dritter Abschnitt · Das Familienvermögen', 'Art. 335–359', []),
                ]),
            ]),
            ('ZGB-2-3', 'Dritte Abteilung · Der Erwachsenenschutz', 'Art. 360–456', [
                ('ZGB-2-3-1', 'Zehnter Titel · Die eigene Vorsorge und Massnahmen von Gesetzes wegen', 'Art. 360–387', [
                    ('ZGB-2-3-1-1', 'Erster Abschnitt · Die eigene Vorsorge', 'Art. 360–373', []),
                    ('ZGB-2-3-1-2', 'Zweiter Abschnitt · Massnahmen von Gesetzes wegen für urteilsunfähige Personen', 'Art. 374–387', []),
                ]),
                ('ZGB-2-3-2', 'Elfter Titel · Die behördlichen Massnahmen', 'Art. 388–439', [
                    ('ZGB-2-3-2-1', 'Erster Abschnitt · Allgemeine Grundsätze', 'Art. 388–389', []),
                    ('ZGB-2-3-2-2', 'Zweiter Abschnitt · Die Beistandschaften', 'Art. 390–425', []),
                    ('ZGB-2-3-2-3', 'Dritter Abschnitt · Die fürsorgerische Unterbringung', 'Art. 426–439', []),
                ]),
                ('ZGB-2-3-3', 'Zwölfter Titel · Organisation', 'Art. 440–456', [
                    ('ZGB-2-3-3-1', 'Erster Abschnitt · Behörden und örtliche Zuständigkeit', 'Art. 440–442', []),
                    ('ZGB-2-3-3-2', 'Zweiter Abschnitt · Verfahren', 'Art. 443–450g', []),
                    ('ZGB-2-3-3-3', 'Dritter Abschnitt · Verhältnis zu Dritten und Zusammenarbeitspflicht', 'Art. 451–453', []),
                    ('ZGB-2-3-3-4', 'Vierter Abschnitt · Verantwortlichkeit', 'Art. 454–456', []),
                ]),
            ]),
        ]),
        ('ZGB-3', 'Dritter Teil · Das Erbrecht', 'Art. 457–640', [
            ('ZGB-3-1', 'Erste Abteilung · Die Erben', 'Art. 457–536', [
                ('ZGB-3-1-1', 'Dreizehnter Titel · Die gesetzlichen Erben', 'Art. 457–466', []),
                ('ZGB-3-1-2', 'Vierzehnter Titel · Die Verfügungen von Todes wegen', 'Art. 467–536', [
                    ('ZGB-3-1-2-1', 'Erster Abschnitt · Die Verfügungsfähigkeit', 'Art. 467–469', []),
                    ('ZGB-3-1-2-2', 'Zweiter Abschnitt · Die Verfügungsfreiheit', 'Art. 470–480', []),
                    ('ZGB-3-1-2-3', 'Dritter Abschnitt · Die Verfügungsarten', 'Art. 481–497', []),
                    ('ZGB-3-1-2-4', 'Vierter Abschnitt · Die Verfügungsformen', 'Art. 498–516', []),
                    ('ZGB-3-1-2-5', 'Fünfter Abschnitt · Die Willensvollstrecker', 'Art. 517–518', []),
                    ('ZGB-3-1-2-6', 'Sechster Abschnitt · Die Ungültigkeit und Herabsetzung der Verfügungen', 'Art. 519–533', []),
                    ('ZGB-3-1-2-7', 'Siebenter Abschnitt · Klagen aus Erbverträgen', 'Art. 534–536', []),
                ]),
            ]),
            ('ZGB-3-2', 'Zweite Abteilung · Der Erbgang', 'Art. 537–640', [
                ('ZGB-3-2-1', 'Fünfzehnter Titel · Die Eröffnung des Erbganges', 'Art. 537–550', []),
                ('ZGB-3-2-2', 'Sechzehnter Titel · Die Wirkung des Erbganges', 'Art. 551–601', [
                    ('ZGB-3-2-2-1', 'Erster Abschnitt · Die Sicherungsmassregeln', 'Art. 551–559', []),
                    ('ZGB-3-2-2-2', 'Zweiter Abschnitt · Der Erwerb der Erbschaft', 'Art. 560–579', []),
                    ('ZGB-3-2-2-3', 'Dritter Abschnitt · Das öffentliche Inventar', 'Art. 580–592', []),
                    ('ZGB-3-2-2-4', 'Vierter Abschnitt · Die amtliche Liquidation', 'Art. 593–597', []),
                    ('ZGB-3-2-2-5', 'Fünfter Abschnitt · Die Erbschaftsklage', 'Art. 598–601', []),
                ]),
                ('ZGB-3-2-3', 'Siebenzehnter Titel · Die Teilung der Erbschaft', 'Art. 602–640', [
                    ('ZGB-3-2-3-1', 'Erster Abschnitt · Die Gemeinschaft vor der Teilung', 'Art. 602–606', []),
                    ('ZGB-3-2-3-2', 'Zweiter Abschnitt · Die Teilungsart', 'Art. 607–620', []),
                    ('ZGB-3-2-3-3', 'Dritter Abschnitt · Die Ausgleichung', 'Art. 626–633', []),
                    ('ZGB-3-2-3-4', 'Vierter Abschnitt · Abschluss und Wirkung der Teilung', 'Art. 634–640', []),
                ]),
            ]),
        ]),
        ('ZGB-4', 'Vierter Teil · Das Sachenrecht', 'Art. 641–977', [
            ('ZGB-4-1', 'Erste Abteilung · Das Eigentum', 'Art. 641–729', [
                ('ZGB-4-1-1', 'Achtzehnter Titel · Allgemeine Bestimmungen', 'Art. 641–654a', []),
                ('ZGB-4-1-2', 'Neunzehnter Titel · Das Grundeigentum', 'Art. 655–712t', [
                    ('ZGB-4-1-2-1', 'Erster Abschnitt · Gegenstand, Erwerb und Verlust des Grundeigentums', 'Art. 655–666b', []),
                    ('ZGB-4-1-2-2', 'Zweiter Abschnitt · Inhalt und Beschränkung des Grundeigentums', 'Art. 667–712', []),
                    ('ZGB-4-1-2-3', 'Dritter Abschnitt · Das Stockwerkeigentum', 'Art. 712a–712t', []),
                ]),
                ('ZGB-4-1-3', 'Zwanzigster Titel · Das Fahrniseigentum', 'Art. 713–729', []),
            ]),
            ('ZGB-4-2', 'Zweite Abteilung · Die beschränkten dinglichen Rechte', 'Art. 730–916', [
                ('ZGB-4-2-1', 'Einundzwanzigster Titel · Die Dienstbarkeiten und Grundlasten', 'Art. 730–792', [
                    ('ZGB-4-2-1-1', 'Erster Abschnitt · Die Grunddienstbarkeiten', 'Art. 730–744', []),
                    ('ZGB-4-2-1-2', 'Zweiter Abschnitt · Nutzniessung und andere Dienstbarkeiten', 'Art. 745–781a', []),
                    ('ZGB-4-2-1-3', 'Dritter Abschnitt · Die Grundlasten', 'Art. 782–792', []),
                ]),
                ('ZGB-4-2-2', 'Zweiundzwanzigster Titel · Das Grundpfand', 'Art. 793–876', [
                    ('ZGB-4-2-2-1', 'Erster Abschnitt · Allgemeine Bestimmungen', 'Art. 793–823', []),
                    ('ZGB-4-2-2-2', 'Zweiter Abschnitt · Die Grundpfandverschreibung', 'Art. 824–841', []),
                    ('ZGB-4-2-2-3', 'Dritter Abschnitt · Der Schuldbrief', 'Art. 842–866', []),
                    ('ZGB-4-2-2-4', 'Vierter Abschnitt · Ausgabe von Anleihenstiteln mit Grundpfandrecht', 'Art. 875–876', []),
                ]),
                ('ZGB-4-2-3', 'Dreiundzwanzigster Titel · Das Fahrnispfand', 'Art. 884–916', [
                    ('ZGB-4-2-3-1', 'Erster Abschnitt · Faustpfand und Retentionsrecht', 'Art. 884–898', []),
                    ('ZGB-4-2-3-2', 'Zweiter Abschnitt · Das Pfandrecht an Forderungen und andern Rechten', 'Art. 899–906', []),
                    ('ZGB-4-2-3-3', 'Dritter Abschnitt · Das Versatzpfand', 'Art. 907–915', []),
                    ('ZGB-4-2-3-4', 'Vierter Abschnitt · …', 'Art. 916', []),
                ]),
            ]),
            ('ZGB-4-3', 'Dritte Abteilung · Besitz und Grundbuch', 'Art. 919–977', [
                ('ZGB-4-3-1', 'Vierundzwanzigster Titel · Der Besitz', 'Art. 919–941', []),
                ('ZGB-4-3-2', 'Fünfundzwanzigster Titel · Das Grundbuch', 'Art. 942–977', []),
            ]),
        ]),
    ]),
    ('CH-OR', 'Obligationenrecht (OR, SR 220)', 'Art. 1–1186', [
        ('OR-1', 'Erste Abteilung · Allgemeine Bestimmungen', 'Art. 1–183', [
            ('OR-1-1', 'Erster Titel · Die Entstehung der Obligationen', 'Art. 1–67', [
                ('OR-1-1-1', 'Erster Abschnitt · Die Entstehung durch Vertrag', 'Art. 1–40g', []),
                ('OR-1-1-2', 'Zweiter Abschnitt · Die Entstehung durch unerlaubte Handlungen', 'Art. 41–61', []),
                ('OR-1-1-3', 'Dritter Abschnitt · Die Entstehung aus ungerechtfertigter Bereicherung', 'Art. 62–67', []),
            ]),
            ('OR-1-2', 'Zweiter Titel · Die Wirkung der Obligationen', 'Art. 68–113', [
                ('OR-1-2-1', 'Erster Abschnitt · Die Erfüllung der Obligationen', 'Art. 68–96', []),
                ('OR-1-2-2', 'Zweiter Abschnitt · Die Folgen der Nichterfüllung', 'Art. 97–109', []),
                ('OR-1-2-3', 'Dritter Abschnitt · Beziehungen zu dritten Personen', 'Art. 110–113', []),
            ]),
            ('OR-1-3', 'Dritter Titel · Das Erlöschen der Obligationen', 'Art. 114–142', []),
            ('OR-1-4', 'Vierter Titel · Besondere Verhältnisse bei Obligationen', 'Art. 143–163', [
                ('OR-1-4-1', 'Erster Abschnitt · Die Solidarität', 'Art. 143–150', []),
                ('OR-1-4-2', 'Zweiter Abschnitt · Die Bedingungen', 'Art. 151–157', []),
                ('OR-1-4-3', 'Dritter Abschnitt · Haft- und Reugeld. Lohnabzüge. Konventionalstrafe', 'Art. 158–163', []),
            ]),
            ('OR-1-5', 'Fünfter Titel · Die Abtretung von Forderungen und die Schuldübernahme', 'Art. 164–183', []),
        ]),
        ('OR-2', 'Zweite Abteilung · Die einzelnen Vertragsverhältnisse', 'Art. 184–551', [
            ('OR-2-1', 'Sechster Titel · Kauf und Tausch', 'Art. 184–238', [
                ('OR-2-1-1', 'Erster Abschnitt · Allgemeine Bestimmungen', 'Art. 184–186', []),
                ('OR-2-1-2', 'Zweiter Abschnitt · Der Fahrniskauf', 'Art. 187–215', []),
                ('OR-2-1-3', 'Dritter Abschnitt · Der Grundstückkauf', 'Art. 216–221', []),
                ('OR-2-1-4', 'Vierter Abschnitt · Besondere Arten des Kaufes', 'Art. 222–236', []),
                ('OR-2-1-5', 'Fünfter Abschnitt · Der Tauschvertrag', 'Art. 237–238', []),
            ]),
            ('OR-2-2', 'Siebenter Titel · Die Schenkung', 'Art. 239–252', []),
            ('OR-2-3', 'Achter Titel · Die Miete', 'Art. 253–274', [
                ('OR-2-3-1', 'Erster Abschnitt · Allgemeine Bestimmungen', 'Art. 253–268b', []),
                ('OR-2-3-2', 'Zweiter Abschnitt · Schutz vor missbräuchlichen Mietzinsen und andern missbräuchlichen Forderungen des Vermieters bei der Miete von Wohn- und Geschäftsräumen', 'Art. 269–270e', []),
                ('OR-2-3-3', 'Dritter Abschnitt · Kündigungsschutz bei der Miete von Wohn- und Geschäftsräumen', 'Art. 271–273c', []),
                ('OR-2-3-4', 'Vierter Abschnitt · …', 'Art. 274', []),
            ]),
            ('OR-2-4', 'Achter Titelbis · Die Pacht', 'Art. 275–304', []),
            ('OR-2-5', 'Neunter Titel · Die Leihe', 'Art. 305–318', [
                ('OR-2-5-1', 'Erster Abschnitt · Die Gebrauchsleihe', 'Art. 305–311', []),
                ('OR-2-5-2', 'Zweiter Abschnitt · Das Darlehen', 'Art. 312–318', []),
            ]),
            ('OR-2-6', 'Zehnter Titel · Der Arbeitsvertrag', 'Art. 319–362', [
                ('OR-2-6-1', 'Erster Abschnitt · Der Einzelarbeitsvertrag', 'Art. 319–343', []),
                ('OR-2-6-2', 'Zweiter Abschnitt · Besondere Einzelarbeitsverträge', 'Art. 344–355', []),
                ('OR-2-6-3', 'Dritter Abschnitt · Gesamtarbeitsvertrag und Normalarbeitsvertrag', 'Art. 356–360f', []),
                ('OR-2-6-4', 'Vierter Abschnitt · Zwingende Vorschriften', 'Art. 361–362', []),
            ]),
            ('OR-2-7', 'Elfter Titel · Der Werkvertrag', 'Art. 363–379', []),
            ('OR-2-8', 'Zwölfter Titel · Der Verlagsvertrag', 'Art. 380–393', []),
            ('OR-2-9', 'Dreizehnter Titel · Der Auftrag', 'Art. 394–418v', [
                ('OR-2-9-1', 'Erster Abschnitt · Der einfache Auftrag', 'Art. 394–406', []),
                ('OR-2-9-2', 'Erster Abschnittbis · Auftrag zur Ehe- oder zur Partnerschaftsvermittlung', 'Art. 406a–406h', []),
                ('OR-2-9-3', 'Zweiter Abschnitt · Der Kreditbrief und der Kreditauftrag', 'Art. 407–411', []),
                ('OR-2-9-4', 'Dritter Abschnitt · Der Mäklervertrag', 'Art. 412–418', []),
                ('OR-2-9-5', 'Vierter Abschnitt · Der Agenturvertrag', 'Art. 418a–418v', []),
            ]),
            ('OR-2-10', 'Vierzehnter Titel · Die Geschäftsführung ohne Auftrag', 'Art. 419–424', []),
            ('OR-2-11', 'Fünfzehnter Titel · Die Kommission', 'Art. 425–439', []),
            ('OR-2-12', 'Sechzehnter Titel · Der Frachtvertrag', 'Art. 440–457', []),
            ('OR-2-13', 'Siebzehnter Titel · Die Prokura und andere Handlungsvollmachten', 'Art. 458–465', []),
            ('OR-2-14', 'Achtzehnter Titel · Die Anweisung', 'Art. 466–471', []),
            ('OR-2-15', 'Neunzehnter Titel · Der Hinterlegungsvertrag', 'Art. 472–491', []),
            ('OR-2-16', 'Zwanzigster Titel · Die Bürgschaft', 'Art. 492–512', []),
            ('OR-2-17', 'Einundzwanzigster Titel · Spiel und Wette', 'Art. 513–515a', []),
            ('OR-2-18', 'Zweiundzwanzigster Titel · Der Leibrentenvertrag und die Verpfründung', 'Art. 516–529', []),
            ('OR-2-19', 'Dreiundzwanzigster Titel · Die einfache Gesellschaft', 'Art. 530–551', []),
        ]),
        ('OR-3', 'Dritte Abteilung · Die Handelsgesellschaften und die Genossenschaft', 'Art. 552–926', [
            ('OR-3-1', 'Vierundzwanzigster Titel · Die Kollektivgesellschaft', 'Art. 552–593', [
                ('OR-3-1-1', 'Erster Abschnitt · Begriff und Errichtung', 'Art. 552–556', []),
                ('OR-3-1-2', 'Zweiter Abschnitt · Verhältnis der Gesellschafter unter sich', 'Art. 557–561', []),
                ('OR-3-1-3', 'Dritter Abschnitt · Verhältnis der Gesellschaft zu Dritten', 'Art. 562–573', []),
                ('OR-3-1-4', 'Vierter Abschnitt · Auflösung und Ausscheiden', 'Art. 574–581a', []),
                ('OR-3-1-5', 'Fünfter Abschnitt · Liquidation', 'Art. 582–590', []),
                ('OR-3-1-6', 'Sechster Abschnitt · Verjährung', 'Art. 591–593', []),
            ]),
            ('OR-3-2', 'Fünfundzwanzigster Titel · Die Kommanditgesellschaft', 'Art. 594–619', [
                ('OR-3-2-1', 'Erster Abschnitt · Begriff und Errichtung', 'Art. 594–597', []),
                ('OR-3-2-2', 'Zweiter Abschnitt · Verhältnis der Gesellschafter unter sich', 'Art. 598–601', []),
                ('OR-3-2-3', 'Dritter Abschnitt · Verhältnis der Gesellschaft zu Dritten', 'Art. 602–618', []),
                ('OR-3-2-4', 'Vierter Abschnitt · Auflösung, Liquidation, Verjährung', 'Art. 619', []),
            ]),
            ('OR-3-3', 'Sechsundzwanzigster Titel · Die Aktiengesellschaft', 'Art. 620–763', [
                ('OR-3-3-1', 'Erster Abschnitt · Allgemeine Bestimmungen', 'Art. 620–659b', []),
                ('OR-3-3-2', 'Zweiter Abschnitt · Rechte und Pflichten der Aktionäre', 'Art. 660–697n', []),
                ('OR-3-3-3', 'Dritter Abschnitt · Organisation der Aktiengesellschaft', 'Art. 698–731b', []),
                ('OR-3-3-4', 'Vierter Abschnitt · Vergütungen bei Gesellschaften, deren Aktien an einer Börse kotiert sind', 'Art. 732–735d', []),
                ('OR-3-3-5', 'Fünfter Abschnitt · Auflösung der Aktiengesellschaft', 'Art. 736–751', []),
                ('OR-3-3-6', 'Sechster Abschnitt · Verantwortlichkeit', 'Art. 752–761', []),
                ('OR-3-3-7', 'Siebenter Abschnitt · Beteiligung von Körperschaften des öffentlichen Rechts', 'Art. 762', []),
                ('OR-3-3-8', 'Achter Abschnitt · Ausschluss der Anwendung des Gesetzes auf öffentlich-rechtliche Anstalten', 'Art. 763', []),
            ]),
            ('OR-3-4', 'Siebenundzwanzigster Titel · Die Kommanditaktiengesellschaft', 'Art. 764–771', []),
            ('OR-3-5', 'Achtundzwanzigster Titel · Die Gesellschaft mit beschränkter Haftung', 'Art. 772–827', [
                ('OR-3-5-1', 'Erster Abschnitt · Allgemeine Bestimmungen', 'Art. 772–783', []),
                ('OR-3-5-2', 'Zweiter Abschnitt · Rechte und Pflichten der Gesellschafter', 'Art. 784–803', []),
                ('OR-3-5-3', 'Dritter Abschnitt · Organisation der Gesellschaft', 'Art. 804–820', []),
                ('OR-3-5-4', 'Vierter Abschnitt · Auflösung und Ausscheiden', 'Art. 821–826', []),
                ('OR-3-5-5', 'Fünfter Abschnitt · Verantwortlichkeit', 'Art. 827', []),
            ]),
            ('OR-3-6', 'Neunundzwanzigster Titel · Die Genossenschaft', 'Art. 828–926', [
                ('OR-3-6-1', 'Erster Abschnitt · Begriff und Errichtung', 'Art. 828–838a', []),
                ('OR-3-6-2', 'Zweiter Abschnitt · Erwerb der Mitgliedschaft', 'Art. 839–841', []),
                ('OR-3-6-3', 'Dritter Abschnitt · Verlust der Mitgliedschaft', 'Art. 842–851', []),
                ('OR-3-6-4', 'Vierter Abschnitt · Rechte und Pflichten der Genossenschafter', 'Art. 852–878', []),
                ('OR-3-6-5', 'Fünfter Abschnitt · Organisation der Genossenschaft', 'Art. 879–909', []),
                ('OR-3-6-6', 'Sechster Abschnitt · Auflösung der Genossenschaft', 'Art. 911–915', []),
                ('OR-3-6-7', 'Siebenter Abschnitt · Verantwortlichkeit', 'Art. 916–920', []),
                ('OR-3-6-8', 'Achter Abschnitt · Genossenschaftsverbände', 'Art. 921–925', []),
                ('OR-3-6-9', 'Neunter Abschnitt · Beteiligung von Körperschaften des öffentlichen Rechts', 'Art. 926', []),
            ]),
        ]),
        ('OR-4', 'Vierte Abteilung · Handelsregister, Geschäftsfirmen und kaufmännische Buchführung', 'Art. 927–964l', [
            ('OR-4-1', 'Dreissigster Titel · Das Handelsregister', 'Art. 927–943', []),
            ('OR-4-2', 'Einunddreissigster Titel · Die Geschäftsfirmen', 'Art. 944–956', []),
            ('OR-4-3', 'Zweiunddreissigster Titel · Kaufmännische Buchführung, Rechnungslegung, weitere Transparenz- und Sorgfaltspflichten', 'Art. 957–964l', [
                ('OR-4-3-1', 'Erster Abschnitt · Allgemeine Bestimmungen', 'Art. 957–958f', []),
                ('OR-4-3-2', 'Zweiter Abschnitt · Jahresrechnung und Zwischenabschluss', 'Art. 959–960f', []),
                ('OR-4-3-3', 'Dritter Abschnitt · Rechnungslegung für grössere Unternehmen', 'Art. 961–961d', []),
                ('OR-4-3-4', 'Vierter Abschnitt · Abschluss nach anerkanntem Standard zur Rechnungslegung', 'Art. 962–962a', []),
                ('OR-4-3-5', 'Fünfter Abschnitt · Konzernrechnung', 'Art. 963–964', []),
                ('OR-4-3-6', 'Sechster Abschnitt · Transparenz über nichtfinanzielle Belange', 'Art. 964a–964c', []),
                ('OR-4-3-7', 'Siebter Abschnitt · Transparenz bei Rohstoffunternehmen', 'Art. 964d–964i', []),
                ('OR-4-3-8', 'Achter Abschnitt · Sorgfaltspflichten und Transparenz bezüglich Mineralien und Metallen aus Konfliktgebieten und Kinderarbeit', 'Art. 964j–964l', []),
            ]),
        ]),
        ('OR-5', 'Fünfte Abteilung · Die Wertpapiere', 'Art. 965–1186', [
            ('OR-5-1', 'Dreiunddreissigster Titel · Die Namen-, Inhaber- und Ordrepapiere', 'Art. 965–1155', [
                ('OR-5-1-1', 'Erster Abschnitt · Allgemeine Bestimmungen', 'Art. 965–973i', []),
                ('OR-5-1-2', 'Zweiter Abschnitt · Die Namenpapiere', 'Art. 974–977', []),
                ('OR-5-1-3', 'Dritter Abschnitt · Die Inhaberpapiere', 'Art. 978–989', []),
                ('OR-5-1-4', 'Vierter Abschnitt · Der Wechsel', 'Art. 990–1099', []),
                ('OR-5-1-5', 'Fünfter Abschnitt · Der Check', 'Art. 1100–1144', []),
                ('OR-5-1-6', 'Sechster Abschnitt · Wechselähnliche und andere Ordrepapiere', 'Art. 1145–1152', []),
                ('OR-5-1-7', 'Siebenter Abschnitt · Die Warenpapiere', 'Art. 1153–1155', []),
            ]),
            ('OR-5-2', 'Vierunddreissigster Titel · Anleihensobligationen', 'Art. 1156–1186', [
                ('OR-5-2-1', 'Erster Abschnitt · …', 'Art. 1156', []),
                ('OR-5-2-2', 'Zweiter Abschnitt · Gläubigergemeinschaft bei Anleihensobligationen', 'Art. 1157–1186', []),
            ]),
        ]),
    ], 'OR'),
]
