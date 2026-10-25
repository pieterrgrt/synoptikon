"""Corresponderende artikelen in NL, DE en FR, per thema.

Elk thema is een functionele vraag; per stelsel de artikelen die haar
beantwoorden. Een lid is (stelsel, verwijzing[, rol[, opmerking]]). De
verwijzing wordt gelezen door `services.artikelen.lees`: "3:84", "§ 929",
"art. 1196", "§§ 203–213", "art. 1242 al. 5", "§ 1 ProdHaftG",
"art. L217-3 C. consom.". "—" betekent: geen wettelijke regeling (de
opmerking zegt dan waar het wel geregeld is).

Correspondentie is functioneel, niet terminologisch: dat § 929 BGB en
art. 3:84 BW "corresponderen" betekent dat ze dezelfde vraag beantwoorden,
niet dat ze hetzelfde zeggen. De verschillen staan in rol en opmerking, en
uitgebreider in de vragen en de begrippenkaart. Controleer vóór gebruik in
een werkstuk; de artikelpagina linkt naar de officiële tekst als die als
bron is ingevoerd of geïmporteerd.
"""

CORRESPONDENTIES = [
    # --- Rechtshandelingen -------------------------------------------------
    {
        "titel": "Redelijkheid en billijkheid / Treu und Glauben / bonne foi",
        "rechtsgebied": "Rechtshandelingen",
        "toelichting": "De open norm die het schuldrecht aanvult en beperkt. NL kent twee functies (aanvullend en derogerend), DE leidt beide uit § 242 af, FR noemt de goede trouw sinds 2016 ook voor onderhandelingen en totstandkoming.",
        "artikelen": [
            ("NL", "6:2", "hoofdregel", "Verbintenissen in het algemeen."),
            ("NL", "6:248", "overeenkomsten", "Lid 1 aanvullend, lid 2 derogerend."),
            ("NL", "3:12", "maatstaf", "Wat redelijkheid en billijkheid eisen: rechtsbeginselen, rechtsovertuiging, maatschappelijke belangen."),
            ("DE", "§ 242", "hoofdregel", "Grondslag voor Nebenpflichten, Rechtsmissbrauch, Verwirkung."),
            ("DE", "§ 157", "uitleg", "Uitleg van overeenkomsten naar Treu und Glauben."),
            ("FR", "art. 1104", "hoofdregel", "Onderhandeling, totstandkoming en uitvoering; van openbare orde."),
        ],
    },
    {
        "titel": "Misbruik van recht",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:13", "hoofdregel"),
            ("DE", "§ 226", "smal", "Schikaneverbot: alleen als het enige doel is schade toe te brengen; de ruimere toets loopt via § 242."),
            ("DE", "§ 242", "aanvullend"),
            ("FR", "—", "geen regeling", "Abus de droit is jurisprudentieel (Req. 3 août 1915, Clément-Bayard)."),
        ],
    },
    {
        "titel": "Handelingsbekwaamheid",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:32", "hoofdregel", "Onbekwaamheid → vernietigbaarheid."),
            ("NL", "1:234", "minderjarigen", "Toestemming van de wettelijk vertegenwoordiger; handelingen die in het maatschappelijk verkeer gebruikelijk zijn."),
            ("DE", "§§ 104–113", "hoofdregel", "Geschäftsunfähigkeit (nichtig, § 105) en beschränkte Geschäftsfähigkeit (schwebend unwirksam, § 108)."),
            ("FR", "art. 1145", "hoofdregel"),
            ("FR", "art. 1146", "onbekwamen", "Minderjarigen en beschermde meerderjarigen."),
            ("FR", "art. 1147–1148", "sanctie", "Nullité relative; actes courants blijven geldig."),
        ],
    },
    {
        "titel": "Wil en verklaring; gerechtvaardigd vertrouwen",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:33", "hoofdregel", "Wil die zich door een verklaring heeft geopenbaard."),
            ("NL", "3:35", "vertrouwen", "Gerechtvaardigd vertrouwen op een verklaring."),
            ("DE", "§§ 116–118", "wilsontbreken", "Geheimer Vorbehalt, Scheingeschäft, Mangel der Ernstlichkeit."),
            ("DE", "§ 133", "uitleg", "Wirklicher Wille, niet de letterlijke uitdrukking."),
            ("FR", "art. 1188", "uitleg", "Commune intention des parties; anders de redelijke persoon."),
        ],
    },
    {
        "titel": "Vormvrijheid en vormvoorschriften",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:37 lid 1", "vormvrijheid"),
            ("NL", "3:39", "sanctie", "Nietig bij niet-naleving van een vormvoorschrift."),
            ("DE", "§ 125", "sanctie", "Nichtigkeit wegen Formmangels."),
            ("DE", "§ 311b", "voorbeeld", "Notariële akte bij grondkoop."),
            ("FR", "art. 1172", "vormvrijheid", "Consensualisme; uitzonderingen voor solennele contracten."),
        ],
    },
    {
        "titel": "Nietigheid wegens strijd met de wet, openbare orde of goede zeden",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:40", "hoofdregel", "Lid 1 nietig; lid 2/3 bij strijd met dwingende wetsbepalingen."),
            ("DE", "§ 134", "gesetzliches Verbot"),
            ("DE", "§ 138", "Sittenwidrigkeit"),
            ("FR", "art. 6", "algemeen"),
            ("FR", "art. 1162", "hoofdregel", "Contenu licite; sinds 2016 geen 'cause' meer."),
        ],
    },
    {
        "titel": "Partiële nietigheid en conversie",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:41", "partiële nietigheid"),
            ("NL", "3:42", "conversie"),
            ("DE", "§ 139", "Teilnichtigkeit", "Vermoeden van algehele nietigheid: omgekeerd aan NL."),
            ("DE", "§ 140", "Umdeutung"),
            ("FR", "art. 1184", "partiële nietigheid"),
        ],
    },
    {
        "titel": "Bekrachtiging en bevestiging",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:55", "bevestiging"),
            ("NL", "3:58", "bekrachtiging"),
            ("DE", "§ 141", "Bestätigung nichtiges Rechtsgeschäft"),
            ("DE", "§ 144", "Bestätigung anfechtbares Rechtsgeschäft"),
            ("FR", "art. 1182", "confirmation"),
        ],
    },
    {
        "titel": "Dwaling / Irrtum / erreur",
        "rechtsgebied": "Rechtshandelingen",
        "toelichting": "NL regelt dwaling bij de overeenkomst (Boek 6), DE bij de wilsverklaring (Buch 1), FR bij de geldigheid van het contract.",
        "artikelen": [
            ("NL", "6:228", "hoofdregel", "Kenbaarheid en mededelingsplicht; risicoverdeling lid 2."),
            ("DE", "§ 119", "hoofdregel", "Inhalts-, Erklärungs- en Eigenschaftsirrtum."),
            ("DE", "§§ 121–122", "termijn en schade", "Unverzüglich aanvechten; Vertrauensschaden vergoeden."),
            ("FR", "art. 1132–1136", "hoofdregel", "Qualités essentielles; erreur sur la valeur of op motieven telt niet."),
        ],
    },
    {
        "titel": "Bedrog / arglistige Täuschung / dol",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:44 lid 3", "hoofdregel"),
            ("DE", "§ 123", "hoofdregel"),
            ("DE", "§ 124", "termijn"),
            ("FR", "art. 1137–1139", "hoofdregel", "Réticence dolosive uitdrukkelijk (1137 al. 2)."),
        ],
    },
    {
        "titel": "Bedreiging / Drohung / violence",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:44 lid 2", "hoofdregel"),
            ("DE", "§ 123", "hoofdregel", "Widerrechtliche Drohung."),
            ("FR", "art. 1140–1142", "hoofdregel"),
        ],
    },
    {
        "titel": "Misbruik van omstandigheden / Wucher / abus de dépendance",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:44 lid 4", "hoofdregel", "Vernietigbaar."),
            ("DE", "§ 138 Abs. 2", "deels", "Wucher → nichtig; strenger (auffälliges Missverhältnis)."),
            ("FR", "art. 1143", "deels", "Abus de l'état de dépendance; gecodificeerd in 2016 als vorm van violence."),
        ],
    },
    {
        "titel": "Vernietiging: wijze en terugwerkende kracht",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:49–3:51", "wijze", "Buitengerechtelijke verklaring of rechterlijke uitspraak."),
            ("NL", "3:53", "terugwerking"),
            ("DE", "§ 142", "terugwerking"),
            ("DE", "§ 143", "wijze", "Anfechtungserklärung."),
            ("FR", "art. 1178", "wijze", "Door de rechter, of in onderling overleg vastgesteld; sinds 2016 ook buitengerechtelijk (1178 al. 1)."),
            ("FR", "art. 1179", "absolute/relatieve nietigheid"),
        ],
    },
    {
        "titel": "Termijn voor vernietiging",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:52", "hoofdregel", "Drie jaar."),
            ("DE", "§ 121", "dwaling", "Unverzüglich."),
            ("DE", "§ 124", "bedrog en bedreiging", "Eén jaar."),
            ("FR", "art. 1144", "aanvang", "Vanaf ontdekking (erreur, dol) of einde (violence); termijn zelf in art. 2224 (vijf jaar)."),
        ],
    },
    {
        "titel": "Voorwaarde",
        "rechtsgebied": "Rechtshandelingen",
        "artikelen": [
            ("NL", "3:38", "rechtshandeling"),
            ("NL", "6:21–6:26", "verbintenis"),
            ("DE", "§§ 158–162", "hoofdregel"),
            ("FR", "art. 1304–1304-7", "hoofdregel"),
        ],
    },
    # --- Vertegenwoordiging -----------------------------------------------
    {
        "titel": "Volmacht en vertegenwoordiging",
        "rechtsgebied": "Vertegenwoordiging",
        "artikelen": [
            ("NL", "3:60", "volmacht"),
            ("NL", "3:66", "werking", "Handeling komt voor rekening van de achterman."),
            ("DE", "§ 164", "hoofdregel", "Offenkundigkeitsprinzip."),
            ("DE", "§ 167", "Vollmacht"),
            ("FR", "art. 1153–1154", "hoofdregel"),
        ],
    },
    {
        "titel": "Onbevoegde vertegenwoordiging en schijn van volmacht",
        "rechtsgebied": "Vertegenwoordiging",
        "artikelen": [
            ("NL", "3:61 lid 2", "schijn", "Toerekenbare schijn van volmacht."),
            ("NL", "3:69–3:70", "bekrachtiging en garantie"),
            ("DE", "§ 177", "schwebende Unwirksamkeit"),
            ("DE", "§ 179", "Haftung des Vertreters ohne Vertretungsmacht", "Duldungs- en Anscheinsvollmacht zijn jurisprudentieel."),
            ("FR", "art. 1156", "hoofdregel", "Inclusief mandat apparent (al. 1)."),
        ],
    },
    {
        "titel": "Selbstkontrahieren en tegenstrijdig belang",
        "rechtsgebied": "Vertegenwoordiging",
        "artikelen": [
            ("NL", "3:68", "hoofdregel"),
            ("DE", "§ 181", "hoofdregel"),
            ("FR", "art. 1161", "hoofdregel"),
        ],
    },
    # --- Verjaring ----------------------------------------------------------
    {
        "titel": "Algemene verjaringstermijn",
        "rechtsgebied": "Verjaring",
        "artikelen": [
            ("NL", "3:307", "nakoming overeenkomst", "Vijf jaar na opeisbaarheid."),
            ("NL", "3:308", "periodieke betalingen"),
            ("NL", "3:310", "schadevergoeding", "Vijf jaar subjectief, twintig jaar objectief."),
            ("DE", "§ 195", "hoofdregel", "Drie jaar."),
            ("DE", "§ 199", "aanvang", "Ultimo-Verjährung bij kennis; Höchstfristen in Abs. 2–4."),
            ("FR", "art. 2224", "hoofdregel", "Vijf jaar vanaf kennis."),
        ],
    },
    {
        "titel": "Lange (absolute) verjaringstermijn",
        "rechtsgebied": "Verjaring",
        "artikelen": [
            ("NL", "3:306", "hoofdregel", "Twintig jaar, tenzij de wet anders bepaalt."),
            ("DE", "§ 199 Abs. 2", "hoofdregel", "Dertig jaar bij leven, lichaam, gezondheid, vrijheid; anders tien (Abs. 3)."),
            ("FR", "art. 2232", "hoofdregel", "Délai butoir van twintig jaar."),
        ],
    },
    {
        "titel": "Stuiting, schorsing en verlenging van de verjaring",
        "rechtsgebied": "Verjaring",
        "artikelen": [
            ("NL", "3:316–3:321", "hoofdregel", "Stuiting (nieuwe termijn) en verlenging; geen 'schorsing' in Duitse zin."),
            ("DE", "§§ 203–213", "hoofdregel", "Hemmung, Ablaufhemmung, Neubeginn."),
            ("FR", "art. 2233–2246", "hoofdregel", "Suspension en interruption."),
        ],
    },
    {
        "titel": "Gevolg van verjaring",
        "rechtsgebied": "Verjaring",
        "artikelen": [
            ("NL", "6:3 lid 2", "natuurlijke verbintenis", "De verjaarde vordering blijft als natuurlijke verbintenis bestaan."),
            ("DE", "§ 214", "hoofdregel", "Leistungsverweigerungsrecht (Einrede)."),
            ("FR", "art. 2219", "hoofdregel", "Extinction d'un droit."),
        ],
    },
    # --- Goederenrecht --------------------------------------------------------
    {
        "titel": "Vereisten voor overdracht",
        "rechtsgebied": "Goederenrecht",
        "toelichting": "Causaal traditiestelsel (NL), abstract traditiestelsel (DE), consensueel stelsel (FR). Zie de vraag *Hoe gaat de eigendom van een roerende zaak over?*",
        "artikelen": [
            ("NL", "3:84", "hoofdregel", "Levering krachtens geldige titel door een beschikkingsbevoegde."),
            ("DE", "§ 929", "hoofdregel", "Einigung en Übergabe; abstract van de koop."),
            ("DE", "§ 433", "titel", "De koop verplicht alleen tot overdracht (Trennungsprinzip)."),
            ("FR", "art. 1196", "hoofdregel", "Overgang solo consensu bij de totstandkoming van het contract."),
            ("FR", "art. 1583", "koop"),
            ("FR", "art. 711", "algemeen"),
        ],
    },
    {
        "titel": "Levering van roerende zaken; traditio",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:90", "hoofdregel", "Bezitsverschaffing."),
            ("NL", "3:114–3:115", "bezitsoverdracht", "Feitelijk of via brevi manu, constitutum possessorium, longa manu."),
            ("DE", "§§ 929–931", "hoofdregel", "Übergabe en de surrogaten (S. 2, § 930, § 931)."),
            ("FR", "art. 1604", "faux ami", "Délivrance is een verplichting van de verkoper, géén overdrachtsvereiste."),
        ],
    },
    {
        "titel": "Overdracht van onroerende zaken",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:89", "hoofdregel", "Notariële akte en inschrijving in de openbare registers."),
            ("DE", "§ 873", "hoofdregel", "Einigung en Eintragung."),
            ("DE", "§ 925", "Auflassung"),
            ("FR", "art. 1196", "hoofdregel", "Ook voor onroerende zaken solo consensu; publicité foncière alleen voor tegenwerpelijkheid."),
            ("FR", "art. 710-1", "akte"),
        ],
    },
    {
        "titel": "Bescherming van de verkrijger te goeder trouw (roerende zaken)",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:86", "hoofdregel", "Alleen bij verkrijging anders dan om niet."),
            ("DE", "§§ 932–936", "hoofdregel", "Ook bij schenking (correctie via § 816 Abs. 1 S. 2)."),
            ("FR", "art. 2276", "hoofdregel", "En fait de meubles, la possession vaut titre."),
            ("FR", "art. 1198", "dubbele verkoop", "Eerste in bezit te goeder trouw gaat voor."),
        ],
    },
    {
        "titel": "Gestolen en verloren zaken",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:86 lid 3", "hoofdregel", "Revindicatie gedurende drie jaar, behalve bij winkelkoop door consument."),
            ("DE", "§ 935", "hoofdregel", "Abhanden gekommene Sachen: geen goedtrouwse verkrijging."),
            ("FR", "art. 2276 al. 2", "hoofdregel", "Drie jaar."),
            ("FR", "art. 2277", "markt en winkel", "Terugbetaling van de prijs."),
        ],
    },
    {
        "titel": "Goede trouw en het vermoeden daarvan",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:11", "definitie", "Kennen en behoren te kennen; onderzoeksplicht."),
            ("NL", "3:118 lid 3", "vermoeden"),
            ("DE", "§ 932 Abs. 2", "definitie", "Alleen grove nalatigheid schaadt."),
            ("FR", "art. 2274", "vermoeden"),
        ],
    },
    {
        "titel": "Overdracht tot zekerheid en fiducie",
        "rechtsgebied": "Zekerheidsrechten",
        "artikelen": [
            ("NL", "3:84 lid 3", "verbod", "Fiduciaverbod: geen geldige titel."),
            ("DE", "§ 930", "grondslag", "Sicherungsübereignung via Besitzkonstitut (jurisprudentieel erkend)."),
            ("FR", "art. 2011", "fiducie"),
            ("FR", "art. 2372-1", "fiducie-sûreté"),
        ],
    },
    {
        "titel": "Eigendomsvoorbehoud",
        "rechtsgebied": "Zekerheidsrechten",
        "artikelen": [
            ("NL", "3:92", "hoofdregel"),
            ("DE", "§ 449", "hoofdregel", "In combinatie met § 158 (aufschiebend bedingte Übereignung)."),
            ("FR", "art. 2367", "hoofdregel", "Propriété retenue à titre de garantie."),
        ],
    },
    {
        "titel": "Bezit en houderschap",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:107", "hoofdregel", "Bezit = houden voor zichzelf."),
            ("DE", "§ 854", "unmittelbarer Besitz", "Feitelijke macht, ongeacht animus: ruimer dan NL bezit."),
            ("DE", "§ 868", "mittelbarer Besitz"),
            ("DE", "§ 872", "Eigenbesitz", "Komt het dichtst bij NL bezit."),
            ("FR", "art. 2255", "hoofdregel", "Corpus en animus."),
            ("FR", "art. 2256", "vermoeden"),
        ],
    },
    {
        "titel": "Bezitter vermoed rechthebbende",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:119", "hoofdregel"),
            ("DE", "§ 1006", "hoofdregel"),
            ("FR", "art. 2276", "hoofdregel"),
        ],
    },
    {
        "titel": "Verkrijgende verjaring van roerende zaken",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:99", "goede trouw", "Drie jaar."),
            ("NL", "3:105", "kwade trouw", "Na verjaring van de rechtsvordering tot beëindiging van het bezit."),
            ("DE", "§ 937", "hoofdregel", "Tien jaar Eigenbesitz te goeder trouw."),
            ("FR", "art. 2276", "goede trouw", "Onmiddellijk."),
            ("FR", "art. 2258", "algemeen"),
        ],
    },
    {
        "titel": "Verkrijgende verjaring van onroerende zaken",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:99", "goede trouw", "Tien jaar."),
            ("NL", "3:105", "kwade trouw"),
            ("DE", "§ 900", "Buchersitzung", "Alleen voor wie ten onrechte is ingeschreven (dertig jaar)."),
            ("DE", "§ 927", "Aufgebot"),
            ("FR", "art. 2272", "hoofdregel", "Dertig jaar; tien jaar met juste titre en goede trouw."),
        ],
    },
    {
        "titel": "Eigendom: inhoud",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "5:1", "hoofdregel"),
            ("DE", "§ 903", "hoofdregel"),
            ("FR", "art. 544", "hoofdregel"),
        ],
    },
    {
        "titel": "Revindicatie",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "5:2", "hoofdregel"),
            ("DE", "§ 985", "hoofdregel"),
            ("DE", "§ 986", "verweer", "Recht zum Besitz."),
            ("FR", "art. 544", "grondslag", "Action en revendication is niet afzonderlijk gecodificeerd."),
        ],
    },
    {
        "titel": "Natrekking, vermenging en zaaksvorming (roerend)",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "5:14–5:16", "hoofdregel"),
            ("DE", "§§ 946–950", "hoofdregel", "Verbindung, Vermischung, Verarbeitung."),
            ("FR", "art. 565–577", "hoofdregel", "Accession relativement aux choses mobilières."),
        ],
    },
    {
        "titel": "Natrekking door de grond",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "5:20", "hoofdregel"),
            ("DE", "§§ 93–94", "hoofdregel", "Wesentliche Bestandteile."),
            ("DE", "§ 946", "verbinding met grond"),
            ("FR", "art. 552–553", "hoofdregel"),
        ],
    },
    {
        "titel": "Vruchten",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:9", "definitie"),
            ("NL", "5:17", "eigendom van vruchten"),
            ("DE", "§ 99", "definitie"),
            ("DE", "§§ 953–957", "Erwerb"),
            ("FR", "art. 547–550", "hoofdregel"),
        ],
    },
    {
        "titel": "Gevonden zaken",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "5:5–5:12", "hoofdregel"),
            ("DE", "§§ 965–984", "hoofdregel"),
            ("FR", "art. 717", "verwijzing", "Verwijst naar bijzondere wetten; verder jurisprudentieel."),
        ],
    },
    {
        "titel": "Gemeenschap en mede-eigendom",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:166–3:200", "hoofdregel"),
            ("DE", "§§ 741–758", "Gemeinschaft", "Staat in het Schuldrecht."),
            ("DE", "§§ 1008–1011", "Miteigentum"),
            ("FR", "art. 815–815-18", "indivision"),
            ("FR", "art. 1873-1", "conventionele indivision"),
        ],
    },
    {
        "titel": "Vruchtgebruik",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "3:201", "hoofdregel"),
            ("DE", "§ 1030", "hoofdregel"),
            ("FR", "art. 578", "hoofdregel"),
        ],
    },
    {
        "titel": "Erfdienstbaarheden",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "5:70", "hoofdregel"),
            ("DE", "§ 1018", "hoofdregel"),
            ("FR", "art. 637", "hoofdregel"),
            ("FR", "art. 686", "inhoud"),
        ],
    },
    {
        "titel": "Erfpacht en opstal",
        "rechtsgebied": "Goederenrecht",
        "artikelen": [
            ("NL", "5:85", "erfpacht"),
            ("NL", "5:101", "opstal"),
            ("DE", "§ 1 ErbbauRG", "Erbbaurecht", "Buiten het BGB; combineert functies van erfpacht en opstal."),
            ("FR", "art. L451-1 C. rur.", "bail emphytéotique", "Buiten de Code civil."),
        ],
    },
    {
        "titel": "Pandrecht op roerende zaken",
        "rechtsgebied": "Zekerheidsrechten",
        "artikelen": [
            ("NL", "3:236", "vuistpand"),
            ("NL", "3:237", "stil pand"),
            ("DE", "§§ 1204–1205", "hoofdregel", "Alleen vuistpand; bezitloze zekerheid via Sicherungsübereignung."),
            ("FR", "art. 2333", "gage", "Sinds 2006 ook zonder dépossession, mits ingeschreven (art. 2337)."),
        ],
    },
    {
        "titel": "Hypotheek",
        "rechtsgebied": "Zekerheidsrechten",
        "artikelen": [
            ("NL", "3:260", "hoofdregel"),
            ("DE", "§ 1113", "Hypothek", "Akzessorisch."),
            ("DE", "§ 1191", "Grundschuld", "Niet-accessoir; in de praktijk de norm."),
        ],
    },
    {
        "titel": "Retentierecht",
        "rechtsgebied": "Zekerheidsrechten",
        "artikelen": [
            ("NL", "3:290", "hoofdregel"),
            ("DE", "§ 273", "Zurückbehaltungsrecht", "Persoonlijk, geen zakelijke werking."),
            ("DE", "§ 1000", "bezitter"),
            ("FR", "art. 2286", "hoofdregel"),
        ],
    },
    {
        "titel": "Borgtocht",
        "rechtsgebied": "Zekerheidsrechten",
        "artikelen": [
            ("NL", "7:850", "hoofdregel"),
            ("DE", "§ 765", "hoofdregel"),
            ("FR", "art. 2288", "hoofdregel"),
        ],
    },
    # --- Verbintenissenrecht algemeen ---------------------------------------
    {
        "titel": "Bronnen van verbintenissen",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:1", "hoofdregel", "Verbintenissen ontstaan alleen als dit uit de wet voortvloeit."),
            ("DE", "§ 241", "Schuldverhältnis"),
            ("DE", "§ 311 Abs. 1", "rechtsgeschäftliche Schuldverhältnisse"),
            ("FR", "art. 1100–1100-2", "hoofdregel", "Actes juridiques, faits juridiques, autorité de la loi."),
        ],
    },
    {
        "titel": "Natuurlijke verbintenis",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:3", "hoofdregel"),
            ("DE", "§ 762", "voorbeeld", "Spiel und Wette; geen algemene figuur."),
            ("DE", "§ 814", "terugvordering uitgesloten"),
            ("FR", "art. 1100 al. 2", "hoofdregel", "Devoir de conscience."),
        ],
    },
    {
        "titel": "Hoofdelijke verbondenheid",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:6–6:14", "hoofdregel", "Bij meerdere schuldenaren is hoofdelijkheid niet het uitgangspunt (6:6), maar komt vaak in de wet voor."),
            ("DE", "§ 421", "Gesamtschuld"),
            ("DE", "§ 426", "regres"),
            ("FR", "art. 1310", "uitgangspunt", "Solidariteit wordt niet vermoed."),
            ("FR", "art. 1313", "solidarité passive"),
            ("FR", "art. 1317", "regres"),
        ],
    },
    {
        "titel": "Tijd en plaats van nakoming",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:38", "tijd"),
            ("NL", "6:41", "plaats"),
            ("DE", "§ 271", "tijd"),
            ("DE", "§ 269", "plaats"),
            ("FR", "art. 1305", "terme"),
            ("FR", "art. 1342-6", "plaats"),
        ],
    },
    {
        "titel": "Opschorting; exceptio non adimpleti contractus",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:52", "algemeen"),
            ("NL", "6:262", "wederkerige overeenkomst"),
            ("DE", "§ 273", "Zurückbehaltungsrecht"),
            ("DE", "§ 320", "Einrede des nicht erfüllten Vertrags"),
            ("FR", "art. 1219–1220", "hoofdregel", "Ook anticiperend (1220)."),
        ],
    },
    {
        "titel": "Schuldeisersverzuim",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:58", "hoofdregel"),
            ("DE", "§ 293", "Annahmeverzug"),
            ("FR", "art. 1345", "hoofdregel", "Mise en demeure du créancier."),
        ],
    },
    {
        "titel": "Recht op nakoming",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "3:296", "hoofdregel"),
            ("DE", "§ 241 Abs. 1", "hoofdregel", "Erfüllungsanspruch; grens in § 275."),
            ("FR", "art. 1221", "hoofdregel", "Exécution forcée en nature, tenzij kennelijke wanverhouding."),
            ("FR", "art. 1222", "door een derde"),
        ],
    },
    {
        "titel": "Wanprestatie: aansprakelijkheid voor tekortkoming",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:74", "hoofdregel"),
            ("DE", "§ 280 Abs. 1", "hoofdregel", "Pflichtverletzung; Vertretenmüssen vermoed."),
            ("FR", "art. 1231-1", "hoofdregel"),
            ("FR", "art. 1217", "overzicht remedies"),
        ],
    },
    {
        "titel": "Toerekening en overmacht",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:75", "hoofdregel"),
            ("DE", "§ 276", "Verschulden", "Vorsatz und Fahrlässigkeit, tenzij strengere of mildere aansprakelijkheid."),
            ("FR", "art. 1218", "force majeure"),
        ],
    },
    {
        "titel": "Aansprakelijkheid voor hulppersonen bij nakoming",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:76", "hoofdregel"),
            ("DE", "§ 278", "Erfüllungsgehilfe"),
            ("FR", "—", "geen regeling", "Responsabilité contractuelle du fait d'autrui is jurisprudentieel."),
        ],
    },
    {
        "titel": "Verzuim en ingebrekestelling",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:81–6:83", "hoofdregel"),
            ("DE", "§ 286", "hoofdregel", "Mahnung, met uitzonderingen (Abs. 2–3)."),
            ("FR", "art. 1344", "mise en demeure"),
            ("FR", "art. 1231", "vereiste voor schadevergoeding"),
        ],
    },
    {
        "titel": "Vervangende schadevergoeding",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:87", "hoofdregel"),
            ("DE", "§ 281", "hoofdregel", "Na Nachfrist."),
            ("DE", "§ 283", "bij onmogelijkheid"),
            ("FR", "art. 1231-1", "hoofdregel"),
        ],
    },
    {
        "titel": "Onmogelijkheid van nakoming",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:74 lid 2", "hoofdregel", "Geen ingebrekestelling nodig als nakoming blijvend onmogelijk is."),
            ("DE", "§ 275", "hoofdregel", "Ausschluss der Leistungspflicht."),
            ("DE", "§ 311a", "aanvankelijke onmogelijkheid"),
            ("DE", "§ 326", "tegenprestatie"),
            ("FR", "art. 1218", "force majeure"),
            ("FR", "art. 1351–1351-1", "impossibilité d'exécuter"),
        ],
    },
    {
        "titel": "Ontbinding wegens tekortkoming",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:265", "hoofdregel"),
            ("NL", "6:267", "wijze", "Buitengerechtelijke verklaring of rechterlijke uitspraak."),
            ("NL", "6:271", "gevolg", "Ongedaanmakingsverbintenissen."),
            ("DE", "§ 323", "Rücktritt"),
            ("DE", "§ 346", "Rückgewährschuldverhältnis"),
            ("FR", "art. 1224–1230", "hoofdregel", "Clause résolutoire, notification of rechter."),
        ],
    },
    {
        "titel": "Prijsvermindering",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:270", "partiële ontbinding"),
            ("NL", "7:22", "consumentenkoop"),
            ("DE", "§ 441", "koop"),
            ("FR", "art. 1223", "hoofdregel", "Sinds 2016 algemeen."),
        ],
    },
    {
        "titel": "Onvoorziene omstandigheden",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:258", "hoofdregel"),
            ("DE", "§ 313", "Störung der Geschäftsgrundlage"),
            ("FR", "art. 1195", "imprévision", "Sinds 2016; daarvoor afgewezen (Canal de Craponne, 1876)."),
        ],
    },
    {
        "titel": "Boetebeding",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:91–6:94", "hoofdregel", "Matiging lid 1 art. 6:94."),
            ("DE", "§§ 339–345", "hoofdregel", "Herabsetzung (§ 343); niet tussen kooplieden (§ 348 HGB)."),
            ("FR", "art. 1231-5", "hoofdregel"),
        ],
    },
    {
        "titel": "Exoneratie en beperking van aansprakelijkheid",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:248 lid 2", "toets", "Beroep onaanvaardbaar naar maatstaven van redelijkheid en billijkheid."),
            ("NL", "6:237", "algemene voorwaarden", "Grijze lijst, onder f."),
            ("DE", "§ 276 Abs. 3", "opzet"),
            ("DE", "§ 309", "AGB", "Nr. 7: leven, lichaam, gezondheid en grove schuld."),
            ("FR", "art. 1170", "hoofdregel", "Clause die de essentiële verbintenis uitholt (Chronopost)."),
            ("FR", "art. 1231-3", "voorzienbaarheid"),
        ],
    },
    {
        "titel": "Omvang van de schadevergoeding en causaal verband",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:95–6:98", "hoofdregel", "Toerekening naar redelijkheid (6:98)."),
            ("DE", "§ 249", "Naturalrestitution", "Differenzhypothese; Adäquanz jurisprudentieel."),
            ("DE", "§ 252", "gederfde winst"),
            ("FR", "art. 1231-2", "perte subie, gain manqué"),
            ("FR", "art. 1231-3–1231-4", "voorzienbaarheid en suite immédiate et directe"),
        ],
    },
    {
        "titel": "Eigen schuld van de benadeelde",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:101", "hoofdregel"),
            ("DE", "§ 254", "Mitverschulden"),
            ("FR", "—", "geen regeling", "Faute de la victime: jurisprudentieel (en art. 1254 in het projet de réforme)."),
        ],
    },
    {
        "titel": "Immateriële schade",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:106", "hoofdregel", "Limitatief."),
            ("DE", "§ 253", "hoofdregel", "Abs. 2: Schmerzensgeld."),
            ("FR", "—", "geen regeling", "Préjudice moral wordt ruim vergoed op grond van art. 1240/1231-1 (jurisprudentie)."),
        ],
    },
    {
        "titel": "Wettelijke rente",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:119", "hoofdregel"),
            ("NL", "6:119a", "handelstransacties"),
            ("DE", "§ 288", "Verzugszinsen"),
            ("FR", "art. 1231-6", "intérêts moratoires"),
            ("FR", "art. 1344-1", "hoofdregel"),
        ],
    },
    {
        "titel": "Verrekening",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:127", "hoofdregel", "Door verklaring."),
            ("DE", "§§ 387–389", "hoofdregel", "Door verklaring (§ 388); terugwerkend (§ 389)."),
            ("FR", "art. 1347–1347-1", "hoofdregel", "Sinds 2016 ook door inroepen ('sous réserve d'être invoquée')."),
        ],
    },
    {
        "titel": "Cessie",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "3:94", "hoofdregel", "Akte en mededeling (of stil: art. 3:94 lid 3)."),
            ("DE", "§ 398", "hoofdregel", "Vormvrije overeenkomst; geen mededeling vereist."),
            ("FR", "art. 1321", "hoofdregel", "Schriftelijk (1322)."),
            ("FR", "art. 1323–1324", "tegenwerpelijkheid"),
        ],
    },
    {
        "titel": "Schuldoverneming",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:155", "hoofdregel"),
            ("DE", "§§ 414–415", "hoofdregel"),
            ("FR", "art. 1327–1328-1", "hoofdregel", "Cession de dette, sinds 2016."),
        ],
    },
    {
        "titel": "Contractsoverneming",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:159", "hoofdregel"),
            ("DE", "—", "geen regeling", "Vertragsübernahme is erkend als dreipartijenovereenkomst (jurisprudentie)."),
            ("FR", "art. 1216", "hoofdregel"),
        ],
    },
    {
        "titel": "Subrogatie",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "6:150", "hoofdregel"),
            ("DE", "§ 268", "ablösungsberechtigter Dritter"),
            ("DE", "§ 426 Abs. 2", "hoofdelijke schuldenaar"),
            ("DE", "§ 774", "borg"),
            ("FR", "art. 1346–1346-5", "hoofdregel"),
        ],
    },
    {
        "titel": "Actio Pauliana",
        "rechtsgebied": "Verbintenissenrecht",
        "artikelen": [
            ("NL", "3:45", "hoofdregel"),
            ("DE", "§ 3 AnfG", "hoofdregel", "Buiten het BGB (Anfechtungsgesetz)."),
            ("FR", "art. 1341-2", "action paulienne"),
            ("FR", "art. 1341-1", "action oblique", "Geen NL/DE-tegenhanger."),
        ],
    },
    {
        "titel": "Onverschuldigde betaling",
        "rechtsgebied": "Andere bronnen van verbintenissen",
        "artikelen": [
            ("NL", "6:203", "hoofdregel"),
            ("DE", "§ 812 Abs. 1", "Leistungskondiktion", "S. 1 Alt. 1."),
            ("DE", "§§ 813–814", "uitzonderingen"),
            ("FR", "art. 1302–1302-3", "hoofdregel"),
        ],
    },
    {
        "titel": "Ongerechtvaardigde verrijking",
        "rechtsgebied": "Andere bronnen van verbintenissen",
        "artikelen": [
            ("NL", "6:212", "hoofdregel"),
            ("DE", "§ 812 Abs. 1", "Nichtleistungskondiktion", "S. 1 Alt. 2 (Eingriffskondiktion)."),
            ("DE", "§ 818", "omvang"),
            ("FR", "art. 1303–1303-4", "hoofdregel", "Subsidiair (1303-3)."),
        ],
    },
    {
        "titel": "Zaakwaarneming",
        "rechtsgebied": "Andere bronnen van verbintenissen",
        "artikelen": [
            ("NL", "6:198", "hoofdregel"),
            ("NL", "6:200", "kostenvergoeding"),
            ("DE", "§ 677", "hoofdregel"),
            ("DE", "§ 683", "Aufwendungsersatz"),
            ("FR", "art. 1301–1301-5", "hoofdregel"),
        ],
    },
    {
        "titel": "Ongedaanmaking en restitutie",
        "rechtsgebied": "Andere bronnen van verbintenissen",
        "artikelen": [
            ("NL", "6:271", "na ontbinding"),
            ("NL", "6:203", "na nietigheid"),
            ("DE", "§ 346", "na Rücktritt"),
            ("DE", "§ 818", "na nietigheid"),
            ("FR", "art. 1352–1352-9", "hoofdregel", "Eén regime voor nietigheid, ontbinding en caducité."),
        ],
    },
    # --- Overeenkomsten ---------------------------------------------------------
    {
        "titel": "Begrip overeenkomst",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "6:213", "hoofdregel"),
            ("DE", "—", "geen definitie", "Vertrag als zweiseitiges Rechtsgeschäft; §§ 145 ff."),
            ("FR", "art. 1101", "hoofdregel"),
        ],
    },
    {
        "titel": "Aanbod en aanvaarding",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "6:217", "hoofdregel"),
            ("DE", "§ 145", "Antrag"),
            ("DE", "§ 147", "Annahmefrist"),
            ("FR", "art. 1113–1114", "hoofdregel"),
            ("FR", "art. 1118", "acceptation"),
        ],
    },
    {
        "titel": "Herroepelijkheid van het aanbod",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "6:219", "herroepelijk", "Tenzij termijn of onherroepelijkheid."),
            ("DE", "§ 145", "bindend", "Antrag is bindend, tenzij uitgesloten: omgekeerd aan NL."),
            ("FR", "art. 1115–1116", "deels", "Vrij intrekbaar tot ontvangst; daarna binnen de termijn alleen met schadevergoeding."),
        ],
    },
    {
        "titel": "Afwijkende aanvaarding; battle of forms",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "6:225", "hoofdregel", "Lid 2 ondergeschikte punten; lid 3 first shot."),
            ("DE", "§ 150 Abs. 2", "hoofdregel", "Nieuwe Antrag; bij AGB knock-out (jurisprudentie)."),
            ("FR", "art. 1118 al. 3", "hoofdregel"),
            ("FR", "art. 1119", "algemene voorwaarden", "Al. 2: tegenstrijdige bedingen vervallen (knock-out)."),
        ],
    },
    {
        "titel": "Ontvangsttheorie; moment van totstandkoming",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "3:37 lid 3", "hoofdregel"),
            ("DE", "§ 130", "Zugang"),
            ("FR", "art. 1121", "hoofdregel", "Bij ontvangst van de aanvaarding."),
        ],
    },
    {
        "titel": "Precontractuele aansprakelijkheid",
        "rechtsgebied": "Overeenkomsten",
        "toelichting": "Zie de vraag *Wanneer leidt het afbreken van onderhandelingen tot aansprakelijkheid?*",
        "artikelen": [
            ("NL", "6:2", "grondslag", "Plas/Valburg, CBB/JPO: jurisprudentieel."),
            ("NL", "6:162", "grondslag"),
            ("DE", "§ 311 Abs. 2", "hoofdregel", "Culpa in contrahendo, sinds 2002 gecodificeerd."),
            ("DE", "§ 241 Abs. 2", "Rücksichtnahmepflichten"),
            ("DE", "§ 280 Abs. 1", "Anspruchsgrundlage"),
            ("FR", "art. 1112", "hoofdregel", "Geen vergoeding van verlies van verwachte voordelen."),
        ],
    },
    {
        "titel": "Precontractuele mededelingsplicht",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "6:228 lid 1", "via dwaling", "Onder b: schending van mededelingsplicht."),
            ("DE", "§ 241 Abs. 2", "via c.i.c.", "Aufklärungspflichten; geen algemene informatieplicht."),
            ("FR", "art. 1112-1", "hoofdregel", "Algemene informatieplicht, van openbare orde."),
        ],
    },
    {
        "titel": "Algemene voorwaarden",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "6:231–6:247", "hoofdregel", "Open norm 6:233, zwarte en grijze lijst 6:236–6:237."),
            ("DE", "§§ 305–310", "hoofdregel"),
            ("FR", "art. 1171", "hoofdregel", "Déséquilibre significatif in contrats d'adhésion."),
            ("FR", "art. 1110", "contrat d'adhésion"),
        ],
    },
    {
        "titel": "Uitleg van overeenkomsten",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "3:33", "grondslag", "Haviltex-maatstaf is jurisprudentieel."),
            ("DE", "§ 133", "hoofdregel"),
            ("DE", "§ 157", "overeenkomsten"),
            ("FR", "art. 1188–1192", "hoofdregel"),
        ],
    },
    {
        "titel": "Aanvullende werking",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "6:248 lid 1", "hoofdregel"),
            ("DE", "§ 157", "ergänzende Vertragsauslegung"),
            ("DE", "§ 242", "aanvullend"),
            ("FR", "art. 1194", "hoofdregel", "Équité, usage, loi."),
        ],
    },
    {
        "titel": "Derdenbeding",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "6:253", "hoofdregel"),
            ("DE", "§ 328", "hoofdregel"),
            ("FR", "art. 1205", "hoofdregel"),
        ],
    },
    {
        "titel": "Wederkerige overeenkomst",
        "rechtsgebied": "Overeenkomsten",
        "artikelen": [
            ("NL", "6:261", "hoofdregel"),
            ("DE", "§§ 320–326", "hoofdregel"),
            ("FR", "art. 1106", "definitie"),
        ],
    },
    # --- Bijzondere overeenkomsten -------------------------------------------
    {
        "titel": "Koop",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:1", "hoofdregel"),
            ("DE", "§ 433", "hoofdregel"),
            ("FR", "art. 1582", "hoofdregel"),
        ],
    },
    {
        "titel": "Conformiteit en gebreken bij koop",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:17", "hoofdregel"),
            ("DE", "§ 434", "Sachmangel"),
            ("DE", "§ 437", "Rechte des Käufers"),
            ("FR", "art. 1641", "vices cachés", "Naast de délivrance conforme (1604) en de consumentenregeling."),
            ("FR", "art. L217-3 C. consom.", "consumentenkoop"),
        ],
    },
    {
        "titel": "Klachtplicht en termijnen bij koop",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:23", "hoofdregel"),
            ("DE", "§ 438", "Verjährung"),
            ("DE", "§ 377 HGB", "Rügeobliegenheit", "Alleen bij Handelskauf."),
            ("FR", "art. 1648", "hoofdregel", "Twee jaar na ontdekking."),
        ],
    },
    {
        "titel": "Risico-overgang bij koop",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:10", "hoofdregel", "Bij aflevering."),
            ("NL", "7:11", "consumentenkoop"),
            ("DE", "§ 446", "hoofdregel", "Bij Übergabe."),
            ("DE", "§ 447", "Versendungskauf"),
            ("FR", "art. 1196 al. 3", "hoofdregel", "Res perit domino: met de eigendom."),
        ],
    },
    {
        "titel": "Schenking",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:175", "hoofdregel"),
            ("DE", "§ 516", "hoofdregel"),
            ("DE", "§ 518", "vorm"),
            ("FR", "art. 894", "hoofdregel", "Staat in het erfrecht (libéralités)."),
            ("FR", "art. 931", "vorm", "Notariële akte."),
        ],
    },
    {
        "titel": "Huur",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:201", "hoofdregel"),
            ("DE", "§ 535", "hoofdregel"),
            ("FR", "art. 1709", "hoofdregel"),
            ("FR", "art. 1719", "verplichtingen verhuurder"),
        ],
    },
    {
        "titel": "Koop breekt geen huur",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:226", "hoofdregel"),
            ("DE", "§ 566", "hoofdregel", "Alleen woonruimte en grond (via § 578)."),
            ("FR", "art. 1743", "hoofdregel"),
        ],
    },
    {
        "titel": "Opdracht en lastgeving",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:400", "opdracht"),
            ("NL", "7:414", "lastgeving"),
            ("DE", "§ 662", "Auftrag", "Onbezoldigd."),
            ("DE", "§ 675", "Geschäftsbesorgung", "Bezoldigd."),
            ("FR", "art. 1984", "mandat", "Omvat vertegenwoordiging: faux ami van NL 'lastgeving'."),
        ],
    },
    {
        "titel": "Aanneming van werk",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:750", "hoofdregel"),
            ("DE", "§ 631", "hoofdregel"),
            ("FR", "art. 1710", "louage d'ouvrage"),
            ("FR", "art. 1787", "hoofdregel"),
        ],
    },
    {
        "titel": "Arbeidsovereenkomst",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:610", "hoofdregel"),
            ("DE", "§ 611a", "hoofdregel"),
            ("FR", "art. L1221-1 C. trav.", "hoofdregel", "Code du travail; de Code civil kent alleen louage de services (1780)."),
        ],
    },
    {
        "titel": "Bewaarneming",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:600", "hoofdregel"),
            ("DE", "§ 688", "hoofdregel"),
            ("FR", "art. 1915", "hoofdregel"),
        ],
    },
    {
        "titel": "Vaststellingsovereenkomst",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:900", "hoofdregel"),
            ("DE", "§ 779", "Vergleich"),
            ("FR", "art. 2044", "transaction"),
        ],
    },
    {
        "titel": "Bruikleen",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7A:1777", "hoofdregel"),
            ("DE", "§ 598", "Leihe"),
            ("FR", "art. 1875", "prêt à usage"),
        ],
    },
    {
        "titel": "Verbruikleen en geldlening",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7:129", "geldlening", "Titel 7.2c; de oude titel verbruikleen in Boek 7A is vervallen."),
            ("DE", "§ 488", "Darlehensvertrag"),
            ("DE", "§ 607", "Sachdarlehen"),
            ("FR", "art. 1892", "prêt de consommation"),
        ],
    },
    {
        "titel": "Maatschap / Gesellschaft bürgerlichen Rechts / société",
        "rechtsgebied": "Bijzondere overeenkomsten",
        "artikelen": [
            ("NL", "7A:1655", "hoofdregel"),
            ("DE", "§ 705", "hoofdregel", "Sinds MoPeG (2024) rechtsfähige GbR als uitgangspunt."),
            ("FR", "art. 1832", "hoofdregel", "Société civile; rechtspersoon na inschrijving (1842)."),
        ],
    },
    # --- Onrechtmatige daad ---------------------------------------------------
    {
        "titel": "Onrechtmatige daad: algemene grondslag",
        "rechtsgebied": "Onrechtmatige daad",
        "toelichting": "Drie modellen: één open norm met drie categorieën (NL), drie Tatbestände met beschermde rechtsgoederen (DE), één algemene foutnorm (FR).",
        "artikelen": [
            ("NL", "6:162", "hoofdregel"),
            ("DE", "§ 823 Abs. 1", "Rechtsgutsverletzung"),
            ("DE", "§ 823 Abs. 2", "Schutzgesetzverletzung"),
            ("DE", "§ 826", "sittenwidrige Schädigung"),
            ("FR", "art. 1240–1241", "hoofdregel", "Voorheen art. 1382–1383."),
        ],
    },
    {
        "titel": "Relativiteit",
        "rechtsgebied": "Onrechtmatige daad",
        "artikelen": [
            ("NL", "6:163", "hoofdregel"),
            ("DE", "§ 823 Abs. 2", "Schutzbereich", "Schutzgesetz moet de benadeelde willen beschermen."),
            ("FR", "—", "geen regeling", "Het Franse recht kent geen relativiteitsvereiste."),
        ],
    },
    {
        "titel": "Aansprakelijkheid voor kinderen",
        "rechtsgebied": "Onrechtmatige daad",
        "artikelen": [
            ("NL", "6:169", "hoofdregel", "Risicoaansprakelijkheid tot 14 jaar, schuldaansprakelijkheid 14–16."),
            ("DE", "§ 832", "hoofdregel", "Vermoede schuld (Aufsichtspflicht)."),
            ("FR", "art. 1242 al. 4", "hoofdregel", "Risicoaansprakelijkheid ouders (Bertrand, 1997)."),
        ],
    },
    {
        "titel": "Aansprakelijkheid voor ondergeschikten",
        "rechtsgebied": "Onrechtmatige daad",
        "artikelen": [
            ("NL", "6:170", "hoofdregel", "Risicoaansprakelijkheid."),
            ("DE", "§ 831", "hoofdregel", "Vermoede schuld met Entlastungsbeweis; daarom vaak via contract (§ 278)."),
            ("FR", "art. 1242 al. 5", "hoofdregel"),
        ],
    },
    {
        "titel": "Aansprakelijkheid voor zaken",
        "rechtsgebied": "Onrechtmatige daad",
        "artikelen": [
            ("NL", "6:173", "roerende zaken", "Bijzonder gevaar."),
            ("DE", "—", "geen algemene regeling", "Gefährdungshaftung alleen in bijzondere wetten (StVG, ProdHaftG, …)."),
            ("FR", "art. 1242 al. 1", "hoofdregel", "Algemene aansprakelijkheid du fait des choses (Jand'heur, 1930)."),
        ],
    },
    {
        "titel": "Aansprakelijkheid voor opstallen",
        "rechtsgebied": "Onrechtmatige daad",
        "artikelen": [
            ("NL", "6:174", "hoofdregel"),
            ("DE", "§§ 836–838", "hoofdregel", "Vermoede schuld."),
            ("FR", "art. 1244", "hoofdregel", "Ruine des bâtiments."),
        ],
    },
    {
        "titel": "Aansprakelijkheid voor dieren",
        "rechtsgebied": "Onrechtmatige daad",
        "artikelen": [
            ("NL", "6:179", "hoofdregel"),
            ("DE", "§ 833", "hoofdregel", "Luxustiere risico, Nutztiere vermoede schuld."),
            ("FR", "art. 1243", "hoofdregel"),
        ],
    },
    {
        "titel": "Productaansprakelijkheid",
        "rechtsgebied": "Onrechtmatige daad",
        "toelichting": "Implementatie van Richtlijn 85/374/EEG (vervangen door Richtlijn (EU) 2024/2853).",
        "artikelen": [
            ("NL", "6:185", "hoofdregel"),
            ("DE", "§ 1 ProdHaftG", "hoofdregel", "Buiten het BGB."),
            ("FR", "art. 1245", "hoofdregel"),
            ("FR", "art. 1245-3", "gebrek"),
        ],
    },
    {
        "titel": "Meerdere aansprakelijken",
        "rechtsgebied": "Onrechtmatige daad",
        "artikelen": [
            ("NL", "6:102", "hoofdelijkheid"),
            ("NL", "6:99", "alternatieve causaliteit"),
            ("DE", "§ 830", "Mittäter und Beteiligte"),
            ("DE", "§ 840", "Gesamtschuld"),
            ("FR", "—", "geen regeling", "Obligation in solidum is jurisprudentieel."),
        ],
    },
    # --- Personen- en familierecht -----------------------------------------
    {
        "titel": "Begin van de rechtspersoonlijkheid; nasciturus",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:2", "nasciturus"),
            ("DE", "§ 1", "hoofdregel"),
            ("DE", "§ 1923 Abs. 2", "nasciturus erfrecht"),
            ("FR", "art. 725", "nasciturus erfrecht", "Infans conceptus is verder jurisprudentieel."),
            ("FR", "art. 906", "nasciturus schenking"),
        ],
    },
    {
        "titel": "Meerderjarigheid",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:233", "hoofdregel"),
            ("DE", "§ 2", "hoofdregel"),
            ("FR", "art. 388", "minderjarigheid"),
            ("FR", "art. 414", "meerderjarigheid"),
        ],
    },
    {
        "titel": "Woonplaats",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:10", "hoofdregel"),
            ("DE", "§ 7", "hoofdregel"),
            ("FR", "art. 102", "hoofdregel"),
        ],
    },
    {
        "titel": "Huwelijk",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:30", "hoofdregel"),
            ("DE", "§ 1353", "Wirkungen der Ehe"),
            ("FR", "art. 143", "hoofdregel"),
        ],
    },
    {
        "titel": "Wettelijk huwelijksvermogensregime",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:94", "hoofdregel", "Beperkte gemeenschap van goederen (sinds 2018)."),
            ("DE", "§ 1363", "hoofdregel", "Zugewinngemeinschaft: scheiding met verrekening."),
            ("FR", "art. 1400", "hoofdregel", "Communauté réduite aux acquêts."),
        ],
    },
    {
        "titel": "Echtscheiding",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:151", "hoofdregel", "Duurzame ontwrichting."),
            ("DE", "§§ 1564–1565", "hoofdregel", "Scheitern der Ehe."),
            ("FR", "art. 229", "hoofdregel", "Vier echtscheidingsgronden."),
        ],
    },
    {
        "titel": "Partneralimentatie na scheiding",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:156", "hoofdregel"),
            ("NL", "1:157", "duur", "In beginsel de helft van de huwelijksduur, maximaal vijf jaar."),
            ("DE", "§ 1569", "hoofdregel"),
            ("FR", "art. 270", "deels", "Prestation compensatoire: in beginsel een kapitaal, geen periodieke alimentatie."),
        ],
    },
    {
        "titel": "Moederschap",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:198", "hoofdregel"),
            ("DE", "§ 1591", "hoofdregel"),
            ("FR", "art. 311-25", "hoofdregel"),
        ],
    },
    {
        "titel": "Vaderschap",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:199", "hoofdregel"),
            ("DE", "§ 1592", "hoofdregel"),
            ("FR", "art. 312", "hoofdregel"),
        ],
    },
    {
        "titel": "Adoptie",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:227", "hoofdregel"),
            ("DE", "§ 1741", "hoofdregel"),
            ("FR", "art. 343", "hoofdregel"),
        ],
    },
    {
        "titel": "Ouderlijk gezag",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:245", "hoofdregel"),
            ("NL", "1:247", "inhoud"),
            ("DE", "§ 1626", "hoofdregel"),
            ("FR", "art. 371-1", "hoofdregel"),
        ],
    },
    {
        "titel": "Bescherming van meerderjarigen",
        "rechtsgebied": "Personen- en familierecht",
        "artikelen": [
            ("NL", "1:378", "curatele"),
            ("NL", "1:431", "beschermingsbewind"),
            ("NL", "1:450", "mentorschap"),
            ("DE", "§ 1814", "rechtliche Betreuung", "Eén maatregel op maat."),
            ("FR", "art. 425", "hoofdregel"),
            ("FR", "art. 440", "curatelle en tutelle"),
        ],
    },
    # --- Erfrecht -----------------------------------------------------------------
    {
        "titel": "Erfopvolging bij versterf",
        "rechtsgebied": "Erfrecht",
        "artikelen": [
            ("NL", "4:10", "hoofdregel"),
            ("DE", "§ 1924", "hoofdregel", "Parentelsystem."),
            ("FR", "art. 734", "hoofdregel"),
        ],
    },
    {
        "titel": "Overgang van de nalatenschap van rechtswege",
        "rechtsgebied": "Erfrecht",
        "artikelen": [
            ("NL", "4:182", "hoofdregel", "Saisine."),
            ("DE", "§ 1922", "hoofdregel", "Gesamtrechtsnachfolge."),
            ("DE", "§ 1942", "Anfall"),
            ("FR", "art. 724", "hoofdregel", "Saisine."),
        ],
    },
    {
        "titel": "Aanvaarding en verwerping",
        "rechtsgebied": "Erfrecht",
        "artikelen": [
            ("NL", "4:190", "hoofdregel", "Zuiver, beneficiair of verwerpen."),
            ("DE", "§§ 1942–1944", "hoofdregel", "Ausschlagung binnen zes weken."),
            ("FR", "art. 768", "hoofdregel", "Option successorale."),
        ],
    },
    {
        "titel": "Testament",
        "rechtsgebied": "Erfrecht",
        "artikelen": [
            ("NL", "4:42", "hoofdregel"),
            ("DE", "§ 1937", "Erbeinsetzung"),
            ("DE", "§ 2064", "persoonlijk"),
            ("FR", "art. 895", "hoofdregel"),
        ],
    },
    {
        "titel": "Legitieme portie / Pflichtteil / réserve héréditaire",
        "rechtsgebied": "Erfrecht",
        "toelichting": "NL en DE: geldvordering; FR: de réserve is een deel van de nalatenschap zelf.",
        "artikelen": [
            ("NL", "4:63", "hoofdregel", "Geldvordering van afstammelingen."),
            ("DE", "§ 2303", "hoofdregel", "Geldvordering."),
            ("FR", "art. 912–913", "hoofdregel", "Réserve in natura (sinds 2006 in waarde: art. 924)."),
        ],
    },
    # --- Rechtspersonen ------------------------------------------------------------
    {
        "titel": "Vereniging",
        "rechtsgebied": "Rechtspersonen",
        "artikelen": [
            ("NL", "2:26", "hoofdregel"),
            ("DE", "§ 21", "nicht wirtschaftlicher Verein"),
            ("DE", "§ 55", "eingetragener Verein"),
            ("FR", "art. 1 Loi 1901", "hoofdregel", "Loi du 1er juillet 1901, buiten de Code civil."),
        ],
    },
    {
        "titel": "Stichting",
        "rechtsgebied": "Rechtspersonen",
        "artikelen": [
            ("NL", "2:285", "hoofdregel"),
            ("DE", "§ 80", "hoofdregel"),
            ("FR", "—", "geen regeling in de Code civil", "Fondation: loi n° 87-571 du 23 juillet 1987, art. 18."),
        ],
    },
]
