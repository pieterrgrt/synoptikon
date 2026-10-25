"""Systematiek van het Belgische Burgerlijk Wetboek (2019) en het oud BW.

Het nieuwe BW wordt boek voor boek ingevoerd. De boeken 1, 2 (titel 3),
3, 4, 5, 6 en 8 zijn gegenereerd uit de wetten zoals bekendgemaakt in het
Belgisch Staatsblad (tekst via etaamb.openjustice.be; Justel zelf weigert
geautomatiseerde toegang), tot op afdelingsniveau, met de bereiken uit de
artikelnummers. Inwerkingtreding: Boek 8 1-11-2020, Boek 3 1-9-2021,
Boek 2 titel 3 en Boek 4 1-7-2022, Boeken 1 en 5 1-1-2023, Boek 6 1-1-2025.
Latere wijzigingen (sinds de bekendmaking) zijn niet verwerkt.

Boek 9 (Zekerheden) is in juli 2025 bekendgemaakt en zou op 1-1-2026 in
werking treden; de tekst stond bij het genereren niet in de mirror en de
indeling ontbreekt daarom. Boek 7 (bijzondere contracten) en Boek 10
(verjaring) zijn er nog niet: daarvoor geldt het oud BW (wet "oud BW"),
waarvan alleen de titels met hun 1804-bereik zijn opgenomen.
"""

