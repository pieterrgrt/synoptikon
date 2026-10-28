"""Begrippen uit de overige stelsels voor de begrippenkaart, met hun relaties.

Vult de begrippen van de twee uitgewerkte vragen (NL, DE, FR, EU) aan met BE,
IT, ES, CH, EN, US en AU, en voegt een paar ontbrekende ankers toe (FR:
transfert solo consensu; EU: DCFR). De wettelijke vindplaatsen van BE, IT, ES,
CH en EN zijn getoetst aan de geïmporteerde officiële teksten; definities,
rechtspraak en de typering van de relaties zijn eigen aantekening, daarom
"(niet geverifieerd)".

Relaties verwijzen naar sleutels uit deze lijst of uit `BESTAAND` (begrippen
die al in data_eigendom / data_precontractueel staan).
"""
from __future__ import annotations

NV = " (niet geverifieerd)"

EIGENDOM = "eigendomsoverdracht-roerende-zaken"
PRECONTRACTUEEL = "precontractuele-aansprakelijkheid"

BESTAAND = {
    "nl_levering": ("NL", "levering"),
    "nl_titel": ("NL", "titel"),
    "nl_causaal": ("NL", "causaal stelsel"),
    "nl_bezit": ("NL", "bezit"),
    "de_uebergabe": ("DE", "Übergabe"),
    "de_einigung": ("DE", "Einigung (dinglicher Vertrag)"),
    "de_kausalgeschaeft": ("DE", "Kausalgeschäft / Rechtsgrund"),
    "de_abstraktion": ("DE", "Abstraktionsprinzip"),
    "de_besitz": ("DE", "Besitz"),
    "fr_delivrance": ("FR", "délivrance"),
    "fr_titre": ("FR", "titre (possession vaut titre)"),
    "fr_possession": ("FR", "possession"),
    "nl_precontr": ("NL", "precontractuele aansprakelijkheid (afgebroken onderhandelingen)"),
    "nl_rb": ("NL", "redelijkheid en billijkheid"),
    "nl_positief": ("NL", "positief contractsbelang"),
    "de_cic": ("DE", "culpa in contrahendo"),
    "de_tug": ("DE", "Treu und Glauben"),
    "de_negativ": ("DE", "negatives Interesse (Vertrauensschaden)"),
    "fr_rupture": ("FR", "rupture fautive des pourparlers"),
    "fr_bonne_foi": ("FR", "bonne foi"),
    "fr_chance": ("FR", "perte de chance"),
    "eu_cic": ("EU", "culpa in contrahendo (Rome II)"),
}


def _b(sleutel, stelsel, taal, term, vindplaats, definitie, vraag):
    return {"sleutel": sleutel, "stelsel": stelsel, "taal": taal, "term": term, "vindplaats": vindplaats, "definitie": definitie + NV, "vraag": vraag}


