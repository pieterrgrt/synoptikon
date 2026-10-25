"""Vraag (b): Wanneer leidt het afbreken van onderhandelingen tot aansprakelijkheid?"""

_WETTEN_NL6 = "https://wetten.overheid.nl/BWBR0005289/"
_GII = "https://www.gesetze-im-internet.de/bgb/"
_LEGI = "https://www.legifrance.gouv.fr/codes/article_lc/"

VRAAG = {
    "slug": "precontractuele-aansprakelijkheid",
    "titel": "Wanneer leidt het afbreken van onderhandelingen tot aansprakelijkheid, en voor welke schade?",
    "rechtsgebied": "Verbintenissenrecht",
    "tags": "precontractueel, onderhandelingen, culpa in contrahendo, goede trouw, vertrouwen, positief contractsbelang, negatief contractsbelang, Rome II",
    "omschrijving": (
        "Tertium: *de gevolgen van het afbreken van onderhandelingen over een nog niet gesloten overeenkomst*. Drie deelvragen: "
        "(1) **grondslag** — contractueel, buitencontractueel of een tussenvorm?; (2) **maatstaf** — wanneer is afbreken ongeoorloofd?; "
        "(3) **omvang** — alleen het negatieve belang (gemaakte kosten) of ook het positieve belang (gederfde winst)? "
        "NL heeft een rechtersrechtelijke figuur zonder wettelijke grondslag, DE een gecodificeerde *culpa in contrahendo* met contractuele inslag, "
        "FR sinds 2016 een uitdrukkelijke wettelijke regel in de delictuele sleutel. De EU kwalificeert de figuur autonoom als niet-contractueel (Rome II, Tacconi)."
    ),
    "antwoorden": {
        "NL": {
            "kern": "Ongeschreven recht, ontwikkeld door de Hoge Raad: afbreken is vrij, tenzij dat gezien het gerechtvaardigd vertrouwen van de wederpartij in het totstandkomen van de overeenkomst of de andere omstandigheden onaanvaardbaar is (CBB/JPO); dan kan zelfs het positief contractsbelang verschuldigd zijn (Plas/Valburg).",
            "analyse": (
                "## Grondslag\n"
                "Geen wettelijke bepaling. De Hoge Raad plaatst de onderhandelingsfase sinds **Baris/Riezenkamp** (1957) onder de *goede trouw*: partijen die in onderhandeling treden komen 'tot elkaar in een bijzondere, door de goede trouw beheerste rechtsverhouding'. De dogmatische grondslag is dubbel: art. 6:162 (onrechtmatige daad) voor de aansprakelijkheid, art. 6:2/6:248 (redelijkheid en billijkheid) voor de norm. Het ontwerp-art. 6.5.2.8a dat de figuur zou codificeren is nooit wet geworden.\n\n"
                "## Maatstaf: van drie fasen naar één strenge toets\n"
                "**Plas/Valburg** (1982) leverde het bekende *driefasenmodel*: (1) vrij afbreken; (2) afbreken toegestaan, maar kostenvergoeding verschuldigd; (3) afbreken onaanvaardbaar, met mogelijk vergoeding van gederfde winst. **CBB/JPO** (2005) vatte de maatstaf samen en scherpte haar aan: afbreken is vrij, *tenzij* onaanvaardbaar op grond van gerechtvaardigd vertrouwen in het totstandkomen of andere omstandigheden; de maatstaf is 'streng en tot terughoudendheid nopend'. Relevant: wie heeft tot het vertrouwen bijgedragen, onvoorziene omstandigheden, en bij langdurige onderhandelingen het moment van afbreken tegen de achtergrond van het geheel.\n\n"
                "## Omvang\n"
                "Uniek in de vergelijking: NL aanvaardt in de derde fase in beginsel vergoeding van het **positief contractsbelang** (gederfde winst), omdat de wederpartij erop mocht vertrouwen dat *een* contract tot stand zou komen. DE en FR beperken tot het negatieve belang. Na CBB/JPO wordt de derde fase zelden bereikt; de praktijk is kostenvergoeding (tweede fase, nu veelal via art. 6:212 of 6:162).\n\n"
                "## Vergelijkende observatie\n"
                "Functioneel ligt NL het dichtst bij DE (vertrouwensbescherming, goede trouw als norm), maar zonder de contractuele inkleding van § 311 II en mét de ruimere schadeomvang. Tegenover FR (art. 1112 al. 2) is het verschil in omvang principieel."
            ),
            "bronnen": [
                {
                    "stelsel": "NL", "soort": "rechtspraak", "taal": "nl", "citeertitel": "HR 18 juni 1982 (Plas/Valburg)",
                    "titel": "Plas/Valburg — driefasenleer",
                    "tekst": (
                        "Niet uitgesloten is dat onderhandelingen over een overeenkomst in een zodanig stadium zijn gekomen dat het afbreken zelf van die onderhandelingen onder de gegeven omstandigheden als in strijd met de goede trouw moet worden geacht, omdat partijen over en weer mochten vertrouwen dat enigerlei contract in ieder geval uit de onderhandelingen zou resulteren. In zo een situatie kan er ook plaats zijn voor een verplichting tot vergoeding van gederfde winst.\n\n"
                        "[…] Ook wanneer de onderhandelingen nog niet in een zodanig stadium zijn gekomen, kan het afbreken ervan onder omstandigheden meebrengen dat de afbrekende partij de door de wederpartij gemaakte kosten geheel of gedeeltelijk voor haar rekening moet nemen."
                    ),
                    "vindplaats_type": "ECLI", "vindplaats": "ECLI:NL:HR:1982:AG4405; NJ 1983/723 m.nt. CJHB", "url": "https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:HR:1982:AG4405",
                    "rol": "rechtspraak",
                    "notitie": "Gemeente Valburg brak na vergevorderde onderhandelingen over de bouw van een zwembad af. De HR aanvaardt dat (i) afbreken zelf in strijd met de goede trouw kan zijn met vergoeding van gederfde winst, en (ii) in een eerder stadium kostenvergoeding verschuldigd kan zijn.",
                    "opmerking": "Kernoverwegingen (r.o. 3.4 en 3.5), ingekort. Raadpleeg NJ 1983/723 voor de volledige tekst.",
                },
                {
                    "stelsel": "NL", "soort": "rechtspraak", "taal": "nl", "citeertitel": "HR 12 augustus 2005 (CBB/JPO)",
                    "titel": "Centraal Bureau Bouwtoezicht / JPO Projecten — de strenge maatstaf",
                    "tekst": (
                        "Bij de beoordeling van deze klachten moet worden vooropgesteld dat als maatstaf voor de beoordeling van de schadevergoedingsplicht bij afgebroken onderhandelingen heeft te gelden dat ieder van de onderhandelende partijen — die verplicht zijn hun gedrag mede door elkaars gerechtvaardigde belangen te laten bepalen — vrij is de onderhandelingen af te breken, tenzij dit op grond van het gerechtvaardigd vertrouwen van de wederpartij in het totstandkomen van de overeenkomst of in verband met de andere omstandigheden van het geval onaanvaardbaar zou zijn. Daarbij dient rekening te worden gehouden met de mate waarin en de wijze waarop de partij die de onderhandelingen afbreekt tot het ontstaan van dat vertrouwen heeft bijgedragen en met de gerechtvaardigde belangen van deze partij. Hierbij kan ook van belang zijn of zich in de loop van de onderhandelingen onvoorziene omstandigheden hebben voorgedaan, terwijl, in het geval onderhandelingen ondanks gewijzigde omstandigheden over een lange tijd worden voortgezet, wat betreft dit vertrouwen doorslaggevend is hoe daaromtrent ten slotte op het moment van afbreken van de onderhandelingen moet worden geoordeeld tegen de achtergrond van het gehele verloop van de onderhandelingen.\n\n"
                        "[…] De Hoge Raad merkt op dat het hier gaat om een strenge en tot terughoudendheid nopende maatstaf."
                    ),
                    "vindplaats_type": "ECLI", "vindplaats": "ECLI:NL:HR:2005:AT7337; NJ 2005/467", "url": "https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:HR:2005:AT7337",
                    "rol": "rechtspraak",
                    "notitie": "Standaardformule sinds 2005. De 'drie fasen' worden niet herhaald; de HR spreekt van één hoofdregel (vrijheid) met een uitzondering (onaanvaardbaarheid). Het positief contractsbelang blijft in theorie mogelijk, maar de drempel is hoog.",
                    "opmerking": "Kernoverweging r.o. 3.6 en 3.7.",
                },
                {
                    "stelsel": "NL", "soort": "rechtspraak", "taal": "nl", "citeertitel": "HR 15 november 1957 (Baris/Riezenkamp)",
                    "titel": "Baris/Riezenkamp — de precontractuele goede trouw",
                    "tekst": "Door in onderhandeling te treden over het sluiten van een overeenkomst komen partijen tot elkaar te staan in een bijzondere, door de goede trouw beheerste rechtsverhouding, medebrengende dat zij hun gedrag mede moeten laten bepalen door de gerechtvaardigde belangen van de wederpartij.",
                    "vindplaats_type": "ECLI", "vindplaats": "ECLI:NL:HR:1957:AG2023; NJ 1958/67 m.nt. LEHR", "url": "https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:HR:1957:AG2023",
                    "rol": "rechtspraak",
                    "notitie": "Grondslagarrest; de formule 'gedrag mede laten bepalen door elkaars gerechtvaardigde belangen' keert in CBB/JPO letterlijk terug.",
                    "opmerking": "Kernoverweging, geparafraseerd naar de gangbare citeerwijze.",
                },
                {
                    "stelsel": "NL", "soort": "wet", "taal": "nl", "citeertitel": "art. 6:162 BW",
                    "titel": "Onrechtmatige daad",
                    "tekst": (
                        "1. Hij die jegens een ander een onrechtmatige daad pleegt, welke hem kan worden toegerekend, is verplicht de schade die de ander dientengevolge lijdt, te vergoeden.\n\n"
                        "2. Als onrechtmatige daad worden aangemerkt een inbreuk op een recht en een doen of nalaten in strijd met een wettelijke plicht of met hetgeen volgens ongeschreven recht in het maatschappelijk verkeer betaamt, een en ander behoudens de aanwezigheid van een rechtvaardigingsgrond.\n\n"
                        "3. Een onrechtmatige daad kan aan de dader worden toegerekend, indien zij te wijten is aan zijn schuld of aan een oorzaak welke krachtens de wet of de in het verkeer geldende opvattingen voor zijn rekening komt."
                    ),
                    "vindplaats_type": "BWB", "vindplaats": "BWBR0005289, Boek 6, art. 162", "url": _WETTEN_NL6 + "Boek6/Titeldeel3/Afdeling1/Artikel162/",
                    "geldig_van": "1992-01-01", "systematiek": "BW-6-3-1", "rol": "grondslag",
                    "notitie": "De gangbare processuele grondslag: afbreken in strijd met 'hetgeen volgens ongeschreven recht in het maatschappelijk verkeer betaamt' (lid 2).",
                    "vertalingen": {"de": "1. Wer gegenüber einem anderen eine unerlaubte Handlung begeht, die ihm zugerechnet werden kann, ist verpflichtet, den Schaden, den der andere dadurch erleidet, zu ersetzen. 2. Als unerlaubte Handlung gelten die Verletzung eines Rechts sowie ein Tun oder Unterlassen im Widerspruch zu einer gesetzlichen Pflicht oder zu dem, was nach ungeschriebenem Recht im gesellschaftlichen Verkehr geboten ist, jeweils vorbehaltlich eines Rechtfertigungsgrundes. 3. Eine unerlaubte Handlung kann dem Täter zugerechnet werden, wenn sie auf sein Verschulden oder auf eine Ursache zurückzuführen ist, die kraft Gesetzes oder nach der Verkehrsauffassung in seinen Risikobereich fällt."},
                },
                {
                    "stelsel": "NL", "soort": "wet", "taal": "nl", "citeertitel": "art. 6:2 BW",
                    "titel": "Redelijkheid en billijkheid",
                    "tekst": (
                        "1. Schuldeiser en schuldenaar zijn verplicht zich jegens elkaar te gedragen overeenkomstig de eisen van redelijkheid en billijkheid.\n\n"
                        "2. Een tussen hen krachtens wet, gewoonte of rechtshandeling geldende regel is niet van toepassing, voor zover dit in de gegeven omstandigheden naar maatstaven van redelijkheid en billijkheid onaanvaardbaar zou zijn."
                    ),
                    "vindplaats_type": "BWB", "vindplaats": "BWBR0005289, Boek 6, art. 2", "url": _WETTEN_NL6 + "Boek6/Titeldeel1/Afdeling1/Artikel2/",
                    "geldig_van": "1992-01-01", "systematiek": "BW-6-1-1", "rol": "norm",
                    "notitie": "Geldt strikt genomen tussen schuldeiser en schuldenaar; op de onderhandelingsfase analoog toegepast als uitdrukking van de 'goede trouw' uit Baris/Riezenkamp.",
                    "vertalingen": {"de": "1. Gläubiger und Schuldner sind verpflichtet, sich einander gegenüber nach den Erfordernissen von Redlichkeit und Billigkeit zu verhalten. 2. Eine zwischen ihnen kraft Gesetzes, Gewohnheit oder Rechtsgeschäfts geltende Regel findet keine Anwendung, soweit dies unter den gegebenen Umständen nach Maßstäben von Redlichkeit und Billigkeit unannehmbar wäre."},
                },
                {
                    "stelsel": "NL", "soort": "literatuur", "taal": "nl", "citeertitel": "Asser/Sieburgh 6-III 2022, nr. 192 e.v.",
                    "titel": "Algemeen overeenkomstenrecht — afgebroken onderhandelingen",
                    "tekst": None, "vindplaats_type": "ISBN", "vindplaats": "9789013164787",
                    "rol": "literatuur",
                    "notitie": "Overzicht van de ontwikkeling Baris/Riezenkamp → Plas/Valburg → CBB/JPO en de discussie over de grondslag (onrechtmatige daad vs. redelijkheid en billijkheid).",
                },
            ],
        },
        "DE": {
            "kern": "Culpa in contrahendo, gecodificeerd in § 311 II jo. § 241 II jo. § 280 I BGB: door de Aufnahme von Vertragsverhandlungen ontstaat een (quasi-)contractueel Schuldverhältnis met Rücksichtnahmepflichten; afbreken zonder triftigen Grund na gewekt vertrouwen verplicht tot vergoeding van het negatieve belang (Vertrauensschaden).",
            "analyse": (
                "## Grondslag: gesetzliches Schuldverhältnis\n"
                "Jhering (1861) ontwikkelde de *culpa in contrahendo*; het Reichsgericht aanvaardde haar in de **Linoleumrollen**-zaak (RGZ 78, 239) als gewoonterecht op basis van § 242. De **Schuldrechtsmodernisierung 2002** codificeerde haar: § 311 Abs. 2 laat een *Schuldverhältnis mit Pflichten nach § 241 Abs. 2* ontstaan door (1) Aufnahme von Vertragsverhandlungen, (2) Anbahnung eines Vertrags, (3) ähnliche geschäftliche Kontakte. Dogmatisch is dit een **gesetzliches Schuldverhältnis ohne primäre Leistungspflicht**: contractueel van structuur (§ 278 Gehilfenhaftung, § 280 beweislast), buitencontractueel van ontstaan.\n\n"
                "## Anspruchsgrundlage\n"
                "§§ 280 Abs. 1, 311 Abs. 2, 241 Abs. 2 BGB. Vereist: Schuldverhältnis (§ 311 II), Pflichtverletzung (schending van een Rücksichtnahmepflicht, § 241 II), Vertretenmüssen (vermoed, § 280 I 2), Schaden.\n\n"
                "## Abbruch von Vertragsverhandlungen\n"
                "Uitgangspunt is de **Abschlussfreiheit**: niemand is verplicht te contracteren, en wie afbreekt handelt in beginsel rechtmatig, ook als de ander kosten heeft gemaakt. Pflichtverletzung slechts wanneer een partij (a) het vertrouwen heeft gewekt dat het contract *zeker* tot stand zou komen (*Vertrauenstatbestand*) en (b) vervolgens *ohne triftigen Grund* afbreekt (BGH NJW 1975, 1774; BGH NJW 1996, 1884). Bij **formbedürftige Verträge** (§ 311b: grondstukken) is de lat hoger: alleen bij *vorsätzlicher Treuepflichtverletzung* (BGH 29.03.1996, V ZR 332/94), omdat de vormvoorschriften anders worden uitgehold.\n\n"
                "## Omvang: negatives Interesse\n"
                "Vergoed wordt het **Vertrauensschaden**: de gelaedeerde wordt gesteld alsof hij nooit op het contract had vertrouwd (vergeefse kosten, gemiste alternatieve transacties). Het **Erfüllungsinteresse** is uitgesloten, want er is geen Abschlusspflicht; het mag echter als *Obergrenze* dienen (analoog § 122 Abs. 1). Hier verschilt DE scherp van Plas/Valburg.\n\n"
                "## Vergelijkende observatie\n"
                "De contractuele inkleding geeft praktische voordelen (§ 278 i.p.v. § 831, omkering bewijslast § 280 I 2, 30-jarige in plaats van 3-jarige verjaring vóór 2002; nu gelijk). FR en NL bereiken vergelijkbare uitkomsten in het delictsrecht; alleen de omvang (NL) en de uitdrukkelijke uitsluiting van de perte de chance (FR) wijken af."
            ),
            "bronnen": [
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 311 BGB",
                    "titel": "Rechtsgeschäftliche und rechtsgeschäftsähnliche Schuldverhältnisse",
                    "tekst": (
                        "(1) Zur Begründung eines Schuldverhältnisses durch Rechtsgeschäft sowie zur Änderung des Inhalts eines Schuldverhältnisses ist ein Vertrag zwischen den Beteiligten erforderlich, soweit nicht das Gesetz ein anderes vorschreibt.\n\n"
                        "(2) Ein Schuldverhältnis mit Pflichten nach § 241 Abs. 2 entsteht auch durch\n"
                        "1. die Aufnahme von Vertragsverhandlungen,\n"
                        "2. die Anbahnung eines Vertrags, bei welcher der eine Teil im Hinblick auf eine etwaige rechtsgeschäftliche Beziehung dem anderen Teil die Möglichkeit zur Einwirkung auf seine Rechte, Rechtsgüter und Interessen gewährt oder ihm diese anvertraut, oder\n"
                        "3. ähnliche geschäftliche Kontakte.\n\n"
                        "(3) Ein Schuldverhältnis mit Pflichten nach § 241 Abs. 2 kann auch zu Personen entstehen, die nicht selbst Vertragspartei werden sollen. Ein solches Schuldverhältnis entsteht insbesondere, wenn der Dritte in besonderem Maße Vertrauen für sich in Anspruch nimmt und dadurch die Vertragsverhandlungen oder den Vertragsschluss erheblich beeinflusst."
                    ),
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE030302377", "url": _GII + "__311.html",
                    "geldig_van": "2002-01-01", "systematiek": "BGB-2-3-1", "rol": "hoofdregel",
                    "notitie": "Abs. 2 Nr. 1 is de klassieke c.i.c.; Nr. 2 dekt de 'Linoleumrollen'-situatie (betreden van een winkel); Abs. 3 de Sachwalter- en Eigenhaftung van derden.",
                    "vertalingen": {"nl": "(1) Voor het ontstaan van een verbintenis uit rechtshandeling en voor de wijziging van de inhoud van een verbintenis is een overeenkomst tussen de betrokkenen vereist, tenzij de wet anders bepaalt. (2) Een verbintenis met plichten volgens § 241 lid 2 ontstaat ook door 1. het aanknopen van contractsonderhandelingen, 2. het voorbereiden van een contract, waarbij de ene partij met het oog op een eventuele rechtsbetrekking de andere partij de mogelijkheid geeft op haar rechten, rechtsgoederen en belangen in te werken of deze aan haar toevertrouwt, of 3. soortgelijke zakelijke contacten. (3) Een verbintenis met plichten volgens § 241 lid 2 kan ook ontstaan jegens personen die zelf geen contractspartij zullen worden. Zo'n verbintenis ontstaat in het bijzonder wanneer de derde in bijzondere mate vertrouwen voor zichzelf opeist en daardoor de contractsonderhandelingen of het sluiten van het contract aanzienlijk beïnvloedt."},
                },
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 241 BGB",
                    "titel": "Pflichten aus dem Schuldverhältnis",
                    "tekst": (
                        "(1) Kraft des Schuldverhältnisses ist der Gläubiger berechtigt, von dem Schuldner eine Leistung zu fordern. Die Leistung kann auch in einem Unterlassen bestehen.\n\n"
                        "(2) Das Schuldverhältnis kann nach seinem Inhalt jeden Teil zur Rücksicht auf die Rechte, Rechtsgüter und Interessen des anderen Teils verpflichten."
                    ),
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE023202377", "url": _GII + "__241.html",
                    "geldig_van": "2002-01-01", "systematiek": "BGB-2-1-1", "rol": "norm",
                    "notitie": "Abs. 2: de Rücksichtnahmepflichten (Schutzpflichten) die in de onderhandelingsfase de enige verbintenisinhoud vormen.",
                    "vertalingen": {"nl": "(1) Krachtens de verbintenis is de schuldeiser gerechtigd van de schuldenaar een prestatie te vorderen. De prestatie kan ook bestaan in een nalaten. (2) De verbintenis kan naar haar inhoud ieder van partijen verplichten rekening te houden met de rechten, rechtsgoederen en belangen van de andere partij."},
                },
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 280 BGB",
                    "titel": "Schadensersatz wegen Pflichtverletzung",
                    "tekst": (
                        "(1) Verletzt der Schuldner eine Pflicht aus dem Schuldverhältnis, so kann der Gläubiger Ersatz des hierdurch entstehenden Schadens verlangen. Dies gilt nicht, wenn der Schuldner die Pflichtverletzung nicht zu vertreten hat.\n\n"
                        "(2) Schadensersatz wegen Verzögerung der Leistung kann der Gläubiger nur unter der zusätzlichen Voraussetzung des § 286 verlangen.\n\n"
                        "(3) Schadensersatz statt der Leistung kann der Gläubiger nur unter den zusätzlichen Voraussetzungen des § 281, des § 282 oder des § 283 verlangen."
                    ),
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE027302377", "url": _GII + "__280.html",
                    "geldig_van": "2002-01-01", "systematiek": "BGB-2-1-1", "rol": "grondslag",
                    "notitie": "Centrale Anspruchsgrundlage; Abs. 1 S. 2 keert de bewijslast voor het Vertretenmüssen om — een voordeel boven § 823.",
                    "vertalingen": {"nl": "(1) Schendt de schuldenaar een plicht uit de verbintenis, dan kan de schuldeiser vergoeding van de daardoor ontstane schade vorderen. Dit geldt niet wanneer de schuldenaar de plichtsschending niet behoeft te verantwoorden. (2) Schadevergoeding wegens vertraging van de prestatie kan de schuldeiser slechts onder de aanvullende voorwaarde van § 286 vorderen. (3) Schadevergoeding in plaats van de prestatie kan de schuldeiser slechts onder de aanvullende voorwaarden van § 281, § 282 of § 283 vorderen."},
                },
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 242 BGB",
                    "titel": "Leistung nach Treu und Glauben",
                    "tekst": "Der Schuldner ist verpflichtet, die Leistung so zu bewirken, wie Treu und Glauben mit Rücksicht auf die Verkehrssitte es erfordern.",
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE023302377", "url": _GII + "__242.html",
                    "geldig_van": "1900-01-01", "systematiek": "BGB-2-1-1", "rol": "norm",
                    "notitie": "Historische grondslag van de c.i.c. vóór 2002; nu nog de maatstaf voor de 'triftiger Grund'.",
                    "vertalingen": {"nl": "De schuldenaar is verplicht de prestatie zo te verrichten als de goede trouw (Treu und Glauben) met inachtneming van de verkeersopvattingen vereist."},
                },
                {
                    "stelsel": "DE", "soort": "rechtspraak", "taal": "de", "citeertitel": "RG 7. Dezember 1911 (Linoleumrollen)",
                    "titel": "Linoleumrollenfall — Haftung aus Vertragsanbahnung",
                    "tekst": "Durch die Erklärung des Kaufinteressenten, den Teppich ansehen zu wollen, und die Bereitschaft des Verkäufers, ihn vorzulegen, ist ein den Kauf vorbereitendes Rechtsverhältnis zwischen den Parteien entstanden, das einen vertragsähnlichen Charakter trägt und rechtsgeschäftliche Verbindlichkeiten erzeugt hat: die Pflicht, bei der Vorlegung die Sorgfalt zu beachten, die zum Schutz der Gesundheit und des Eigentums des anderen Teils erforderlich ist.",
                    "vindplaats_type": "RGZ", "vindplaats": "RGZ 78, 239", "url": None,
                    "rol": "rechtspraak",
                    "notitie": "Een klant werd in een warenhuis door omvallende linoleumrollen getroffen. Het RG construeert een 'vertragsähnliches Verhältnis' om de voor de klant gunstiger contractuele regels (§ 278 i.p.v. § 831) toe te passen. Oerbron van wat nu § 311 Abs. 2 Nr. 2 is.",
                    "opmerking": "Kernoverweging, geparafraseerd naar de gangbare citeerwijze in de literatuur.",
                },
                {
                    "stelsel": "DE", "soort": "rechtspraak", "taal": "de", "citeertitel": "BGH 29. März 1996, V ZR 332/94",
                    "titel": "Abbruch von Vertragsverhandlungen bei formbedürftigem Grundstückskaufvertrag",
                    "tekst": "Bei einem formbedürftigen Vertrag kommt eine Haftung aus Verschulden bei Vertragsschluss wegen Abbruchs der Vertragsverhandlungen nur in Betracht, wenn der Abbrechende eine besonders schwerwiegende, in der Regel vorsätzliche Treuepflichtverletzung begangen hat; der Abbruch ohne triftigen Grund genügt insoweit nicht, weil sonst der Formzweck des § 313 BGB a.F. [jetzt § 311b Abs. 1] umgangen würde.",
                    "vindplaats_type": "NJW", "vindplaats": "NJW 1996, 1884", "url": None,
                    "rol": "rechtspraak",
                    "notitie": "Hoofdregel voor niet-vormgebonden contracten: aansprakelijkheid bij afbreken *ohne triftigen Grund* nadat vertrouwen op het zeker tot stand komen is gewekt (vaste rechtspraak sinds BGH NJW 1975, 1774). Bij vormvoorschriften: alleen bij opzettelijke Treuepflichtverletzung.",
                    "opmerking": "Leitsatz, geparafraseerd.",
                },
                {
                    "stelsel": "DE", "soort": "literatuur", "taal": "de", "citeertitel": "MüKoBGB/Emmerich, 9. Aufl. 2022, § 311 Rn. 157 ff.",
                    "titel": "Abbruch von Vertragsverhandlungen",
                    "tekst": None, "vindplaats_type": "ISBN", "vindplaats": "9783406777424",
                    "rol": "literatuur",
                    "notitie": "Systematisch overzicht van Vertrauenstatbestand, triftiger Grund, vormgebonden contracten en omvang (negatives Interesse).",
                },
            ],
        },
        "FR": {
            "kern": "Sinds 2016 wettelijk: onderhandelingen zijn vrij in begin, verloop én afbreken, maar moeten de bonne foi eerbiedigen (art. 1112 al. 1); bij faute is de schade delictueel te vergoeden (art. 1240), met uitdrukkelijke uitsluiting van het verlies van de contractvoordelen en de perte de chance (art. 1112 al. 2, codificatie Manoukian).",
            "analyse": (
                "## Grondslag: responsabilité délictuelle\n"
                "Vóór 2016 was de *rupture abusive des pourparlers* zuiver rechtersrecht op basis van art. 1382 (oud). De **Ordonnance 2016-131** codificeerde haar in art. 1112, in de nieuwe *Sous-section 1 — Les négociations* van het hoofdstuk over de contractsvorming. De kwalificatie blijft **buitencontractueel**: er is nog geen contract, dus art. 1240 (ex 1382) is de aansprakelijkheidsgrondslag; art. 1112 geeft de gedragsnorm en de schadebeperking.\n\n"
                "## Maatstaf: liberté et bonne foi\n"
                "Art. 1112 al. 1 stelt de **vrijheid** voorop (*l'initiative, le déroulement et la rupture … sont libres*) en onderwerpt haar *impérativement* aan de **bonne foi** — de precontractuele uitloper van art. 1104 (*négociés, formés et exécutés de bonne foi*, d'ordre public). Faute is bijv. plotseling afbreken na lange onderhandelingen zonder motief, parallelle onderhandelingen onder exclusiviteitsbelofte, of voortzetten zonder werkelijke contractswil (*pourparlers de pure forme*). Een *motif légitime* sluit faute uit.\n\n"
                "## Omvang: Manoukian gecodificeerd\n"
                "**Cass. com. 26 nov. 2003 (Manoukian)**: de schade door afbreken omvat niet de voordelen van het niet-gesloten contract, en evenmin de *perte de chance* die te verwerven. Art. 1112 al. 2 nam dat over; de ratificatiewet 2018 voegde — na kritiek dat de ordonnance de perte de chance openliet — de woorden *ni la perte de chance d'obtenir ces avantages* toe. Vergoedbaar zijn dus: gemaakte kosten (études, frais de négociation), en eventueel gemiste kansen op *andere* contracten.\n\n"
                "## Flankerende plichten\n"
                "Art. 1112-1 (*devoir d'information*, d'ordre public) en art. 1112-2 (*confidentialité*) completeren het regime; schending ervan is zelfstandig fautief.\n\n"
                "## Vergelijkende observatie\n"
                "FR is het meest uitgesproken over de **omvang**: zelfs de perte de chance is uitgesloten, waar DE die binnen het negatieve belang soms toelaat en NL het positieve belang in beginsel aanvaardt. Qua **maatstaf** convergeren de drie: vrijheid als uitgangspunt, aansprakelijkheid bij gewekt vertrouwen plus afbreken zonder goede grond."
            ),
            "bronnen": [
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 1112 C. civ.",
                    "titel": "Les négociations précontractuelles",
                    "tekst": (
                        "L'initiative, le déroulement et la rupture des négociations précontractuelles sont libres. Ils doivent impérativement satisfaire aux exigences de la bonne foi.\n\n"
                        "En cas de faute commise dans les négociations, la réparation du préjudice qui en résulte ne peut avoir pour objet de compenser ni la perte des avantages attendus du contrat non conclu, ni la perte de chance d'obtenir ces avantages."
                    ),
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000036829820", "url": _LEGI + "LEGIARTI000036829820",
                    "geldig_van": "2018-10-01", "systematiek": "CC-III-III-I-2-1-1", "rol": "hoofdregel",
                    "notitie": "Versie na de loi de ratification 2018-287. De woorden 'ni la perte de chance d'obtenir ces avantages' ontbraken in de versie van de ordonnance (1 okt. 2016 – 30 sept. 2018); zie de concordantie.",
                    "vertalingen": {
                        "nl": "Het beginnen, het verloop en het afbreken van precontractuele onderhandelingen zijn vrij. Zij moeten dwingend voldoen aan de eisen van de goede trouw. In geval van een fout begaan tijdens de onderhandelingen kan de vergoeding van de daaruit voortvloeiende schade niet strekken tot compensatie van het verlies van de voordelen die van het niet-gesloten contract werden verwacht, noch van het verlies van de kans om die voordelen te verkrijgen.",
                        "de": "Die Aufnahme, der Verlauf und der Abbruch vorvertraglicher Verhandlungen sind frei. Sie müssen zwingend den Anforderungen von Treu und Glauben genügen. Im Falle eines bei den Verhandlungen begangenen Verschuldens kann der Ersatz des daraus entstehenden Schadens weder den Verlust der vom nicht geschlossenen Vertrag erwarteten Vorteile noch den Verlust der Chance, diese Vorteile zu erlangen, zum Gegenstand haben.",
                    },
                },
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 1112 C. civ. (versie 2016)",
                    "titel": "Les négociations précontractuelles — tekst van de ordonnance",
                    "tekst": (
                        "L'initiative, le déroulement et la rupture des négociations précontractuelles sont libres. Ils doivent impérativement satisfaire aux exigences de la bonne foi.\n\n"
                        "En cas de faute commise dans les négociations, la réparation du préjudice qui en résulte ne peut avoir pour objet de compenser la perte des avantages attendus du contrat non conclu."
                    ),
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000032040893", "url": _LEGI + "LEGIARTI000032040893/2016-10-01",
                    "geldig_van": "2016-10-01", "geldig_tot": "2018-09-30", "systematiek": "CC-III-III-I-2-1-1", "rol": "historische versie",
                    "notitie": "Vervallen versie, opgenomen om de wijziging van 2018 zichtbaar te maken. Van toepassing op contracten waarover tussen 1 okt. 2016 en 30 sept. 2018 is onderhandeld (art. 16 loi 2018-287).",
                },
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 1112-1 C. civ.",
                    "titel": "Le devoir d'information",
                    "tekst": (
                        "Celle des parties qui connaît une information dont l'importance est déterminante pour le consentement de l'autre doit l'en informer dès lors que, légitimement, cette dernière ignore cette information ou fait confiance à son cocontractant.\n\n"
                        "Néanmoins, ce devoir d'information ne porte pas sur l'estimation de la valeur de la prestation.\n\n"
                        "Ont une importance déterminante les informations qui ont un lien direct et nécessaire avec le contenu du contrat ou la qualité des parties.\n\n"
                        "Il incombe à celui qui prétend qu'une information lui était due de prouver que l'autre partie la lui devait, à charge pour cette autre partie de prouver qu'elle l'a fournie.\n\n"
                        "Les parties ne peuvent ni limiter, ni exclure ce devoir.\n\n"
                        "Outre la responsabilité de celui qui en était tenu, le manquement à ce devoir d'information peut entraîner l'annulation du contrat dans les conditions prévues aux articles 1130 et suivants."
                    ),
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000032040891", "url": _LEGI + "LEGIARTI000032040891",
                    "geldig_van": "2016-10-01", "systematiek": "CC-III-III-I-2-1-1", "rol": "flankerend",
                    "notitie": "Algemene precontractuele informatieplicht; d'ordre public (al. 5). NL kent slechts een via dwaling (art. 6:228) en Baris/Riezenkamp afgeleide mededelingsplicht; DE via c.i.c. (Aufklärungspflichten).",
                },
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 1104 C. civ.",
                    "titel": "La bonne foi",
                    "tekst": "Les contrats doivent être négociés, formés et exécutés de bonne foi.\n\nCette disposition est d'ordre public.",
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000032040772", "url": _LEGI + "LEGIARTI000032040772",
                    "geldig_van": "2016-10-01", "systematiek": "CC-III-III-I-1", "rol": "norm",
                    "notitie": "Breidt de bonne foi van oud art. 1134 al. 3 (alleen 'exécutées') uit tot de onderhandelings- en vormingsfase.",
                    "vertalingen": {"nl": "Overeenkomsten moeten te goeder trouw worden onderhandeld, gesloten en uitgevoerd. Deze bepaling is van openbare orde."},
                },
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 1240 C. civ.",
                    "titel": "Responsabilité du fait personnel",
                    "tekst": "Tout fait quelconque de l'homme, qui cause à autrui un dommage, oblige celui par la faute duquel il est arrivé à le réparer.",
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000032041571", "url": _LEGI + "LEGIARTI000032041571",
                    "geldig_van": "2016-10-01", "systematiek": "CC-III-III-II", "rol": "grondslag",
                    "notitie": "Ex art. 1382; ongewijzigde tekst sinds 1804. De aansprakelijkheidsgrondslag voor de rupture fautive.",
                    "vertalingen": {"nl": "Elke daad van de mens, die aan een ander schade toebrengt, verplicht degene door wiens schuld zij is ontstaan haar te vergoeden."},
                },
                {
                    "stelsel": "FR", "soort": "rechtspraak", "taal": "fr", "citeertitel": "Cass. com. 26 nov. 2003 (Manoukian)",
                    "titel": "Manoukian c/ Wajsfisz — exclusion de la perte de chance",
                    "tekst": "Les circonstances constitutives d'une faute commise dans l'exercice du droit de rupture unilatérale des pourparlers précontractuels ne sont pas la cause du préjudice consistant dans la perte d'une chance de réaliser les gains que permettait d'espérer la conclusion du contrat.",
                    "vindplaats_type": "pourvoi", "vindplaats": "n° 00-10.243 et 00-10.949, Bull. civ. IV, n° 186", "url": "https://www.legifrance.gouv.fr/juri/id/JURITEXT000007048275",
                    "rol": "rechtspraak",
                    "notitie": "De société Alain Manoukian onderhandelde maandenlang over de overname van aandelen; de verkopers sloten intussen met een derde. De faute (abrupt afbreken, parallelle onderhandelingen verzwegen) stond vast, maar het causaal verband met de gederfde winst — zelfs als perte de chance — werd ontkend. Gecodificeerd in art. 1112 al. 2 (2018).",
                    "opmerking": "Attendu de principe.",
                },
                {
                    "stelsel": "FR", "soort": "literatuur", "taal": "fr", "citeertitel": "Chantepie & Latina, Le nouveau droit des obligations, 2e éd. 2018, n° 196 s.",
                    "titel": "Les négociations (art. 1112 à 1112-2)",
                    "tekst": None, "vindplaats_type": "ISBN", "vindplaats": "9782247179251",
                    "rol": "literatuur",
                },
            ],
        },
        "EU": {
            "kern": "Geen materiële Unieregel; wel een autonome kwalificatie: precontractuele aansprakelijkheid is 'niet-contractueel' (HvJ Tacconi, art. 7 punt 2 Brussel I-bis) en krijgt in Rome II een eigen conflictregel (art. 12: de lex contractus van het beoogde contract).",
            "analyse": (
                "## Kwalificatie: autonoom en niet-contractueel\n"
                "In **Tacconi** (C-334/00) oordeelde het Hof dat een vordering wegens precontractuele aansprakelijkheid, bij gebreke van *vrijwillig aangegane verbintenissen*, geen 'verbintenis uit overeenkomst' is (art. 5 punt 1 EEX-Verdrag) maar een 'verbintenis uit onrechtmatige daad' (art. 5 punt 3, nu art. 7 punt 2 Brussel I-bis). Dat is opmerkelijk tegenover de Duitse contractuele inkleding: het Unierecht volgt hier functioneel de Franse en Nederlandse opvatting.\n\n"
                "## Conflictregel: Rome II art. 12\n"
                "Rome II (864/2007) sluit de c.i.c. uitdrukkelijk in (art. 2 lid 1) en geeft haar een **eigen regel** die de delictuele kwalificatie weer corrigeert: toepasselijk is het recht dat *het beoogde contract* beheerst of zou hebben beheerst (lid 1, *accessoire aanknoping*), subsidiair de lex loci damni, de gemeenschappelijke gewone verblijfplaats of de nauwste band (lid 2). Overweging 30 begrenst het begrip tot schending van informatieplichten en *afbreken van onderhandelingen*; letsel tijdens onderhandelingen valt onder art. 4.\n\n"
                "## Soft law\n"
                "PECL art. 2:301 en DCFR II.–3:301 formuleren de gemeenschappelijke kern: vrijheid om te onderhandelen en af te breken, aansprakelijkheid bij handelen *contrary to good faith and fair dealing*, in het bijzonder bij onderhandelen zonder werkelijke contractswil. Beide beperken de vergoeding tot het verlies door de schending (negatief belang) — dichter bij DE/FR dan bij Plas/Valburg.\n\n"
                "## Vergelijkende observatie\n"
                "De Unie is hier geen vierde materieel stelsel maar een **meta-niveau**: zij dwingt tot een gemeenschappelijke kwalificatie die de nationale dogmatische verschillen (contract/delict) voor bevoegdheid en toepasselijk recht neutraliseert."
            ),
            "bronnen": [
                {
                    "stelsel": "EU", "soort": "wet", "taal": "nl", "citeertitel": "art. 12 Verordening (EG) nr. 864/2007 (Rome II)",
                    "titel": "Precontractuele aansprakelijkheid",
                    "tekst": (
                        "1. De niet-contractuele verbintenis die voortvloeit uit onderhandelingen voorafgaand aan het sluiten van een overeenkomst, wordt, ongeacht of de overeenkomst al dan niet daadwerkelijk is gesloten, beheerst door het recht dat van toepassing is op de overeenkomst of dat op de overeenkomst van toepassing zou zijn geweest indien zij was gesloten.\n\n"
                        "2. Indien het toepasselijke recht niet op grond van lid 1 kan worden bepaald, wordt de verbintenis beheerst door:\n"
                        "a) het recht van het land waar de schade zich voordoet, ongeacht in welk land de schadeveroorzakende gebeurtenis zich heeft voorgedaan en ongeacht in welke landen de indirecte gevolgen van die gebeurtenis zich hebben voorgedaan, of\n"
                        "b) indien de partijen hun gewone verblijfplaats in hetzelfde land hebben op het tijdstip waarop de schadeveroorzakende gebeurtenis zich voordoet, het recht van dat land, of\n"
                        "c) indien uit het geheel der omstandigheden blijkt dat de niet-contractuele verbintenis die voortvloeit uit onderhandelingen voorafgaand aan het sluiten van een overeenkomst, een kennelijk nauwere band heeft met een ander dan het onder a) en b) bedoelde land, het recht van dat andere land."
                    ),
                    "vindplaats_type": "CELEX", "vindplaats": "32007R0864", "url": "https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:32007R0864",
                    "geldig_van": "2009-01-11", "systematiek": "EU-SEC-IPR", "rol": "conflictenrecht",
                    "notitie": "Het opschrift luidt in de Nederlandse versie 'Precontractuele aansprakelijkheid'; de Engelse 'Culpa in contrahendo', de Duitse 'Verschulden bei Vertragsverhandlungen', de Franse 'Culpa in contrahendo'. Overweging 30: autonoom begrip, niet noodzakelijk in de zin van het nationale recht.",
                    "vertalingen": {
                        "en": "1. The law applicable to a non-contractual obligation arising out of dealings prior to the conclusion of a contract, regardless of whether the contract was actually concluded or not, shall be the law that applies to the contract or that would have been applicable to it had it been entered into. 2. Where the law applicable cannot be determined on the basis of paragraph 1, it shall be: (a) the law of the country in which the damage occurs, irrespective of the country in which the event giving rise to the damage occurred and irrespective of the country or countries in which the indirect consequences of that event occurred; or (b) where the parties have their habitual residence in the same country at the time when the event giving rise to the damage occurs, the law of that country; or (c) where it is clear from all the circumstances of the case that the non-contractual obligation arising out of dealings prior to the conclusion of a contract is manifestly more closely connected with a country other than that indicated in points (a) and (b), the law of that other country.",
                    },
                },
                {
                    "stelsel": "EU", "soort": "rechtspraak", "taal": "nl", "citeertitel": "HvJ EG 17 september 2002, C-334/00 (Tacconi)",
                    "titel": "Fonderie Officine Meccaniche Tacconi SpA / Heinrich Wagner Sinto Maschinenfabrik GmbH",
                    "tekst": "In omstandigheden als die van het hoofdgeding, waarin geen sprake is van door een partij jegens een andere vrijwillig aangegane verbintenissen bij onderhandelingen over het sluiten van een overeenkomst, maar wel van een eventuele schending van rechtsregels, met name van de regel die partijen verplicht te goeder trouw te handelen bij deze onderhandelingen, is de vordering waarmee de precontractuele aansprakelijkheid van de verweerder wordt ingeroepen een vordering uit onrechtmatige daad in de zin van artikel 5, sub 3, van het Executieverdrag.",
                    "vindplaats_type": "ECLI", "vindplaats": "ECLI:EU:C:2002:499; CELEX 62000CJ0334", "url": "https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:62000CJ0334",
                    "rol": "rechtspraak",
                    "notitie": "Italiaanse eiser, Duitse verweerder, Italiaans recht (art. 1337 c.c., responsabilità precontrattuale). Het Hof kwalificeert autonoom: zonder vrijwillig aangegane verbintenis geen 'verbintenis uit overeenkomst'. Vgl. Handte (C-26/91).",
                    "opmerking": "Dictum.",
                },
                {
                    "stelsel": "EU", "soort": "softlaw", "taal": "en", "citeertitel": "PECL art. 2:301",
                    "titel": "Negotiations Contrary to Good Faith",
                    "tekst": (
                        "(1) A party is free to negotiate and is not liable for failure to reach an agreement.\n\n"
                        "(2) However, a party who has negotiated or broken off negotiations contrary to good faith and fair dealing is liable for the losses caused to the other party.\n\n"
                        "(3) It is contrary to good faith and fair dealing, in particular, for a party to enter into or continue negotiations with no real intention of reaching an agreement with the other party."
                    ),
                    "vindplaats_type": "PECL", "vindplaats": "Lando/Beale (eds.), Principles of European Contract Law, Parts I and II, 2000", "url": None,
                    "systematiek": "EU-SOFT", "rol": "soft law",
                    "notitie": "Vrijwel letterlijk overgenomen in DCFR II.–3:301 en UNIDROIT PICC art. 2.1.15. Lid 1 = de vrijheid van art. 1112 al. 1 C. civ. en de hoofdregel van CBB/JPO; lid 3 = de Franse 'pourparlers de pure forme'.",
                },
            ],
        },
    },
    "begrippen": [
        {"sleutel": "nl_precontr", "stelsel": "NL", "taal": "nl", "term": "precontractuele aansprakelijkheid (afgebroken onderhandelingen)", "vindplaats": "HR Plas/Valburg; HR CBB/JPO; art. 6:162 BW",
         "definitie": "Rechtersrechtelijke figuur: aansprakelijkheid voor het afbreken van onderhandelingen wanneer dat, gelet op het gerechtvaardigd vertrouwen van de wederpartij of de andere omstandigheden, onaanvaardbaar is. Kan tot vergoeding van het positief contractsbelang leiden."},
        {"sleutel": "de_cic", "stelsel": "DE", "taal": "de", "term": "culpa in contrahendo", "vindplaats": "§§ 311 Abs. 2, 241 Abs. 2, 280 Abs. 1 BGB",
         "definitie": "Haftung für die schuldhafte Verletzung von Rücksichtnahmepflichten aus dem durch Aufnahme von Vertragsverhandlungen begründeten gesetzlichen Schuldverhältnis. Ersatz des negativen Interesses (Vertrauensschaden); Abschlussfreiheit bleibt gewahrt."},
        {"sleutel": "fr_rupture", "stelsel": "FR", "taal": "fr", "term": "rupture fautive des pourparlers", "vindplaats": "art. 1112, 1240 C. civ.",
         "definitie": "Responsabilité extracontractuelle pour faute dans la conduite ou la rupture des négociations, en violation de la bonne foi (art. 1112 al. 1). Réparation limitée : ni les avantages attendus du contrat, ni la perte de chance de les obtenir (art. 1112 al. 2)."},
        {"sleutel": "eu_cic", "stelsel": "EU", "taal": "en", "term": "culpa in contrahendo (Rome II)", "vindplaats": "art. 12 Rome II; overweging 30; HvJ Tacconi",
         "definitie": "Autonomous notion: non-contractual obligation arising out of dealings prior to the conclusion of a contract, covering violation of the duty of disclosure and the breakdown of negotiations. Governed by the (putative) lex contractus."},
        {"sleutel": "nl_rb", "stelsel": "NL", "taal": "nl", "term": "redelijkheid en billijkheid", "vindplaats": "art. 3:12, 6:2, 6:248 BW",
         "definitie": "Objectieve gedragsnorm (de 'goede trouw' in objectieve zin van het oude BW) met aanvullende en derogerende werking. Te onderscheiden van de subjectieve goede trouw van art. 3:11 (niet weten en niet behoren te weten)."},
        {"sleutel": "de_tug", "stelsel": "DE", "taal": "de", "term": "Treu und Glauben", "vindplaats": "§ 242 BGB (§ 157)",
         "definitie": "Objektiver Verhaltensmaßstab (Generalklausel) für Inhalt und Ausübung von Rechten und Pflichten. Streng zu trennen vom guten Glauben (§ 932: subjektive Gutgläubigkeit)."},
        {"sleutel": "fr_bonnefoi", "stelsel": "FR", "taal": "fr", "term": "bonne foi", "vindplaats": "art. 1104, 1112 C. civ.; art. 2274, 2276 C. civ.",
         "definitie": "Notion à double sens : (i) norme objective de loyauté dans la négociation, la formation et l'exécution du contrat (art. 1104) ; (ii) croyance erronée et légitime du possesseur (art. 2274, 550), présumée. La langue française ne distingue pas lexicalement les deux."},
        {"sleutel": "nl_positief", "stelsel": "NL", "taal": "nl", "term": "positief contractsbelang", "vindplaats": "HR Plas/Valburg",
         "definitie": "De schade die bestaat in het verschil tussen de werkelijke vermogenstoestand en die waarin de benadeelde zou hebben verkeerd als het contract was gesloten en nagekomen (gederfde winst). In de derde fase van Plas/Valburg in beginsel vergoedbaar."},
        {"sleutel": "de_negativ", "stelsel": "DE", "taal": "de", "term": "negatives Interesse (Vertrauensschaden)", "vindplaats": "§ 122 Abs. 1, §§ 311 Abs. 2, 280 BGB",
         "definitie": "Der Schaden, den der Geschädigte dadurch erleidet, dass er auf den Vertragsschluss vertraut hat: er ist so zu stellen, als hätte er nie vertraut. Gegenbegriff: Erfüllungsinteresse (positives Interesse)."},
        {"sleutel": "fr_pertechance", "stelsel": "FR", "taal": "fr", "term": "perte de chance", "vindplaats": "art. 1112 al. 2 C. civ.; Cass. com. Manoukian",
         "definitie": "La disparition actuelle et certaine d'une éventualité favorable. En principe réparable en droit français, mais expressément exclue en matière de rupture des pourparlers (perte de chance d'obtenir les avantages du contrat)."},
    ],
    "relaties": [
        ("nl_precontr", "de_cic", "deels", "Zelfde functie (vertrouwensbescherming bij afbreken) maar NL ongeschreven en delictueel, DE gecodificeerd en quasi-contractueel; NL laat het positieve belang toe, DE niet."),
        ("nl_precontr", "fr_rupture", "deels", "Beide delictueel van grondslag; FR sluit de perte de chance en de contractsvoordelen uitdrukkelijk uit waar NL in de derde fase gederfde winst toelaat."),
        ("de_cic", "fr_rupture", "deels", "DE: Schuldverhältnis met Rücksichtnahmepflichten (§ 311 II); FR: responsabilité délictuelle (art. 1240) met wettelijke gedragsnorm (art. 1112). Omvang in beide tot het negatieve belang beperkt."),
        ("eu_cic", "de_cic", "faux_ami", "Rome II gebruikt de Duitse term maar kwalificeert de figuur juist als niet-contractueel (Tacconi), tegengesteld aan de Duitse dogmatiek."),
        ("eu_cic", "nl_precontr", "equivalent", "De autonome EU-notie dekt het Nederlandse geval (afbreken van onderhandelingen) volledig; overweging 30 noemt het uitdrukkelijk."),
        ("eu_cic", "fr_rupture", "equivalent", "FR kwalificeert eveneens delictueel; art. 12 Rome II wijkt alleen voor het toepasselijke recht af van de lex loci damni."),
        ("nl_rb", "de_tug", "equivalent", "Beide objectieve gedragsnormen met aanvullende en beperkende werking; § 242 is historisch het model voor art. 6:2/6:248."),
        ("nl_rb", "fr_bonnefoi", "deels", "FR 'bonne foi' omvat zowel de objectieve norm (art. 1104) als de subjectieve goede trouw (art. 2276); NL splitst in redelijkheid en billijkheid (objectief) en goede trouw (subjectief, art. 3:11)."),
        ("de_tug", "fr_bonnefoi", "deels", "DE scheidt Treu und Glauben (§ 242) lexicaal van guter Glaube (§ 932); FR gebruikt voor beide 'bonne foi'."),
        ("nl_positief", "de_negativ", "geen", "Tegengestelde schadebegrippen: NL aanvaardt in de derde fase het positieve belang, DE beperkt de c.i.c. tot het negatieve."),
        ("de_negativ", "fr_pertechance", "deels", "De perte de chance kan in DE onder het negatieve belang vallen (gemiste alternatieve transactie); in FR is zij bij rupture des pourparlers uitgesloten voor zover zij de contractsvoordelen betreft."),
        ("nl_positief", "fr_pertechance", "geen", "Art. 1112 al. 2 sluit precies uit wat Plas/Valburg toelaat: de (kans op) voordelen van het niet-gesloten contract."),
    ],
}
