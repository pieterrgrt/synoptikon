"""Stelsels van Oost-Europa, Turkije, het Midden-Oosten en Afrika (post-Sovjet, islamitisch, gemengd, OHADA).

Zelfde vorm als `seed/stelsels.py`. De systematiek is de hoofdindeling van het burgerlijk wetboek met
artikelbereiken: met de hand uit de officiële inhoudsopgave waar geen open bron is (RU), anders uit de import.
"""

# code, naam, taal, toelichting, actief, rechtsfamilie
STELSELS = [
    ("RU", "Rusland", "ru", "Гражданский кодекс РФ (1994–2006, vier delen): naar Nederlands en Duits model, hervormd in 2013–2015; geen open bron bereikbaar (pravo.gov.ru weigert verbindingen van buiten Rusland)", True, "post_sovjet"),
    ("TR", "Turkije", "tr", "Türk Medeni Kanunu (2001) en Türk Borçlar Kanunu (2011): de Zwitserse ZGB en het OR, sinds 1926 overgenomen en vertaald; tekst van mevzuat.gov.tr, geconsolideerd", True, "germaans"),
    ("AE", "Verenigde Arabische Emiraten", "ar", "قانون المعاملات المدنية (decreet-wet 25/2025, sinds 1 juni 2026; opvolger van de wet van 1985): naar de Majalla en het Jordaanse wetboek, met de islamitische fiqh als aanvullende bron; geen tekst (uaelegislation.gov.ae blokkeert geautomatiseerde toegang via Cloudflare)", True, "islamitisch"),
]

GK_RF = [
    ("RU-1", "Часть первая", "art. 1–453", [
        ("RU-I", "Раздел I. Общие положения", "art. 1–208", [
            ("RU-I-1", "Подраздел 1. Основные положения", "art. 1–16.1", []),
            ("RU-I-2", "Подраздел 2. Лица", "art. 17–127", []),
            ("RU-I-3", "Подраздел 3. Объекты гражданских прав", "art. 128–152", []),
            ("RU-I-4", "Подраздел 4. Сделки, решения собраний и представительство", "art. 153–189", []),
            ("RU-I-5", "Подраздел 5. Сроки. Исковая давность", "art. 190–208", []),
        ]),
        ("RU-II", "Раздел II. Право собственности и другие вещные права", "art. 209–306", []),
        ("RU-III", "Раздел III. Общая часть обязательственного права", "art. 307–453", [
            ("RU-III-1", "Подраздел 1. Общие положения об обязательствах", "art. 307–419", []),
            ("RU-III-2", "Подраздел 2. Общие положения о договоре", "art. 420–453", []),
        ]),
    ]),
    ("RU-2", "Часть вторая", "art. 454–1109", [
        ("RU-IV", "Раздел IV. Отдельные виды обязательств", "art. 454–1109", []),
    ]),
    ("RU-3", "Часть третья", "art. 1110–1224", [
        ("RU-V", "Раздел V. Наследственное право", "art. 1110–1185", []),
        ("RU-VI", "Раздел VI. Международное частное право", "art. 1186–1224", []),
    ]),
    ("RU-4", "Часть четвертая", "art. 1225–1551", [
        ("RU-VII", "Раздел VII. Права на результаты интеллектуальной деятельности и средства индивидуализации", "art. 1225–1551", []),
    ]),
]

# Uit de import van mevzuat.gov.tr (TMK stand 2027-06-30, TBK stand 2026-07-31); het TBK draagt wet "TBK".
TMK = [
    ("TR-0", "Başlangıç", "art. 1–7", []),
    ("TR-1", "Birinci Kitap · Kişiler Hukuku", "art. 8–117", [
        ("TR-1-1", "Birinci Kısım · Gerçek Kişiler", "art. 8–46", []),
        ("TR-1-2", "İkinci Kısım · Tüzel Kişiler", "art. 47–117", []),
    ]),
    ("TR-2", "İkinci Kitap · Aile Hukuku", "art. 118–494", [
        ("TR-2-1", "Birinci Kısım · Evlilik Hukuku", "art. 118–281", []),
        ("TR-2-2", "İkinci Kısım · Hısımlık", "art. 282–395", []),
        ("TR-2-3", "Üçüncü Kısım · Vesayet", "art. 396–494", []),
    ]),
    ("TR-3", "Üçüncü Kitap · Miras Hukuku", "art. 495–682", [
        ("TR-3-1", "Birinci Kısım · Mirasçılar", "art. 495–574", []),
        ("TR-3-2", "İkinci Kısım · Mirasın Geçmesi", "art. 575–682", []),
    ]),
    ("TR-4", "Dördüncü Kitap · Eşya Hukuku", "art. 683–1030", [
        ("TR-4-1", "Birinci Kısım · Mülkiyet", "art. 683–778", []),
        ("TR-4-2", "İkinci Kısım · Sınırlı Aynî Haklar", "art. 779–972", []),
        ("TR-4-3", "Üçüncü Kısım · Zilyetlik ve Tapu Sicili", "art. 973–1030", []),
    ]),
    ("TR-TBK", "Türk Borçlar Kanunu (TBK, 6098)", "art. 1–649", [
        ("TBK-1", "Birinci Kısım · Genel Hükümler", "art. 1–206", []),
        ("TBK-2", "İkinci Kısım · Özel Borç İlişkileri", "art. 207–649", []),
    ], "TBK"),
]

# Hoofdindeling van de nieuwe wet (decreet-wet 25/2025), volgens een overzicht van lylawyers.com; de officiële
# inhoudsopgave was niet bereikbaar. Aanvullen zodra er een tekstbron is.
CTL_AE = [
    ("AE-0", "الباب التمهيدي · Inleidende bepalingen", "art. 1–98", []),
    ("AE-1", "الكتاب الأول · الالتزامات (verbintenissen)", "art. 99–444", []),
    ("AE-2", "الكتاب الثاني · العقود المسماة (benoemde contracten)", "art. 445–1035", []),
    ("AE-3", "الكتاب الثالث · الحقوق العينية (zakelijke rechten)", "art. 1036–1295", []),
    ("AE-4", "الكتاب الرابع · التأمينات العينية (zakelijke zekerheden)", "art. 1296–1422", []),
]

SYSTEMATIEK = {
    "RU": GK_RF,
    "TR": TMK,
    "AE": CTL_AE,
}
