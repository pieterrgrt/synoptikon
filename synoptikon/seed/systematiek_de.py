"""Systematiek van het BGB, alle niveaus: Buch › Abschnitt › Titel › Untertitel › Kapitel › Unterkapitel.

Gegenereerd uit de officiële XML van gesetze-im-internet.de (builddate
20260926215507); bereiken zijn de eerste en laatste paragraaf van elke eenheid,
weggefallene inbegrepen. Ververs met `synoptikon import de bgb --systematiek`.
"""

BGB = [
    ('BGB-1', 'Buch 1 · Allgemeiner Teil', '§§ 1–240a', [
        ('BGB-1-1', 'Abschnitt 1 · Personen', '§§ 1–89', [
            ('BGB-1-1-1', 'Titel 1 · Natürliche Personen, Verbraucher, Unternehmer', '§§ 1–14', []),
            ('BGB-1-1-2', 'Titel 2 · Juristische Personen', '§§ 21–89', [
                ('BGB-1-1-2-1', 'Untertitel 1 · Vereine', '§§ 21–79a', [
                    ('BGB-1-1-2-1-1', 'Kapitel 1 · Allgemeine Vorschriften', '§§ 21–54', []),
                    ('BGB-1-1-2-1-2', 'Kapitel 2 · Eingetragene Vereine', '§§ 55–79a', []),
                ]),
                ('BGB-1-1-2-2', 'Untertitel 2 · Rechtsfähige Stiftungen', '§§ 80–88', []),
                ('BGB-1-1-2-3', 'Untertitel 3 · Juristische Personen des öffentlichen Rechts', '§ 89', []),
            ]),
        ]),
        ('BGB-1-2', 'Abschnitt 2 · Sachen und Tiere', '§§ 90–103', []),
        ('BGB-1-3', 'Abschnitt 3 · Rechtsgeschäfte', '§§ 104–185', [
            ('BGB-1-3-1', 'Titel 1 · Geschäftsfähigkeit', '§§ 104–113', []),
            ('BGB-1-3-2', 'Titel 2 · Willenserklärung', '§§ 116–144', []),
            ('BGB-1-3-3', 'Titel 3 · Vertrag', '§§ 145–157', []),
            ('BGB-1-3-4', 'Titel 4 · Bedingung und Zeitbestimmung', '§§ 158–163', []),
            ('BGB-1-3-5', 'Titel 5 · Vertretung und Vollmacht', '§§ 164–181', []),
            ('BGB-1-3-6', 'Titel 6 · Einwilligung und Genehmigung', '§§ 182–185', []),
        ]),
        ('BGB-1-4', 'Abschnitt 4 · Fristen, Termine', '§§ 186–193', []),
        ('BGB-1-5', 'Abschnitt 5 · Verjährung', '§§ 194–218', [
            ('BGB-1-5-1', 'Titel 1 · Gegenstand und Dauer der Verjährung', '§§ 194–202', []),
            ('BGB-1-5-2', 'Titel 2 · Hemmung, Ablaufhemmung und Neubeginn der Verjährung', '§§ 203–213', []),
            ('BGB-1-5-3', 'Titel 3 · Rechtsfolgen der Verjährung', '§§ 214–218', []),
        ]),
        ('BGB-1-6', 'Abschnitt 6 · Ausübung der Rechte, Selbstverteidigung, Selbsthilfe', '§§ 226–231', []),
        ('BGB-1-7', 'Abschnitt 7 · Sicherheitsleistung', '§§ 232–240a', []),
    ]),
    ('BGB-2', 'Buch 2 · Recht der Schuldverhältnisse', '§§ 241–853', [
        ('BGB-2-1', 'Abschnitt 1 · Inhalt der Schuldverhältnisse', '§§ 241–304', [
            ('BGB-2-1-1', 'Titel 1 · Verpflichtung zur Leistung', '§§ 241–292', []),
            ('BGB-2-1-2', 'Titel 2 · Verzug des Gläubigers', '§§ 293–304', []),
        ]),
        ('BGB-2-2', 'Abschnitt 2 · Gestaltung rechtsgeschäftlicher Schuldverhältnisse durch Allgemeine Geschäftsbedingungen', '§§ 305–310', []),
        ('BGB-2-3', 'Abschnitt 3 · Schuldverhältnisse aus Verträgen', '§§ 311–361', [
            ('BGB-2-3-1', 'Titel 1 · Begründung, Inhalt und Beendigung', '§§ 311–319', [
                ('BGB-2-3-1-1', 'Untertitel 1 · Begründung', '§§ 311–311c', []),
                ('BGB-2-3-1-2', 'Untertitel 2 · Grundsätze bei Verbraucherverträgen und besondere Vertriebsformen', '§§ 312–312m', [
                    ('BGB-2-3-1-2-1', 'Kapitel 1 · Anwendungsbereich und Grundsätze bei Verbraucherverträgen', '§§ 312–312a', []),
                    ('BGB-2-3-1-2-2', 'Kapitel 2 · Außerhalb von Geschäftsräumen geschlossene Verträge und Fernabsatzverträge', '§§ 312b–312h', []),
                    ('BGB-2-3-1-2-3', 'Kapitel 3 · Verträge im elektronischen Geschäftsverkehr; Online-Marktplätze', '§§ 312i–312l', []),
                    ('BGB-2-3-1-2-4', 'Kapitel 4 · Abweichende Vereinbarungen und Beweislast', '§ 312m', []),
                ]),
                ('BGB-2-3-1-3', 'Untertitel 3 · Anpassung und Beendigung von Verträgen', '§§ 313–314', []),
                ('BGB-2-3-1-4', 'Untertitel 4 · Einseitige Leistungsbestimmungsrechte', '§§ 315–319', []),
            ]),
            ('BGB-2-3-2', 'Titel 2 · Gegenseitiger Vertrag', '§§ 320–326', []),
            ('BGB-2-3-2a', 'Titel 2a · Verträge über digitale Produkte', '§§ 327–327u', [
                ('BGB-2-3-2a-1', 'Untertitel 1 · Verbraucherverträge über digitale Produkte', '§§ 327–327s', []),
                ('BGB-2-3-2a-2', 'Untertitel 2 · Besondere Bestimmungen für Verträge über digitale Produkte zwischen Unternehmern', '§§ 327t–327u', []),
            ]),
            ('BGB-2-3-3', 'Titel 3 · Versprechen der Leistung an einen Dritten', '§§ 328–335', []),
            ('BGB-2-3-4', 'Titel 4 · Draufgabe, Vertragsstrafe', '§§ 336–345', []),
            ('BGB-2-3-5', 'Titel 5 · Rücktritt; Widerrufsrecht bei Verbraucherverträgen', '§§ 346–361', [
                ('BGB-2-3-5-1', 'Untertitel 1 · Rücktritt', '§§ 346–354', []),
                ('BGB-2-3-5-2', 'Untertitel 2 · Widerrufsrecht bei Verbraucherverträgen', '§§ 355–361', []),
            ]),
        ]),
        ('BGB-2-4', 'Abschnitt 4 · Erlöschen der Schuldverhältnisse', '§§ 362–397', [
            ('BGB-2-4-1', 'Titel 1 · Erfüllung', '§§ 362–371', []),
            ('BGB-2-4-2', 'Titel 2 · Hinterlegung', '§§ 372–386', []),
            ('BGB-2-4-3', 'Titel 3 · Aufrechnung', '§§ 387–396', []),
            ('BGB-2-4-4', 'Titel 4 · Erlass', '§ 397', []),
        ]),
        ('BGB-2-5', 'Abschnitt 5 · Übertragung einer Forderung', '§§ 398–413', []),
        ('BGB-2-6', 'Abschnitt 6 · Schuldübernahme', '§§ 414–419', []),
        ('BGB-2-7', 'Abschnitt 7 · Mehrheit von Schuldnern und Gläubigern', '§§ 420–432', []),
        ('BGB-2-8', 'Abschnitt 8 · Einzelne Schuldverhältnisse', '§§ 433–853', [
            ('BGB-2-8-1', 'Titel 1 · Kauf, Tausch', '§§ 433–480', [
                ('BGB-2-8-1-1', 'Untertitel 1 · Allgemeine Vorschriften', '§§ 433–453', []),
                ('BGB-2-8-1-2', 'Untertitel 2 · Besondere Arten des Kaufs', '§§ 454–473', [
                    ('BGB-2-8-1-2-1', 'Kapitel 1 · Kauf auf Probe', '§§ 454–455', []),
                    ('BGB-2-8-1-2-2', 'Kapitel 2 · Wiederkauf', '§§ 456–462', []),
                    ('BGB-2-8-1-2-3', 'Kapitel 3 · Vorkauf', '§§ 463–473', []),
                ]),
                ('BGB-2-8-1-3', 'Untertitel 3 · Verbrauchsgüterkauf', '§§ 474–479', []),
                ('BGB-2-8-1-4', 'Untertitel 4 · Reparaturverpflichtung des Herstellers', '§§ 479a–479g', []),
                ('BGB-2-8-1-5', 'Untertitel 5 · Tausch', '§ 480', []),
            ]),
            ('BGB-2-8-2', 'Titel 2 · Teilzeit-Wohnrechteverträge, Verträge über langfristige Urlaubsprodukte, Vermittlungsverträge und Tauschsystemverträge', '§§ 481–487', []),
            ('BGB-2-8-3', 'Titel 3 · Darlehensvertrag; Finanzierungshilfen und Ratenlieferungsverträge zwischen einem Unternehmer und einem Verbraucher', '§§ 488–515', [
                ('BGB-2-8-3-1', 'Untertitel 1 · Darlehensvertrag', '§§ 488–505e', [
                    ('BGB-2-8-3-1-1', 'Kapitel 1 · Allgemeine Vorschriften', '§§ 488–490', []),
                    ('BGB-2-8-3-1-2', 'Kapitel 2 · Besondere Vorschriften für Verbraucherdarlehensverträge', '§§ 491–505e', []),
                ]),
                ('BGB-2-8-3-2', 'Untertitel 2 · Finanzierungshilfen zwischen einem Unternehmer und einem Verbraucher', '§§ 506–509', []),
                ('BGB-2-8-3-3', 'Untertitel 3 · Ratenlieferungsverträge zwischen einem Unternehmer und einem Verbraucher', '§ 510', []),
                ('BGB-2-8-3-4', 'Untertitel 4 · Beratungsleistungen bei Immobiliar-Verbraucherdarlehensverträgen', '§ 511', []),
                ('BGB-2-8-3-5', 'Untertitel 5 · Unabdingbarkeit, Anwendung auf Existenzgründer', '§§ 512–513', []),
                ('BGB-2-8-3-6', 'Untertitel 6 · Unentgeltliche Darlehensverträge und unentgeltliche Finanzierungshilfen zwischen einem Unternehmer und einem Verbraucher', '§§ 514–515', []),
            ]),
            ('BGB-2-8-4', 'Titel 4 · Schenkung', '§§ 516–534', []),
            ('BGB-2-8-5', 'Titel 5 · Mietvertrag, Pachtvertrag', '§§ 535–597', [
                ('BGB-2-8-5-1', 'Untertitel 1 · Allgemeine Vorschriften für Mietverhältnisse', '§§ 535–548a', []),
                ('BGB-2-8-5-2', 'Untertitel 2 · Mietverhältnisse über Wohnraum', '§§ 549–577a', [
                    ('BGB-2-8-5-2-1', 'Kapitel 1 · Allgemeine Vorschriften', '§§ 549–555', []),
                    ('BGB-2-8-5-2-1a', 'Kapitel 1a · Erhaltungs- und Modernisierungsmaßnahmen', '§§ 555a–555f', []),
                    ('BGB-2-8-5-2-2', 'Kapitel 2 · Die Miete', '§§ 556–561', [
                        ('BGB-2-8-5-2-2-1', 'Unterkapitel 1 · Vereinbarungen über die Miete', '§§ 556–556c', []),
                        ('BGB-2-8-5-2-2-1a', 'Unterkapitel 1a · Vereinbarungen über die Miethöhe bei Mietbeginn in Gebieten mit angespannten Wohnungsmärkten', '§§ 556d–556g', []),
                        ('BGB-2-8-5-2-2-2', 'Unterkapitel 2 · Regelungen über die Miethöhe', '§§ 557–561', []),
                    ]),
                    ('BGB-2-8-5-2-3', 'Kapitel 3 · Pfandrecht des Vermieters', '§§ 562–562d', []),
                    ('BGB-2-8-5-2-4', 'Kapitel 4 · Wechsel der Vertragsparteien', '§§ 563–567b', []),
                    ('BGB-2-8-5-2-5', 'Kapitel 5 · Beendigung des Mietverhältnisses', '§§ 568–576b', [
                        ('BGB-2-8-5-2-5-1', 'Unterkapitel 1 · Allgemeine Vorschriften', '§§ 568–572', []),
                        ('BGB-2-8-5-2-5-2', 'Unterkapitel 2 · Mietverhältnisse auf unbestimmte Zeit', '§§ 573–574c', []),
                        ('BGB-2-8-5-2-5-3', 'Unterkapitel 3 · Mietverhältnisse auf bestimmte Zeit', '§§ 575–575a', []),
                        ('BGB-2-8-5-2-5-4', 'Unterkapitel 4 · Werkwohnungen', '§§ 576–576b', []),
                    ]),
                    ('BGB-2-8-5-2-6', 'Kapitel 6 · Besonderheiten bei der Bildung von Wohnungseigentum an vermieteten Wohnungen', '§§ 577–577a', []),
                ]),
                ('BGB-2-8-5-3', 'Untertitel 3 · Mietverhältnisse über andere Sachen und digitale Produkte', '§§ 578–580a', []),
                ('BGB-2-8-5-4', 'Untertitel 4 · Pachtvertrag', '§§ 581–584b', []),
                ('BGB-2-8-5-5', 'Untertitel 5 · Landpachtvertrag', '§§ 585–597', []),
            ]),
            ('BGB-2-8-6', 'Titel 6 · Leihe', '§§ 598–606', []),
            ('BGB-2-8-7', 'Titel 7 · Sachdarlehensvertrag', '§§ 607–610', []),
            ('BGB-2-8-8', 'Titel 8 · Dienstvertrag und ähnliche Verträge', '§§ 611–630h', [
                ('BGB-2-8-8-1', 'Untertitel 1 · Dienstvertrag', '§§ 611–630', []),
                ('BGB-2-8-8-2', 'Untertitel 2 · Behandlungsvertrag', '§§ 630a–630h', []),
            ]),
            ('BGB-2-8-9', 'Titel 9 · Werkvertrag und ähnliche Verträge', '§§ 631–651y', [
                ('BGB-2-8-9-1', 'Untertitel 1 · Werkvertrag', '§§ 631–650o', [
                    ('BGB-2-8-9-1-1', 'Kapitel 1 · Allgemeine Vorschriften', '§§ 631–650', []),
                    ('BGB-2-8-9-1-2', 'Kapitel 2 · Bauvertrag', '§§ 650a–650h', []),
                    ('BGB-2-8-9-1-3', 'Kapitel 3 · Verbraucherbauvertrag', '§§ 650i–650n', []),
                    ('BGB-2-8-9-1-4', 'Kapitel 4 · Unabdingbarkeit', '§ 650o', []),
                ]),
                ('BGB-2-8-9-2', 'Untertitel 2 · Architektenvertrag und Ingenieurvertrag', '§§ 650p–650t', []),
                ('BGB-2-8-9-3', 'Untertitel 3 · Bauträgervertrag', '§§ 650u–651', []),
                ('BGB-2-8-9-4', 'Untertitel 4 · Pauschalreisevertrag, Reisevermittlung und Vermittlung verbundener Reiseleistungen', '§§ 651a–651y', []),
            ]),
            ('BGB-2-8-10', 'Titel 10 · Maklervertrag', '§§ 652–656d', [
                ('BGB-2-8-10-1', 'Untertitel 1 · Allgemeine Vorschriften', '§§ 652–655', []),
                ('BGB-2-8-10-2', 'Untertitel 2 · Vermittlung von Verbraucherdarlehensverträgen und entgeltlichen Finanzierungshilfen', '§§ 655a–655e', []),
                ('BGB-2-8-10-3', 'Untertitel 3 · Ehevermittlung', '§ 656', []),
                ('BGB-2-8-10-4', 'Untertitel 4 · Vermittlung von Kaufverträgen über Wohnungen und Einfamilienhäuser', '§§ 656a–656d', []),
            ]),
            ('BGB-2-8-11', 'Titel 11 · Auslobung', '§§ 657–661a', []),
            ('BGB-2-8-12', 'Titel 12 · Auftrag, Geschäftsbesorgungsvertrag und Zahlungsdienste', '§§ 662–676c', [
                ('BGB-2-8-12-1', 'Untertitel 1 · Auftrag', '§§ 662–674', []),
                ('BGB-2-8-12-2', 'Untertitel 2 · Geschäftsbesorgungsvertrag', '§§ 675–675b', []),
                ('BGB-2-8-12-3', 'Untertitel 3 · Zahlungsdienste', '§§ 675c–676c', [
                    ('BGB-2-8-12-3-1', 'Kapitel 1 · Allgemeine Vorschriften', '§§ 675c–675e', []),
                    ('BGB-2-8-12-3-2', 'Kapitel 2 · Zahlungsdienstevertrag', '§§ 675f–675i', []),
                    ('BGB-2-8-12-3-3', 'Kapitel 3 · Erbringung und Nutzung von Zahlungsdiensten', '§§ 675j–676c', [
                        ('BGB-2-8-12-3-3-1', 'Unterkapitel 1 · Autorisierung von Zahlungsvorgängen; Zahlungsinstrumente; Verweigerung des Zugangs zum Zahlungskonto', '§§ 675j–675m', []),
                        ('BGB-2-8-12-3-3-2', 'Unterkapitel 2 · Ausführung von Zahlungsvorgängen', '§§ 675n–675t', []),
                        ('BGB-2-8-12-3-3-3', 'Unterkapitel 3 · Haftung', '§§ 675u–676c', []),
                    ]),
                ]),
            ]),
            ('BGB-2-8-13', 'Titel 13 · Geschäftsführung ohne Auftrag', '§§ 677–687', []),
            ('BGB-2-8-14', 'Titel 14 · Verwahrung', '§§ 688–700', []),
            ('BGB-2-8-15', 'Titel 15 · Einbringung von Sachen bei Gastwirten', '§§ 701–704', []),
            ('BGB-2-8-16', 'Titel 16 · Gesellschaft', '§§ 705–740c', [
                ('BGB-2-8-16-1', 'Untertitel 1 · Allgemeine Bestimmungen', '§ 705', []),
                ('BGB-2-8-16-2', 'Untertitel 2 · Rechtsfähige Gesellschaft', '§§ 706–739', [
                    ('BGB-2-8-16-2-1', 'Kapitel 1 · Sitz; Registrierung', '§§ 706–707d', []),
                    ('BGB-2-8-16-2-2', 'Kapitel 2 · Rechtsverhältnis der Gesellschafter untereinander und der Gesellschafter zur Gesellschaft', '§§ 708–718', []),
                    ('BGB-2-8-16-2-3', 'Kapitel 3 · Rechtsverhältnis der Gesellschaft zu Dritten', '§§ 719–722', []),
                    ('BGB-2-8-16-2-4', 'Kapitel 4 · Ausscheiden eines Gesellschafters', '§§ 723–728b', []),
                    ('BGB-2-8-16-2-5', 'Kapitel 5 · Auflösung der Gesellschaft', '§§ 729–734', []),
                    ('BGB-2-8-16-2-6', 'Kapitel 6 · Liquidation der Gesellschaft', '§§ 735–739', []),
                ]),
                ('BGB-2-8-16-3', 'Untertitel 3 · Nicht rechtsfähige Gesellschaft', '§§ 740–740c', []),
            ]),
            ('BGB-2-8-17', 'Titel 17 · Gemeinschaft', '§§ 741–758', []),
            ('BGB-2-8-18', 'Titel 18 · Leibrente', '§§ 759–761', []),
            ('BGB-2-8-19', 'Titel 19 · Unvollkommene Verbindlichkeiten', '§§ 762–764', []),
            ('BGB-2-8-20', 'Titel 20 · Bürgschaft', '§§ 765–778', []),
            ('BGB-2-8-21', 'Titel 21 · Vergleich', '§ 779', []),
            ('BGB-2-8-22', 'Titel 22 · Schuldversprechen, Schuldanerkenntnis', '§§ 780–782', []),
            ('BGB-2-8-23', 'Titel 23 · Anweisung', '§§ 783–792', []),
            ('BGB-2-8-24', 'Titel 24 · Schuldverschreibung auf den Inhaber', '§§ 793–808', []),
            ('BGB-2-8-25', 'Titel 25 · Vorlegung von Sachen', '§§ 809–811', []),
            ('BGB-2-8-26', 'Titel 26 · Ungerechtfertigte Bereicherung', '§§ 812–822', []),
            ('BGB-2-8-27', 'Titel 27 · Unerlaubte Handlungen', '§§ 823–853', []),
        ]),
    ]),
    ('BGB-3', 'Buch 3 · Sachenrecht', '§§ 854–1296', [
        ('BGB-3-1', 'Abschnitt 1 · Besitz', '§§ 854–872', []),
        ('BGB-3-2', 'Abschnitt 2 · Allgemeine Vorschriften über Rechte an Grundstücken', '§§ 873–902', []),
        ('BGB-3-3', 'Abschnitt 3 · Eigentum', '§§ 903–1011', [
            ('BGB-3-3-1', 'Titel 1 · Inhalt des Eigentums', '§§ 903–924', []),
            ('BGB-3-3-2', 'Titel 2 · Erwerb und Verlust des Eigentums an Grundstücken', '§§ 925–928', []),
            ('BGB-3-3-3', 'Titel 3 · Erwerb und Verlust des Eigentums an beweglichen Sachen', '§§ 929–984', [
                ('BGB-3-3-3-1', 'Untertitel 1 · Übertragung', '§§ 929–936', []),
                ('BGB-3-3-3-2', 'Untertitel 2 · Ersitzung', '§§ 937–945', []),
                ('BGB-3-3-3-3', 'Untertitel 3 · Verbindung, Vermischung, Verarbeitung', '§§ 946–952', []),
                ('BGB-3-3-3-4', 'Untertitel 4 · Erwerb von Erzeugnissen und sonstigen Bestandteilen einer Sache', '§§ 953–957', []),
                ('BGB-3-3-3-5', 'Untertitel 5 · Aneignung', '§§ 958–964', []),
                ('BGB-3-3-3-6', 'Untertitel 6 · Fund', '§§ 965–984', []),
            ]),
            ('BGB-3-3-4', 'Titel 4 · Ansprüche aus dem Eigentum', '§§ 985–1007', []),
            ('BGB-3-3-5', 'Titel 5 · Miteigentum', '§§ 1008–1011', []),
        ]),
        ('BGB-3-4', 'Abschnitt 4 · Dienstbarkeiten', '§§ 1018–1093', [
            ('BGB-3-4-1', 'Titel 1 · Grunddienstbarkeiten', '§§ 1018–1029', []),
            ('BGB-3-4-2', 'Titel 2 · Nießbrauch', '§§ 1030–1089', [
                ('BGB-3-4-2-1', 'Untertitel 1 · Nießbrauch an Sachen', '§§ 1030–1067', []),
                ('BGB-3-4-2-2', 'Untertitel 2 · Nießbrauch an Rechten', '§§ 1068–1084', []),
                ('BGB-3-4-2-3', 'Untertitel 3 · Nießbrauch an einem Vermögen', '§§ 1085–1089', []),
            ]),
            ('BGB-3-4-3', 'Titel 3 · Beschränkte persönliche Dienstbarkeiten', '§§ 1090–1093', []),
        ]),
        ('BGB-3-5', 'Abschnitt 5 · Vorkaufsrecht', '§§ 1094–1104', []),
        ('BGB-3-6', 'Abschnitt 6 · Reallasten', '§§ 1105–1112', []),
        ('BGB-3-7', 'Abschnitt 7 · Hypothek, Grundschuld, Rentenschuld', '§§ 1113–1203', [
            ('BGB-3-7-1', 'Titel 1 · Hypothek', '§§ 1113–1190', []),
            ('BGB-3-7-2', 'Titel 2 · Grundschuld, Rentenschuld', '§§ 1191–1203', [
                ('BGB-3-7-2-1', 'Untertitel 1 · Grundschuld', '§§ 1191–1198', []),
                ('BGB-3-7-2-2', 'Untertitel 2 · Rentenschuld', '§§ 1199–1203', []),
            ]),
        ]),
        ('BGB-3-8', 'Abschnitt 8 · Pfandrecht an beweglichen Sachen und an Rechten', '§§ 1204–1296', [
            ('BGB-3-8-1', 'Titel 1 · Pfandrecht an beweglichen Sachen', '§§ 1204–1259', []),
            ('BGB-3-8-2', 'Titel 2 · Pfandrecht an Rechten', '§§ 1273–1296', []),
        ]),
    ]),
    ('BGB-4', 'Buch 4 · Familienrecht', '§§ 1297–1888', [
        ('BGB-4-1', 'Abschnitt 1 · Bürgerliche Ehe', '§§ 1297–1588', [
            ('BGB-4-1-1', 'Titel 1 · Verlöbnis', '§§ 1297–1302', []),
            ('BGB-4-1-2', 'Titel 2 · Eingehung der Ehe', '§§ 1303–1312', [
                ('BGB-4-1-2-1', 'Untertitel 1 · Ehefähigkeit', '§§ 1303–1305', []),
                ('BGB-4-1-2-2', 'Untertitel 2 · Eheverbote', '§§ 1306–1308', []),
                ('BGB-4-1-2-3', 'Untertitel 3 · Ehefähigkeitszeugnis', '§ 1309', []),
                ('BGB-4-1-2-4', 'Untertitel 4 · Eheschließung', '§§ 1310–1312', []),
            ]),
            ('BGB-4-1-3', 'Titel 3 · Aufhebung der Ehe', '§§ 1313–1318', []),
            ('BGB-4-1-4', 'Titel 4 · Wiederverheiratung nach Todeserklärung', '§§ 1319–1320', []),
            ('BGB-4-1-5', 'Titel 5 · Wirkungen der Ehe im Allgemeinen', '§§ 1353–1362', []),
            ('BGB-4-1-6', 'Titel 6 · Eheliches Güterrecht', '§§ 1363–1519', [
                ('BGB-4-1-6-1', 'Untertitel 1 · Gesetzliches Güterrecht', '§§ 1363–1390', []),
                ('BGB-4-1-6-2', 'Untertitel 2 · Vertragliches Güterrecht', '§§ 1408–1519', [
                    ('BGB-4-1-6-2-1', 'Kapitel 1 · Allgemeine Vorschriften', '§§ 1408–1413', []),
                    ('BGB-4-1-6-2-2', 'Kapitel 2 · Gütertrennung', '§ 1414', []),
                    ('BGB-4-1-6-2-3', 'Kapitel 3 · Gütergemeinschaft', '§§ 1415–1518', [
                        ('BGB-4-1-6-2-3-1', 'Unterkapitel 1 · Allgemeine Vorschriften', '§§ 1415–1421', []),
                        ('BGB-4-1-6-2-3-2', 'Unterkapitel 2 · Verwaltung des Gesamtguts durch einen Ehegatten', '§§ 1422–1449', []),
                        ('BGB-4-1-6-2-3-3', 'Unterkapitel 3 · Gemeinschaftliche Verwaltung des Gesamtguts durch die Ehegatten', '§§ 1450–1470', []),
                        ('BGB-4-1-6-2-3-4', 'Unterkapitel 4 · Auseinandersetzung des Gesamtguts', '§§ 1471–1482', []),
                        ('BGB-4-1-6-2-3-5', 'Unterkapitel 5 · Fortgesetzte Gütergemeinschaft', '§§ 1483–1518', []),
                    ]),
                    ('BGB-4-1-6-2-4', 'Kapitel 4 · Wahl-Zugewinngemeinschaft', '§ 1519', []),
                ]),
            ]),
            ('BGB-4-1-7', 'Titel 7 · Scheidung der Ehe', '§§ 1564–1587', [
                ('BGB-4-1-7-1', 'Untertitel 1 · Scheidungsgründe', '§§ 1564–1568', []),
                ('BGB-4-1-7-1a', 'Untertitel 1a · Behandlung der Ehewohnung und der Haushaltsgegenstände anlässlich der Scheidung', '§§ 1568a–1568b', []),
                ('BGB-4-1-7-2', 'Untertitel 2 · Unterhalt des geschiedenen Ehegatten', '§§ 1569–1586b', [
                    ('BGB-4-1-7-2-1', 'Kapitel 1 · Grundsatz', '§ 1569', []),
                    ('BGB-4-1-7-2-2', 'Kapitel 2 · Unterhaltsberechtigung', '§§ 1570–1580', []),
                    ('BGB-4-1-7-2-3', 'Kapitel 3 · Leistungsfähigkeit und Rangfolge', '§§ 1581–1584', []),
                    ('BGB-4-1-7-2-4', 'Kapitel 4 · Gestaltung des Unterhaltsanspruchs', '§§ 1585–1585c', []),
                    ('BGB-4-1-7-2-5', 'Kapitel 5 · Ende des Unterhaltsanspruchs', '§§ 1586–1586b', []),
                ]),
                ('BGB-4-1-7-3', 'Untertitel 3 · Versorgungsausgleich', '§ 1587', []),
            ]),
            ('BGB-4-1-8', 'Titel 8 · Kirchliche Verpflichtungen', '§ 1588', []),
        ]),
        ('BGB-4-2', 'Abschnitt 2 · Verwandtschaft', '§§ 1589–1772', [
            ('BGB-4-2-1', 'Titel 1 · Allgemeine Vorschriften', '§§ 1589–1590', []),
            ('BGB-4-2-2', 'Titel 2 · Abstammung', '§§ 1591–1600d', []),
            ('BGB-4-2-3', 'Titel 3 · Unterhaltspflicht', '§§ 1601–1615n', [
                ('BGB-4-2-3-1', 'Untertitel 1 · Allgemeine Vorschriften', '§§ 1601–1615', []),
                ('BGB-4-2-3-2', 'Untertitel 2 · Besondere Vorschriften für das Kind und seine nicht miteinander verheirateten Eltern', '§§ 1615a–1615n', []),
            ]),
            ('BGB-4-2-4', 'Titel 4 · Rechtsverhältnis zwischen den Eltern und dem Kind im Allgemeinen', '§§ 1616–1625', []),
            ('BGB-4-2-5', 'Titel 5 · Elterliche Sorge', '§§ 1626–1698b', []),
            ('BGB-4-2-6', 'Titel 6 · Beistandschaft', '§§ 1712–1717', []),
            ('BGB-4-2-7', 'Titel 7 · Annahme als Kind', '§§ 1741–1772', [
                ('BGB-4-2-7-1', 'Untertitel 1 · Annahme Minderjähriger', '§§ 1741–1766a', []),
                ('BGB-4-2-7-2', 'Untertitel 2 · Annahme Volljähriger', '§§ 1767–1772', []),
            ]),
        ]),
        ('BGB-4-3', 'Abschnitt 3 · Vormundschaft, Pflegschaft für Minderjährige, rechtliche Betreuung, sonstige Pflegschaft', '§§ 1773–1888', [
            ('BGB-4-3-1', 'Titel 1 · Vormundschaft', '§§ 1773–1808', [
                ('BGB-4-3-1-1', 'Untertitel 1 · Begründung der Vormundschaft', '§§ 1773–1787', [
                    ('BGB-4-3-1-1-1', 'Kapitel 1 · Bestellte Vormundschaft', '§§ 1773–1785', [
                        ('BGB-4-3-1-1-1-1', 'Unterkapitel 1 · Allgemeine Vorschriften', '§§ 1773–1777', []),
                        ('BGB-4-3-1-1-1-2', 'Unterkapitel 2 · Auswahl des Vormunds', '§§ 1778–1785', []),
                    ]),
                    ('BGB-4-3-1-1-2', 'Kapitel 2 · Gesetzliche Amtsvormundschaft', '§§ 1786–1787', []),
                ]),
                ('BGB-4-3-1-2', 'Untertitel 2 · Führung der Vormundschaft', '§§ 1788–1801', [
                    ('BGB-4-3-1-2-1', 'Kapitel 1 · Allgemeine Vorschriften', '§§ 1788–1794', []),
                    ('BGB-4-3-1-2-2', 'Kapitel 2 · Personensorge', '§§ 1795–1797', []),
                    ('BGB-4-3-1-2-3', 'Kapitel 3 · Vermögenssorge', '§§ 1798–1801', []),
                ]),
                ('BGB-4-3-1-3', 'Untertitel 3 · Beratung und Aufsicht durch das Familiengericht', '§§ 1802–1803', []),
                ('BGB-4-3-1-4', 'Untertitel 4 · Beendigung der Vormundschaft', '§§ 1804–1807', []),
                ('BGB-4-3-1-5', 'Untertitel 5 · Vergütung und Aufwendungsersatz', '§ 1808', []),
            ]),
            ('BGB-4-3-2', 'Titel 2 · Pflegschaft für Minderjährige', '§§ 1809–1813', []),
            ('BGB-4-3-3', 'Titel 3 · Rechtliche Betreuung', '§§ 1814–1881', [
                ('BGB-4-3-3-1', 'Untertitel 1 · Betreuerbestellung', '§§ 1814–1820', []),
                ('BGB-4-3-3-2', 'Untertitel 2 · Führung der Betreuung', '§§ 1821–1860', [
                    ('BGB-4-3-3-2-1', 'Kapitel 1 · Allgemeine Vorschriften', '§§ 1821–1826', []),
                    ('BGB-4-3-3-2-2', 'Kapitel 2 · Personenangelegenheiten', '§§ 1827–1834', []),
                    ('BGB-4-3-3-2-3', 'Kapitel 3 · Vermögensangelegenheiten', '§§ 1835–1860', [
                        ('BGB-4-3-3-2-3-1', 'Unterkapitel 1 · Allgemeine Vorschriften', '§§ 1835–1837', []),
                        ('BGB-4-3-3-2-3-2', 'Unterkapitel 2 · Verwaltung von Geld, Wertpapieren und Wertgegenständen', '§§ 1838–1845', []),
                        ('BGB-4-3-3-2-3-3', 'Unterkapitel 3 · Anzeigepflichten', '§§ 1846–1847', []),
                        ('BGB-4-3-3-2-3-4', 'Unterkapitel 4 · Genehmigungsbedürftige Rechtsgeschäfte', '§§ 1848–1854', []),
                        ('BGB-4-3-3-2-3-5', 'Unterkapitel 5 · Genehmigungserklärung', '§§ 1855–1858', []),
                        ('BGB-4-3-3-2-3-6', 'Unterkapitel 6 · Befreiungen', '§§ 1859–1860', []),
                    ]),
                ]),
                ('BGB-4-3-3-3', 'Untertitel 3 · Beratung und Aufsicht durch das Betreuungsgericht', '§§ 1861–1867', []),
                ('BGB-4-3-3-4', 'Untertitel 4 · Beendigung, Aufhebung oder Änderung von Betreuung und Einwilligungsvorbehalt', '§§ 1868–1874', []),
                ('BGB-4-3-3-5', 'Untertitel 5 · Vergütung und Aufwendungsersatz', '§§ 1875–1881', []),
            ]),
            ('BGB-4-3-4', 'Titel 4 · Sonstige Pflegschaft', '§§ 1882–1888', []),
        ]),
    ]),
    ('BGB-5', 'Buch 5 · Erbrecht', '§§ 1922–2385', [
        ('BGB-5-1', 'Abschnitt 1 · Erbfolge', '§§ 1922–1941', []),
        ('BGB-5-2', 'Abschnitt 2 · Rechtliche Stellung des Erben', '§§ 1942–2063', [
            ('BGB-5-2-1', 'Titel 1 · Annahme und Ausschlagung der Erbschaft, Fürsorge des Nachlassgerichts', '§§ 1942–1966', []),
            ('BGB-5-2-2', 'Titel 2 · Haftung des Erben für die Nachlassverbindlichkeiten', '§§ 1967–2017', [
                ('BGB-5-2-2-1', 'Untertitel 1 · Nachlassverbindlichkeiten', '§§ 1967–1969', []),
                ('BGB-5-2-2-2', 'Untertitel 2 · Aufgebot der Nachlassgläubiger', '§§ 1970–1974', []),
                ('BGB-5-2-2-3', 'Untertitel 3 · Beschränkung der Haftung des Erben', '§§ 1975–1992', []),
                ('BGB-5-2-2-4', 'Untertitel 4 · Inventarerrichtung, unbeschränkte Haftung des Erben', '§§ 1993–2013', []),
                ('BGB-5-2-2-5', 'Untertitel 5 · Aufschiebende Einreden', '§§ 2014–2017', []),
            ]),
            ('BGB-5-2-3', 'Titel 3 · Erbschaftsanspruch', '§§ 2018–2031', []),
            ('BGB-5-2-4', 'Titel 4 · Mehrheit von Erben', '§§ 2032–2063', [
                ('BGB-5-2-4-1', 'Untertitel 1 · Rechtsverhältnis der Erben untereinander', '§§ 2032–2057a', []),
                ('BGB-5-2-4-2', 'Untertitel 2 · Rechtsverhältnis zwischen den Erben und den Nachlassgläubigern', '§§ 2058–2063', []),
            ]),
        ]),
        ('BGB-5-3', 'Abschnitt 3 · Testament', '§§ 2064–2273', [
            ('BGB-5-3-1', 'Titel 1 · Allgemeine Vorschriften', '§§ 2064–2086', []),
            ('BGB-5-3-2', 'Titel 2 · Erbeinsetzung', '§§ 2087–2099', []),
            ('BGB-5-3-3', 'Titel 3 · Einsetzung eines Nacherben', '§§ 2100–2146', []),
            ('BGB-5-3-4', 'Titel 4 · Vermächtnis', '§§ 2147–2191', []),
            ('BGB-5-3-5', 'Titel 5 · Auflage', '§§ 2192–2196', []),
            ('BGB-5-3-6', 'Titel 6 · Testamentsvollstrecker', '§§ 2197–2228', []),
            ('BGB-5-3-7', 'Titel 7 · Errichtung und Aufhebung eines Testaments', '§§ 2229–2264', []),
            ('BGB-5-3-8', 'Titel 8 · Gemeinschaftliches Testament', '§§ 2265–2273', []),
        ]),
        ('BGB-5-4', 'Abschnitt 4 · Erbvertrag', '§§ 2274–2302', []),
        ('BGB-5-5', 'Abschnitt 5 · Pflichtteil', '§§ 2303–2338', []),
        ('BGB-5-6', 'Abschnitt 6 · Erbunwürdigkeit', '§§ 2339–2345', []),
        ('BGB-5-7', 'Abschnitt 7 · Erbverzicht', '§§ 2346–2352', []),
        ('BGB-5-8', 'Abschnitt 8 · Erbschein', '§§ 2353–2370', []),
        ('BGB-5-9', 'Abschnitt 9 · Erbschaftskauf', '§§ 2371–2385', []),
    ]),
]