BE = [
    ('BE-1', 'Boek 1 · Algemene bepalingen', 'art. 1.1–1.12', []),
    ('BE-2', 'Boek 2 · Personen, familie en relatievermogensrecht', 'art. 2.3.1–2.3.88', [
        ('BE-2-3', 'Titel 3 · Relatievermogensrecht', 'art. 2.3.1–2.3.88', [
            ('BE-2-3-1', 'Ondertitel 1 · Huwelijksvermogensrecht', 'art. 2.3.1–2.3.81', [
                ('BE-2-3-1-1', 'Hoofdstuk 1 · Huwelijksovereenkomsten', 'art. 2.3.1–2.3.11', []),
                ('BE-2-3-1-2', 'Hoofdstuk 2 · Algemene bepalingen', 'art. 2.3.12–2.3.15', []),
                ('BE-2-3-1-3', 'Hoofdstuk 3 · Wettelijk stelsel', 'art. 2.3.16–2.3.51', [
                    ('BE-2-3-1-3-1', 'Afdeling 1 · Eigen vermogens en gemeenschappelijk vermogen', 'art. 2.3.16–2.3.25', [
                        ('BE-2-3-1-3-1-1', 'Onderafdeling 1 · Algemene bepaling', 'art. 2.3.16', []),
                        ('BE-2-3-1-3-1-2', 'Onderafdeling 2 · Baten van de eigen vermogens', 'art. 2.3.17–2.3.19', []),
                        ('BE-2-3-1-3-1-3', 'Onderafdeling 3 · Bewijs en wederbelegging', 'art. 2.3.20–2.3.21', []),
                        ('BE-2-3-1-3-1-4', 'Onderafdeling 4 · Baten van het gemeenschappelijk vermogen', 'art. 2.3.22', []),
                        ('BE-2-3-1-3-1-5', 'Onderafdeling 5 · Lasten van de eigen vermogens en van het gemeenschappelijk vermogen', 'art. 2.3.23–2.3.25', []),
                    ]),
                    ('BE-2-3-1-3-2', 'Afdeling 2 · Rechten van de schuldeisers', 'art. 2.3.26–2.3.28', []),
                    ('BE-2-3-1-3-3', 'Afdeling 3 · Bestuur van het gemeenschappelijk vermogen', 'art. 2.3.29–2.3.38', []),
                    ('BE-2-3-1-3-4', 'Afdeling 4 · Bestuur van het eigen vermogen', 'art. 2.3.39', []),
                    ('BE-2-3-1-3-5', 'Afdeling 5 · Gemeenschappelijke bepaling met betrekking tot het bestuur van de eigen vermogens en het gemeenschappelijk vermogen', 'art. 2.3.40', []),
                    ('BE-2-3-1-3-6', 'Afdeling 6 · Ontbinding van het wettelijk stelsel', 'art. 2.3.41–2.3.51', [
                        ('BE-2-3-1-3-6-1', 'Onderafdeling 1 · Algemene bepalingen', 'art. 2.3.41–2.3.43', []),
                        ('BE-2-3-1-3-6-2', 'Onderafdeling 2 · Vergoedingsrekeningen', 'art. 2.3.44–2.3.47', []),
                        ('BE-2-3-1-3-6-3', 'Onderafdeling 3 · Verrekening van de lasten', 'art. 2.3.48', []),
                        ('BE-2-3-1-3-6-4', 'Onderafdeling 4 · Verrekening van de vergoedingen', 'art. 2.3.49', []),
                        ('BE-2-3-1-3-6-5', 'Onderafdeling 5 · Verdeling', 'art. 2.3.50', []),
                        ('BE-2-3-1-3-6-6', 'Onderafdeling 6 · Schulden tussen echtgenoten', 'art. 2.3.51', []),
                    ]),
                ]),
                ('BE-2-3-1-4', 'Hoofdstuk 4 · Overeenkomsten die het wettelijk stelsel kunnen wijzigen', 'art. 2.3.52–2.3.60', [
                    ('BE-2-3-1-4-1', 'Afdeling 1 · Algemene bepaling', 'art. 2.3.52', []),
                    ('BE-2-3-1-4-2', 'Afdeling 2 · Uitbreiding van het gemeenschappelijk vermogen', 'art. 2.3.53–2.3.54', []),
                    ('BE-2-3-1-4-3', 'Afdeling 3 · Bedingen tot afwijking van de wijze van vereffening of van verdeling', 'art. 2.3.55–2.3.60', []),
                ]),
                ('BE-2-3-1-5', 'Hoofdstuk 5 · Scheiding van goederen', 'art. 2.3.61–2.3.81', [
                    ('BE-2-3-1-5-1', 'Afdeling 1 · Conventionele scheiding van goederen', 'art. 2.3.61–2.3.77', []),
                    ('BE-2-3-1-5-2', 'Afdeling 2 · Gerechtelijke scheiding van goederen', 'art. 2.3.78–2.3.80', []),
                    ('BE-2-3-1-5-3', 'Afdeling 3 · Rechterlijke billijkheidscorrectie', 'art. 2.3.81', []),
                ]),
            ]),
            ('BE-2-3-2', 'Ondertitel 2 · Centraal register voor huwelijksovereenkomsten', 'art. 2.3.82–2.3.88', []),
        ]),
    ]),
    ('BE-3', 'Boek 3 · Goederen', 'art. 3.1–3.188', [
        ('BE-3-1', 'Titel 1 · Algemene bepalingen', 'art. 3.1–3.37', [
            ('BE-3-1-1', 'Ondertitel 1 · Statuut van de bepalingen', 'art. 3.1–3.2', []),
            ('BE-3-1-2', 'Ondertitel 2 · Algemene bepalingen inzake zakelijke rechten', 'art. 3.3–3.6', []),
            ('BE-3-1-3', 'Ondertitel 3 · Algemene bepalingen inzake het voorwerp van zakelijke rechten', 'art. 3.7–3.12', []),
            ('BE-3-1-4', 'Ondertitel 4 · Algemene bepalingen inzake het verkrijgen en tenietgaan van zakelijke rechten', 'art. 3.13–3.17', []),
            ('BE-3-1-5', 'Ondertitel 5 · Publiciteit van zakelijke rechten', 'art. 3.18–3.34', [
                ('BE-3-1-5-1', 'Hoofdstuk 1 · Feitelijke macht over de goederen', 'art. 3.18–3.29', [
                    ('BE-3-1-5-1-1', 'Afdeling 1 · Algemene bepalingen', 'art. 3.18–3.22', []),
                    ('BE-3-1-5-1-2', 'Afdeling 2 · Bewijsfunctie van bezit', 'art. 3.23–3.24', []),
                    ('BE-3-1-5-1-3', 'Afdeling 3 · Beschermende functie van bezit', 'art. 3.25', []),
                    ('BE-3-1-5-1-4', 'Afdeling 4 · Verkrijgende functie van bezit', 'art. 3.26–3.29', []),
                ]),
                ('BE-3-1-5-2', 'Hoofdstuk 2 · Regime van de onroerende publiciteit', 'art. 3.30–3.34', []),
            ]),
            ('BE-3-1-6', 'Ondertitel 6 · Vermogen', 'art. 3.35–3.37', [
                ('BE-3-1-6-1', 'Hoofdstuk 1 · Algemeen', 'art. 3.35–3.36', []),
                ('BE-3-1-6-2', 'Hoofdstuk 2 · Kwaliteitsrekeningen', 'art. 3.37', []),
            ]),
        ]),
        ('BE-3-2', 'Titel 2 · Indelingen van goederen', 'art. 3.38–3.49', [
            ('BE-3-2-1', 'Ondertitel 1 · Algemene categorieën', 'art. 3.38–3.42', []),
            ('BE-3-2-2', 'Ondertitel 2 · Kwalificaties volgens gebruik of toe-eigeningsmogelijkheid', 'art. 3.43–3.45', []),
            ('BE-3-2-3', 'Ondertitel 3 · Kwalificatie volgens onroerende of roerende aard', 'art. 3.46–3.49', []),
        ]),
        ('BE-3-3', 'Titel 3 · Eigendomsrecht', 'art. 3.50–3.67', [
            ('BE-3-3-1', 'Ondertitel 1 · Algemene bepalingen', 'art. 3.50–3.55', []),
            ('BE-3-3-2', 'Ondertitel 2 · Algemene bepalingen inzake roerende eigendom', 'art. 3.56–3.60', []),
            ('BE-3-3-3', 'Ondertitel 3 · Algemene bepalingen inzake onroerende eigendom', 'art. 3.61–3.67', []),
        ]),
        ('BE-3-4', 'Titel 4 · Mede-eigendom', 'art. 3.68–3.100', [
            ('BE-3-4-1', 'Ondertitel 1 · Toevallige mede-eigendom', 'art. 3.69–3.75', []),
            ('BE-3-4-2', 'Ondertitel 2 · Vrijwillige mede-eigendom', 'art. 3.76–3.77', []),
            ('BE-3-4-3', 'Ondertitel 3 · Gedwongen mede-eigendom', 'art. 3.78–3.100', [
                ('BE-3-4-3-1', 'Hoofdstuk 1 · Algemene bepalingen', 'art. 3.78–3.83', []),
                ('BE-3-4-3-2', 'Hoofdstuk 2 · Gedwongen mede-eigendom van gebouwen of groepen van gebouwen', 'art. 3.84–3.100', [
                    ('BE-3-4-3-2-1', 'Afdeling 1 · Algemene bepalingen', 'art. 3.84–3.85', []),
                    ('BE-3-4-3-2-2', 'Afdeling 2 · Rechtspersoonlijkheid van de vereniging van mede-eigenaars.', 'art. 3.86', []),
                    ('BE-3-4-3-2-3', 'Afdeling 3 · Organen van de vereniging van mede-eigenaars', 'art. 3.87–3.91', []),
                    ('BE-3-4-3-2-4', 'Afdeling 4 · Rechtsvorderingen - Openbaarheid - Tegenstelbaarheid en overdracht.', 'art. 3.92–3.96', []),
                    ('BE-3-4-3-2-5', 'Afdeling 5 · Ontbinding en vereffening', 'art. 3.97–3.99', []),
                    ('BE-3-4-3-2-6', 'Afdeling 6 · Dwingend karakter', 'art. 3.100', []),
                ]),
            ]),
        ]),
        ('BE-3-5', 'Titel 5 · Burenrelaties', 'art. 3.101–3.137', [
            ('BE-3-5-1', 'Ondertitel 1 · Burenhinder', 'art. 3.101–3.102', []),
            ('BE-3-5-2', 'Ondertitel 2 · Gemene afsluiting', 'art. 3.103–3.113', []),
            ('BE-3-5-3', 'Ondertitel 3 · Erfdienstbaarheden', 'art. 3.114–3.137', [
                ('BE-3-5-3-1', 'Hoofdstuk 1 · Algemene bepalingen', 'art. 3.114–3.116', []),
                ('BE-3-5-3-2', 'Hoofdstuk 2 · Erfdienstbaarheden door menselijk handelen', 'art. 3.117–3.128', [
                    ('BE-3-5-3-2-1', 'Afdeling 1 · Specifieke wijzen van verkrijging', 'art. 3.117–3.119', []),
                    ('BE-3-5-3-2-2', 'Afdeling 2 · Rechten en verplichtingen van de partijen', 'art. 3.120–3.125', []),
                    ('BE-3-5-3-2-3', 'Afdeling 3 · Specifieke wijzen van tenietgaan', 'art. 3.126–3.128', []),
                ]),
                ('BE-3-5-3-3', 'Hoofdstuk 3 · Wettelijke erfdienstbaarheden', 'art. 3.129–3.137', [
                    ('BE-3-5-3-3-1', 'Afdeling 1 · Water', 'art. 3.129–3.131', []),
                    ('BE-3-5-3-3-2', 'Afdeling 2 · Afstanden', 'art. 3.132–3.134', []),
                    ('BE-3-5-3-3-3', 'Afdeling 3 · Ingeslotenheid', 'art. 3.135–3.137', []),
                ]),
            ]),
        ]),
        ('BE-3-6', 'Titel 6 · Recht van vruchtgebruik', 'art. 3.138–3.166', [
            ('BE-3-6-1', 'Ondertitel 1 · Definitie, voorwerp en duurtijd', 'art. 3.138–3.141', []),
            ('BE-3-6-2', 'Ondertitel 2 · Rechten van de partijen', 'art. 3.142–3.149', []),
            ('BE-3-6-3', 'Ondertitel 3 · Verplichtingen van de partijen', 'art. 3.150–3.157', []),
            ('BE-3-6-4', 'Ondertitel 4 · Specifieke bepalingen inzake het tenietgaan', 'art. 3.158–3.161', []),
            ('BE-3-6-5', 'Ondertitel 5 · Specifieke bepalingen betreffende bijzondere goederen', 'art. 3.162–3.166', []),
        ]),
        ('BE-3-7', 'Titel 7 · Erfpachtrecht', 'art. 3.167–3.176', [
            ('BE-3-7-1', 'Ondertitel 1 · Definitie, voorwerp en duurtijd', 'art. 3.167–3.169', []),
            ('BE-3-7-2', 'Ondertitel 2 · Specifieke wijzen van verkrijging', 'art. 3.170', []),
            ('BE-3-7-3', 'Ondertitel 3 · Rechten en verplichtingen van de partijen', 'art. 3.171–3.173', []),
            ('BE-3-7-4', 'Ondertitel 4 · Specifieke wijzen van tenietgaan', 'art. 3.174–3.176', []),
        ]),
        ('BE-3-8', 'Titel 8 · Opstalrecht', 'art. 3.177–3.188', [
            ('BE-3-8-1', 'Ondertitel 1 · Definitie, voorwerp en duurtijd', 'art. 3.177–3.180', []),
            ('BE-3-8-2', 'Ondertitel 2 · Specifieke wijzen van verkrijging', 'art. 3.181–3.182', []),
            ('BE-3-8-3', 'Ondertitel 3 · Rechten en verplichtingen van de partijen', 'art. 3.183–3.185', []),
            ('BE-3-8-4', 'Ondertitel 4 · Specifieke wijzen van tenietgaan', 'art. 3.186–3.188', []),
        ]),
    ]),
    ('BE-4', 'Boek 4 · Nalatenschappen, schenkingen en testamenten', 'art. 4.1–4.266', [
        ('BE-4-1', 'Titel 1 · Nalatenschappen en wettelijke erfopvolging', 'art. 4.1–4.131', [
            ('BE-4-1-1', 'Ondertitel 1 · Algemene bepalingen', 'art. 4.1–4.3', []),
            ('BE-4-1-2', 'Ondertitel 2 · Hoedanigheden vereist om te erven', 'art. 4.4–4.5', []),
            ('BE-4-1-3', 'Ondertitel 3 · Onwaardigheid om te erven', 'art. 4.6–4.9', []),
            ('BE-4-1-4', 'Ondertitel 4 · Wettelijke erfopvolging', 'art. 4.10–4.31', [
                ('BE-4-1-4-1', 'Hoofdstuk 1 · Algemene bepalingen', 'art. 4.10–4.12', []),
                ('BE-4-1-4-2', 'Hoofdstuk 2 · Plaatsvervulling', 'art. 4.13–4.15', []),
                ('BE-4-1-4-3', 'Hoofdstuk 3 · Aanwezigheid van afstammelingen', 'art. 4.16', []),
                ('BE-4-1-4-4', 'Hoofdstuk 4 · Erfrechtelijke roeping van de echtgenoot en de wettelijk samenwonende', 'art. 4.17–4.23', [
                    ('BE-4-1-4-4-1', 'Afdeling 1 · De langstlevende echtgenoot', 'art. 4.17–4.22', []),
                    ('BE-4-1-4-4-2', 'Afdeling 2 · De langstlevende wettelijk samenwonende', 'art. 4.23', []),
                ]),
                ('BE-4-1-4-5', 'Hoofdstuk 5 · Recht van wettelijke terugkeer', 'art. 4.24–4.25', []),
                ('BE-4-1-4-6', 'Hoofdstuk 6 · Afwezigheid van afstammelingen en aanwezigheid van nauwe zijverwanten', 'art. 4.26–4.27', []),
                ('BE-4-1-4-7', 'Hoofdstuk 7 · Afwezigheid van afstammelingen en van nauwe zijverwanten', 'art. 4.28–4.30', []),
                ('BE-4-1-4-8', 'Hoofdstuk 8 · Nalatenschap van de kinderloos overleden geadopteerde', 'art. 4.31', []),
            ]),
            ('BE-4-1-5', 'Ondertitel 5 · Rechten van de Staat', 'art. 4.32–4.33', []),
            ('BE-4-1-6', 'Ondertitel 6 · Erfkeuze', 'art. 4.34–4.59', [
                ('BE-4-1-6-1', 'Hoofdstuk 1 · Algemene bepalingen', 'art. 4.34–4.40', []),
                ('BE-4-1-6-2', 'Hoofdstuk 2 · Zuivere aanvaarding van de nalatenschap', 'art. 4.41–4.43', []),
                ('BE-4-1-6-3', 'Hoofdstuk 3 · Verwerping van de nalatenschap', 'art. 4.44–4.48', []),
                ('BE-4-1-6-4', 'Hoofdstuk 4 · Aanvaarding onder voorrecht van boedelbeschrijving', 'art. 4.49–4.57', []),
                ('BE-4-1-6-5', 'Hoofdstuk 5 · Onbeheerde nalatenschappen', 'art. 4.58', []),
                ('BE-4-1-6-6', 'Hoofdstuk 6 · Bewijs van erfgenaamschap', 'art. 4.59', []),
            ]),
            ('BE-4-1-7', 'Ondertitel 7 · Omzetting van het vruchtgebruik van de langstlevende echtgenoot', 'art. 4.60–4.64', []),
            ('BE-4-1-8', 'Ondertitel 8 · Verdeling en inbreng', 'art. 4.65–4.105', [
                ('BE-4-1-8-1', 'Hoofdstuk 1 · Verdeling', 'art. 4.65–4.82', [
                    ('BE-4-1-8-1-1', 'Afdeling 1 · Algemene bepalingen', 'art. 4.65–4.68', []),
                    ('BE-4-1-8-1-2', 'Afdeling 2 · Vordering tot verdeling', 'art. 4.69–4.70', []),
                    ('BE-4-1-8-1-3', 'Afdeling 3 · Bepalingen die voor elke verdeling gelden', 'art. 4.71–4.77', []),
                    ('BE-4-1-8-1-4', 'Afdeling 4 · Bijzondere bepalingen', 'art. 4.78–4.80', []),
                    ('BE-4-1-8-1-5', 'Afdeling 5 · Overdracht van erfrechten en erfuitkoop', 'art. 4.81–4.82', []),
                ]),
                ('BE-4-1-8-2', 'Hoofdstuk 2 · Inbreng', 'art. 4.83–4.97', [
                    ('BE-4-1-8-2-1', 'Afdeling 1 · Inbreng van giften', 'art. 4.83–4.93', []),
                    ('BE-4-1-8-2-2', 'Afdeling 2 · Inbreng van schulden', 'art. 4.94–4.97', []),
                ]),
                ('BE-4-1-8-3', 'Hoofdstuk 3 · Schulden en lasten van de nalatenschap', 'art. 4.98–4.101', []),
                ('BE-4-1-8-4', 'Hoofdstuk 4 · Gevolgen van de verdeling en vrijwaring van de kavels', 'art. 4.102–4.103', []),
                ('BE-4-1-8-5', 'Hoofdstuk 5 · Betwisting van de verdeling', 'art. 4.104–4.105', []),
            ]),
            ('BE-4-1-9', 'Ondertitel 9 · Kleine nalatenschappen', 'art. 4.106–4.113', []),
            ('BE-4-1-10', 'Ondertitel 10 · Erfregeling landbouwbedrijven', 'art. 4.114–4.124', []),
            ('BE-4-1-11', 'Ondertitel 11 · Centraal erfrechtregister', 'art. 4.125–4.131', []),
        ]),
        ('BE-4-2', 'Titel 2 · Schenkingen, testamenten en erfovereenkomsten', 'art. 4.132–4.266', [
            ('BE-4-2-1', 'Ondertitel 1 · Algemene bepalingen', 'art. 4.132–4.134', []),
            ('BE-4-2-2', 'Ondertitel 2 · Bekwaamheid', 'art. 4.135–4.144', [
                ('BE-4-2-2-1', 'Hoofdstuk 1 · Algemene bepalingen', 'art. 4.135–4.137', []),
                ('BE-4-2-2-2', 'Hoofdstuk 2 · Minderjarigen en beschermde meerderjarigen', 'art. 4.138–4.139', []),
                ('BE-4-2-2-3', 'Hoofdstuk 3 · Specifieke onbekwaamheden', 'art. 4.140–4.144', []),
            ]),
            ('BE-4-2-3', 'Ondertitel 3 · Beschikbaar deel en inkorting', 'art. 4.145–4.157', [
                ('BE-4-2-3-1', 'Hoofdstuk 1 · Beschikbaar deel', 'art. 4.145–4.149', []),
                ('BE-4-2-3-2', 'Hoofdstuk 2 · Inkorting', 'art. 4.150–4.157', []),
            ]),
            ('BE-4-2-4', 'Ondertitel 4 · Schenkingen', 'art. 4.158–4.177', [
                ('BE-4-2-4-1', 'Hoofdstuk 1 · Vorm van de schenkingen', 'art. 4.158–4.160', []),
                ('BE-4-2-4-2', 'Hoofdstuk 2 · Aanvaarding van de schenkingen', 'art. 4.161–4.167', []),
                ('BE-4-2-4-3', 'Hoofdstuk 3 · Voorwerp en modaliteiten van de schenkingen', 'art. 4.168–4.172', []),
                ('BE-4-2-4-4', 'Hoofdstuk 4 · Ontbinding en herroeping van schenkingen', 'art. 4.173–4.177', []),
            ]),
            ('BE-4-2-5', 'Ondertitel 5 · Testamenten', 'art. 4.178–4.219', [
                ('BE-4-2-5-1', 'Hoofdstuk 1 · Vormen van de testamenten', 'art. 4.178–4.191', [
                    ('BE-4-2-5-1-1', 'Afdeling 1 · Algemene bepalingen', 'art. 4.178–4.180', []),
                    ('BE-4-2-5-1-2', 'Afdeling 2 · Vormvereisten', 'art. 4.181–4.185', []),
                    ('BE-4-2-5-1-3', 'Afdeling 3 · Bijzonder toegelaten testamentsvormen', 'art. 4.186–4.189', []),
                    ('BE-4-2-5-1-4', 'Afdeling 4 · Sanctionering', 'art. 4.190', []),
                    ('BE-4-2-5-1-5', 'Afdeling 5 · Formaliteiten na overlijden', 'art. 4.191', []),
                ]),
                ('BE-4-2-5-2', 'Hoofdstuk 2 · Legaten', 'art. 4.192–4.219', [
                    ('BE-4-2-5-2-1', 'Afdeling 1 · Algemene bepaling', 'art. 4.192', []),
                    ('BE-4-2-5-2-2', 'Afdeling 2 · Algemeen legaat', 'art. 4.193–4.194', []),
                    ('BE-4-2-5-2-3', 'Afdeling 3 · Legaat onder algemene titel', 'art. 4.195–4.196', []),
                    ('BE-4-2-5-2-4', 'Afdeling 4 · Gemeenschappelijke bepalingen voor legaten met een algemene roeping of met een roeping onder algemene titel', 'art. 4.197–4.200', []),
                    ('BE-4-2-5-2-5', 'Afdeling 5 · Bijzondere legaten', 'art. 4.201–4.206', []),
                    ('BE-4-2-5-2-6', 'Afdeling 6 · Bijzondere bepalingen inzake legaten', 'art. 4.207–4.210', []),
                    ('BE-4-2-5-2-7', 'Afdeling 7 · Testamentuitvoerder', 'art. 4.211–4.214', []),
                    ('BE-4-2-5-2-8', 'Afdeling 8 · Herroeping en verval van testamenten', 'art. 4.215–4.219', []),
                ]),
            ]),
            ('BE-4-2-6', 'Ondertitel 6 · Toegelaten gift met bewaarplicht ten voordele van derden', 'art. 4.220–4.228', []),
            ('BE-4-2-7', 'Ondertitel 7 · Ouderlijke boedelverdeling', 'art. 4.229–4.231', []),
            ('BE-4-2-8', 'Ondertitel 8 · Schenkingen ten voordele van het huwelijk', 'art. 4.232–4.236', []),
            ('BE-4-2-9', 'Ondertitel 9 · Schenkingen tussen echtgenoten', 'art. 4.237–4.241', []),
            ('BE-4-2-10', 'Ondertitel 10 · Erfovereenkomsten', 'art. 4.243–4.259', [
                ('BE-4-2-10-2', 'Hoofdstuk 2 · Sanctionering van niet toegelaten erfovereenkomsten', 'art. 4.245', []),
                ('BE-4-2-10-3', 'Hoofdstuk 3 · Gevolgen van de erfovereenkomsten', 'art. 4.246–4.248', []),
                ('BE-4-2-10-4', 'Hoofdstuk 4 · Vorm van de erfovereenkomsten', 'art. 4.249–4.252', []),
                ('BE-4-2-10-5', 'Hoofdstuk 5 · Publiciteit van de erfovereenkomsten', 'art. 4.253', []),
                ('BE-4-2-10-6', 'Hoofdstuk 6 · De globale erfovereenkomst', 'art. 4.254–4.259', []),
            ]),
            ('BE-4-2-11', 'Ondertitel 11 · Centraal register van testamenten', 'art. 4.260–4.266', []),
        ]),
    ]),
    ('BE-5', 'Boek 5 · Verbintenissen', 'art. 5.1–5.270', [
        ('BE-5-1', 'Titel 1 · Inleidende bepalingen', 'art. 5.1–5.3', []),
        ('BE-5-2', 'Titel 2 · Bronnen van verbintenissen', 'art. 5.4–5.137', [
            ('BE-5-2-1', 'Ondertitel 1 · Rechtshandelingen', 'art. 5.4–5.126', [
                ('BE-5-2-1-1', 'Hoofdstuk 1 · Contract', 'art. 5.4–5.124', [
                    ('BE-5-2-1-1-1', 'Afdeling 1 · Inleidende bepalingen', 'art. 5.4–5.13', []),
                    ('BE-5-2-1-1-2', 'Afdeling 2 · Totstandkoming van het contract', 'art. 5.14–5.63', [
                        ('BE-5-2-1-1-2-1', 'Onderafdeling 1 · Dynamische totstandkoming van het contract', 'art. 5.14–5.26', []),
                        ('BE-5-2-1-1-2-2', 'Onderafdeling 2 · Geldigheidsvereisten', 'art. 5.27–5.56', []),
                        ('BE-5-2-1-1-2-3', 'Onderafdeling 3 · Nietigheid', 'art. 5.57–5.63', []),
                    ]),
                    ('BE-5-2-1-1-3', 'Afdeling 3 · Interpretatie en kwalificatie van het contract', 'art. 5.64–5.68', [
                        ('BE-5-2-1-1-3-1', 'Onderafdeling 1 · Interpretatie van het contract', 'art. 5.64–5.66', []),
                        ('BE-5-2-1-1-3-2', 'Onderafdeling 2 · Kwalificatie van het contract', 'art. 5.67–5.68', []),
                    ]),
                    ('BE-5-2-1-1-4', 'Afdeling 4 · Gevolgen van het contract tussen partijen', 'art. 5.69–5.81', [
                        ('BE-5-2-1-1-4-1', 'Onderafdeling 1 · Bindende kracht', 'art. 5.69–5.74', []),
                        ('BE-5-2-1-1-4-2', 'Onderafdeling 2 · Duur van het contract', 'art. 5.75–5.78', []),
                        ('BE-5-2-1-1-4-3', 'Onderafdeling 3 · Eigendomsoverdragend gevolg van bepaalde contracten', 'art. 5.79–5.81', []),
                    ]),
                    ('BE-5-2-1-1-5', 'Afdeling 5 · Niet-nakoming van de contractuele verbintenis en gevolgen', 'art. 5.82–5.102', [
                        ('BE-5-2-1-1-5-1', 'Onderafdeling 1 · Toerekenbare niet-nakoming van de schuldenaar', 'art. 5.82–5.98', []),
                        ('BE-5-2-1-1-5-2', 'Onderafdeling 2 · Ontoerekenbare niet-nakoming', 'art. 5.99–5.102', []),
                    ]),
                    ('BE-5-2-1-1-6', 'Afdeling 6 · Gevolgen van het contract voor derden', 'art. 5.103–5.111', []),
                    ('BE-5-2-1-1-7', 'Afdeling 7 · Tenietgaan van het contract', 'art. 5.112–5.124', [
                        ('BE-5-2-1-1-7-1', 'Onderafdeling 1 · Gronden van tenietgaan', 'art. 5.112–5.114', []),
                        ('BE-5-2-1-1-7-2', 'Onderafdeling 2 · Restitutie', 'art. 5.115–5.124', []),
                    ]),
                ]),
                ('BE-5-2-1-2', 'Hoofdstuk 2 · Eenzijdige rechtshandeling', 'art. 5.125–5.126', []),
            ]),
            ('BE-5-2-2', 'Ondertitel 2 · Rechtsfeiten', 'art. 5.127–5.137', [
                ('BE-5-2-2-1', 'Hoofdstuk 1 · Inleidende bepaling', 'art. 5.127', []),
                ('BE-5-2-2-2', 'Hoofdstuk 2 · Zaakwaarneming', 'art. 5.128–5.132', []),
                ('BE-5-2-2-3', 'Hoofdstuk 3 · Onverschuldigde betaling', 'art. 5.133–5.134', []),
                ('BE-5-2-2-4', 'Hoofdstuk 4 · Ongerechtvaardigde verrijking', 'art. 5.135–5.137', []),
            ]),
        ]),
        ('BE-5-3', 'Titel 3 · Algemeen regime van de verbintenis', 'art. 5.138–5.270', [
            ('BE-5-3-1', 'Ondertitel 1 · Inleidende bepaling', 'art. 5.138', []),
            ('BE-5-3-2', 'Ondertitel 2 · Modaliteiten van de verbintenis', 'art. 5.139–5.155', [
                ('BE-5-3-2-1', 'Hoofdstuk 1 · Voorwaardelijke verbintenis', 'art. 5.139–5.148', []),
                ('BE-5-3-2-2', 'Hoofdstuk 2 · Verbintenis met tijdsbepaling', 'art. 5.149–5.155', []),
            ]),
            ('BE-5-3-3', 'Ondertitel 3 · Verbintenissen met pluraliteit van voorwerpen of subjecten', 'art. 5.156–5.173', [
                ('BE-5-3-3-1', 'Hoofdstuk 1 · Verbintenissen met pluraliteit van voorwerpen', 'art. 5.156–5.158', []),
                ('BE-5-3-3-2', 'Hoofdstuk 2 · Verbintenissen met pluraliteit van subjecten', 'art. 5.159–5.173', [
                    ('BE-5-3-3-2-1', 'Afdeling 1 · Beginsel van de verdeling', 'art. 5.159', []),
                    ('BE-5-3-3-2-2', 'Afdeling 2 · Hoofdelijkheid tussen schuldenaars', 'art. 5.160–5.165', []),
                    ('BE-5-3-3-2-3', 'Afdeling 3 · Ondeelbaarheid tussen schuldenaars', 'art. 5.166–5.167', []),
                    ('BE-5-3-3-2-4', 'Afdeling 4 · Verbintenissen in solidum', 'art. 5.168–5.169', []),
                    ('BE-5-3-3-2-5', 'Afdeling 5 · Hoofdelijkheid en ondeelbaarheid tussen schuldeisers', 'art. 5.170–5.173', []),
                ]),
            ]),
            ('BE-5-3-4', 'Ondertitel 4 · Overdracht van verbintenissen', 'art. 5.174–5.193', [
                ('BE-5-3-4-1', 'Hoofdstuk 1 · Overdracht van schuldvordering', 'art. 5.174–5.186', [
                    ('BE-5-3-4-1-1', 'Afdeling 1 · Voorwerp', 'art. 5.174–5.178', []),
                    ('BE-5-3-4-1-2', 'Afdeling 2 · Tegenwerpelijkheid aan derden', 'art. 5.179–5.183', []),
                    ('BE-5-3-4-1-3', 'Afdeling 3 · Verbintenissen van partijen', 'art. 5.184–5.186', []),
                ]),
                ('BE-5-3-4-2', 'Hoofdstuk 2 · Overdracht van schuld', 'art. 5.187–5.192', []),
                ('BE-5-3-4-3', 'Hoofdstuk 3 · Overdracht van contract', 'art. 5.193', []),
            ]),
            ('BE-5-3-5', 'Ondertitel 5 · Nakoming van de verbintenis', 'art. 5.194–5.223', [
                ('BE-5-3-5-1', 'Hoofdstuk 1 · Inleidende bepaling', 'art. 5.194', []),
                ('BE-5-3-5-2', 'Hoofdstuk 2 · Betaling', 'art. 5.195–5.216', [
                    ('BE-5-3-5-2-1', 'Afdeling 1 · Gemeenschappelijke bepalingen', 'art. 5.195–5.204', []),
                    ('BE-5-3-5-2-2', 'Afdeling 2 · Bijzondere bepalingen voor de geldelijke verbintenissen', 'art. 5.205–5.207', []),
                    ('BE-5-3-5-2-3', 'Afdeling 3 · Toerekening van betalingen', 'art. 5.208–5.210', []),
                    ('BE-5-3-5-2-4', 'Afdeling 4 · Schuldeisersverzuim', 'art. 5.211–5.216', []),
                ]),
                ('BE-5-3-5-3', 'Hoofdstuk 3 · Betaling met subrogatie', 'art. 5.217–5.223', []),
            ]),
            ('BE-5-3-6', 'Ondertitel 6 · Niet-nakoming van de verbintenis', 'art. 5.224–5.241', [
                ('BE-5-3-6-1', 'Hoofdstuk 1 · Inleidende bepaling', 'art. 5.224', []),
                ('BE-5-3-6-2', 'Hoofdstuk 2 · Toerekenbaarheid van de niet-nakoming', 'art. 5.225–5.230', []),
                ('BE-5-3-6-3', 'Hoofdstuk 3 · Ingebrekestelling', 'art. 5.231–5.233', []),
                ('BE-5-3-6-4', 'Hoofdstuk 4 · Uitvoering in natura', 'art. 5.234–5.236', []),
                ('BE-5-3-6-5', 'Hoofdstuk 5 · Herstel van de schade', 'art. 5.237–5.238', []),
                ('BE-5-3-6-6', 'Hoofdstuk 6 · Opschortingsrecht', 'art. 5.239', []),
                ('BE-5-3-6-7', 'Hoofdstuk 7 · Nalatigheidsinterest', 'art. 5.240–5.241', []),
            ]),
            ('BE-5-3-7', 'Ondertitel 7 · Maatregelen ter bescherming van de rechten van de schuldeiser', 'art. 5.242–5.243', []),
            ('BE-5-3-8', 'Ondertitel 8 · Gronden van tenietgaan van de verbintenis', 'art. 5.244–5.270', [
                ('BE-5-3-8-1', 'Hoofdstuk 1 · Algemene bepaling', 'art. 5.244', []),
                ('BE-5-3-8-2', 'Hoofdstuk 2 · Schuldvernieuwing', 'art. 5.245–5.249', []),
                ('BE-5-3-8-3', 'Hoofdstuk 3 · Kwijtschelding van schuld en de eenzijdige afstand', 'art. 5.250–5.253', []),
                ('BE-5-3-8-4', 'Hoofdstuk 4 · Schuldvergelijking', 'art. 5.254–5.264', []),
                ('BE-5-3-8-5', 'Hoofdstuk 5 · Verval van de verbintenis door verdwijning van het voorwerp', 'art. 5.265–5.267', []),
                ('BE-5-3-8-6', 'Hoofdstuk 6 · Schuldvermenging', 'art. 5.268–5.270', []),
            ]),
        ]),
    ]),
    ('BE-6', 'Boek 6 · Buitencontractuele aansprakelijkheid', 'art. 6.1–6.55', [
        ('BE-6-1', 'Hoofdstuk 1 · Inleidende bepalingen', 'art. 6.1–6.4', [
            ('BE-6-1-1', 'Afdeling 1 · Algemene bepaling', 'art. 6.1', []),
            ('BE-6-1-2', 'Afdeling 2 · Samenloop', 'art. 6.2–6.3', []),
            ('BE-6-1-3', 'Afdeling 3 · Rechtspersonen', 'art. 6.4', []),
        ]),
        ('BE-6-2', 'Hoofdstuk 2 · Feiten die tot aansprakelijkheid leiden', 'art. 6.5–6.17', [
            ('BE-6-2-1', 'Afdeling 1 · Aansprakelijkheid voor eigen daad', 'art. 6.5–6.11', [
                ('BE-6-2-1-1', 'Onderafdeling 1 · Fout', 'art. 6.5–6.6', []),
                ('BE-6-2-1-2', 'Onderafdeling 2 · Gronden van uitsluiting van aansprakelijkheid voor fout', 'art. 6.7–6.8', []),
                ('BE-6-2-1-3', 'Onderafdeling 3 · Aansprakelijkheid van minderjarigen en geestesgestoorden', 'art. 6.9–6.11', []),
            ]),
            ('BE-6-2-2', 'Afdeling 2 · Aansprakelijkheid voor andermans daad', 'art. 6.12–6.15', []),
            ('BE-6-2-3', 'Afdeling 3 · Aansprakelijkheid voor zaken en dieren', 'art. 6.16–6.17', []),
        ]),
        ('BE-6-3', 'Hoofdstuk 3 · Oorzakelijk verband', 'art. 6.18–6.23', [
            ('BE-6-3-1', 'Afdeling 1 · Basisregels', 'art. 6.18', []),
            ('BE-6-3-2', 'Afdeling 2 · Pluraliteit van aansprakelijken', 'art. 6.19–6.21', []),
            ('BE-6-3-3', 'Afdeling 3 · Causale onzekerheid - Proportionele aansprakelijkheid', 'art. 6.22', []),
        ]),
        ('BE-6-4', 'Hoofdstuk 4 · Schade', 'art. 6.24–6.29', []),
        ('BE-6-5', 'Hoofdstuk 5 · Gevolgen van aansprakelijkheid', 'art. 6.30–6.39', [
            ('BE-6-5-1', 'Afdeling 1 · Basisregels', 'art. 6.30–6.32', []),
            ('BE-6-5-2', 'Afdeling 2 · Herstel in natura', 'art. 6.33', []),
            ('BE-6-5-3', 'Afdeling 3 · Raming van de schade', 'art. 6.34–6.39', []),
        ]),
        ('BE-6-6', 'Hoofdstuk 6 · Bevel of verbod', 'art. 6.40', []),
        ('BE-6-7', 'Hoofdstuk 7 · Bijzondere aansprakelijkheidsregimes', 'art. 6.41–6.55', [
            ('BE-6-7-1', 'Afdeling 1 · Aansprakelijkheid voor gebrekkige producten', 'art. 6.41–6.55', []),
        ]),
    ]),
    ('BE-8', 'Boek 8 · Bewijs', 'art. 8.1–8.39', [
        ('BE-8-1', 'Hoofdstuk 1 · Algemene bepalingen', 'art. 8.1–8.7', [
            ('BE-8-1-1', 'Afdeling 1 · Definities', 'art. 8.1', []),
            ('BE-8-1-2', 'Afdeling 2 · Aanvullend karakter van de bewijsregels', 'art. 8.2', []),
            ('BE-8-1-3', 'Afdeling 3 · Voorwerp van het bewijs', 'art. 8.3', []),
            ('BE-8-1-4', 'Afdeling 4 · Bewijslast', 'art. 8.4', []),
            ('BE-8-1-5', 'Afdeling 5 · Bewijsstandaard', 'art. 8.5–8.6', []),
            ('BE-8-1-6', 'Afdeling 6 · Wettelijke vermoedens', 'art. 8.7', []),
        ]),
        ('BE-8-2', 'Hoofdstuk 2 · Toelaatbaarheid van de bewijsmiddelen', 'art. 8.8–8.14', [
            ('BE-8-2-1', 'Afdeling 1 · Algemene bepalingen', 'art. 8.8–8.9', []),
            ('BE-8-2-2', 'Afdeling 2 · Uitzonderingen op het gereglementeerde bewijsstelsel', 'art. 8.10–8.14', []),
        ]),
        ('BE-8-3', 'Hoofdstuk 3 · Bewijsmiddelen', 'art. 8.15–8.39', [
            ('BE-8-3-1', 'Afdeling 1 · Bewijs door ondertekend geschrift', 'art. 8.15–8.27', [
                ('BE-8-3-1-1', 'Onderafdeling 1 · Authentieke akte', 'art. 8.15–8.17', []),
                ('BE-8-3-1-2', 'Onderafdeling 2 · Onderhandse akte', 'art. 8.18–8.22', []),
                ('BE-8-3-1-3', 'Onderafdeling 3 · Onderhandse akte die mede wordt ondertekend door de advocaten van de partijen', 'art. 8.23', []),
                ('BE-8-3-1-4', 'Onderafdeling 4 · Andere geschriften', 'art. 8.24', []),
                ('BE-8-3-1-5', 'Onderafdeling 5 · Afschriften', 'art. 8.25–8.26', []),
                ('BE-8-3-1-6', 'Onderafdeling 6 · Teruggave van de akte door de schuldeiser aan de schuldenaar', 'art. 8.27', []),
            ]),
            ('BE-8-3-2', 'Afdeling 2 · Bewijs door getuigen', 'art. 8.28', []),
            ('BE-8-3-3', 'Afdeling 3 · Bewijs door feitelijke vermoedens', 'art. 8.29', []),
            ('BE-8-3-4', 'Afdeling 4 · Bekentenis', 'art. 8.30–8.32', []),
            ('BE-8-3-5', 'Afdeling 5 · Eed', 'art. 8.33–8.39', [
                ('BE-8-3-5-1', 'Onderafdeling 1 · Beslissende eed', 'art. 8.34–8.37', []),
                ('BE-8-3-5-2', 'Onderafdeling 2 · Ambtshalve opgelegde eed', 'art. 8.38–8.39', []),
            ]),
        ]),
    ]),
]

