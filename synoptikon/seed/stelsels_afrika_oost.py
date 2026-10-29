"""Stelsels van Oost-Europa, Turkije, het Midden-Oosten en Afrika (post-Sovjet, islamitisch, gemengd, OHADA).

Zelfde vorm als `seed/stelsels.py`. De systematiek is de hoofdindeling van het burgerlijk wetboek met
artikelbereiken: met de hand uit de officiële inhoudsopgave waar geen open bron is (RU), anders uit de import.
"""

# code, naam, taal, toelichting, actief, rechtsfamilie
STELSELS = [
    ("RU", "Rusland", "ru", "Гражданский кодекс РФ (1994–2006, vier delen): naar Nederlands en Duits model, hervormd in 2013–2015; geen open bron bereikbaar (pravo.gov.ru weigert verbindingen van buiten Rusland)", True, "post_sovjet"),
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

SYSTEMATIEK = {
    "RU": GK_RF,
}
