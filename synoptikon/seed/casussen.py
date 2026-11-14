"""Drie voorbeeldcasussen voor de Klausurtrainer: BGB Allgemeiner Teil en Allgemeines Schuldrecht, niveau AG-Fall.

Eigen werk, geschreven aan de hand van de lokale BGB-tekst; elke norm hieronder is tegen die tekst nagelopen (bestaan en
strekking), de oplossingen volgen de wet en de heersende leer. Ze laden met `geverifieerd=False`: de app toont de
Lösungsskizze als "niet geverifieerd" tot Pieter haar zelf heeft nagekeken. Sachverhalt en Fallfrage in het Duits, zoals
in de Klausur; de toelichting bij de skizze in het Nederlands met de Duitse vaktermen.

Vorm van `skizze`: zie `Casus.skizze` (niveau 1 = Anspruch, 2 = Voraussetzung, 3 = onderpunt).
"""
from __future__ import annotations


def _p(niveau: int, titel: str, inhoud: str = "", normen: tuple[str, ...] = (), groep: str = "overig", probleem: bool = False) -> dict:
    return {"niveau": niveau, "titel": titel, "groep": groep, "normen": list(normen), "inhoud": inhoud, "probleem": probleem}


CASUSSEN: list[dict] = [
    {
        "sleutel": "vertippter-preis",
        "titel": "Der vertippte Preis",
        "onderwerp": "Anfechtung wegen Erklärungsirrtums, Ersatz des Vertrauensschadens",
        "niveau": "ag",
        "vak": "ZR Ia",
        "sachverhalt": (
            "V betreibt einen kleinen Fahrradladen in Berlin. K interessiert sich für ein bestimmtes gebrauchtes Rennrad aus dem Laden "
            "und bittet V per E-Mail um ein Angebot. V will das Rad, das 980 € wert ist, für 980 € anbieten. Beim Schreiben der E-Mail "
            "vertippt er sich und schreibt: „Ich biete Ihnen das Rennrad für 890 € an.“ K antwortet noch am selben Tag per E-Mail: "
            "„Einverstanden, ich nehme Ihr Angebot an.“\n\n"
            "Im Vertrauen auf den Kauf bestellt K am nächsten Tag bei einem Online-Händler Klickpedale für 60 €, die nur an dieses "
            "Rennrad passen und die er nicht zurückgeben kann.\n\n"
            "Als V drei Tage später die Rechnung schreiben will, bemerkt er seinen Tippfehler. Er ruft K sofort an, erklärt ihm das "
            "Versehen und sagt, zu 890 € lasse er sich an dem Geschäft nicht festhalten. K besteht auf Lieferung des Rades zum Preis "
            "von 890 €. Jedenfalls will er die 60 € für die Pedale ersetzt haben."
        ),
        "fallfrage": (
            "1. Kann K von V Übergabe und Übereignung des Rennrads Zug um Zug gegen Zahlung von 890 € verlangen?\n"
            "2. Kann K von V Ersatz der 60 € verlangen?"
        ),
        "normen": ["§ 433 Abs. 1 S. 1 BGB", "§ 130 Abs. 1 S. 1 BGB", "§ 133 BGB", "§ 157 BGB", "§ 119 Abs. 1 BGB", "§ 121 Abs. 1 S. 1 BGB",
                   "§ 142 Abs. 1 BGB", "§ 143 Abs. 1 BGB", "§ 143 Abs. 2 BGB", "§ 122 Abs. 1 BGB", "§ 122 Abs. 2 BGB"],
        "skizze": [
            _p(1, "A. Anspruch K gegen V auf Übergabe und Übereignung aus § 433 Abs. 1 S. 1 BGB", normen=("§ 433 Abs. 1 S. 1 BGB",), groep="vertrag"),
            _p(2, "I. Anspruch entstanden: Kaufvertrag", "Twee overeenstemmende Willenserklärungen, Angebot en Annahme (§§ 145 ff. BGB).",
               ("§ 145 BGB", "§ 147 BGB")),
            _p(3, "1. Angebot des V", "De e-mail van V is een Angebot, geen invitatio ad offerendum: ze richt zich tot K en noemt zaak en prijs. "
               "Inhoud door Auslegung vanuit de objektiver Empfängerhorizont: 890 €. Wat V wilde (980 €) was voor K niet kenbaar. "
               "Wirksam met Zugang bij K.", ("§ 133 BGB", "§ 157 BGB", "§ 130 Abs. 1 S. 1 BGB"), probleem=True),
            _p(3, "2. Annahme des K", "K neemt dezelfde dag aan, dus tijdig; de Kaufvertrag over 890 € is gesloten.", ("§ 147 Abs. 2 BGB",)),
            _p(2, "II. Anspruch erloschen: Anfechtung", "De Willenserklärung van V is van aanvang af nichtig als hij haar wirksam angefochten heeft; "
               "daarmee valt de Kaufvertrag weg.", ("§ 142 Abs. 1 BGB",)),
            _p(3, "1. Anfechtungsgrund: Erklärungsirrtum", "V wilde een verklaring met deze inhoud helemaal niet afgeven: hij verschreef zich "
               "(Verschreiben, Vertippen). Dat is het Erklärungsirrtum van § 119 Abs. 1 Alt. 2, niet het Inhaltsirrtum van Alt. 1. De dwaling is "
               "ook erheblich: bij kennis van de zaak en verstandige beoordeling had V niet voor 890 € aangeboden.", ("§ 119 Abs. 1 BGB",), probleem=True),
            _p(3, "2. Anfechtungserklärung gegenüber dem Anfechtungsgegner", "Het woord 'anfechten' hoeft niet te vallen; genoeg is dat duidelijk "
               "wordt dat V wegens de vergissing niet aan het Geschäft gebonden wil zijn. Anfechtungsgegner is bij een Vertrag de andere "
               "partij, K.", ("§ 143 Abs. 1 BGB", "§ 143 Abs. 2 BGB"), probleem=True),
            _p(3, "3. Anfechtungsfrist", "Unverzüglich, dus ohne schuldhaftes Zögern, nadat V de dwaling ontdekte: hij belde meteen.",
               ("§ 121 Abs. 1 S. 1 BGB",)),
            _p(2, "III. Ergebnis", "De Kaufvertrag is ex tunc nichtig; K heeft geen Anspruch op Übergabe en Übereignung.", ("§ 142 Abs. 1 BGB",)),
            _p(1, "B. Anspruch K gegen V auf Ersatz der 60 € aus § 122 Abs. 1 BGB", normen=("§ 122 Abs. 1 BGB",), groep="vertragsaehnlich"),
            _p(2, "I. Nach § 119 BGB angefochtene Willenserklärung", "Gegeven, zie A. II.", ("§ 119 Abs. 1 BGB",)),
            _p(2, "II. Vertrauensschaden", "K is te stellen alsof hij nooit van het Geschäft had gehoord (negatives Interesse): de 60 € voor de "
               "pedalen gaf hij uit in vertrouwen op de geldigheid. Bovengrens is het Erfüllungsinteresse: het rad is 980 € waard en kostte "
               "890 €, dus 90 €. De 60 € blijven daaronder.", ("§ 122 Abs. 1 BGB",), probleem=True),
            _p(2, "III. Kein Ausschluss", "K kende de grond van de Anfechtbarkeit niet en hoefde hem niet te kennen: 890 € voor een rad van 980 € "
               "valt niet op.", ("§ 122 Abs. 2 BGB",)),
            _p(2, "IV. Ergebnis", "K kan van V 60 € verlangen."),
        ],
    },
    {
        "sleutel": "mofa-des-minderjaehrigen",
        "titel": "Das Mofa",
        "onderwerp": "Beschränkte Geschäftsfähigkeit, Taschengeldparagraph, Abstraktionsprinzip",
        "niveau": "ag",
        "vak": "ZR Ia",
        "sachverhalt": (
            "Der 16-jährige M möchte ein gebrauchtes Mofa kaufen. Seine Eltern haben ihm das ausdrücklich verboten. Trotzdem einigt er "
            "sich mit dem volljährigen V, der M für volljährig hält, über den Kauf des Mofas des V für 400 €. M zahlt 100 € in bar aus "
            "seinem ersparten Taschengeld an; die restlichen 300 € soll er in drei Monatsraten von je 100 € zahlen. V übergibt M das "
            "Mofa sofort; beide sind sich einig, dass M Eigentümer werden soll.\n\n"
            "Als die Eltern des M eine Woche später von dem Geschäft erfahren, erklären sie gegenüber V, sie seien damit nicht "
            "einverstanden. Die Geldscheine, mit denen M bezahlt hat, liegen noch getrennt von anderem Geld in der Kasse des V."
        ),
        "fallfrage": (
            "1. Kann V von M Zahlung der restlichen 300 € verlangen?\n"
            "2. Kann V von M Herausgabe des Mofas verlangen?\n"
            "3. Kann M von V die 100 € zurückverlangen?"
        ),
        "normen": ["§ 433 Abs. 2 BGB", "§ 2 BGB", "§ 106 BGB", "§ 107 BGB", "§ 108 Abs. 1 BGB", "§ 110 BGB", "§ 182 Abs. 1 BGB",
                   "§ 929 S. 1 BGB", "§ 985 BGB", "§ 812 Abs. 1 S. 1 Alt. 1 BGB"],
        "skizze": [
            _p(1, "A. Anspruch V gegen M auf Zahlung von 300 € aus § 433 Abs. 2 BGB", normen=("§ 433 Abs. 2 BGB",), groep="vertrag"),
            _p(2, "I. Kaufvertrag: Einigung", "V en M zijn het eens over zaak en prijs."),
            _p(2, "II. Wirksamkeit der Willenserklärung des M", "M is 16 en dus beschränkt geschäftsfähig.", ("§ 2 BGB", "§ 106 BGB")),
            _p(3, "1. Lediglich rechtlicher Vorteil?", "Nee: de Kaufvertrag verplicht M tot betaling van de Kaufpreis. Het komt aan op de "
               "rechtlichen, niet op de wirtschaftlichen Folgen.", ("§ 107 BGB",), probleem=True),
            _p(3, "2. Einwilligung der gesetzlichen Vertreter", "Ontbreekt; de ouders hebben de koop uitdrukkelijk verboden.", ("§ 107 BGB",)),
            _p(3, "3. § 110 BGB (Taschengeldparagraph)", "Niet vervuld. De Minderjährige moet de vertragsmäßige Leistung bewirkt hebben, dus "
               "volledig hebben voldaan; bij een Ratenkauf is dat pas zo na de laatste termijn. Bovendien is zakgeld niet ter vrije "
               "beschikking gelaten voor een aankoop die de ouders uitdrukkelijk verboden hebben.", ("§ 110 BGB",), probleem=True),
            _p(3, "4. Genehmigung", "De Vertrag was schwebend unwirksam; de ouders hebben de Genehmigung tegenover V geweigerd, daarmee is hij "
               "definitief unwirksam. Dat V dacht dat M volljährig was helpt hem niet: de goede trouw aan de Geschäftsfähigkeit wordt niet "
               "beschermd.", ("§ 108 Abs. 1 BGB", "§ 182 Abs. 1 BGB"), probleem=True),
            _p(2, "III. Ergebnis", "Geen Kaufvertrag, geen Anspruch op 300 €."),
            _p(1, "B. Anspruch V gegen M auf Herausgabe des Mofas aus § 985 BGB", normen=("§ 985 BGB",), groep="dinglich"),
            _p(2, "I. Eigentum des V", "V was eigenaar, maar kan zijn eigendom aan M verloren hebben door Übereignung nach § 929 S. 1 BGB.",
               ("§ 929 S. 1 BGB",)),
            _p(3, "1. Einigung", "De dingliche Einigung brengt M alleen het eigendom en is voor hem lediglich rechtlich vorteilhaft; zij is "
               "zonder Einwilligung wirksam. Dat de Kaufvertrag unwirksam is, raakt de Übereignung niet (Trennungs- und "
               "Abstraktionsprinzip).", ("§ 107 BGB", "§ 929 S. 1 BGB"), probleem=True),
            _p(3, "2. Übergabe, Berechtigung", "V heeft het Mofa overhandigd en was als eigenaar berechtigt."),
            _p(2, "II. Ergebnis", "M is eigenaar geworden; geen Anspruch uit § 985 BGB."),
            _p(1, "C. Anspruch V gegen M auf Herausgabe des Mofas aus § 812 Abs. 1 S. 1 Alt. 1 BGB", normen=("§ 812 Abs. 1 S. 1 Alt. 1 BGB",),
               groep="bereicherung"),
            _p(2, "I. Etwas erlangt", "Eigendom en bezit van het Mofa."),
            _p(2, "II. Durch Leistung des V", "V heeft het vermogen van M bewust en doelgericht vermeerderd, om zijn vermeende plicht uit de "
               "Kaufvertrag te vervullen."),
            _p(2, "III. Ohne Rechtsgrund", "De Kaufvertrag is unwirksam (zie A).", probleem=True),
            _p(2, "IV. Ergebnis", "M moet het Mofa teruggeven en terugübereignen.", ("§ 812 Abs. 1 S. 1 Alt. 1 BGB", "§ 818 Abs. 1 BGB")),
            _p(1, "D. Anspruch M gegen V auf Herausgabe der Geldscheine aus § 985 BGB", normen=("§ 985 BGB",), groep="dinglich"),
            _p(2, "I. Eigentum des M", "M is eigenaar gebleven: de Übereignung van het geld aan V kost hem zijn eigendom en is dus niet "
               "lediglich rechtlich vorteilhaft; zonder Einwilligung was zij schwebend unwirksam en door de weigering van de Genehmigung "
               "definitief unwirksam. De biljetten zijn niet vermengd (§§ 948, 947 BGB spelen niet).", ("§ 107 BGB", "§ 108 Abs. 1 BGB"), probleem=True),
            _p(2, "II. Besitz des V ohne Recht zum Besitz", "V bezit de biljetten; een Recht zum Besitz heeft hij zonder wirksamen Kaufvertrag "
               "niet.", ("§ 986 BGB",)),
            _p(2, "III. Ergebnis", "M kan de biljetten opeisen."),
            _p(1, "E. Anspruch M gegen V aus § 812 Abs. 1 S. 1 Alt. 1 BGB", normen=("§ 812 Abs. 1 S. 1 Alt. 1 BGB",), groep="bereicherung"),
            _p(2, "I. Etwas erlangt durch Leistung ohne Rechtsgrund", "V heeft door de Leistung van M het bezit van de biljetten verkregen "
               "(geen eigendom, zie D), zonder Rechtsgrund. M kan ook langs deze weg teruggave verlangen."),
        ],
    },
    {
        "sleutel": "verbranntes-gemaelde",
        "titel": "Das verbrannte Gemälde",
        "onderwerp": "Nachträgliche Unmöglichkeit, Schadensersatz statt der Leistung, Gegenleistung",
        "niveau": "ag",
        "vak": "ZR Ia",
        "sachverhalt": (
            "V verkauft K am 1. März ein Ölgemälde, ein Unikat, für 5.000 €. Das Gemälde hat einen Marktwert von 6.000 €. Die Übergabe "
            "soll am 10. März erfolgen, der Kaufpreis ist bei Übergabe zu zahlen.\n\n"
            "Am 8. März stellt V das Gemälde in seinem Atelier unachtsam direkt neben einen eingeschalteten Heizstrahler. Es fängt Feuer "
            "und verbrennt vollständig.\n\n"
            "K verlangt Lieferung des Gemäldes, hilfsweise Schadensersatz in Höhe von 1.000 €. V meint, er schulde nichts mehr; "
            "seinerseits verlangt er den Kaufpreis."
        ),
        "fallfrage": (
            "1. Kann K von V Übergabe und Übereignung des Gemäldes verlangen?\n"
            "2. Kann K von V Schadensersatz in Höhe von 1.000 € verlangen?\n"
            "3. Kann V von K Zahlung von 5.000 € verlangen?"
        ),
        "normen": ["§ 433 Abs. 1 S. 1 BGB", "§ 433 Abs. 2 BGB", "§ 275 Abs. 1 BGB", "§ 280 Abs. 1 BGB", "§ 280 Abs. 3 BGB", "§ 283 BGB",
                   "§ 276 BGB", "§ 249 Abs. 1 BGB", "§ 326 Abs. 1 S. 1 BGB", "§ 326 Abs. 2 BGB"],
        "skizze": [
            _p(1, "A. Anspruch K gegen V auf Übergabe und Übereignung aus § 433 Abs. 1 S. 1 BGB", normen=("§ 433 Abs. 1 S. 1 BGB",), groep="vertrag"),
            _p(2, "I. Anspruch entstanden", "Wirksamer Kaufvertrag van 1 maart."),
            _p(2, "II. Anspruch erloschen: Unmöglichkeit", "Het schilderij is een Unikat, dus een Stückschuld; na de brand kan niemand het nog "
               "leveren (objektive Unmöglichkeit, na het sluiten van de Vertrag ingetreden). De Leistungspflicht is van rechtswege "
               "uitgesloten; of V de Unmöglichkeit te vertreten heeft doet hier niet ter zake.", ("§ 275 Abs. 1 BGB",), probleem=True),
            _p(2, "III. Ergebnis", "Geen Anspruch op levering."),
            _p(1, "B. Anspruch K gegen V auf Schadensersatz statt der Leistung aus §§ 280 Abs. 1, 3, 283 BGB",
               normen=("§ 280 Abs. 1 BGB", "§ 280 Abs. 3 BGB", "§ 283 BGB"), groep="vertrag"),
            _p(2, "I. Schuldverhältnis", "De Kaufvertrag."),
            _p(2, "II. Pflichtverletzung", "V levert niet, omdat de Leistung nach § 275 Abs. 1 BGB uitgesloten is. Het hindernis ontstond na "
               "het sluiten van de Vertrag: dus § 283 BGB, niet § 311a Abs. 2 BGB.", ("§ 283 BGB", "§ 311a Abs. 2 BGB"), probleem=True),
            _p(2, "III. Vertretenmüssen", "Wordt vermoed (§ 280 Abs. 1 S. 2 BGB) en staat hier ook vast: V handelde fahrlässig door het "
               "schilderij naast een brandende straalkachel te zetten.", ("§ 280 Abs. 1 BGB", "§ 276 BGB")),
            _p(2, "IV. Keine Fristsetzung", "§ 283 S. 1 BGB eist geen Fristsetzung: zij zou bij Unmöglichkeit zinloos zijn.", ("§ 283 BGB",)),
            _p(2, "V. Schaden", "K is te stellen alsof behoorlijk was geleverd. Hij had een schilderij van 6.000 € gekregen voor 5.000 €, die hij "
               "nu niet meer hoeft te betalen (§ 326 Abs. 1 S. 1 BGB): 1.000 €.", ("§ 249 Abs. 1 BGB", "§ 326 Abs. 1 S. 1 BGB"), probleem=True),
            _p(2, "VI. Ergebnis", "K kan 1.000 € verlangen."),
            _p(1, "C. Anspruch V gegen K auf Zahlung von 5.000 € aus § 433 Abs. 2 BGB", normen=("§ 433 Abs. 2 BGB",), groep="vertrag"),
            _p(2, "I. Anspruch entstanden", "Kaufvertrag."),
            _p(2, "II. Anspruch erloschen", "De Kaufvertrag is een gegenseitiger Vertrag; V hoeft nach § 275 Abs. 1 BGB niet te leveren, dus "
               "vervalt de Anspruch op de Gegenleistung. Een uitzondering nach § 326 Abs. 2 BGB is er niet: K is voor de brand niet "
               "verantwoordelijk en was niet in Annahmeverzug.", ("§ 326 Abs. 1 S. 1 BGB", "§ 326 Abs. 2 BGB"), probleem=True),
            _p(2, "III. Ergebnis", "V kan de Kaufpreis niet verlangen."),
        ],
    },
]


def laad(db, overschrijf: bool = False) -> int:
    """Zet de voorbeeldcasussen in de database (herkend aan `sleutel`). Bestaande blijven staan, tenzij `overschrijf`."""
    from sqlalchemy import select

    from ..models import Casus

    n = 0
    for spec in CASUSSEN:
        c = db.scalar(select(Casus).where(Casus.sleutel == spec["sleutel"]))
        if c is not None and not overschrijf:
            continue
        if c is None:
            c = Casus(sleutel=spec["sleutel"], profiel_id=None, herkomst="seed", geverifieerd=False)
            db.add(c)
        for veld in ("titel", "onderwerp", "niveau", "vak", "sachverhalt", "fallfrage", "normen", "skizze"):
            setattr(c, veld, spec[veld])
        n += 1
    db.flush()
    return n