BEGRIPPEN = [
    # --- eigendomsoverdracht van roerende zaken ---------------------------------------
    _b("fr_consensu", "FR", "fr", "transfert solo consensu", "art. 1196, 1583 C. civ.",
       "Le transfert de propriété d'un corps certain s'opère par le seul échange des consentements, lors de la conclusion du contrat (art. 1196 al. 1), "
       "sans tradition ; les parties peuvent le différer (réserve de propriété). La délivrance n'est que l'exécution d'une obligation du vendeur.", EIGENDOM),
    _b("be_wil", "BE", "nl", "overdracht door loutere wilsovereenstemming", "art. 3.14 § 2 BW",
       "De overdracht gebeurt door een rechtshandeling tot overdracht van een beschikkingsbevoegde, in uitvoering van een geldige titel (verbintenis tot geven). "
       "Die rechtshandeling komt tot stand door de loutere wilsovereenstemming en wordt vermoed samen te vallen met het aangaan van de verbintenis; "
       "bij soortzaken pas bij specificatie, bij toekomstige goederen pas bij hun ontstaan.", EIGENDOM),
    _b("be_levering", "BE", "nl", "levering (koop)", "art. 1604 oud BW",
       "Verbintenis van de verkoper om de verkochte zaak in de macht en het bezit van de koper te brengen: uitvoering van de koop, geen vereiste voor de "
       "eigendomsovergang, die al door de wilsovereenstemming plaatsvond.", EIGENDOM),
    _b("be_bezit", "BE", "nl", "bezit", "art. 3.18 BW",
       "De feitelijke uitoefening van een recht als ware men de titularis ervan, rechtstreeks of via een derde. Wie een goed houdt zonder zich als titularis "
       "te gedragen, is detentor; detentie wordt slechts bezit door titelomzetting (art. 3.20).", EIGENDOM),
    _b("be_328", "BE", "nl", "onmiddellijke verkrijging te goeder trouw", "art. 3.24, 3.28 BW",
       "Wie onder bezwarende titel en te goeder trouw een zakelijk recht op een roerend goed verkrijgt van een beschikkingsonbevoegde, wordt titularis zodra "
       "hij het ongestoord bezit (art. 3.28); de bezitter te goeder trouw wordt vermoed een titel te hebben (art. 3.24). Opvolger van art. 2279 oud BW.", EIGENDOM),
    _b("it_consenso", "IT", "it", "consenso traslativo", "art. 1376 c.c.",
       "Nei contratti che hanno per oggetto il trasferimento della proprietà di una cosa determinata, la proprietà si trasmette e si acquista per effetto del "
       "consenso delle parti legittimamente manifestato (principio consensualistico, sulla scia del Code civil).", EIGENDOM),
    _b("it_consegna", "IT", "it", "consegna", "art. 1476, 1477 c.c.",
       "Obbligazione principale del venditore (art. 1476 n. 1): consegnare la cosa nello stato in cui si trovava al momento della vendita. "
       "Non è requisito del trasferimento della proprietà di cosa determinata.", EIGENDOM),
    _b("it_possesso", "IT", "it", "possesso", "art. 1140, 1141 c.c.",
       "Il potere sulla cosa che si manifesta in un'attività corrispondente all'esercizio della proprietà o di altro diritto reale. "
       "Chi ha la cosa per un altro (conduttore, depositario) è detentore, non possessore.", EIGENDOM),
    _b("it_1153", "IT", "it", "possesso vale titolo", "art. 1153 c.c.",
       "Chi riceve beni mobili da un non proprietario ne acquista la proprietà mediante il possesso, purché sia in buona fede al momento della consegna "
       "e sussista un titolo idoneo al trasferimento della proprietà.", EIGENDOM),
    _b("es_titulo_modo", "ES", "es", "teoría del título y el modo", "art. 609, 1095 CC",
       "La propiedad se transmite por consecuencia de ciertos contratos mediante la tradición (art. 609): el contrato (título) no basta, hace falta la "
       "entrega (modo); el acreedor no adquiere derecho real hasta la entrega (art. 1095). Sistema causal: la nulidad del título impide la transmisión.", EIGENDOM),
    _b("es_tradicion", "ES", "es", "tradición (entrega)", "art. 1462–1464 CC",
       "Se entiende entregada la cosa vendida cuando se pone en poder y posesión del comprador; admite formas espiritualizadas, como el otorgamiento "
       "de escritura pública (art. 1462.2). Es el 'modo' que completa la transmisión.", EIGENDOM),
    _b("es_posesion", "ES", "es", "posesión", "art. 430 CC",
       "Posesión natural: la tenencia de una cosa o el disfrute de un derecho; posesión civil: esa misma tenencia unida a la intención de haber la cosa "
       "como suya.", EIGENDOM),
    _b("es_464", "ES", "es", "la posesión equivale al título", "art. 464 CC",
       "La posesión de los bienes muebles, adquirida de buena fe, equivale al título; quien perdió la cosa o fue privado ilegalmente de ella puede "
       "reivindicarla. Alcance discutido (tesis romanista o germanista).", EIGENDOM),
    _b("ch_kausal", "CH", "de", "Kausalitätsprinzip", "Art. 714 Abs. 1, Art. 974 Abs. 2 ZGB; BGE 55 II 302",
       "Die Übertragung des Fahrniseigentums setzt neben dem Besitzübergang einen gültigen Rechtsgrund voraus. Anders als in Deutschland gilt das "
       "Kausalprinzip (BGE 55 II 302); für Grundstücke ausdrücklich Art. 974 Abs. 2 ZGB.", EIGENDOM),
    _b("ch_besitzuebergang", "CH", "de", "Besitzübergang (Übergabe)", "Art. 714 Abs. 1, Art. 922–925 ZGB",
       "Zur Übertragung des Fahrniseigentums bedarf es des Überganges des Besitzes: Übergabe der Sache oder der Mittel, die die Gewalt über sie "
       "verschaffen (Art. 922); Besitzanweisung und Besitzkonstitut als Ersatz (Art. 924).", EIGENDOM),
    _b("ch_besitz", "CH", "de", "Besitz", "Art. 919, 920 ZGB",
       "Wer die tatsächliche Gewalt über eine Sache hat, ist ihr Besitzer. Selbständiger (Eigentümer) und unselbständiger Besitz (etwa der Mieter): "
       "beide sind Besitzer (Art. 920).", EIGENDOM),
    _b("ch_gutglaube", "CH", "de", "gutgläubiger Fahrniserwerb", "Art. 714 Abs. 2, Art. 933–934 ZGB",
       "Wer eine bewegliche Sache in gutem Glauben zu Eigentum übertragen erhält, wird Eigentümer, auch wenn der Veräusserer nicht verfügen durfte, "
       "sofern die Sache anvertraut war (Art. 933); abhanden gekommene Sachen kann der Besitzer während fünf Jahren zurückfordern (Art. 934).", EIGENDOM),
    _b("en_property", "EN", "en", "passing of property (intention)", "s 16–18 SGA 1979",
       "In a sale of specific or ascertained goods, property passes when the parties intend it to pass (s 17); absent a contrary intention the rules in s 18 "
       "apply (Rule 1: unconditional contract for specific goods in a deliverable state — on conclusion of the contract). No property passes in "
       "unascertained goods until they are ascertained (s 16).", EIGENDOM),
    _b("en_delivery", "EN", "en", "delivery", "s 27, s 61(1) SGA 1979",
       "Voluntary transfer of possession from one person to another (s 61(1)). The seller's duty to deliver (s 27) is a contractual obligation, "
       "not a requirement for the passing of property.", EIGENDOM),
    _b("en_possession", "EN", "en", "possession", "common law; Torts (Interference with Goods) Act 1977",
       "Factual control coupled with an intention to possess. Possession is itself a root of title (relativity of title) and is protected by conversion "
       "and trespass to goods; a bailee is in possession.", EIGENDOM),
    _b("en_nemo_dat", "EN", "en", "nemo dat quod non habet", "s 21–25 SGA 1979; s 2 FA 1889",
       "A buyer acquires no better title than the seller had (s 21(1)), subject to closed exceptions: estoppel, mercantile agents, sale under a voidable "
       "title, seller or buyer in possession (ss 23–25). No general protection of the good-faith purchaser.", EIGENDOM),
    _b("us_title", "US", "en", "passing of title", "UCC § 2-401",
       "Title passes in any manner and on any conditions explicitly agreed; otherwise at the time and place at which the seller completes performance "
       "with reference to physical delivery (§ 2-401(2)). Article 2 deliberately makes most rights and remedies independent of where title lies.", EIGENDOM),
    _b("us_entrustment", "US", "en", "entrustment", "UCC § 2-403",
       "A person with voidable title can transfer good title to a good-faith purchaser for value (§ 2-403(1)); entrusting goods to a merchant who deals "
       "in goods of that kind gives him power to transfer all rights of the entruster to a buyer in ordinary course of business (§ 2-403(2)).", EIGENDOM),
    _b("au_property", "AU", "en", "property passes when intended", "s 22, 23 Sale of Goods Act 1923 (NSW)",
       "Modelled on the English Sale of Goods Act 1893: property in specific or ascertained goods passes when the parties intend it to pass, with "
       "statutory rules for ascertaining that intention. The same scheme applies in the other states.", EIGENDOM),
    _b("eu_dcfr", "EU", "en", "transfer of ownership (DCFR)", "art. VIII.-2:101, VIII.-2:202 DCFR",
       "Ownership of goods passes if the goods exist and are transferable, the transferor has the right or authority to transfer, the transferee is "
       "entitled to it under a contract or other juridical act, and the parties agree on the time or — by default — the goods are delivered. "
       "Causal: if the underlying act is invalid, ownership is treated as never having passed (VIII.-2:202).", EIGENDOM),

    # --- precontractuele aansprakelijkheid ------------------------------------------
    _b("be_precontr", "BE", "nl", "precontractuele aansprakelijkheid", "art. 5.15–5.17 BW",
       "Partijen zijn vrij onderhandelingen aan te vatten, te voeren en af te breken, maar handelen te goeder trouw (art. 5.15). De aansprakelijkheid is "
       "buitencontractueel (art. 5.17 lid 1). Bij foutief afbreken: terugplaatsing in de toestand zonder onderhandelingen; bij rechtmatig vertrouwen dat "
       "het contract zonder enige twijfel gesloten zou worden ook de verwachte netto-voordelen (art. 5.17 lid 2).", PRECONTRACTUEEL),
    _b("be_goede_trouw", "BE", "nl", "goede trouw", "art. 5.15, 5.73 BW; art. 1.10 BW",
       "Objectieve gedragsnorm: een contract moet te goeder trouw worden uitgevoerd (art. 5.73), met aanvullende en beperkende werking; in de "
       "onderhandelingsfase via art. 5.15 en de informatieplicht van art. 5.16. Het verbod van rechtsmisbruik staat algemeen in art. 1.10.", PRECONTRACTUEEL),
    _b("it_resp", "IT", "it", "responsabilità precontrattuale", "art. 1337, 1338 c.c.; Cass. 12 luglio 2016, n. 14188",
       "Le parti, nello svolgimento delle trattative e nella formazione del contratto, devono comportarsi secondo buona fede (art. 1337). Natura discussa: "
       "extracontrattuale (art. 2043) per la giurisprudenza tradizionale, da 'contatto sociale qualificato' (contrattuale) per Cass. 14188/2016. "
       "Risarcimento dell'interesse negativo.", PRECONTRACTUEEL),
    _b("it_buona_fede", "IT", "it", "buona fede (correttezza)", "art. 1175, 1337, 1366, 1375 c.c.",
       "Buona fede in senso oggettivo: regola di condotta nelle trattative (art. 1337), nell'interpretazione (art. 1366) e nell'esecuzione del contratto "
       "(art. 1375), equivalente alla correttezza dell'art. 1175. Distinta dalla buona fede soggettiva (ignoranza di ledere l'altrui diritto, art. 1147).", PRECONTRACTUEEL),
    _b("it_interesse_negativo", "IT", "it", "interesse negativo", "art. 1338 c.c.",
       "Il danno subito per aver confidato nella conclusione o nella validità del contratto: spese inutili e occasioni alternative perdute; "
       "esclude l'interesse positivo all'esecuzione.", PRECONTRACTUEEL),
    _b("es_culpa", "ES", "es", "culpa in contrahendo", "art. 1902, 7.1 CC; jurisprudencia del TS",
       "Sin regulación específica: la ruptura injustificada de los tratos preliminares que defrauda la confianza suscitada se reconduce a la "
       "responsabilidad extracontractual (art. 1902), con fundamento en la buena fe (art. 7.1). Se indemniza el interés negativo.", PRECONTRACTUEEL),
    _b("es_buena_fe", "ES", "es", "buena fe", "art. 7.1, 1258 CC",
       "Los derechos deben ejercitarse conforme a las exigencias de la buena fe (art. 7.1); los contratos obligan también a las consecuencias que, "
       "según su naturaleza, sean conformes a la buena fe (art. 1258).", PRECONTRACTUEEL),
    _b("ch_cic", "CH", "de", "culpa in contrahendo (Vertrauenshaftung)", "Art. 2 ZGB; BGE 120 II 331",
       "Haftung für die Verletzung vorvertraglicher Pflichten aus dem durch Vertragsverhandlungen begründeten Vertrauensverhältnis (Art. 2 ZGB). "
       "Nicht kodifiziert; das Bundesgericht ordnet sie als Vertrauenshaftung eigener Art zwischen Vertrag und Delikt ein. Ersatz grundsätzlich "
       "des negativen Interesses.", PRECONTRACTUEEL),
    _b("ch_tug", "CH", "de", "Treu und Glauben", "Art. 2 Abs. 1 ZGB",
       "Jedermann hat in der Ausübung seiner Rechte und in der Erfüllung seiner Pflichten nach Treu und Glauben zu handeln (Art. 2 Abs. 1); "
       "der offenbare Rechtsmissbrauch findet keinen Rechtsschutz (Abs. 2). Vom guten Glauben (Art. 3) unterschieden.", PRECONTRACTUEEL),
    _b("ch_negativ", "CH", "de", "negatives Interesse", "Art. 26, 39 OR",
       "Ersatz des aus dem Dahinfallen des Vertrages erwachsenen Schadens: der Geschädigte ist so zu stellen, wie wenn er nie auf den Vertrag "
       "vertraut hätte (Art. 26 Abs. 1 OR beim fahrlässigen Irrtum, Art. 39 Abs. 1 OR beim vollmachtlosen Vertreter).", PRECONTRACTUEEL),
    _b("en_no_duty", "EN", "en", "no duty to negotiate in good faith", "Walford v Miles [1992] 2 AC 128 (HL)",
       "English law recognises no general duty to negotiate in good faith: an agreement to negotiate is unenforceable for uncertainty and each party "
       "may withdraw at any time. Protection is piecemeal: misrepresentation, collateral contract, restitution for work requested in anticipation "
       "of a contract, estoppel.", PRECONTRACTUEEL),
    _b("en_good_faith", "EN", "en", "good faith", "Yam Seng v ITC [2013] EWHC 111 (QB); s 62 CRA 2015",
       "No general organising principle of good faith in English contract law. A duty may be implied in 'relational' contracts as a matter of "
       "construction; statutory good faith in consumer law (unfair terms, s 62 CRA 2015).", PRECONTRACTUEEL),
    _b("en_misrep", "EN", "en", "misrepresentation", "s 2(1) MA 1967; Royscot Trust v Rogerson [1991] 2 QB 297",
       "A false statement of fact or law inducing a contract. Damages under s 2(1) are assessed on the tort (deceit) measure — reliance, "
       "not expectation — unless the representor proves reasonable belief in its truth.", PRECONTRACTUEEL),
    _b("en_reliance", "EN", "en", "reliance loss", "Anglia Television v Reed [1972] 1 QB 60",
       "Wasted expenditure incurred in reliance on the contract, recoverable as an alternative to expectation loss, including pre-contractual "
       "expenditure within the parties' contemplation; capped by what the claimant would have earned.", PRECONTRACTUEEL),
    _b("us_promissory", "US", "en", "promissory estoppel", "Rest. 2d Contracts § 90; Hoffman v Red Owl Stores, 133 N.W.2d 267 (Wis. 1965)",
       "A promise which the promisor should reasonably expect to induce action or forbearance, and which does induce it, is binding if injustice can be "
       "avoided only by enforcement. Hoffman v Red Owl applied it to failed negotiations and awarded reliance damages.", PRECONTRACTUEEL),
    _b("us_good_faith", "US", "en", "duty of good faith and fair dealing", "Rest. 2d Contracts § 205; UCC § 1-304",
       "Every contract imposes upon each party a duty of good faith and fair dealing in its performance and its enforcement — not in its "
       "negotiation (Rest. 2d § 205 cmt. c).", PRECONTRACTUEEL),
    _b("au_estoppel", "AU", "en", "equitable estoppel", "Waltons Stores (Interstate) Ltd v Maher (1988) 164 CLR 387",
       "A party may be prevented from departing from an assumption it induced — that a contract would be concluded — where departure would be "
       "unconscionable; relief is proportionate to the detriment. Unlike English promissory estoppel it can found a cause of action.", PRECONTRACTUEEL),
    _b("au_s18", "AU", "en", "misleading or deceptive conduct", "s 18 ACL",
       "A person must not, in trade or commerce, engage in conduct that is misleading or deceptive or likely to mislead or deceive. Applies to "
       "pre-contractual negotiations, including silence and representations about future matters (s 4 ACL); no fault required.", PRECONTRACTUEEL),
]


