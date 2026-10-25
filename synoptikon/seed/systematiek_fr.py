"""Systematiek van de Code civil: Livre › Titre › (Sous-titre) › Chapitre › Section › Sous-section.

Alle titres van de vijf boeken, met de structuur na de hervorming van het
verbintenissenrecht (ordonnance n° 2016-131), de verjaringshervorming van
2008 en de zekerhedenhervorming van 2021. Het verbintenissenrecht (Livre III,
Titres III, IV en IV bis), de koop en de bezitsregels zijn tot op
sous-sectionniveau uitgewerkt. `synoptikon systematiek fr LEGITEXT000006070721`
vult de rest aan uit een Légifrance-import.

Gecontroleerd tegen de artikelenlijst van de LEGI-database van de DILA
(stand 16-09-2026, via een niet-officieel extract): alle grensartikelen
bestaan en geen geldend artikel valt buiten de boom. De namen van de
titres en secties zijn daarmee níet gecontroleerd; de LEGI-indeling zelf
kwam via Légifrance (Cloudflare) en de PISTE-API niet binnen.
"""

CC = [
    ("CC-TP", "Titre préliminaire · De la publication, des effets et de l'application des lois en général", "art. 1–6-2", []),
    ("CC-I", "Livre Ier · Des personnes", "art. 7–515-13-1", [
        ("CC-I-I", "Titre Ier · Des droits civils", "art. 7–16-14", []),
        ("CC-I-Ibis", "Titre Ier bis · De la nationalité française", "art. 17–33-2", []),
        ("CC-I-II", "Titre II · Des actes de l'état civil", "art. 34–101-2", []),
        ("CC-I-III", "Titre III · Du domicile", "art. 102–111", []),
        ("CC-I-IV", "Titre IV · Des absents", "art. 112–132", []),
        ("CC-I-V", "Titre V · Du mariage", "art. 143–227", []),
        ("CC-I-VI", "Titre VI · Du divorce", "art. 229–309", []),
        ("CC-I-VII", "Titre VII · De la filiation", "art. 310-1–342-13", []),
        ("CC-I-VIII", "Titre VIII · De la filiation adoptive", "art. 343–370-5", []),
        ("CC-I-IX", "Titre IX · De l'autorité parentale", "art. 371–387-6", []),
        ("CC-I-X", "Titre X · De la minorité et de l'émancipation", "art. 388–413-8", []),
        ("CC-I-XI", "Titre XI · De la majorité et des majeurs protégés par la loi", "art. 414–495-9", []),
        ("CC-I-XII", "Titre XII · De la gestion du patrimoine des mineurs et majeurs en tutelle", "art. 496–515", []),
        ("CC-I-XIII", "Titre XIII · Du pacte civil de solidarité et du concubinage", "art. 515-1–515-8", []),
        ("CC-I-XIV", "Titre XIV · Des mesures de protection des victimes de violences", "art. 515-9–515-13-1", []),
    ]),
    ("CC-II", "Livre II · Des biens et des différentes modifications de la propriété", "art. 515-14–710-1", [
        ("CC-II-I", "Titre Ier · De la distinction des biens", "art. 516–543", []),
        ("CC-II-II", "Titre II · De la propriété", "art. 544–577", [
            ("CC-II-II-I", "Chapitre Ier · Du droit d'accession sur ce qui est produit par la chose", "art. 547–550", []),
            ("CC-II-II-II", "Chapitre II · Du droit d'accession sur ce qui s'unit et s'incorpore à la chose", "art. 551–577", []),
        ]),
        ("CC-II-III", "Titre III · De l'usufruit, de l'usage et de l'habitation", "art. 578–636", []),
        ("CC-II-IV", "Titre IV · Des servitudes ou services fonciers", "art. 637–710", []),
        ("CC-II-V", "Titre V · De la publicité foncière", "art. 710-1", []),
    ]),
    ("CC-III", "Livre III · Des différentes manières dont on acquiert la propriété", "art. 711–2278", [
        ("CC-III-DG", "Dispositions générales", "art. 711–717", []),
        ("CC-III-I", "Titre Ier · Des successions", "art. 720–892", []),
        ("CC-III-II", "Titre II · Des libéralités", "art. 893–1099-1", []),
        ("CC-III-III", "Titre III · Des sources d'obligations", "art. 1100–1303-4", [
            ("CC-III-III-I", "Sous-titre Ier · Le contrat", "art. 1101–1231-7", [
                ("CC-III-III-I-1", "Chapitre Ier · Dispositions liminaires", "art. 1101–1111-1", []),
                ("CC-III-III-I-2", "Chapitre II · La formation du contrat", "art. 1112–1187", [
                    ("CC-III-III-I-2-1", "Section 1 · La conclusion du contrat", "art. 1112–1127-4", [
                        ("CC-III-III-I-2-1-1", "Sous-section 1 · Les négociations", "art. 1112–1112-2", []),
                        ("CC-III-III-I-2-1-2", "Sous-section 2 · L'offre et l'acceptation", "art. 1113–1122", []),
                        ("CC-III-III-I-2-1-3", "Sous-section 3 · Le pacte de préférence et la promesse unilatérale", "art. 1123–1124", []),
                        ("CC-III-III-I-2-1-4", "Sous-section 4 · Dispositions propres au contrat conclu par voie électronique", "art. 1125–1127-4", []),
                    ]),
                    ("CC-III-III-I-2-2", "Section 2 · La validité du contrat", "art. 1128–1171", [
                        ("CC-III-III-I-2-2-1", "Sous-section 1 · Le consentement", "art. 1129–1144", []),
                        ("CC-III-III-I-2-2-2", "Sous-section 2 · La capacité et la représentation", "art. 1145–1161", []),
                        ("CC-III-III-I-2-2-3", "Sous-section 3 · Le contenu du contrat", "art. 1162–1171", []),
                    ]),
                    ("CC-III-III-I-2-3", "Section 3 · La forme du contrat", "art. 1172–1177", []),
                    ("CC-III-III-I-2-4", "Section 4 · Les sanctions", "art. 1178–1187", [
                        ("CC-III-III-I-2-4-1", "Sous-section 1 · La nullité", "art. 1178–1185", []),
                        ("CC-III-III-I-2-4-2", "Sous-section 2 · La caducité", "art. 1186–1187", []),
                    ]),
                ]),
                ("CC-III-III-I-3", "Chapitre III · L'interprétation du contrat", "art. 1188–1192", []),
                ("CC-III-III-I-4", "Chapitre IV · Les effets du contrat", "art. 1193–1231-7", [
                    ("CC-III-III-I-4-1", "Section 1 · Les effets du contrat entre les parties", "art. 1193–1198", [
                        ("CC-III-III-I-4-1-1", "Sous-section 1 · Force obligatoire", "art. 1193–1195", []),
                        ("CC-III-III-I-4-1-2", "Sous-section 2 · Effet translatif", "art. 1196–1198", []),
                    ]),
                    ("CC-III-III-I-4-2", "Section 2 · Les effets du contrat à l'égard des tiers", "art. 1199–1209", []),
                    ("CC-III-III-I-4-3", "Section 3 · La durée du contrat", "art. 1210–1215", []),
                    ("CC-III-III-I-4-4", "Section 4 · La cession de contrat", "art. 1216–1216-3", []),
                    ("CC-III-III-I-4-5", "Section 5 · L'inexécution du contrat", "art. 1217–1231-7", [
                        ("CC-III-III-I-4-5-1", "Sous-section 1 · L'exception d'inexécution", "art. 1219–1220", []),
                        ("CC-III-III-I-4-5-2", "Sous-section 2 · L'exécution forcée en nature", "art. 1221–1222", []),
                        ("CC-III-III-I-4-5-3", "Sous-section 3 · La réduction du prix", "art. 1223", []),
                        ("CC-III-III-I-4-5-4", "Sous-section 4 · La résolution", "art. 1224–1230", []),
                        ("CC-III-III-I-4-5-5", "Sous-section 5 · La réparation du préjudice résultant de l'inexécution du contrat", "art. 1231–1231-7", []),
                    ]),
                ]),
            ]),
            ("CC-III-III-II", "Sous-titre II · La responsabilité extracontractuelle", "art. 1240–1252", [
                ("CC-III-III-II-1", "Chapitre Ier · La responsabilité extracontractuelle en général", "art. 1240–1244", []),
                ("CC-III-III-II-2", "Chapitre II · La responsabilité du fait des produits défectueux", "art. 1245–1245-17", []),
                ("CC-III-III-II-3", "Chapitre III · La réparation du préjudice écologique", "art. 1246–1252", []),
            ]),
            ("CC-III-III-III", "Sous-titre III · Autres sources d'obligations", "art. 1300–1303-4", [
                ("CC-III-III-III-1", "Chapitre Ier · La gestion d'affaires", "art. 1301–1301-5", []),
                ("CC-III-III-III-2", "Chapitre II · Le paiement de l'indu", "art. 1302–1302-3", []),
                ("CC-III-III-III-3", "Chapitre III · L'enrichissement injustifié", "art. 1303–1303-4", []),
            ]),
        ]),
        ("CC-III-IV", "Titre IV · Du régime général des obligations", "art. 1304–1352-9", [
            ("CC-III-IV-1", "Chapitre Ier · Les modalités de l'obligation", "art. 1304–1320", [
                ("CC-III-IV-1-1", "Section 1 · L'obligation conditionnelle", "art. 1304–1304-7", []),
                ("CC-III-IV-1-2", "Section 2 · L'obligation à terme", "art. 1305–1305-5", []),
                ("CC-III-IV-1-3", "Section 3 · L'obligation plurale", "art. 1306–1320", []),
            ]),
            ("CC-III-IV-2", "Chapitre II · Les opérations sur obligations", "art. 1321–1340", [
                ("CC-III-IV-2-1", "Section 1 · La cession de créance", "art. 1321–1326", []),
                ("CC-III-IV-2-2", "Section 2 · La cession de dette", "art. 1327–1328-1", []),
                ("CC-III-IV-2-3", "Section 3 · La novation", "art. 1329–1335", []),
                ("CC-III-IV-2-4", "Section 4 · La délégation", "art. 1336–1340", []),
            ]),
            ("CC-III-IV-3", "Chapitre III · Les actions ouvertes au créancier", "art. 1341–1341-3", []),
            ("CC-III-IV-4", "Chapitre IV · L'extinction de l'obligation", "art. 1342–1351-1", [
                ("CC-III-IV-4-1", "Section 1 · Le paiement", "art. 1342–1346-5", []),
                ("CC-III-IV-4-2", "Section 2 · La compensation", "art. 1347–1348-2", []),
                ("CC-III-IV-4-3", "Section 3 · La confusion", "art. 1349–1349-1", []),
                ("CC-III-IV-4-4", "Section 4 · La remise de dette", "art. 1350–1350-2", []),
                ("CC-III-IV-4-5", "Section 5 · L'impossibilité d'exécuter", "art. 1351–1351-1", []),
            ]),
            ("CC-III-IV-5", "Chapitre V · Les restitutions", "art. 1352–1352-9", []),
        ]),
        ("CC-III-IVbis", "Titre IV bis · De la preuve des obligations", "art. 1353–1386-1", []),
        ("CC-III-V", "Titre V · Du contrat de mariage et des régimes matrimoniaux", "art. 1387–1581", []),
        ("CC-III-VI", "Titre VI · De la vente", "art. 1582–1701-1", [
            ("CC-III-VI-I", "Chapitre Ier · De la nature et de la forme de la vente", "art. 1582–1593", []),
            ("CC-III-VI-II", "Chapitre II · Qui peut acheter ou vendre", "art. 1594–1597", []),
            ("CC-III-VI-III", "Chapitre III · Des choses qui peuvent être vendues", "art. 1598–1601", []),
            ("CC-III-VI-IV", "Chapitre IV · Des obligations du vendeur", "art. 1602–1649", [
                ("CC-III-VI-IV-1", "Section 1 · Dispositions générales", "art. 1602–1603", []),
                ("CC-III-VI-IV-2", "Section 2 · De la délivrance", "art. 1604–1624", []),
                ("CC-III-VI-IV-3", "Section 3 · De la garantie", "art. 1625–1649", []),
            ]),
            ("CC-III-VI-V", "Chapitre V · Des obligations de l'acheteur", "art. 1650–1657", []),
            ("CC-III-VI-VI", "Chapitre VI · De la nullité et de la résolution de la vente", "art. 1658–1685", []),
            ("CC-III-VI-VIII", "Chapitre VIII · Du transport des créances et autres droits incorporels", "art. 1689–1701-1", []),
        ]),
        ("CC-III-VII", "Titre VII · De l'échange", "art. 1702–1707", []),
        ("CC-III-VIII", "Titre VIII · Du contrat de louage", "art. 1708–1831", []),
        ("CC-III-VIIIbis", "Titre VIII bis · Du contrat de promotion immobilière", "art. 1831-1–1831-5", []),
        ("CC-III-IX", "Titre IX · De la société", "art. 1832–1873", []),
        ("CC-III-IXbis", "Titre IX bis · Des conventions relatives à l'exercice des droits indivis", "art. 1873-1–1873-18", []),
        ("CC-III-X", "Titre X · Du prêt", "art. 1874–1914", []),
        ("CC-III-XI", "Titre XI · Du dépôt et du séquestre", "art. 1915–1963", []),
        ("CC-III-XII", "Titre XII · Des contrats aléatoires", "art. 1965–1983", []),
        ("CC-III-XIII", "Titre XIII · Du mandat", "art. 1984–2010", []),
        ("CC-III-XIV", "Titre XIV · De la fiducie", "art. 2011–2030", []),
        ("CC-III-XV", "Titre XV · Des transactions", "art. 2044–2052", []),
        ("CC-III-XVI", "Titre XVI · De la convention d'arbitrage", "art. 2059–2061", []),
        ("CC-III-XVII", "Titre XVII · De la convention de procédure participative", "art. 2062–2068", []),
        ("CC-III-XX", "Titre XX · De la prescription extinctive", "art. 2219–2254", [
            ("CC-III-XX-I", "Chapitre Ier · Dispositions générales", "art. 2219–2223", []),
            ("CC-III-XX-II", "Chapitre II · Des délais et du point de départ de la prescription extinctive", "art. 2224–2227", []),
            ("CC-III-XX-III", "Chapitre III · Du cours de la prescription extinctive", "art. 2228–2246", []),
            ("CC-III-XX-IV", "Chapitre IV · Des conditions de la prescription extinctive", "art. 2247–2254", []),
        ]),
        ("CC-III-XXI", "Titre XXI · De la possession et de la prescription acquisitive", "art. 2255–2278", [
            ("CC-III-XXI-I", "Chapitre Ier · Dispositions générales", "art. 2255–2257", []),
            ("CC-III-XXI-II", "Chapitre II · De la prescription acquisitive", "art. 2258–2277", [
                ("CC-III-XXI-II-1", "Section 1 · Dispositions générales", "art. 2258–2271", []),
                ("CC-III-XXI-II-2", "Section 2 · De la prescription acquisitive en matière immobilière", "art. 2272–2275", []),
                ("CC-III-XXI-II-3", "Section 3 · De la prescription acquisitive en matière mobilière", "art. 2276–2277", []),
            ]),
            ("CC-III-XXI-III", "Chapitre III · De la protection possessoire", "art. 2278", []),
        ]),
    ]),
    ("CC-IV", "Livre IV · Des sûretés", "art. 2284–2488-12", [
        ("CC-IV-DG", "Dispositions générales", "art. 2284–2287", []),
        ("CC-IV-I", "Titre Ier · Des sûretés personnelles", "art. 2287-1–2322", []),
        ("CC-IV-II", "Titre II · Des sûretés réelles", "art. 2323–2488-12", []),
    ]),
    ("CC-V", "Livre V · Dispositions applicables à Mayotte", "art. 2489–2534", []),
]

# Codes die in eerdere versies van de voorbeeldinhoud een andere betekenis
# hadden. De seed hernoemt ze voordat de boom wordt bijgewerkt.
HERNOEMD = {
    "CC-III-XXI-III-3": "CC-III-XXI-II-3",  # sectie mobiliaire verjaring hoort in Chapitre II
}
