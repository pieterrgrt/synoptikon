"""Stelsels van Oost-Europa, Turkije, het Midden-Oosten en Afrika (post-Sovjet, islamitisch, gemengd, OHADA).

Zelfde vorm als `seed/stelsels.py`. De systematiek is de hoofdindeling van het burgerlijk wetboek met
artikelbereiken: met de hand uit de officiële inhoudsopgave waar geen open bron is (RU), anders uit de import.
"""

# code, naam, taal, toelichting, actief, rechtsfamilie
STELSELS = [
    ("RU", "Rusland", "ru", "Гражданский кодекс РФ (1994–2006, vier delen): naar Nederlands en Duits model, hervormd in 2013–2015; geen open bron bereikbaar (pravo.gov.ru weigert verbindingen van buiten Rusland)", True, "post_sovjet"),
    ("TR", "Turkije", "tr", "Türk Medeni Kanunu (2001) en Türk Borçlar Kanunu (2011): de Zwitserse ZGB en het OR, sinds 1926 overgenomen en vertaald; tekst van mevzuat.gov.tr, geconsolideerd", True, "germaans"),
    ("AE", "Verenigde Arabische Emiraten", "ar", "قانون المعاملات المدنية (decreet-wet 25/2025, sinds 1 juni 2026; opvolger van de wet van 1985): naar de Majalla en het Jordaanse wetboek, met de islamitische fiqh als aanvullende bron; geen tekst (uaelegislation.gov.ae blokkeert geautomatiseerde toegang via Cloudflare)", True, "islamitisch"),
    ("ZA", "Zuid-Afrika", "en", "Geen codificatie: Romeins-Hollands gemeen recht met Engelse invloed, getoetst aan de Grondwet van 1996; geen tekst (SAFLII en lawlibrary.org.za staan achter een Cloudflare-controle)", True, "gemengd"),
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

# Zuid-Afrika: geen burgerlijk wetboek; zoals bij EN ordent de boom de wetten per rubriek. Hoofdstukken van de
# Grondwet uit de officiële tekst (sections), de Consumer Protection Act alleen met zijn eerste twee hoofdstukken.
ZA = [
    ("ZA-CONST", "Constitution of the Republic of South Africa, 1996", "ss 1–243", [
        ("ZA-CONST-1", "Chapter 1 · Founding Provisions", "ss 1–6", []),
        ("ZA-CONST-2", "Chapter 2 · Bill of Rights", "ss 7–39", []),
        ("ZA-CONST-3", "Chapter 3 · Co-operative Government", "ss 40–41", []),
        ("ZA-CONST-4", "Chapter 4 · Parliament", "ss 42–82", []),
        ("ZA-CONST-5", "Chapter 5 · The President and National Executive", "ss 83–102", []),
        ("ZA-CONST-6", "Chapter 6 · Provinces", "ss 103–150", []),
        ("ZA-CONST-7", "Chapter 7 · Local Government", "ss 151–164", []),
        ("ZA-CONST-8", "Chapter 8 · Courts and Administration of Justice", "ss 165–180", []),
        ("ZA-CONST-9", "Chapter 9 · State Institutions Supporting Constitutional Democracy", "ss 181–194", []),
        ("ZA-CONST-10", "Chapter 10 · Public Administration", "ss 195–197", []),
        ("ZA-CONST-11", "Chapter 11 · Security Services", "ss 198–210", []),
        ("ZA-CONST-12", "Chapter 12 · Traditional Leaders", "ss 211–212", []),
        ("ZA-CONST-13", "Chapter 13 · Finance", "ss 213–230A", []),
        ("ZA-CONST-14", "Chapter 14 · General Provisions", "ss 231–243", []),
    ], "Constitution 1996"),
    ("ZA-CONTRACT", "Contract en consument (het contractenrecht zelf is ongecodificeerd gemeen recht)", "", [
        ("ZA-CPA2008", "Consumer Protection Act 68 of 2008", "", [
            ("ZA-CPA2008-1", "Chapter 1 · Interpretation, Purpose and Application", "ss 1–7", []),
            ("ZA-CPA2008-2", "Chapter 2 · Fundamental Consumer Rights", "ss 8–67", []),
        ], "CPA 2008"),
    ]),
]

# Uit de import van mevzuat.gov.tr (stand 2027-06-30 resp. 2026-07-31): Kitap › Kısım, voor de TBK Kısım › Bölüm.
TMK = [
    ("TR-0", "BAŞLANGIÇ", "art. 1–7", []),
    ("TR-1", "BİRİNCİ KİTAP · KİŞİLER HUKUKU", "art. 8–117", [
        ("TR-1-1", "BİRİNCİ KISIM · GERÇEK KİŞİLER", "art. 8–46", []),
        ("TR-1-2", "İKİNCİ KISIM · TÜZEL KİŞİLER", "art. 47–117", []),
    ]),
    ("TR-2", "İKİNCİ KİTAP · AİLE HUKUKU", "art. 118–494", [
        ("TR-2-1", "BİRİNCİ KISIM · EVLİLİK HUKUKU", "art. 118–281", []),
        ("TR-2-2", "İKİNCİ KISIM · HISIMLIK", "art. 282–395", []),
        ("TR-2-3", "ÜÇÜNCÜ KISIM · VESAYET", "art. 396–494", []),
    ]),
    ("TR-3", "ÜÇÜNCÜ KİTAP · MİRAS HUKUKU", "art. 495–682", [
        ("TR-3-1", "BİRİNCİ KISIM · MİRASÇILAR", "art. 495–574", []),
        ("TR-3-2", "İKİNCİ KISIM · MİRASIN GEÇMESİ", "art. 575–682", []),
    ]),
    ("TR-4", "DÖRDÜNCÜ KİTAP · EŞYA HUKUKU", "art. 683–1030", [
        ("TR-4-1", "BİRİNCİ KISIM · MÜLKİYET", "art. 683–778", []),
        ("TR-4-2", "İKİNCİ KISIM · SINIRLI AYNÎ HAKLAR", "art. 779–972", []),
        ("TR-4-3", "ÜÇÜNCÜ KISIM · ZİLYETLİK VE TAPU SİCİLİ", "art. 973–1030", []),
    ]),
    ("TR-TBK", "Türk Borçlar Kanunu", "art. 1–649", [
        ("TR-TBK-1", "BİRİNCİ KISIM · Genel Hükümler", "art. 1–206", [
            ("TR-TBK-1-1", "BİRİNCİ BÖLÜM · Borç İlişkisinin Kaynakları", "art. 1–82", []),
            ("TR-TBK-1-2", "İKİNCİ BÖLÜM · Borç İlişkisinin Hükümleri", "art. 83–130", []),
            ("TR-TBK-1-3", "ÜÇÜNCÜ BÖLÜM · Borçların ve Borç İlişkilerinin Sona Ermesi, Zamanaşımı", "art. 131–161", []),
            ("TR-TBK-1-4", "DÖRDÜNCÜ BÖLÜM · Borç İlişkilerinde Özel Durumlar", "art. 162–182", []),
            ("TR-TBK-1-5", "BEŞİNCİ BÖLÜM · Borç İlişkilerinde Taraf Değişiklikleri", "art. 183–206", []),
        ]),
        ("TR-TBK-2", "İKİNCİ KISIM · Özel Borç İlişkileri", "art. 207–649", [
            ("TR-TBK-2-1", "BİRİNCİ BÖLÜM · Satış Sözleşmesi", "art. 207–281", []),
            ("TR-TBK-2-4", "DÖRDÜNCÜ BÖLÜM · Kira Sözleşmesi", "art. 299–378", []),
            ("TR-TBK-2-6", "ALTINCI BÖLÜM · Hizmet Sözleşmeleri", "art. 393–469", []),
            ("TR-TBK-2-7", "YEDİNCİ BÖLÜM · Eser Sözleşmesi", "art. 470–486", []),
            ("TR-TBK-2-9", "DOKUZUNCU BÖLÜM · Vekâlet İlişkileri", "art. 502–525", []),
            ("TR-TBK-2-15", "ONBEŞİNCİ BÖLÜM · Kefalet Sözleşmesi", "art. 581–603", []),
            ("TR-TBK-2-18", "ONSEKİZİNCİ BÖLÜM · Adi Ortaklık Sözleşmesi", "art. 620–649", []),
        ]),
    ], "TBK"),
]

SYSTEMATIEK = {
    "RU": GK_RF,
    "TR": TMK,
    "TR": TMK,
    "AE": CTL_AE,
    "ZA": ZA,
}
