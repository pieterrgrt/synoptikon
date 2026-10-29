"""Systematiek van de Code civil du Québec (C.c.Q., L.Q. 1991, c. 64, in werking sinds 1 januari 1994): Livre › Titre.

Gegenereerd uit de geconsolideerde XML van Données Québec (stand september 2026). De bereiken zijn het laagste en
hoogste artikelnummer per eenheid; ingevoegde artikelen dragen een punt (521.1, 2874.1). Koppen zoals in de bron.
De andere wetten (Code de procédure civile, Loi sur la protection du consommateur, Charte) krijgen hun boom uit de
import.
"""

CCQ = [
    ('QC-1', 'LIVRE PREMIER · DES PERSONNES', 'art. 1–364', [
        ('QC-1-1', 'TITRE PREMIER · DE LA JOUISSANCE ET DE L’EXERCICE DES DROITS CIVILS', 'art. 1–9', []),
        ('QC-1-2', 'TITRE DEUXIÈME · DE CERTAINS DROITS DE LA PERSONNALITÉ', 'art. 10–49', []),
        ('QC-1-3', 'TITRE TROISIÈME · DE CERTAINS ÉLÉMENTS RELATIFS À L’ÉTAT DES PERSONNES', 'art. 50–152.1', []),
        ('QC-1-4', 'TITRE QUATRIÈME · DE LA CAPACITÉ DES PERSONNES', 'art. 153–297.27', []),
        ('QC-1-5', 'TITRE CINQUIÈME · DES PERSONNES MORALES', 'art. 298–364', []),
    ]),
    ('QC-2', 'LIVRE DEUXIÈME · DE LA FAMILLE', 'art. 365–612', [
        ('QC-2-1', 'TITRE PREMIER · DU MARIAGE', 'art. 365–521', []),
        ('QC-2-2', 'TITRE PREMIER.1 · DE L’UNION CIVILE', 'art. 521.1–521.19', []),
        ('QC-2-3', 'TITRE PREMIER.2 · DE L’UNION PARENTALE', 'art. 521.20–521.47', []),
        ('QC-2-4', 'TITRE DEUXIÈME · DE LA FILIATION', 'art. 522–584.1', []),
        ('QC-2-5', 'TITRE TROISIÈME · DE L’OBLIGATION ALIMENTAIRE', 'art. 585–596.1', []),
        ('QC-2-6', 'TITRE QUATRIÈME · DE L’AUTORITÉ PARENTALE', 'art. 597–612', []),
    ]),
    ('QC-3', 'LIVRE TROISIÈME · DES SUCCESSIONS', 'art. 613–898', [
        ('QC-3-1', 'TITRE PREMIER · DE L’OUVERTURE DES SUCCESSIONS ET DES QUALITÉS REQUISES POUR SUCCÉDER', 'art. 613–624', []),
        ('QC-3-2', 'TITRE DEUXIÈME · DE LA TRANSMISSION DE LA SUCCESSION', 'art. 625–652', []),
        ('QC-3-3', 'TITRE TROISIÈME · DE LA DÉVOLUTION LÉGALE DES SUCCESSIONS', 'art. 653–702', []),
        ('QC-3-4', 'TITRE QUATRIÈME · DES TESTAMENTS', 'art. 703–775', []),
        ('QC-3-5', 'TITRE CINQUIÈME · DE LA LIQUIDATION DE LA SUCCESSION', 'art. 776–835', []),
        ('QC-3-6', 'TITRE SIXIÈME · DU PARTAGE DE LA SUCCESSION', 'art. 836–898', []),
    ]),
    ('QC-4', 'LIVRE QUATRIÈME · DES BIENS', 'art. 898.1–1370', [
        ('QC-4-1', 'DISPOSITION GÉNÉRALE', 'art. 898.1', []),
        ('QC-4-2', 'TITRE PREMIER · DE LA DISTINCTION DES BIENS ET DE LEUR APPROPRIATION', 'art. 899–946', []),
        ('QC-4-3', 'TITRE DEUXIÈME · DE LA PROPRIÉTÉ', 'art. 947–1008', []),
        ('QC-4-4', 'TITRE TROISIÈME · DES MODALITÉS DE LA PROPRIÉTÉ', 'art. 1009–1118', []),
        ('QC-4-5', 'TITRE QUATRIÈME · DES DÉMEMBREMENTS DU DROIT DE PROPRIÉTÉ', 'art. 1119–1211', []),
        ('QC-4-6', 'TITRE CINQUIÈME · DES RESTRICTIONS À LA LIBRE DISPOSITION DE CERTAINS BIENS', 'art. 1212–1255', []),
        ('QC-4-7', 'TITRE SIXIÈME · DE CERTAINS PATRIMOINES D’AFFECTATION', 'art. 1256–1298', []),
        ('QC-4-8', 'TITRE SEPTIÈME · DE L’ADMINISTRATION DU BIEN D’AUTRUI', 'art. 1299–1370', []),
    ]),
    ('QC-5', 'LIVRE CINQUIÈME · DES OBLIGATIONS', 'art. 1371–2643', [
        ('QC-5-1', 'TITRE PREMIER · DES OBLIGATIONS EN GÉNÉRAL', 'art. 1371–1707', []),
        ('QC-5-2', 'TITRE DEUXIÈME · DES CONTRATS NOMMÉS', 'art. 1708–2643', []),
    ]),
    ('QC-6', 'LIVRE SIXIÈME · DES PRIORITÉS ET DES HYPOTHÈQUES', 'art. 2644–2802', [
        ('QC-6-1', 'TITRE PREMIER · DU GAGE COMMUN DES CRÉANCIERS', 'art. 2644–2649', []),
        ('QC-6-2', 'TITRE DEUXIÈME · DES PRIORITÉS', 'art. 2650–2659', []),
        ('QC-6-3', 'TITRE TROISIÈME · DES HYPOTHÈQUES', 'art. 2660–2802', []),
    ]),
    ('QC-7', 'LIVRE SEPTIÈME · DE LA PREUVE', 'art. 2803–2874.1', [
        ('QC-7-1', 'TITRE PREMIER · DU RÉGIME GÉNÉRAL DE LA PREUVE', 'art. 2803–2810', []),
        ('QC-7-2', 'TITRE DEUXIÈME · DES MOYENS DE PREUVE', 'art. 2811–2856', []),
        ('QC-7-3', 'TITRE TROISIÈME · DE LA RECEVABILITÉ DES ÉLÉMENTS ET DES MOYENS DE PREUVE', 'art. 2857–2874.1', []),
    ]),
    ('QC-8', 'LIVRE HUITIÈME · DE LA PRESCRIPTION', 'art. 2875–2933', [
        ('QC-8-1', 'TITRE PREMIER · DU RÉGIME DE LA PRESCRIPTION', 'art. 2875–2909', []),
        ('QC-8-2', 'TITRE DEUXIÈME · DE LA PRESCRIPTION ACQUISITIVE', 'art. 2910–2920', []),
        ('QC-8-3', 'TITRE TROISIÈME · DE LA PRESCRIPTION EXTINCTIVE', 'art. 2921–2933', []),
    ]),
    ('QC-9', 'LIVRE NEUVIÈME · DE LA PUBLICITÉ DES DROITS', 'art. 2934–3075.1', [
        ('QC-9-1', 'TITRE PREMIER · DU DOMAINE DE LA PUBLICITÉ', 'art. 2934–2940', []),
        ('QC-9-2', 'TITRE DEUXIÈME · DES EFFETS DE LA PUBLICITÉ', 'art. 2941–2968', []),
        ('QC-9-3', 'TITRE TROISIÈME · DES MODALITÉS DE LA PUBLICITÉ', 'art. 2969–3025', []),
        ('QC-9-4', 'TITRE QUATRIÈME · DE L’IMMATRICULATION DES IMMEUBLES', 'art. 3026–3056', []),
        ('QC-9-5', 'TITRE CINQUIÈME · DE LA RADIATION', 'art. 3057–3075.1', []),
    ]),
    ('QC-10', 'LIVRE DIXIÈME · DU DROIT INTERNATIONAL PRIVÉ', 'art. 3076–3168', [
        ('QC-10-1', 'TITRE PREMIER · DISPOSITIONS GÉNÉRALES', 'art. 3076–3082', []),
        ('QC-10-2', 'TITRE DEUXIÈME · DES CONFLITS DE LOIS', 'art. 3083–3133', []),
        ('QC-10-3', 'TITRE TROISIÈME · DE LA COMPÉTENCE INTERNATIONALE DES AUTORITÉS DU QUÉBEC', 'art. 3134–3154', []),
        ('QC-10-4', 'TITRE QUATRIÈME · DE LA RECONNAISSANCE ET DE L’EXÉCUTION DES DÉCISIONS ÉTRANGÈRES ET DE LA COMPÉTENCE DES AUTORITÉS ÉTRANGÈRES', 'art. 3155–3168', []),
    ]),
]

QC = [
    *CCQ,
    ('QC-CPC', 'Code de procédure civile (RLRQ, c. C-25.01, 2016)', '', [], 'C.p.c.'),
    ('QC-LPC', 'Loi sur la protection du consommateur (RLRQ, c. P-40.1)', '', [], 'L.p.c.'),
    ('QC-CHARTE', 'Charte des droits et libertés de la personne (RLRQ, c. C-12)', '', [], 'Charte québécoise'),
]
