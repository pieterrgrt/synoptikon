"""Omzetting en uitvoering van Unierecht op artikelniveau, en roepnamen van handelingen.

Waar staat een richtlijn in het nationale recht? Cellar weet welke *wetten*
een lidstaat als omzetting heeft gemeld (EuNim), niet in welk *artikel* van
welk wetboek de regel terechtkwam. Deze tabel legt dat vast voor de
richtlijnen en verordeningen die in het privaatrecht en het digitale recht
het zwaarst wegen, voor alle stelsels in Synoptikon.

Eigen aantekening, niet tegen de officiële teksten gecontroleerd: elke regel
wordt geladen met `geverifieerd=False` en in de app zo getoond. Bereiken
zijn de kern van de omzetting, geen uitputtende concordantie. Wie een regel
controleert, zet hem in de app op geverifieerd.

Vorm per regel: O(celex, stelsel, wet, van, tot, eu_artikel, soort, opmerking, wet_titel).
`wet` None = hoofdcodificatie; `van` None = de wet als geheel (dan zegt
`wet_titel` welke wet). Soorten: zie models.OMZETTING_SOORTEN.
"""
from __future__ import annotations

from typing import NamedTuple


class O(NamedTuple):
    celex: str
    stelsel: str
    wet: str | None
    van: str | None
    tot: str | None = None
    eu_artikel: str | None = None
    soort: str = "omzetting"
    opmerking: str | None = None
    wet_titel: str | None = None


ROEPNAMEN: dict[str, str] = {
    # digitaal recht
    "32016R0679": "AVG (GDPR)", "32022R2065": "DSA (digitaledienstenverordening)", "32022R1925": "DMA (digitalemarktenverordening)",
    "32024R1689": "AI-verordening (AI Act)", "32023R2854": "Dataverordening (Data Act)", "32022R0868": "Datagovernanceverordening",
    "32022R2554": "DORA", "32023R1114": "MiCA", "32014R0910": "eIDAS-verordening", "32022L2555": "NIS2-richtlijn",
    "32024R2847": "Cyberweerbaarheidsverordening (CRA)", "32019R1150": "P2B-verordening", "32018R0302": "Geoblockingverordening",
    "32017R1128": "Portabiliteitsverordening", "32002L0058": "E-privacyrichtlijn", "32018R1725": "EUDPR", "32016L0680": "Richtlijn gegevensbescherming opsporing",
    "32019L0790": "DSM-richtlijn (auteursrecht)", "32000L0031": "Richtlijn elektronische handel", "32015L2366": "PSD2",
    # internationaal privaatrecht
    "32008R0593": "Rome I", "32007R0864": "Rome II", "32012R1215": "Brussel I-bis", "32012R0650": "Erfrechtverordening",
    "32015R0848": "Insolventieverordening", "32019R1111": "Brussel II-ter", "32016R1103": "Huwelijksvermogensverordening",
    "32016R1104": "Verordening vermogensgevolgen geregistreerde partnerschappen", "32006R1896": "Europees betalingsbevel",
    "32007R0861": "Europese procedure voor geringe vorderingen", "32004R0805": "Europese executoriale titel",
    # consumenten- en overeenkomstenrecht
    "31985L0374": "Productaansprakelijkheidsrichtlijn (1985)", "32024L2853": "Productaansprakelijkheidsrichtlijn (2024)",
    "31993L0013": "Richtlijn oneerlijke bedingen", "32011L0083": "Richtlijn consumentenrechten", "32019L0770": "Richtlijn digitale inhoud",
    "32019L0771": "Richtlijn verkoop van goederen", "32011L0007": "Richtlijn betalingsachterstand", "32005L0029": "Richtlijn oneerlijke handelspraktijken",
    "31986L0653": "Handelsagentenrichtlijn", "32008L0048": "Consumentenkredietrichtlijn (2008)", "32023L2225": "Consumentenkredietrichtlijn (2023)",
    "32015L2302": "Pakketreisrichtlijn", "32014L0017": "Hypothecairkredietrichtlijn", "32020L1828": "Richtlijn representatieve vorderingen",
    "32016L0943": "Bedrijfsgeheimenrichtlijn", "32014L0104": "Richtlijn schadevergoedingsacties mededinging", "32002L0047": "Richtlijn financiëlezekerheidsovereenkomsten",
    "32023R0988": "Algemene productveiligheidsverordening (GPSR)", "32004R0261": "Verordening luchtvaartpassagiersrechten", "32017R2394": "CPC-verordening",
    "32024L0825": "Richtlijn consumentenbekwaamheid groene transitie", "32006L0114": "Richtlijn misleidende en vergelijkende reclame",
    # vennootschaps-, insolventie- en arbeidsrecht
    "32017L1132": "Vennootschapsrichtlijn", "32019L1023": "Herstructureringsrichtlijn", "32022L2464": "CSRD", "32024L1760": "CSDDD",
    "32001L0023": "Richtlijn overgang van ondernemingen", "31999L0070": "Richtlijn arbeidsovereenkomsten voor bepaalde tijd",
    "32019L1152": "Richtlijn transparante en voorspelbare arbeidsvoorwaarden", "32003L0088": "Arbeidstijdenrichtlijn",
}