# Oud BW: titels uit de oorspronkelijke Code civil van 1804, nog geldend tot hercodificatie.
OUD_BW = [
    ('BE-OBW', 'Oud Burgerlijk Wetboek (1804) · wat nog niet hercodificeerd is', '', [
        ('BE-OBW-I', 'Boek I · Personen', 'art. 7–515', []),
        ('BE-OBW-III-6', 'Boek III Titel VI · Koop', 'art. 1582–1701', []),
        ('BE-OBW-III-7', 'Boek III Titel VII · Ruil', 'art. 1702–1707', []),
        ('BE-OBW-III-8', 'Boek III Titel VIII · Huur', 'art. 1708–1831', []),
        ('BE-OBW-III-10', 'Boek III Titel X · Lening', 'art. 1874–1914', []),
        ('BE-OBW-III-11', 'Boek III Titel XI · Bewaargeving en sekwestratie', 'art. 1915–1963', []),
        ('BE-OBW-III-12', 'Boek III Titel XII · Kanscontracten', 'art. 1964–1983', []),
        ('BE-OBW-III-13', 'Boek III Titel XIII · Lastgeving', 'art. 1984–2010', []),
        ('BE-OBW-III-15', 'Boek III Titel XV · Dading', 'art. 2044–2058', []),
        ('BE-OBW-III-20', 'Boek III Titel XX · Verjaring', 'art. 2219–2281', []),
    ], 'oud BW'),
]
