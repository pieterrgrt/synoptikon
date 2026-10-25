"""Vraag (a): Hoe gaat de eigendom van een roerende zaak over?"""

_WETTEN_NL = "https://wetten.overheid.nl/BWBR0005291/"
_GII = "https://www.gesetze-im-internet.de/bgb/"
_LEGI = "https://www.legifrance.gouv.fr/codes/article_lc/"

VRAAG = {
    "slug": "eigendomsoverdracht-roerende-zaken",
    "titel": "Hoe gaat de eigendom van een roerende zaak over?",
    "rechtsgebied": "Goederenrecht",
    "tags": "eigendom, overdracht, levering, titel, abstractie, causaal stelsel, roerende zaken, bezit",
    "omschrijving": (
        "Tertium: *de overgang van eigendom van een lichamelijke roerende zaak krachtens overeenkomst* (typisch: koop). "
        "Welke handelingen zijn vereist, op welk moment gaat de eigendom over, en wat is het gevolg als de onderliggende "
        "overeenkomst nietig blijkt? Drie modellen: **causaal traditiestelsel** (NL), **abstract traditiestelsel** (DE) en "
        "**consensueel stelsel** (FR, *solo consensu*). De EU laat het eigendomsrecht aan de lidstaten (art. 345 VWEU) en "
        "regelt slechts flankerend (risico-overgang, conflictenrecht)."
    ),
    "antwoorden": {
        "NL": {
            "kern": "Causaal traditiestelsel: overdracht vereist levering (bezitsverschaffing) krachtens geldige titel door een beschikkingsbevoegde; valt de titel weg, dan is er nooit eigendom overgegaan.",
            "analyse": (
                "## Drie vereisten (art. 3:84 lid 1 BW)\n"
                "1. **Geldige titel**: de rechtsverhouding die de overdracht rechtvaardigt, meestal de koop. Nietigheid of vernietiging van de titel (met terugwerkende kracht, art. 3:53) betekent dat de eigendom *nooit* is overgegaan: het **causale stelsel**. De vervreemder revindiceert (art. 5:2) en hoeft niet terug te vallen op een persoonlijke vordering uit onverschuldigde betaling.\n"
                "2. **Beschikkingsbevoegdheid**: in beginsel alleen de eigenaar (nemo plus). Derdenbescherming via art. 3:86 (roerende zaken, niet-registergoederen: verkrijger te goeder trouw *anders dan om niet*).\n"
                "3. **Levering**: voor roerende zaken in de macht van de vervreemder door *bezitsverschaffing* (art. 3:90 lid 1), die volgens art. 3:114 feitelijk of via de drie traditiones ficta van art. 3:115 kan (brevi manu, constitutum possessorium, longa manu).\n\n"
                "## Goederenrechtelijke overeenkomst?\n"
                "Of naast titel en levering een afzonderlijke 'goederenrechtelijke overeenkomst' nodig is, is omstreden (Meijers: ja, als onderdeel van de levering; vgl. de Duitse *Einigung*). Praktisch relevant bij wilsgebreken die alleen de leveringshandeling raken.\n\n"
                "## Moment van overgang\n"
                "Bij de levering, niet bij de koop. Tot dan blijft de verkoper eigenaar; risico gaat bij consumentenkoop pas over bij bezorging (art. 7:11).\n\n"
                "## Vergelijkende observatie\n"
                "NL staat tussen DE en FR in: wél een afzonderlijke leveringshandeling (anders dan FR), maar géén abstractie (anders dan DE). Art. 3:84 lid 3 (fiduciaverbod) laat zien dat de *strekking* van de titel goederenrechtelijk telt: een zuiver zekerheidsdoel is geen geldige titel."
            ),
            "bronnen": [
                {
                    "stelsel": "NL", "soort": "wet", "taal": "nl", "citeertitel": "art. 3:84 BW",
                    "titel": "Vereisten voor overdracht",
                    "tekst": (
                        "1. Voor overdracht van een goed wordt vereist een levering krachtens geldige titel, verricht door hem die bevoegd is over het goed te beschikken.\n\n"
                        "2. Bij de titel moet het goed met voldoende bepaaldheid omschreven zijn.\n\n"
                        "3. Een rechtshandeling die ten doel heeft een goed over te dragen tot zekerheid of die de strekking mist het goed na de overdracht in het vermogen van de verkrijger te doen vallen, is geen geldige titel van overdracht van dat goed.\n\n"
                        "4. Wordt ter uitvoering van een voorwaardelijke verbintenis geleverd, dan wordt slechts een recht verkregen, dat aan dezelfde voorwaarde als die verbintenis is onderworpen."
                    ),
                    "vindplaats_type": "BWB", "vindplaats": "BWBR0005291, Boek 3, art. 84", "url": _WETTEN_NL + "Boek3/Titeldeel4/Afdeling2/Artikel84/",
                    "geldig_van": "1992-01-01", "systematiek": "BW-3-4-2", "rol": "hoofdregel",
                    "notitie": "Drieluik titel–bevoegdheid–levering. Lid 3 is het fiduciaverbod (Sogelease, HR 19 mei 1995: 'werkelijke overdracht' is wél toegestaan).",
                    "vertalingen": {
                        "de": "1. Zur Übertragung eines Gutes ist eine Lieferung (levering) aufgrund eines gültigen Titels erforderlich, vorgenommen von demjenigen, der über das Gut zu verfügen befugt ist. 2. Im Titel muss das Gut hinreichend bestimmt umschrieben sein. 3. Ein Rechtsgeschäft, das die Übertragung eines Gutes zur Sicherheit bezweckt oder nicht darauf gerichtet ist, das Gut nach der Übertragung in das Vermögen des Erwerbers fallen zu lassen, ist kein gültiger Titel zur Übertragung dieses Gutes. 4. Wird in Erfüllung einer bedingten Verbindlichkeit geliefert, so wird nur ein Recht erworben, das derselben Bedingung unterliegt wie diese Verbindlichkeit.",
                    },
                },
                {
                    "stelsel": "NL", "soort": "wet", "taal": "nl", "citeertitel": "art. 3:90 BW",
                    "titel": "Levering van roerende zaken, niet-registergoederen",
                    "tekst": (
                        "1. De levering vereist voor de overdracht van roerende zaken, niet-registergoederen, die in de macht van de vervreemder zijn, geschiedt door aan de verkrijger het bezit der zaak te verschaffen.\n\n"
                        "2. Blijft de zaak na de levering in handen van de vervreemder, dan werkt de levering tegenover een derde die een ouder recht op de zaak heeft, eerst vanaf het tijdstip dat de zaak in handen van de verkrijger is gekomen, tenzij de oudere gerechtigde met vervreemding heeft ingestemd."
                    ),
                    "vindplaats_type": "BWB", "vindplaats": "BWBR0005291, Boek 3, art. 90", "url": _WETTEN_NL + "Boek3/Titeldeel4/Afdeling2/Artikel90/",
                    "geldig_van": "1992-01-01", "systematiek": "BW-3-4-2", "rol": "levering",
                    "notitie": "Lid 2 beperkt de werking van het constitutum possessorium tegenover oudere gerechtigden: relativering van de levering c.p.",
                    "vertalingen": {
                        "de": "1. Die zur Übertragung beweglicher Sachen, die keine Registergüter sind und sich in der Gewalt des Veräußerers befinden, erforderliche Lieferung erfolgt dadurch, dass dem Erwerber der Besitz der Sache verschafft wird. 2. Bleibt die Sache nach der Lieferung in den Händen des Veräußerers, so wirkt die Lieferung gegenüber einem Dritten mit einem älteren Recht an der Sache erst von dem Zeitpunkt an, in dem die Sache in die Hände des Erwerbers gelangt ist, es sei denn, der ältere Berechtigte hat der Veräußerung zugestimmt.",
                    },
                },
                {
                    "stelsel": "NL", "soort": "wet", "taal": "nl", "citeertitel": "art. 3:86 BW",
                    "titel": "Bescherming van de verkrijger te goeder trouw",
                    "tekst": (
                        "1. Ondanks onbevoegdheid van de vervreemder is een overdracht overeenkomstig artikel 90, 91 of 93 van een roerende zaak, niet-registergoed, of een recht aan toonder of order geldig, indien de overdracht anders dan om niet geschiedt en de verkrijger te goeder trouw is.\n\n"
                        "2. Rust op een in het vorige lid genoemd goed dat overeenkomstig artikel 90, 91 of 93 anders dan om niet wordt overgedragen, een beperkt recht dat de verkrijger op dat tijdstip kent noch behoort te kennen, dan vervalt dit recht, in geval van overdracht overeenkomstig artikel 91 onder dezelfde voorwaarde als waaronder wordt overgedragen.\n\n"
                        "3. Niettemin kan de eigenaar van een roerende zaak, die het bezit daarvan door diefstal heeft verloren, deze gedurende drie jaren, te rekenen van de dag van de diefstal af, als zijn eigendom opeisen, tenzij:\n"
                        "a. de zaak door een natuurlijke persoon die niet in de uitoefening van een beroep of bedrijf handelde, is verkregen van een vervreemder die van het verhandelen aan het publiek van soortgelijke zaken anders dan als veilinghouder zijn bedrijf maakt in een daartoe bestemde bedrijfsruimte, zijnde een gebouwde onroerende zaak of een gedeelte daarvan met de bij het een en ander behorende grond, en in de normale uitoefening van dat bedrijf handelde; of\n"
                        "b. het geld dan wel toonder- of orderpapier betreft.\n\n"
                        "4. Op de termijn van lid 3 zijn de artikelen 316, 318 en 319 betreffende de stuiting van de verjaring van een rechtsvordering van overeenkomstige toepassing."
                    ),
                    "vindplaats_type": "BWB", "vindplaats": "BWBR0005291, Boek 3, art. 86", "url": _WETTEN_NL + "Boek3/Titeldeel4/Afdeling2/Artikel86/",
                    "geldig_van": "1992-01-01", "systematiek": "BW-3-4-2", "rol": "bescherming derden",
                    "notitie": "Functioneel equivalent van § 932 BGB en art. 2276 C. civ.; anders dan § 932 vereist NL verkrijging *om baat*; de driejaarstermijn bij diefstal spiegelt art. 2276 al. 2 C. civ.",
                },
                {
                    "stelsel": "NL", "soort": "wet", "taal": "nl", "citeertitel": "art. 3:114 BW",
                    "titel": "Bezitsoverdracht",
                    "tekst": "Een bezitter draagt zijn bezit over door de verkrijger in staat te stellen die macht uit te oefenen, die hij zelf over het goed kon uitoefenen.",
                    "vindplaats_type": "BWB", "vindplaats": "BWBR0005291, Boek 3, art. 114", "url": _WETTEN_NL + "Boek3/Titeldeel5/Artikel114/",
                    "geldig_van": "1992-01-01", "systematiek": "BW-3-5", "rol": "levering",
                },
                {
                    "stelsel": "NL", "soort": "wet", "taal": "nl", "citeertitel": "art. 3:115 BW",
                    "titel": "Bezitsoverdracht zonder feitelijke handeling (traditio ficta)",
                    "tekst": (
                        "Voor de overdracht van het bezit is een tweezijdige verklaring zonder feitelijke handeling voldoende:\n\n"
                        "a. wanneer de vervreemder de zaak bezit en hij haar krachtens een bij de levering gemaakt beding voortaan voor de verkrijger houdt;\n\n"
                        "b. wanneer de verkrijger houder van de zaak voor de vervreemder was;\n\n"
                        "c. wanneer een derde voor de vervreemder de zaak hield, en haar na de overdracht voor de ontvanger houdt. In dit geval gaat het bezit niet over voordat de derde de overdracht heeft erkend, dan wel de vervreemder of de verkrijger de overdracht aan hem heeft medegedeeld."
                    ),
                    "vindplaats_type": "BWB", "vindplaats": "BWBR0005291, Boek 3, art. 115", "url": _WETTEN_NL + "Boek3/Titeldeel5/Artikel115/",
                    "geldig_van": "1992-01-01", "systematiek": "BW-3-5", "rol": "levering",
                    "notitie": "a = constitutum possessorium (§ 930 BGB), b = traditio brevi manu (§ 929 S. 2 BGB), c = traditio longa manu (vgl. § 931 BGB, maar NL eist erkenning of mededeling).",
                },
                {
                    "stelsel": "NL", "soort": "literatuur", "taal": "nl", "citeertitel": "Asser/Bartels & Van Mierlo 3-IV 2021",
                    "titel": "Algemeen goederenrecht, nr. 200 e.v. (overdracht), nr. 280 e.v. (causaal stelsel)",
                    "tekst": None,
                    "vindplaats_type": "ISBN", "vindplaats": "9789013161717", "url": None,
                    "rol": "literatuur",
                    "notitie": "Standaardwerk; nr. 280 e.v. over de keuze voor het causale stelsel in het NBW en de Duitse abstractie als verworpen alternatief.",
                },
            ],
        },
        "DE": {
            "kern": "Abstraktes Traditionsprinzip: Einigung (dinglicher Vertrag) und Übergabe (§ 929) — losgelöst van het schuldrechtelijke Kausalgeschäft; is de koop nietig, dan is de verkrijger toch eigenaar en moet via § 812 terugleveren.",
            "analyse": (
                "## Trennungs- en Abstraktionsprinzip\n"
                "Het BGB scheidt het **Verpflichtungsgeschäft** (koop, § 433: verplicht slechts tot *übergeben und Eigentum verschaffen*) van het **Verfügungsgeschäft** (de eigendomsoverdracht zelf, §§ 929 ff.). Dat is het *Trennungsprinzip*. Het *Abstraktionsprinzip* voegt daaraan toe dat de geldigheid van de Verfügung **niet afhangt** van de geldigheid van het Kausalgeschäft.\n\n"
                "## Tatbestand § 929 S. 1\n"
                "1. **Einigung**: dinglicher Vertrag, gericht op eigendomsovergang; onderworpen aan het algemene rechtshandelingenrecht (§§ 104 ff., 116 ff.).\n"
                "2. **Übergabe**: volledige opgave van bezit door de vervreemder en bezitsverkrijging door de verkrijger (Realakt). Surrogaten: § 929 S. 2 (brevi manu), § 930 (Besitzkonstitut), § 931 (Abtretung des Herausgabeanspruchs).\n"
                "3. **Einigsein** op het moment van Übergabe (de Einigung is tot dan vrij herroepbaar, anders dan de obligatoire koop).\n"
                "4. **Berechtigung** van de vervreemder; anders gutgläubiger Erwerb §§ 932–935 (niet bij *abhanden gekommene Sachen*, § 935).\n\n"
                "## Gevolg bij nietige koop\n"
                "De verkrijger wordt eigenaar; de vervreemder heeft slechts een **Bereicherungsanspruch** (§ 812 Abs. 1 S. 1 Alt. 1, *Leistungskondiktion*) — een persoonlijke vordering, zwakker in faillissement en bij doorverkoop. Correcties: *Fehleridentität* (hetzelfde wilsgebrek raakt ook de Einigung, bijv. § 123), *Bedingungszusammenhang* (§ 158: Einigung onder voorwaarde van geldige koop) en *Geschäftseinheit* (§ 139, door de BGH terughoudend toegepast).\n\n"
                "## Vergelijkende observatie\n"
                "De abstractie beschermt het rechtsverkeer (verkrijgers hoeven de titel niet te onderzoeken) ten koste van de vervreemder. NL en FR bereiken derdenbescherming langs een andere weg: art. 3:86 BW en art. 2276 C. civ. beschermen de *verdere* verkrijger te goeder trouw, zonder de eerste verkrijger eigenaar te maken."
            ),
            "bronnen": [
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 929 BGB",
                    "titel": "Einigung und Übergabe",
                    "tekst": (
                        "Zur Übertragung des Eigentums an einer beweglichen Sache ist erforderlich, dass der Eigentümer die Sache dem Erwerber übergibt und beide darüber einig sind, dass das Eigentum übergehen soll. "
                        "Ist der Erwerber im Besitz der Sache, so genügt die Einigung über den Übergang des Eigentums."
                    ),
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE091902377", "url": _GII + "__929.html",
                    "geldig_van": "1900-01-01", "systematiek": "BGB-3-3-3-1", "rol": "hoofdregel",
                    "notitie": "Satz 1: Einigung + Übergabe. Satz 2: traditio brevi manu. Let op: de Einigung is een *Vertrag* (dinglicher Vertrag), niet louter een wilsverklaring.",
                    "vertalingen": {
                        "nl": "Voor de overdracht van de eigendom van een roerende zaak is vereist dat de eigenaar de zaak aan de verkrijger overgeeft en dat beiden het erover eens zijn dat de eigendom zal overgaan. Is de verkrijger in het bezit van de zaak, dan volstaat de wilsovereenstemming over de eigendomsovergang.",
                        "fr": "Le transfert de la propriété d'une chose mobilière requiert que le propriétaire remette la chose à l'acquéreur et que les deux soient d'accord sur le transfert de la propriété. Si l'acquéreur est en possession de la chose, l'accord sur le transfert de la propriété suffit.",
                    },
                },
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 930 BGB",
                    "titel": "Besitzkonstitut",
                    "tekst": "Ist der Eigentümer im Besitz der Sache, so kann die Übergabe dadurch ersetzt werden, dass zwischen ihm und dem Erwerber ein Rechtsverhältnis vereinbart wird, vermöge dessen der Erwerber den mittelbaren Besitz erlangt.",
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE092002377", "url": _GII + "__930.html",
                    "geldig_van": "1900-01-01", "systematiek": "BGB-3-3-3-1", "rol": "levering",
                    "notitie": "Grondslag van de Sicherungsübereignung — wat in NL door art. 3:84 lid 3 juist wordt uitgesloten.",
                    "vertalingen": {"nl": "Is de eigenaar in het bezit van de zaak, dan kan de overgave worden vervangen door een tussen hem en de verkrijger overeengekomen rechtsverhouding krachtens welke de verkrijger het middellijke bezit verkrijgt."},
                },
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 931 BGB",
                    "titel": "Abtretung des Herausgabeanspruchs",
                    "tekst": "Ist ein Dritter im Besitz der Sache, so kann die Übergabe dadurch ersetzt werden, dass der Eigentümer dem Erwerber den Anspruch auf Herausgabe der Sache abtritt.",
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE092102377", "url": _GII + "__931.html",
                    "geldig_van": "1900-01-01", "systematiek": "BGB-3-3-3-1", "rol": "levering",
                    "vertalingen": {"nl": "Is een derde in het bezit van de zaak, dan kan de overgave worden vervangen door cessie door de eigenaar aan de verkrijger van de vordering tot afgifte van de zaak."},
                },
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 932 BGB",
                    "titel": "Gutgläubiger Erwerb vom Nichtberechtigten",
                    "tekst": (
                        "(1) Durch eine nach § 929 erfolgte Veräußerung wird der Erwerber auch dann Eigentümer, wenn die Sache nicht dem Veräußerer gehört, es sei denn, dass er zu der Zeit, zu der er nach diesen Vorschriften das Eigentum erwerben würde, nicht in gutem Glauben ist. In dem Falle des § 929 Satz 2 gilt dies jedoch nur dann, wenn der Erwerber den Besitz von dem Veräußerer erlangt hatte.\n\n"
                        "(2) Der Erwerber ist nicht in gutem Glauben, wenn ihm bekannt oder infolge grober Fahrlässigkeit unbekannt ist, dass die Sache nicht dem Veräußerer gehört."
                    ),
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE092202377", "url": _GII + "__932.html",
                    "geldig_van": "1900-01-01", "systematiek": "BGB-3-3-3-1", "rol": "bescherming derden",
                    "notitie": "Goede trouw wordt vermoed; grove nalatigheid schaadt. Geen vereiste van verkrijging om baat (anders: § 816 Abs. 1 S. 2 bij onentgeltliche Verfügung, en art. 3:86 BW).",
                    "vertalingen": {"nl": "(1) Door een vervreemding overeenkomstig § 929 wordt de verkrijger ook eigenaar wanneer de zaak niet aan de vervreemder toebehoort, tenzij hij op het tijdstip waarop hij volgens deze voorschriften de eigendom zou verkrijgen, niet te goeder trouw is. In het geval van § 929, tweede zin, geldt dit echter alleen wanneer de verkrijger het bezit van de vervreemder had verkregen. (2) De verkrijger is niet te goeder trouw wanneer hem bekend is, of ten gevolge van grove nalatigheid onbekend is, dat de zaak niet aan de vervreemder toebehoort."},
                },
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 433 BGB",
                    "titel": "Vertragstypische Pflichten beim Kaufvertrag",
                    "tekst": (
                        "(1) Durch den Kaufvertrag wird der Verkäufer einer Sache verpflichtet, dem Käufer die Sache zu übergeben und das Eigentum an der Sache zu verschaffen. Der Verkäufer hat dem Käufer die Sache frei von Sach- und Rechtsmängeln zu verschaffen.\n\n"
                        "(2) Der Käufer ist verpflichtet, dem Verkäufer den vereinbarten Kaufpreis zu zahlen und die gekaufte Sache abzunehmen."
                    ),
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE042502377", "url": _GII + "__433.html",
                    "geldig_van": "2002-01-01", "systematiek": "BGB-2-8-1", "rol": "verbintenis",
                    "notitie": "Trennungsprinzip in de wettekst zelf: de koop *verplicht* tot eigendomsverschaffing, bewerkt haar niet. Vergelijk art. 1583 C. civ., waar de koop de eigendom overdraagt.",
                    "vertalingen": {"nl": "(1) Door de koopovereenkomst wordt de verkoper van een zaak verplicht de zaak aan de koper over te geven en hem de eigendom van de zaak te verschaffen. De verkoper moet de koper de zaak vrij van materiële en juridische gebreken verschaffen. (2) De koper is verplicht de verkoper de overeengekomen koopprijs te betalen en de gekochte zaak af te nemen."},
                },
                {
                    "stelsel": "DE", "soort": "wet", "taal": "de", "citeertitel": "§ 812 BGB",
                    "titel": "Herausgabeanspruch (ungerechtfertigte Bereicherung)",
                    "tekst": (
                        "(1) Wer durch die Leistung eines anderen oder in sonstiger Weise auf dessen Kosten etwas ohne rechtlichen Grund erlangt, ist ihm zur Herausgabe verpflichtet. Diese Verpflichtung besteht auch dann, wenn der rechtliche Grund später wegfällt oder der mit einer Leistung nach dem Inhalt des Rechtsgeschäfts bezweckte Erfolg nicht eintritt.\n\n"
                        "(2) Als Leistung gilt auch die durch Vertrag erfolgte Anerkennung des Bestehens oder des Nichtbestehens eines Schuldverhältnisses."
                    ),
                    "vindplaats_type": "GII", "vindplaats": "BJNR001950896BJNE080002377", "url": _GII + "__812.html",
                    "geldig_van": "1900-01-01", "systematiek": "BGB-2-8-26", "rol": "correctie abstractie",
                    "notitie": "Het sluitstuk van het Abstraktionsprinzip: zonder rechtsgrond toch eigenaar, dus *Rückübereignung* via Leistungskondiktion (Abs. 1 S. 1 Alt. 1).",
                    "vertalingen": {"nl": "(1) Wie door de prestatie van een ander of op andere wijze te diens koste iets zonder rechtsgrond verkrijgt, is jegens hem tot afgifte verplicht. Deze verplichting bestaat ook wanneer de rechtsgrond later wegvalt of het met een prestatie volgens de inhoud van de rechtshandeling beoogde resultaat niet intreedt. (2) Als prestatie geldt ook de bij overeenkomst gedane erkenning van het bestaan of niet-bestaan van een verbintenis."},
                },
                {
                    "stelsel": "DE", "soort": "literatuur", "taal": "de", "citeertitel": "Baur/Stürner, Sachenrecht, 18. Aufl. 2009, § 5 Rn. 40 ff.",
                    "titel": "Trennungs- und Abstraktionsprinzip",
                    "tekst": None, "vindplaats_type": "ISBN", "vindplaats": "9783406541797",
                    "rol": "literatuur",
                    "notitie": "Klassieke uiteenzetting van de abstractie en haar correcties (Fehleridentität, Bedingungszusammenhang, § 139).",
                },
            ],
        },
        "FR": {
            "kern": "Consensueel stelsel: de eigendom gaat over door de enkele wilsovereenstemming (solo consensu, art. 1196, 1583); levering (délivrance) is slechts een verbintenis van de verkoper; derden worden beschermd door art. 2276 ('en fait de meubles, la possession vaut titre') en art. 1198.",
            "analyse": (
                "## Transfert solo consensu\n"
                "Art. 1196 al. 1 (sinds 2016, voorheen art. 1138 en 711) legt het beginsel vast: bij contracten *ayant pour objet l'aliénation de la propriété* gaat de eigendom over *lors de la conclusion du contrat*. Voor de koop herhaalt art. 1583 het: *la propriété est acquise de droit à l'acheteur … dès qu'on est convenu de la chose et du prix*. Er is dus **geen afzonderlijke goederenrechtelijke handeling**; het contract is tegelijk titel en modus (*effet translatif du contrat*).\n\n"
                "## Rol van de délivrance\n"
                "De *délivrance* (art. 1604) is géén overdrachtsvereiste maar een **verbintenis van de verkoper** (*obligation de délivrer*, art. 1603). Wie haar met de Nederlandse 'levering' gelijkstelt, maakt een vergissing: een klassieke faux ami.\n\n"
                "## Correcties op het consensualisme\n"
                "- *Choses de genre*: overgang pas bij individualisering (art. 1585 e.v.; impliciet in art. 1196 al. 2 'la nature des choses').\n"
                "- *Clause de réserve de propriété* (art. 2367 e.v.): uitstel 'par la volonté des parties'.\n"
                "- Risico volgt eigendom (*res perit domino*, art. 1196 al. 3), tenzij ingebrekestelling.\n\n"
                "## Derdenbescherming\n"
                "Omdat de eigendom al bij het contract overgaat, moet het verkeer worden beschermd tegen onzichtbare overdrachten: art. 1198 al. 1 (bij dubbele verkoop wint wie te goeder trouw als eerste bezit neemt) en art. 2276 (bezit van roerende zaken geldt als titel; revindicatie bij verlies of diefstal gedurende drie jaar). Beide zijn functioneel equivalent aan art. 3:86 BW en § 932 BGB, maar systematisch verankerd in het *bezit*, niet in de overdracht.\n\n"
                "## Nietigheid van de koop\n"
                "Het stelsel is **causaal**: *nullité* werkt terug (art. 1178), de eigendom is nooit overgegaan en wordt gerevindiceerd; *restitutions* volgens art. 1352 e.v. Hier staat FR dicht bij NL en tegenover DE."
            ),
            "bronnen": [
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 1196 C. civ.",
                    "titel": "L'effet translatif",
                    "tekst": (
                        "Dans les contrats ayant pour objet l'aliénation de la propriété ou la cession d'un autre droit, le transfert s'opère lors de la conclusion du contrat.\n\n"
                        "Ce transfert peut être différé par la volonté des parties, la nature des choses ou par l'effet de la loi.\n\n"
                        "Le transfert de propriété emporte transfert des risques de la chose. Toutefois le débiteur de l'obligation de délivrer en retrouve la charge à compter de sa mise en demeure, conformément à l'article 1344-2 et sous réserve des règles prévues à l'article 1351-1."
                    ),
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000032040711", "url": _LEGI + "LEGIARTI000032040711",
                    "geldig_van": "2016-10-01", "systematiek": "CC-III-III-I-4-1-2", "rol": "hoofdregel",
                    "notitie": "Opvolger van art. 1138 (oud). Het consensualisme is nu een algemene contractenrechtelijke regel (Livre III, Titre III), niet langer verstopt in de koop.",
                    "vertalingen": {
                        "nl": "In overeenkomsten die de vervreemding van eigendom of de overdracht van een ander recht tot voorwerp hebben, vindt de overgang plaats bij het sluiten van de overeenkomst. Deze overgang kan worden uitgesteld door de wil van partijen, door de aard van de zaken of door de werking van de wet. De overgang van eigendom brengt de overgang van het risico van de zaak mee. De schuldenaar van de verbintenis tot aflevering draagt het risico echter opnieuw vanaf zijn ingebrekestelling, overeenkomstig artikel 1344-2 en behoudens de regels van artikel 1351-1.",
                        "de": "Bei Verträgen, die die Veräußerung des Eigentums oder die Abtretung eines anderen Rechts zum Gegenstand haben, erfolgt der Übergang mit dem Abschluss des Vertrags. Dieser Übergang kann durch den Willen der Parteien, die Natur der Sachen oder kraft Gesetzes hinausgeschoben werden. Der Eigentumsübergang bewirkt den Übergang der Gefahr der Sache. Der Schuldner der Übergabepflicht trägt die Gefahr jedoch wieder ab seiner Inverzugsetzung gemäß Artikel 1344-2 und vorbehaltlich der Regeln des Artikels 1351-1.",
                    },
                },
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 1198 C. civ.",
                    "titel": "Conflit entre acquéreurs successifs",
                    "tekst": (
                        "Lorsque deux acquéreurs successifs d'un même meuble corporel tiennent leur droit d'une même personne, celui qui a pris possession de ce meuble en premier est préféré, même si son droit est postérieur, à condition qu'il soit de bonne foi.\n\n"
                        "Lorsque deux acquéreurs successifs de droits portant sur un même immeuble tiennent leur droit d'une même personne, celui qui a, le premier, publié son titre d'acquisition passé en la forme authentique au fichier immobilier est préféré, même si son droit est postérieur, à condition qu'il soit de bonne foi."
                    ),
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000032040705", "url": _LEGI + "LEGIARTI000032040705",
                    "geldig_van": "2016-10-01", "systematiek": "CC-III-III-I-4-1-2", "rol": "bescherming derden",
                    "notitie": "Opvolger van art. 1141 (oud). Laat zien dat *possession* het consensualisme corrigeert: feitelijke macht beslist tussen twee 'eigenaars'.",
                    "vertalingen": {"nl": "Wanneer twee opeenvolgende verkrijgers van dezelfde lichamelijke roerende zaak hun recht van dezelfde persoon afleiden, wordt degene die als eerste het bezit van die zaak heeft genomen voorgetrokken, ook al is zijn recht van latere datum, mits hij te goeder trouw is. Wanneer twee opeenvolgende verkrijgers van rechten op dezelfde onroerende zaak hun recht van dezelfde persoon afleiden, wordt degene die als eerste zijn in authentieke vorm verleden verkrijgingstitel in het hypotheekregister heeft gepubliceerd voorgetrokken, ook al is zijn recht van latere datum, mits hij te goeder trouw is."},
                },
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 2276 C. civ.",
                    "titel": "En fait de meubles, la possession vaut titre",
                    "tekst": (
                        "En fait de meubles, la possession vaut titre.\n\n"
                        "Néanmoins, celui qui a perdu ou auquel il a été volé une chose peut la revendiquer pendant trois ans à compter du jour de la perte ou du vol, contre celui dans les mains duquel il la trouve ; sauf à celui-ci son recours contre celui duquel il la tient."
                    ),
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000019017433", "url": _LEGI + "LEGIARTI000019017433",
                    "geldig_van": "2008-06-19", "systematiek": "CC-III-XXI-III-3", "rol": "bescherming derden",
                    "notitie": "Vóór 2008: art. 2279. Dubbele functie (*fonction probatoire* en *fonction acquisitive*). 'Titre' betekent hier *rechtsgrond/eigendomsbewijs*, niet de Nederlandse 'titel' van art. 3:84 — tweede faux ami. Vgl. art. 3:86 lid 3 BW (drie jaar bij diefstal) en § 935 BGB (geen gutgläubiger Erwerb bij abhanden gekommene Sachen, zonder termijn).",
                    "vertalingen": {
                        "nl": "Ten aanzien van roerende zaken geldt bezit als titel. Niettemin kan hij die een zaak heeft verloren of van wie een zaak is gestolen, haar gedurende drie jaar vanaf de dag van het verlies of de diefstal opeisen van degene in wiens handen hij haar aantreft; onverminderd diens verhaal op degene van wie hij haar heeft verkregen.",
                        "de": "Bei beweglichen Sachen gilt der Besitz als Titel. Wer jedoch eine Sache verloren hat oder wem sie gestohlen wurde, kann sie drei Jahre lang, vom Tag des Verlusts oder Diebstahls an, von demjenigen herausverlangen, in dessen Händen er sie findet; diesem bleibt der Rückgriff gegen denjenigen vorbehalten, von dem er sie hat.",
                    },
                },
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 1583 C. civ.",
                    "titel": "Perfection de la vente",
                    "tekst": "Elle est parfaite entre les parties, et la propriété est acquise de droit à l'acheteur à l'égard du vendeur, dès qu'on est convenu de la chose et du prix, quoique la chose n'ait pas encore été livrée ni le prix payé.",
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000006441280", "url": _LEGI + "LEGIARTI000006441280",
                    "geldig_van": "1804-03-16", "systematiek": "CC-III-VI-I", "rol": "koop",
                    "notitie": "Ongewijzigde Napoleontische tekst. 'Quoique la chose n'ait pas encore été livrée': het tegendeel van § 433/§ 929 BGB en art. 3:84/3:90 BW.",
                    "vertalingen": {"nl": "Zij [de koop] is tussen partijen voltooid, en de eigendom is van rechtswege door de koper verkregen ten opzichte van de verkoper, zodra men het eens is geworden over de zaak en de prijs, ook al is de zaak nog niet afgeleverd en de prijs nog niet betaald."},
                },
                {
                    "stelsel": "FR", "soort": "wet", "taal": "fr", "citeertitel": "art. 1604 C. civ.",
                    "titel": "La délivrance",
                    "tekst": "La délivrance est le transport de la chose vendue en la puissance et possession de l'acheteur.",
                    "vindplaats_type": "LEGIARTI", "vindplaats": "LEGIARTI000006441308", "url": _LEGI + "LEGIARTI000006441308",
                    "geldig_van": "1804-03-16", "systematiek": "CC-III-VI-IV", "rol": "verbintenis",
                    "notitie": "Délivrance = uitvoering van een verbintenis van de verkoper (art. 1603), niet constitutief voor de eigendomsovergang.",
                    "vertalingen": {"nl": "De aflevering is het brengen van de verkochte zaak in de macht en het bezit van de koper."},
                },
                {
                    "stelsel": "FR", "soort": "literatuur", "taal": "fr", "citeertitel": "Terré, Simler, Lequette & Chénedé, Les obligations, 13e éd. 2022, n° 660 s.",
                    "titel": "L'effet translatif du contrat",
                    "tekst": None, "vindplaats_type": "ISBN", "vindplaats": "9782247216543",
                    "rol": "literatuur",
                },
            ],
        },
        "EU": {
            "kern": "Geen Unieregel voor de eigendomsovergang zelf (art. 345 VWEU; art. 4 sub b CISG sluit haar uit); flankerend: risico-overgang bij consumentenkoop (art. 20 Richtlijn 2011/83/EU) en het DCFR als model (VIII.–2:101: consensueel met leveringsvereiste tenzij anders overeengekomen).",
            "analyse": (
                "## Bevoegdheidsvoorbehoud\n"
                "Art. 345 VWEU laat 'de regeling van het eigendomsrecht in de lidstaten' onverlet. Het HvJ legt dat beperkt uit (het ontslaat lidstaten niet van de verkeersvrijheden), maar de **wijze van eigendomsovergang** is onbetwist nationaal. Ook het Weens Koopverdrag (CISG, geen EU-recht maar in alle drie de stelsels van kracht) regelt in art. 4 sub b uitdrukkelijk *niet* 'de gevolgen die het contract kan hebben voor de eigendom van de verkochte zaken'.\n\n"
                "## Wat de Unie wél regelt\n"
                "- **Risico-overgang** bij consumentenkoop: art. 20 Richtlijn 2011/83/EU koppelt het risico aan het *fysieke bezit* van de consument, los van de nationale eigendomsregel. Dat harmoniseert feitelijk het gevolg waar FR (*res perit domino*) en DE/NL (§ 446 BGB, art. 7:10 BW: bij aflevering) uiteenlopen.\n"
                "- **Conflictenrecht**: de *lex rei sitae* is in alle lidstaten ongeschreven of nationaal gecodificeerd (art. 10:127 BW, art. 43 EGBGB); de Unie heeft het zakelijke conflictenrecht niet geharmoniseerd, anders dan het verbintenissenrecht (Rome I).\n\n"
                "## Soft law als tertium\n"
                "Het DCFR (Boek VIII) kiest in VIII.–2:101 een **gemengd model**: de overgang vereist een geldige *underlying contract or other juridical act* (causaal, zoals NL/FR), én in beginsel *delivery* (traditie, zoals NL/DE), maar partijen kunnen het moment vrij bepalen (naar FR). Het DCFR is daarmee zelf een rechtsvergelijkend compromis en maakt de drie modellen goed zichtbaar."
            ),
            "bronnen": [
                {
                    "stelsel": "EU", "soort": "wet", "taal": "nl", "citeertitel": "art. 345 VWEU",
                    "titel": "Regeling van het eigendomsrecht",
                    "tekst": "De Verdragen laten de regeling van het eigendomsrecht in de lidstaten onverlet.",
                    "vindplaats_type": "CELEX", "vindplaats": "12016E345", "url": "https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:12016E345",
                    "geldig_van": "2009-12-01", "systematiek": "EU-VWEU", "rol": "bevoegdheid",
                    "notitie": "Ex art. 295 EG, ex art. 222 EEG. Het HvJ (o.a. C-105/12 t/m C-107/12, Essent) leest het eng: geen vrijbrief voor beperkingen van de verkeersvrijheden.",
                    "vertalingen": {
                        "de": "Die Verträge lassen die Eigentumsordnung in den verschiedenen Mitgliedstaaten unberührt.",
                        "fr": "Les traités ne préjugent en rien le régime de la propriété dans les États membres.",
                        "en": "The Treaties shall in no way prejudice the rules in Member States governing the system of property ownership.",
                    },
                },
                {
                    "stelsel": "EU", "soort": "wet", "taal": "nl", "citeertitel": "art. 20 Richtlijn 2011/83/EU",
                    "titel": "Risico-overgang (consumentenrechten)",
                    "tekst": "Voor overeenkomsten waarbij de handelaar de goederen opstuurt naar de consument, gaat het risico van verlies of beschadiging van de goederen over op de consument zodra hij of een door hem aangewezen derde partij, die niet de vervoerder is, de goederen fysiek in bezit heeft gekregen. Het risico gaat echter over op de consument bij levering aan de vervoerder, als deze van de consument de opdracht heeft gekregen de goederen te vervoeren en deze keuze niet door de handelaar was geboden, onverminderd de rechten van de consument ten aanzien van de vervoerder.",
                    "vindplaats_type": "CELEX", "vindplaats": "32011L0083", "url": "https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:32011L0083",
                    "geldig_van": "2014-06-13", "systematiek": "EU-SEC-CONS", "rol": "flankerend",
                    "notitie": "Omgezet in art. 7:11 BW en § 475 Abs. 2 BGB; in FR art. L. 216-4 C. consom. Het risico wordt losgekoppeld van de eigendomsvraag.",
                },
                {
                    "stelsel": "EU", "soort": "softlaw", "taal": "en", "citeertitel": "DCFR VIII.–2:101",
                    "titel": "Requirements for the transfer of ownership in general",
                    "tekst": (
                        "(1) The transfer of ownership of goods under this Chapter requires that:\n\n"
                        "(a) the goods exist;\n(b) the goods are transferable;\n(c) the transferor has the right or authority to transfer the ownership;\n(d) the transferee is entitled as against the transferor to the transfer of ownership by virtue of a contract or other juridical act, a court order or a rule of law; and\n(e) there is an agreement as to the time ownership is to pass and the conditions of this agreement are met, or, in the absence of such agreement, delivery or an equivalent to delivery.\n\n"
                        "(2) For the purposes of paragraph (1)(e) the delivery or equivalent to delivery must be based on, or referable to, the entitlement under the contract or other juridical act, court order or rule of law.\n\n"
                        "(3) Where the contract or other juridical act, court order or rule of law defines the goods in generic terms, ownership can pass only when the goods are identified to it. […]"
                    ),
                    "vindplaats_type": "DCFR", "vindplaats": "Von Bar/Clive (eds.), DCFR Full Edition, Vol. 5, 2009, p. 4381 e.v.", "url": None,
                    "systematiek": "EU-SOFT", "rol": "soft law",
                    "notitie": "Causaal (lid 1 sub d, lid 2) + traditie als default (lid 1 sub e) + partijautonomie over het moment. Een bewust compromis tussen de drie nationale modellen.",
                    "opmerking": "Tekst ingekort; leden 4 en 5 weggelaten.",
                },
                {
                    "stelsel": "EU", "soort": "wet", "taal": "en", "citeertitel": "art. 4 CISG",
                    "titel": "Scope of the Convention (exclusion of property effects)",
                    "tekst": "This Convention governs only the formation of the contract of sale and the rights and obligations of the seller and the buyer arising from such a contract. In particular, except as otherwise expressly provided in this Convention, it is not concerned with: (a) the validity of the contract or of any of its provisions or of any usage; (b) the effect which the contract may have on the property in the goods sold.",
                    "vindplaats_type": "UNTS", "vindplaats": "1489 UNTS 3", "url": "https://uncitral.un.org/en/texts/salegoods/conventions/sale_of_goods/cisg",
                    "geldig_van": "1988-01-01", "systematiek": "EU-SOFT", "rol": "afbakening",
                    "opmerking": "Geen Unierecht; opgenomen omdat het de gemeenschappelijke uitsluiting van de eigendomsvraag uit het geharmoniseerde kooprecht markeert. NL, DE en FR zijn verdragspartij.",
                },
            ],
        },
    },
    "begrippen": [
        {"sleutel": "nl_levering", "stelsel": "NL", "taal": "nl", "term": "levering", "vindplaats": "art. 3:84, 3:90 BW",
         "definitie": "De rechtshandeling waardoor, krachtens titel, de overdracht wordt voltooid; voor roerende zaken bezitsverschaffing (art. 3:90, 3:114, 3:115). Omvat zowel de feitelijke handeling als (volgens de heersende leer) de goederenrechtelijke wilsovereenstemming."},
        {"sleutel": "de_uebergabe", "stelsel": "DE", "taal": "de", "term": "Übergabe", "vindplaats": "§ 929 S. 1 BGB",
         "definitie": "Realakt: vollständige Aufgabe des Besitzes durch den Veräußerer und Erlangung des Besitzes durch den Erwerber (oder Geheißperson). Neben der Einigung zweites Tatbestandsmerkmal der Übereignung; ersetzbar durch §§ 930, 931."},
        {"sleutel": "de_einigung", "stelsel": "DE", "taal": "de", "term": "Einigung (dinglicher Vertrag)", "vindplaats": "§ 929 S. 1 BGB",
         "definitie": "Der auf den Eigentumsübergang gerichtete dingliche Vertrag. Abstrakt vom Kausalgeschäft; bis zur Übergabe frei widerruflich; unterliegt den allgemeinen Regeln über Willenserklärungen."},
        {"sleutel": "fr_delivrance", "stelsel": "FR", "taal": "fr", "term": "délivrance", "vindplaats": "art. 1604 C. civ.",
         "definitie": "Le transport de la chose vendue en la puissance et possession de l'acheteur : exécution d'une obligation du vendeur (art. 1603), sans effet sur le transfert de propriété, qui s'opère solo consensu."},
        {"sleutel": "nl_titel", "stelsel": "NL", "taal": "nl", "term": "titel", "vindplaats": "art. 3:84 lid 1 BW",
         "definitie": "De rechtsverhouding die de overdracht rechtvaardigt (iusta causa traditionis), doorgaans de obligatoire overeenkomst. Geldigheidsvereiste voor de overdracht: causaal stelsel."},
        {"sleutel": "de_kausalgeschaeft", "stelsel": "DE", "taal": "de", "term": "Kausalgeschäft / Rechtsgrund", "vindplaats": "§ 433, § 812 Abs. 1 BGB",
         "definitie": "Das schuldrechtliche Verpflichtungsgeschäft, das den Rechtsgrund (causa) für die Verfügung bildet. Kraft Abstraktionsprinzips keine Wirksamkeitsvoraussetzung der Übereignung; sein Fehlen begründet nur die Leistungskondiktion."},
        {"sleutel": "fr_titre", "stelsel": "FR", "taal": "fr", "term": "titre (possession vaut titre)", "vindplaats": "art. 2276 C. civ.",
         "definitie": "Dans la maxime « en fait de meubles, la possession vaut titre », le titre désigne le titre de propriété (justification du droit), non une causa de transfert : la possession de bonne foi dispense de prouver l'acquisition."},
        {"sleutel": "de_abstraktion", "stelsel": "DE", "taal": "de", "term": "Abstraktionsprinzip", "vindplaats": "§§ 929, 812 BGB (ungeschrieben)",
         "definitie": "Grundsatz, dass die Wirksamkeit des Verfügungsgeschäfts von der Wirksamkeit des zugrunde liegenden Verpflichtungsgeschäfts unabhängig ist. Ergänzt das Trennungsprinzip. Korrekturen: Fehleridentität, Bedingungszusammenhang, § 139."},
        {"sleutel": "nl_causaal", "stelsel": "NL", "taal": "nl", "term": "causaal stelsel", "vindplaats": "art. 3:84 lid 1 BW",
         "definitie": "De geldigheid van de overdracht hangt af van de geldigheid van de titel. Nietigheid of vernietiging van de titel betekent dat geen eigendom is overgegaan; de vervreemder revindiceert."},
        {"sleutel": "nl_bezit", "stelsel": "NL", "taal": "nl", "term": "bezit", "vindplaats": "art. 3:107 BW",
         "definitie": "Het houden van een goed voor zichzelf. Wie voor een ander houdt is houder, geen bezitter (art. 3:107 lid 4, 3:108)."},
        {"sleutel": "de_besitz", "stelsel": "DE", "taal": "de", "term": "Besitz", "vindplaats": "§ 854 BGB",
         "definitie": "Die tatsächliche Gewalt über eine Sache, unabhängig vom Willen, sie als eigene zu haben: auch der Mieter ist (Fremd-)Besitzer. Unterscheidung Eigen-/Fremdbesitz (§ 872), unmittelbarer/mittelbarer Besitz (§ 868)."},
        {"sleutel": "fr_possession", "stelsel": "FR", "taal": "fr", "term": "possession", "vindplaats": "art. 2255 C. civ.",
         "definitie": "La détention ou la jouissance d'une chose que nous tenons ou exerçons par nous-mêmes, ou par un autre qui la tient ou l'exerce en notre nom : corpus et animus domini. Le détenteur précaire (locataire) n'est pas possesseur (art. 2266)."},
    ],
    "relaties": [
        ("nl_levering", "de_uebergabe", "deels", "Übergabe is alleen de feitelijke handeling (Realakt); de NL levering omvat ook de wilsovereenstemming, die in DE als afzonderlijke Einigung geldt. Übergabe + Einigung ≈ levering."),
        ("nl_levering", "fr_delivrance", "faux_ami", "Délivrance is uitvoering van een verbintenis van de verkoper en heeft geen goederenrechtelijk effect; de eigendom is al solo consensu overgegaan. Levering is in NL constitutief."),
        ("de_uebergabe", "fr_delivrance", "faux_ami", "Beide betekenen 'overgave', maar Übergabe is overdrachtsvereiste, délivrance slechts een contractuele verbintenis."),
        ("nl_levering", "de_einigung", "deels", "De goederenrechtelijke overeenkomst zit in NL verscholen in de levering; in DE is zij een zelfstandig dinglicher Vertrag."),
        ("nl_titel", "de_kausalgeschaeft", "deels", "Inhoudelijk dezelfde figuur (de causa), maar in NL geldigheidsvereiste (causaal), in DE niet (abstract)."),
        ("nl_titel", "fr_titre", "faux_ami", "In art. 2276 betekent 'titre' eigendomsbewijs/rechtsgrond van het bezit, niet de iusta causa traditionis van art. 3:84 BW."),
        ("de_abstraktion", "nl_causaal", "geen", "Tegengestelde beginselen; NL heeft bewust voor het causale stelsel gekozen (Meijers)."),
        ("nl_bezit", "de_besitz", "deels", "NL bezit vereist houden voor zichzelf (animus domini); DE Besitz is louter tatsächliche Gewalt, ook de huurder is Besitzer. NL 'houderschap' ≈ DE 'Fremdbesitz'."),
        ("nl_bezit", "fr_possession", "equivalent", "Beide eisen corpus én animus domini; de houder/détenteur précaire is geen bezitter."),
        ("de_besitz", "fr_possession", "faux_ami", "FR possession vereist animus domini; DE Besitz niet. De Franse détenteur précaire is in DE wél Besitzer."),
    ],
}