OMZETTINGEN: list[O] = [
    # --- Productaansprakelijkheid 85/374 ---------------------------------------------------
    O("31985L0374", "NL", None, "6:185", "6:193", None, opmerking="Afdeling 6.3.3 BW; art. 6 richtlijn (gebrek) in 6:186, art. 7 (verweren) in 6:185 lid 1"),
    O("31985L0374", "DE", "ProdHaftG", "1", "19", None, opmerking="Afzonderlijke wet naast § 823 BGB; § 3 Fehler, § 4 Hersteller"),
    O("31985L0374", "FR", None, "1245", "1245-17", None, opmerking="Oud art. 1386-1 e.v., vernummerd in 2016; ingevoerd pas in 1998 na veroordeling (C-293/91)"),
    O("31985L0374", "BE", None, None, None, None, opmerking="Afzonderlijke wet; niet opgenomen in Boek 6 BW", wet_titel="Wet van 25 februari 1991 betreffende de aansprakelijkheid voor produkten met gebreken"),
    O("31985L0374", "IT", "c. cons.", "114", "127", None, opmerking="Oorspronkelijk d.P.R. 224/1988, sinds 2005 in de Codice del consumo"),
    O("31985L0374", "ES", "TRLGDCU", "128", "149", None, opmerking="Libro III TRLGDCU"),
    O("31985L0374", "EN", "CPA 1987", "1", "9", None, soort="voortgezet", opmerking="Part I Consumer Protection Act 1987; blijft na de Brexit nationaal recht"),
    O("31985L0374", "CH", "PrHG", "1", "14", None, soort="navolging", opmerking="Produktehaftpflichtgesetz 1993, naar het voorbeeld van de richtlijn (Swisslex)"),
    # --- Oneerlijke bedingen 93/13 -------------------------------------------------------------
    O("31993L0013", "NL", None, "6:231", "6:247", None, opmerking="Afdeling 6.5.3 (algemene voorwaarden) bestond al sinds 1992; de richtlijn is erin 'ingelezen'"),
    O("31993L0013", "NL", None, "6:238", None, "5", opmerking="Lid 2: uitleg in het voordeel van de consument"),
    O("31993L0013", "DE", None, "305", "310", None, opmerking="Voormalig AGBG; § 310 Abs. 3 voor consumentenovereenkomsten, § 307 Inhaltskontrolle"),
    O("31993L0013", "DE", None, "305c", None, "5", opmerking="Abs. 2: Unklarheitenregel"),
    O("31993L0013", "FR", "C. consom.", "L212-1", "L212-2", None, opmerking="Clauses abusives; zwarte en grijze lijst in R212-1 en R212-2"),
    O("31993L0013", "BE", "WER", "VI.82", "VI.87", None),
    O("31993L0013", "IT", "c. cons.", "33", "38", None, opmerking="Voorheen art. 1469-bis e.v. c.c. (1996), in 2005 overgebracht"),
    O("31993L0013", "ES", "TRLGDCU", "82", "91", None, opmerking="Naast de Ley 7/1998 sobre Condiciones Generales de la Contratación"),
    O("31993L0013", "EN", "CRA 2015", "61", "76", None, soort="voortgezet", opmerking="Part 2 CRA 2015 (verving de Regulations 1999)"),
    O("31993L0013", "CH", "UWG", "8", None, None, soort="navolging", opmerking="Ten dele: sinds 2012 een open inhoudstoets voor consumenten-AGB"),
    # --- Consumentenrechten 2011/83 --------------------------------------------------------------
    O("32011L0083", "NL", None, "6:230g", "6:230z", None, opmerking="Afdeling 6.5.2B BW"),
    O("32011L0083", "DE", None, "312", "312k", None, opmerking="Nebst §§ 355–357d (Widerruf) en Art. 246a EGBGB (informatie)"),
    O("32011L0083", "DE", None, "355", "361", "9–16", opmerking="Herroepingsrecht"),
    O("32011L0083", "FR", "C. consom.", "L221-1", "L221-29", None, opmerking="Contrats conclus à distance et hors établissement"),
    O("32011L0083", "BE", "WER", "VI.45", "VI.73", None),
    O("32011L0083", "IT", "c. cons.", "45", "67", None),
    O("32011L0083", "ES", "TRLGDCU", "92", "113", None),
    O("32011L0083", "EN", None, None, None, None, soort="voortgezet",
      wet_titel="Consumer Contracts (Information, Cancellation and Additional Charges) Regulations 2013 (SI 2013/3134)"),
    # --- Verkoop van goederen 2019/771 ------------------------------------------------------------
    O("32019L0771", "NL", None, "7:5", "7:25", None, opmerking="Consumentenkoop in titel 7.1 BW; Implementatiewet 2022 (Stb. 2022, 164)"),
    O("32019L0771", "NL", None, "7:18", None, "6–7", opmerking="Subjectieve en objectieve conformiteitseisen"),
    O("32019L0771", "NL", None, "7:18a", None, "11", opmerking="Lid 2: bewijsvermoeden van non-conformiteit, één jaar na aflevering"),
    O("32019L0771", "DE", None, "474", "479", None, opmerking="Verbrauchsgüterkauf; Sachmangelbegriff in § 434, Rechtsbehelfe §§ 437–445"),
    O("32019L0771", "DE", None, "434", None, "6–7", opmerking="Subjektive, objektive Anforderungen en Montageanforderungen"),
    O("32019L0771", "FR", "C. consom.", "L217-1", "L217-32", None, opmerking="Garantie légale de conformité (ordonnance 2021-1247)"),
    O("32019L0771", "BE", "oud BW", "1649bis", "1649novies", None, opmerking="Consumentenkoop in het oud BW, herschreven bij wet van 20 maart 2022"),
    O("32019L0771", "IT", "c. cons.", "128", "135-septies", None, opmerking="d.lgs. 170/2021"),
    O("32019L0771", "ES", "TRLGDCU", "114", "127", None, opmerking="RDL 7/2021, één regeling voor goederen en digitale inhoud"),
    # --- Digitale inhoud 2019/770 ------------------------------------------------------------------
    O("32019L0770", "NL", None, "7:50aa", "7:50ap", None, opmerking="Titel 7.1AA BW"),
    O("32019L0770", "DE", None, "327", "327u", None, opmerking="Verträge über digitale Produkte, in het Allgemeines Schuldrecht"),
    O("32019L0770", "FR", "C. consom.", "L224-25-1", "L224-25-31", None),
    O("32019L0770", "BE", "oud BW", "1701/1", "1701/19", None, opmerking="Eigen titel in het oud BW (wet van 20 maart 2022)"),
    O("32019L0770", "IT", "c. cons.", "135-octies", "135-vicies-ter", None, opmerking="d.lgs. 173/2021"),
    O("32019L0770", "ES", "TRLGDCU", "114", "127", None, opmerking="Samen met de goederenkoop (RDL 7/2021)"),
    # --- Betalingsachterstand 2011/7 -------------------------------------------------------------
    O("32011L0007", "NL", None, "6:119a", "6:119b", None, opmerking="Wettelijke handelsrente; termijnen in 6:119a en 6:119b"),
    O("32011L0007", "DE", None, "286", "288", None, opmerking="§ 286 Abs. 3, § 288 Abs. 2 en 5; maximale termijnen in § 271a"),
    O("32011L0007", "FR", "C. com.", "L441-10", "L441-16", None, opmerking="Délais de paiement, pénalités et indemnité forfaitaire de 40 €"),
    O("32011L0007", "BE", None, None, None, None, wet_titel="Wet van 2 augustus 2002 betreffende de bestrijding van de betalingsachterstand bij handelstransacties"),
    O("32011L0007", "IT", None, None, None, None, wet_titel="Decreto legislativo 9 ottobre 2002, n. 231 (gewijzigd bij d.lgs. 192/2012)"),
    O("32011L0007", "ES", None, None, None, None, wet_titel="Ley 3/2004 por la que se establecen medidas de lucha contra la morosidad en las operaciones comerciales"),
    O("32011L0007", "EN", "LP(I)A 1998", None, None, None, soort="voortgezet", opmerking="Ouder dan de richtlijn; aangepast bij SI 2013/395"),
    # --- Oneerlijke handelspraktijken 2005/29 --------------------------------------------------
    O("32005L0029", "NL", None, "6:193a", "6:193j", None, opmerking="Afdeling 6.3.3A BW; zwarte lijst in 6:193g en 6:193i"),
    O("32005L0029", "DE", "UWG", "3", "5b", None, opmerking="Met de 'schwarze Liste' in de Anhang zu § 3 Abs. 3 UWG"),
    O("32005L0029", "FR", "C. consom.", "L121-1", "L121-7", None),
    O("32005L0029", "BE", "WER", "VI.92", "VI.105", None),
    O("32005L0029", "IT", "c. cons.", "18", "27-quater", None),
    O("32005L0029", "ES", None, None, None, None, opmerking="art. 19–31 LCD", wet_titel="Ley 3/1991 de Competencia Desleal"),
    O("32005L0029", "EN", None, None, None, None, soort="voortgezet", opmerking="De Consumer Protection from Unfair Trading Regulations 2008 zijn in 2025 vervangen door Part 4 Chapter 1",
      wet_titel="Digital Markets, Competition and Consumers Act 2024"),
    # --- Elektronische handel 2000/31 ---------------------------------------------------------
    O("32000L0031", "NL", None, "3:15d", "3:15f", None, opmerking="Informatieplichten dienstverleners. Art. 12–15 (aansprakelijkheid tussenpersonen) zijn per 17-2-2024 vervangen door art. 4–8 DSA; art. 6:196c BW is daarom vervallen"),
    O("32000L0031", "NL", None, "6:227a", "6:227c", "9–11", opmerking="Elektronisch contracteren"),
    O("32000L0031", "DE", None, "312i", "312j", "10–11", opmerking="Pflichten im elektronischen Geschäftsverkehr"),
    O("32000L0031", "FR", None, "1125", "1127-4", "9–11", opmerking="Contrat conclu par voie électronique"),
    O("32000L0031", "FR", None, None, None, None, wet_titel="Loi n° 2004-575 du 21 juin 2004 pour la confiance dans l'économie numérique (LCEN)"),
    O("32000L0031", "BE", "WER", "XII.1", "XII.26", None),
    O("32000L0031", "IT", None, None, None, None, wet_titel="Decreto legislativo 9 aprile 2003, n. 70"),
    O("32000L0031", "ES", None, None, None, None, wet_titel="Ley 34/2002 de servicios de la sociedad de la información y de comercio electrónico (LSSI)"),
    O("32000L0031", "EN", None, None, None, None, soort="voortgezet", wet_titel="Electronic Commerce (EC Directive) Regulations 2002 (SI 2002/2013)"),
    # --- Handelsagenten 86/653 ---------------------------------------------------------------------
    O("31986L0653", "NL", None, "7:428", "7:445", None, opmerking="Afdeling 7.7.4 BW; klantenvergoeding in 7:442"),
    O("31986L0653", "DE", "HGB", "84", "92c", None, opmerking="Ausgleichsanspruch in § 89b HGB (model voor art. 17 lid 2)"),
    O("31986L0653", "FR", "C. com.", "L134-1", "L134-17", None, opmerking="Indemnité de fin de contrat in L134-12 (model voor art. 17 lid 3)"),
    O("31986L0653", "BE", "WER", "X.1", "X.25", None, opmerking="Boek X, sinds 2014; voorheen wet van 13 april 1995"),
    O("31986L0653", "IT", None, "1742", "1753", None, opmerking="Codice civile, aangepast bij d.lgs. 303/1991 en 65/1999"),
    O("31986L0653", "ES", None, None, None, None, wet_titel="Ley 12/1992 sobre Contrato de Agencia"),
    O("31986L0653", "EN", None, None, None, None, soort="voortgezet", wet_titel="Commercial Agents (Council Directive) Regulations 1993 (SI 1993/3053)"),
    # --- Consumentenkrediet 2008/48 en 2023/2225 ---------------------------------------------
    O("32008L0048", "NL", None, "7:57", "7:126", None, opmerking="Titel 7.2A BW, naast de Wft"),
    O("32008L0048", "DE", None, "491", "505e", None, opmerking="Verbraucherdarlehensvertrag"),
    O("32008L0048", "FR", "C. consom.", "L312-1", "L312-94", None),
    O("32008L0048", "BE", "WER", "VII.64", "VII.144", None),
    O("32008L0048", "IT", None, None, None, None, opmerking="art. 121–126 TUB", wet_titel="Decreto legislativo 1° settembre 1993, n. 385 (Testo unico bancario)"),
    O("32008L0048", "ES", None, None, None, None, wet_titel="Ley 16/2011 de contratos de crédito al consumo"),
    O("32008L0048", "EN", None, None, None, None, soort="voortgezet", wet_titel="Consumer Credit Act 1974 (aangepast bij SI 2010/1010)"),
    O("32023L2225", "NL", None, "7:57", "7:126", None, opmerking="Titel 7.2A BW wordt aangepast; omzettingstermijn 20-11-2025, toepassing vanaf 20-11-2026"),
    O("32023L2225", "DE", None, "491", "505e", None, opmerking="Aanpassing van het Verbraucherdarlehensrecht"),
    # --- Pakketreizen 2015/2302 ---------------------------------------------------------------
    O("32015L2302", "NL", None, "7:500", "7:513", None, opmerking="Titel 7.7A BW"),
    O("32015L2302", "DE", None, "651a", "651y", None, opmerking="Pauschalreisevertrag; informatie in Art. 250–253 EGBGB"),
    O("32015L2302", "FR", None, None, None, None, opmerking="art. L211-1 e.v.", wet_titel="Code du tourisme"),
    O("32015L2302", "BE", None, None, None, None, wet_titel="Wet van 21 november 2017 betreffende de verkoop van pakketreizen, gekoppelde reisarrangementen en reisdiensten"),
    O("32015L2302", "IT", None, None, None, None, opmerking="art. 32–51-novies", wet_titel="Codice del turismo (d.lgs. 79/2011)"),
    O("32015L2302", "ES", "TRLGDCU", "150", "170", None, opmerking="Libro IV TRLGDCU"),
    O("32015L2302", "EN", None, None, None, None, soort="voortgezet", wet_titel="Package Travel and Linked Travel Arrangements Regulations 2018 (SI 2018/634)"),
    # --- Schadevergoeding mededingingsrecht 2014/104 --------------------------------------------
    O("32014L0104", "NL", None, "6:193k", "6:193t", None, opmerking="Afdeling 6.3.4 BW"),
    O("32014L0104", "DE", None, None, None, None, opmerking="§§ 33–33h GWB", wet_titel="Gesetz gegen Wettbewerbsbeschränkungen (GWB)"),
    O("32014L0104", "FR", "C. com.", "L481-1", "L481-14", None),
    O("32014L0104", "BE", "WER", "XVII.71", "XVII.90", None),
    O("32014L0104", "IT", None, None, None, None, wet_titel="Decreto legislativo 19 gennaio 2017, n. 3"),
    O("32014L0104", "ES", None, None, None, None, opmerking="art. 71–81 LDC", wet_titel="Ley 15/2007 de Defensa de la Competencia"),
    # --- Bedrijfsgeheimen 2016/943 --------------------------------------------------------------
    O("32016L0943", "NL", None, None, None, None, wet_titel="Wet bescherming bedrijfsgeheimen (2018)"),
    O("32016L0943", "DE", None, None, None, None, wet_titel="Gesetz zum Schutz von Geschäftsgeheimnissen (GeschGehG, 2019)"),
    O("32016L0943", "FR", "C. com.", "L151-1", "L154-1", None, opmerking="Loi n° 2018-670"),
    O("32016L0943", "BE", "WER", "XI.332/1", "XI.332/5", None, opmerking="Met procedurele bepalingen in het Ger.W."),
    O("32016L0943", "IT", None, None, None, None, opmerking="art. 98–99 c.p.i., aangepast bij d.lgs. 63/2018", wet_titel="Codice della proprietà industriale"),
    O("32016L0943", "ES", None, None, None, None, wet_titel="Ley 1/2019 de Secretos Empresariales"),
    O("32016L0943", "EN", None, None, None, None, soort="voortgezet", wet_titel="Trade Secrets (Enforcement, etc.) Regulations 2018 (SI 2018/597)"),
    # --- Representatieve vorderingen 2020/1828 ------------------------------------------------
    O("32020L1828", "NL", None, "3:305a", "3:305e", None, opmerking="WAMCA (2020) ging aan de richtlijn vooraf; procesrecht in art. 1018b e.v. Rv"),
    O("32020L1828", "DE", None, None, None, None, wet_titel="Verbraucherrechtedurchsetzungsgesetz (VDuG, 2023)"),
    O("32020L1828", "BE", "WER", "XVII.35", "XVII.70", None, opmerking="Rechtsvordering tot collectief herstel"),
    O("32020L1828", "IT", "c. cons.", "140-ter", "140-quaterdecies", None, opmerking="d.lgs. 28/2023"),
    # --- Financiëlezekerheidsovereenkomsten 2002/47 -----------------------------------------
    O("32002L0047", "NL", None, "7:51", "7:55", None, opmerking="Titel 7.2 BW"),
    O("32002L0047", "FR", None, None, None, None, opmerking="art. L211-38 e.v.", wet_titel="Code monétaire et financier"),
    # --- Overgang van ondernemingen 2001/23 en arbeid bepaalde tijd 1999/70 ----------------------
    O("32001L0023", "NL", None, "7:662", "7:666", None),
    O("32001L0023", "DE", None, "613a", None, None),
    O("32001L0023", "FR", None, None, None, None, opmerking="art. L1224-1 e.v.", wet_titel="Code du travail"),
    O("32001L0023", "BE", None, None, None, None, wet_titel="Collectieve arbeidsovereenkomst nr. 32bis (1985)"),
    O("32001L0023", "IT", None, "2112", None, None),
    O("32001L0023", "ES", None, None, None, None, opmerking="art. 44", wet_titel="Estatuto de los Trabajadores (RDL 2/2015)"),
    O("32001L0023", "EN", None, None, None, None, soort="voortgezet", wet_titel="Transfer of Undertakings (Protection of Employment) Regulations 2006 (TUPE)"),
    O("31999L0070", "NL", None, "7:668a", None, None, opmerking="Ketenregeling"),
    O("31999L0070", "DE", None, None, None, None, opmerking="§ 14 TzBfG", wet_titel="Teilzeit- und Befristungsgesetz"),
    O("31999L0070", "IT", None, None, None, None, opmerking="art. 19–29", wet_titel="Decreto legislativo 15 giugno 2015, n. 81"),
    O("31999L0070", "ES", None, None, None, None, opmerking="art. 15", wet_titel="Estatuto de los Trabajadores (RDL 2/2015)"),
    # --- Herstructurering 2019/1023 ---------------------------------------------------------
    O("32019L1023", "NL", None, None, None, None, opmerking="Ging deels aan de richtlijn vooraf; art. 369–387 Fw", wet_titel="Wet homologatie onderhands akkoord (WHOA, 2021)"),
    O("32019L1023", "DE", None, None, None, None, wet_titel="Unternehmensstabilisierungs- und -restrukturierungsgesetz (StaRUG, 2021)"),
    O("32019L1023", "FR", None, None, None, None, wet_titel="Ordonnance n° 2021-1193 du 15 septembre 2021 (Livre VI Code de commerce)"),
    O("32019L1023", "IT", None, None, None, None, wet_titel="Codice della crisi d'impresa e dell'insolvenza (d.lgs. 14/2019, aangepast bij d.lgs. 83/2022)"),
    O("32019L1023", "ES", None, None, None, None, wet_titel="Ley 16/2022 de reforma del texto refundido de la Ley Concursal"),
    # --- Verordeningen: uitvoering en verwijzing --------------------------------------------
    O("32016R0679", "NL", None, None, None, None, "uitvoering", wet_titel="Uitvoeringswet Algemene verordening gegevensbescherming (UAVG, 2018)"),
    O("32016R0679", "DE", None, None, None, None, "uitvoering", wet_titel="Bundesdatenschutzgesetz (BDSG, 2018)"),
    O("32016R0679", "FR", None, None, None, None, "uitvoering", wet_titel="Loi n° 78-17 du 6 janvier 1978 relative à l'informatique, aux fichiers et aux libertés (herzien 2018)"),
    O("32016R0679", "BE", None, None, None, None, "uitvoering", wet_titel="Wet van 30 juli 2018 betreffende de bescherming van natuurlijke personen met betrekking tot de verwerking van persoonsgegevens"),
    O("32016R0679", "IT", None, None, None, None, "uitvoering", wet_titel="Codice in materia di protezione dei dati personali (d.lgs. 196/2003, aangepast bij d.lgs. 101/2018)"),
    O("32016R0679", "ES", None, None, None, None, "uitvoering", wet_titel="Ley Orgánica 3/2018 de Protección de Datos Personales y garantía de los derechos digitales (LOPDGDD)"),
    O("32016R0679", "EN", None, None, None, None, "voortgezet", opmerking="De verordening zelf voortgezet als 'UK GDPR'", wet_titel="Data Protection Act 2018"),
    O("32016R0679", "CH", None, None, None, None, "navolging", opmerking="Geen omzetting; herzien met het oog op de adequaatheid", wet_titel="Bundesgesetz über den Datenschutz (DSG, 2023)"),
    O("32022R2065", "DE", None, None, None, None, "uitvoering", opmerking="Bundesnetzagentur als Digital Services Coordinator", wet_titel="Digitale-Dienste-Gesetz (DDG, 2024)"),
    O("32022R2065", "FR", None, None, None, None, "uitvoering", opmerking="Arcom als coördinator digitale diensten",
      wet_titel="Loi n° 2024-449 du 21 mai 2024 visant à sécuriser et à réguler l'espace numérique (SREN)"),
    O("32022R2065", "IT", None, None, None, None, "uitvoering", opmerking="AGCOM aangewezen", wet_titel="Decreto-legge 15 settembre 2023, n. 123"),
    O("32024R1689", "IT", None, None, None, None, "uitvoering", opmerking="Aanvullende nationale regels en aanwijzing van autoriteiten (AgID, ACN)",
      wet_titel="Legge 23 settembre 2025, n. 132 (disposizioni e deleghe in materia di intelligenza artificiale)"),
    O("32008R0593", "NL", None, "10:154", None, None, "verwijzing", opmerking="Boek 10 verklaart Rome I van toepassing, ook buiten haar werkingssfeer"),
    O("32008R0593", "DE", "EGBGB", "3", None, None, "verwijzing", opmerking="Art. 3 Nr. 1 lit. b; aanvullend Art. 46b–46d EGBGB"),
    O("32007R0864", "NL", None, "10:159", None, None, "verwijzing"),
    O("32007R0864", "DE", "EGBGB", "3", None, None, "verwijzing", opmerking="Art. 3 Nr. 1 lit. a; Art. 38–42 EGBGB voor wat Rome II uitsluit"),
    O("32012R0650", "NL", None, "10:145", None, None, "verwijzing", opmerking="Titel 10.12 BW"),
    O("32012R0650", "DE", None, None, None, None, "uitvoering", wet_titel="Internationales Erbrechtsverfahrensgesetz (IntErbRVG, 2015)"),
]