def _r(van, naar, typ, toelichting):
    return (van, naar, typ, toelichting + NV)


RELATIES = [
    # --- overdracht --------------------------------------------------------------------
    _r("fr_consensu", "nl_levering", "geen", "FR kent geen levering als overdrachtsvereiste: de eigendom gaat solo consensu over; NL eist levering krachtens geldige titel."),
    _r("fr_consensu", "be_wil", "deels", "Zelfde uitkomst (overgang bij wilsovereenstemming), maar BE onderscheidt sinds 2021 uitdrukkelijk de titel (verbintenis tot geven) van de rechtshandeling tot overdracht."),
    _r("fr_consensu", "it_consenso", "equivalent", "Art. 1376 c.c. volgt het Franse consensualisme: overgang door de wilsovereenstemming bij een bepaalde zaak."),
    _r("fr_consensu", "en_property", "deels", "Geen van beide eist levering. FR: overgang bij de contractsluiting; EN: wanneer partijen dat willen, met s 18 Rule 1 als vermoeden van overgang bij de contractsluiting."),
    _r("es_titulo_modo", "nl_causaal", "deels", "Beide causaal en met een traditio-vereiste; ES aanvaardt vergeestelijkte vormen (notariële akte als levering, art. 1462.2 CC)."),
    _r("es_titulo_modo", "fr_consensu", "geen", "Spanje wijkt bewust af van het Franse consensualisme: titel alleen draagt niet over."),
    _r("es_titulo_modo", "de_abstraktion", "geen", "Spanje is causaal: zonder geldige titel geen eigendomsovergang."),
    _r("ch_kausal", "nl_causaal", "equivalent", "Beide: overdracht vereist een geldige rechtsgrond en bezitsverschaffing."),
    _r("ch_kausal", "de_abstraktion", "geen", "Het ZGB nam de Duitse structuur (Besitzübergang) over maar verwierp het Abstraktionsprinzip (BGE 55 II 302)."),
    _r("ch_besitzuebergang", "de_uebergabe", "equivalent", "Zelfde Realakt met dezelfde surrogaten (Besitzanweisung, Besitzkonstitut)."),
    _r("ch_besitzuebergang", "nl_levering", "deels", "CH Besitzübergang is het feitelijke deel van de NL levering; de wilsovereenstemming zit in CH in het Verfügungsgeschäft."),
    _r("es_tradicion", "nl_levering", "deels", "Beide constitutief (modo), maar de tradición instrumental (art. 1462.2 CC) gaat verder dan de NL bezitsverschaffing."),
    _r("es_tradicion", "fr_delivrance", "faux_ami", "Zelfde betekenis 'overgave', maar in ES vereiste voor de eigendomsovergang, in FR alleen uitvoering van de koop."),
    _r("it_consegna", "fr_delivrance", "equivalent", "Beide: verbintenis van de verkoper, zonder goederenrechtelijk effect bij een bepaalde zaak."),
    _r("it_consegna", "nl_levering", "faux_ami", "Consegna is uitvoering van de koop; de NL levering is overdrachtsvereiste."),
    _r("be_levering", "fr_delivrance", "equivalent", "Art. 1604 oud BW is dezelfde bepaling als art. 1604 C. civ."),
    _r("be_levering", "nl_levering", "faux_ami", "Zelfde woord in dezelfde taal, ander begrip: in BE een verbintenis van de verkoper, in NL de rechtshandeling die de eigendom overdraagt."),
    _r("en_delivery", "nl_levering", "faux_ami", "Delivery is in EN alleen een contractuele plicht (s 27 SGA); property gaat over naar de wil van partijen."),
    _r("en_delivery", "fr_delivrance", "equivalent", "Beide: overdracht van het bezit als uitvoering van de koop, los van de eigendomsovergang."),
    _r("us_title", "en_property", "deels", "Beide volgen in de eerste plaats de wil van partijen; zonder afspraak gaat title in de US over bij de levering (§ 2-401(2)), property in EN bij specifieke zaken al bij de contractsluiting."),
    _r("au_property", "en_property", "equivalent", "De Australische Sale of Goods Acts nemen het Engelse schema van 1893 over."),
    _r("eu_dcfr", "nl_causaal", "deels", "Het DCFR is causaal en eist standaard levering, maar laat partijen een ander tijdstip kiezen."),
    _r("eu_dcfr", "de_abstraktion", "geen", "Het DCFR kiest uitdrukkelijk voor het causale stelsel (VIII.-2:202)."),
    # --- bezit ------------------------------------------------------------------------------
    _r("be_bezit", "nl_bezit", "equivalent", "Beide eisen uitoefening als rechthebbende; de BE detentor is de NL houder."),
    _r("be_bezit", "fr_possession", "equivalent", "Art. 3.18 BW moderniseert dezelfde Franse figuur (corpus en animus)."),
    _r("it_possesso", "fr_possession", "equivalent", "Beide: macht over de zaak met animus domini; de detentore is geen possessore."),
    _r("it_possesso", "de_besitz", "deels", "IT onderscheidt possesso van detenzione; in DE is ook de huurder Besitzer."),
    _r("es_posesion", "de_besitz", "deels", "De posesión natural (louter houden) ligt dicht bij de DE Besitz; de posesión civil (met animus) bij de Eigenbesitz."),
    _r("ch_besitz", "de_besitz", "equivalent", "Beide zuiver feitelijke macht; selbständiger/unselbständiger Besitz ≈ Eigen-/Fremdbesitz."),
    _r("ch_besitz", "nl_bezit", "faux_ami", "De CH-huurder is Besitzer (Art. 920 ZGB); in NL is hij houder, geen bezitter."),
    _r("en_possession", "nl_bezit", "deels", "EN possession eist geen animus domini (ook de bailee bezit), maar beschermt bezit wel als relatieve titel."),
    # --- verkrijging te goeder trouw ---------------------------------------------------------
    _r("be_328", "fr_titre", "equivalent", "Art. 3.28 BW vervangt art. 2279 oud BW, dat gelijk was aan art. 2276 C. civ."),
    _r("it_1153", "fr_titre", "deels", "Zelfde maxime; IT eist daarnaast uitdrukkelijk een titolo idoneo."),
    _r("es_464", "fr_titre", "deels", "Zelfde maxime, maar de draagwijdte van art. 464 CC (verkrijging of alleen bewijs) is omstreden."),
    _r("ch_gutglaube", "fr_titre", "deels", "Beide beschermen de verkrijger te goeder trouw van roerende zaken; CH onderscheidt uitdrukkelijk anvertraute van abhanden gekommene Sachen."),
    _r("en_nemo_dat", "fr_titre", "geen", "EN beschermt de verkrijger te goeder trouw alleen in gesloten uitzonderingen; FR maakt van bezit te goeder trouw de hoofdregel."),
    _r("us_entrustment", "en_nemo_dat", "deels", "Zelfde vertrekpunt (nemo dat), maar de UCC-entrustmentregel is een ruimere uitzondering dan de Engelse mercantile agent."),
    # --- precontractueel -------------------------------------------------------------------
    _r("be_precontr", "nl_precontr", "deels", "Art. 5.17 BW codificeert in wezen de NL driefasenleer (Plas/Valburg): negatief belang, en bij gerechtvaardigd vertrouwen in de totstandkoming ook het positieve. Wel buitencontractueel."),
    _r("be_precontr", "fr_rupture", "deels", "Beide buitencontractueel; BE staat uitzonderlijk de verwachte netto-voordelen toe, die art. 1112 al. 2 C. civ. juist uitsluit."),
    _r("be_precontr", "eu_cic", "equivalent", "De BE-kwalificatie (buitencontractueel) sluit aan bij art. 12 Rome II."),
    _r("it_resp", "de_cic", "deels", "Zelfde functie; art. 1337 c.c. is een uitdrukkelijke goede-trouwnorm, de aard (contractueel of niet) is in IT omstreden."),
    _r("it_resp", "fr_rupture", "deels", "Beide beperken de vergoeding tot het negatieve belang; IT heeft een eigen bepaling, FR sinds 2016 art. 1112."),
    _r("it_resp", "eu_cic", "equivalent", "Voor de verwijzing kwalificeert art. 12 Rome II autonoom, ongeacht het Italiaanse debat over contatto sociale."),
    _r("es_culpa", "fr_rupture", "equivalent", "Beide delictueel via de algemene schadeclausule (art. 1902 CC / art. 1240 C. civ.)."),
    _r("es_culpa", "de_cic", "faux_ami", "Zelfde term, andere grondslag: in ES delictueel, in DE een quasi-contractueel Schuldverhältnis (§ 311 Abs. 2 BGB)."),
    _r("ch_cic", "de_cic", "deels", "Zelfde naam en functie; CH ongecodificeerd en als Vertrauenshaftung sui generis, DE gecodificeerd in § 311 Abs. 2 BGB."),
    _r("en_no_duty", "nl_precontr", "geen", "EN kent geen aansprakelijkheid voor het afbreken van onderhandelingen als zodanig."),
    _r("en_no_duty", "fr_rupture", "geen", "Waar FR de vrijheid van onderhandelen begrenst door de bonne foi, laat EN die vrijheid onbegrensd (Walford v Miles)."),
    _r("us_promissory", "nl_precontr", "deels", "Functioneel equivalent voor vertrouwensschade bij afgebroken onderhandelingen (Hoffman v Red Owl), maar via een belofte en niet via goede trouw."),
    _r("au_estoppel", "us_promissory", "deels", "Beide kunnen als zwaard dienen; AU bindt het aan unconscionability en beperkt het herstel tot wat het nadeel vergt."),
    _r("au_s18", "en_misrep", "deels", "S 18 ACL gaat verder dan misrepresentation: geen schuld vereist en ook zwijgen en uitlatingen over de toekomst vallen eronder."),
    # --- goede trouw ------------------------------------------------------------------------
    _r("be_goede_trouw", "nl_rb", "equivalent", "BE houdt de oude term 'goede trouw' aan voor wat NL sinds 1992 'redelijkheid en billijkheid' noemt."),
    _r("be_goede_trouw", "fr_bonne_foi", "equivalent", "Zelfde Franse traditie; BE heeft de norm in Boek 5 en art. 1.10 verder uitgewerkt."),
    _r("it_buona_fede", "fr_bonne_foi", "equivalent", "Beide kennen de objectieve en de subjectieve goede trouw onder één woord; IT gebruikt daarnaast correttezza."),
    _r("it_buona_fede", "de_tug", "equivalent", "Objectieve buona fede/correttezza ≈ Treu und Glauben (§ 242 BGB)."),
    _r("es_buena_fe", "fr_bonne_foi", "equivalent", "Beide: objectieve norm voor uitoefening van rechten en de inhoud van overeenkomsten."),
    _r("ch_tug", "de_tug", "equivalent", "Art. 2 ZGB is als algemene norm van het hele privaatrecht nog ruimer geformuleerd dan § 242 BGB."),
    _r("en_good_faith", "de_tug", "deels", "Geen algemeen beginsel in EN; alleen een stilzwijgende plicht in relational contracts en wettelijke goede trouw in het consumentenrecht."),
    _r("us_good_faith", "de_tug", "deels", "Geldt in de US voor uitvoering en handhaving, niet voor het onderhandelen."),
    # --- schade ------------------------------------------------------------------------------
    _r("it_interesse_negativo", "de_negativ", "equivalent", "Dezelfde pandektistische figuur."),
    _r("ch_negativ", "de_negativ", "equivalent", "Dezelfde figuur; het OR noemt het 'Schaden aus dem Dahinfallen des Vertrages'."),
    _r("en_reliance", "de_negativ", "deels", "Reliance loss is in EN een contractuele schadepost die door het verwachtingsbelang wordt begrensd; het negatieve belang in DE staat los van de overeenkomst."),
]
