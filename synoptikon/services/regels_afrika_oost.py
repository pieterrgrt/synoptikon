"""Citeerregels voor Oost-Europa, Turkije, het Midden-Oosten en Afrika.

* **RU** (ГК РФ): `ст. 10 ГК РФ`, met punt-nummers voor ingevoegde artikelen (`ст. 434.1`). Leden heten `п.`
  (пункт) en `ч.` (часть) en staan vóór het artikel ("п. 1 ст. 10"): het nummer na `п.`/`ч.` is geen artikel.
* **TR** (TMK): `TMK m. 706`, `TBK m. 49`; geciteerd met de afkorting en "m." (madde). Tijdelijke artikelen als
  `Geçici 1`.
"""
from __future__ import annotations

from .artikelen import Regels

# Een nummer direct na "п. " of "ч. " (punt, deel) is een lid, geen artikel.
_RU_NR = r"(?<!п\.\s)(?<!ч\.\s)(?<!пп\.\s)\d+(?:\.\d+)?"

REGELS = {
    "RU": Regels(
        "ГК РФ",
        ("Конституция РФ", "ГПК РФ", "АПК РФ", "УК РФ", "СК РФ", "ЖК РФ", "ЗК РФ", "ЗоЗПП", "Закон об АО", "Закон об ООО"),
        nummer=_RU_NR,
        namen={"ГК РФ": "Гражданский кодекс Российской Федерации", "Конституция РФ": "Конституция Российской Федерации (1993)",
               "ГПК РФ": "Гражданский процессуальный кодекс Российской Федерации", "АПК РФ": "Арбитражный процессуальный кодекс Российской Федерации",
               "УК РФ": "Уголовный кодекс Российской Федерации", "СК РФ": "Семейный кодекс Российской Федерации",
               "ЖК РФ": "Жилищный кодекс Российской Федерации", "ЗК РФ": "Земельный кодекс Российской Федерации",
               "ЗоЗПП": "Закон Российской Федерации «О защите прав потребителей» (1992)",
               "Закон об АО": "Федеральный закон «Об акционерных обществах» (1995)",
               "Закон об ООО": "Федеральный закон «Об обществах с ограниченной ответственностью» (1998)"},
    ),
    "TR": Regels(
        "TMK",
        ("TBK", "TTK", "HMK", "TCK", "TKHK", "MÖHUK", "Anayasa", "İİK"),
        nummer=r"\d+(?:/[A-Z])?",
        namen={"TMK": "Türk Medeni Kanunu (4721)", "TBK": "Türk Borçlar Kanunu (6098)", "TTK": "Türk Ticaret Kanunu (6102)",
               "HMK": "Hukuk Muhakemeleri Kanunu (6100)", "TCK": "Türk Ceza Kanunu (5237)",
               "TKHK": "Tüketicinin Korunması Hakkında Kanun (6502)", "MÖHUK": "Milletlerarası Özel Hukuk ve Usul Hukuku Hakkında Kanun (5718)",
               "Anayasa": "Türkiye Cumhuriyeti Anayasası (1982)", "İİK": "İcra ve İflas Kanunu (2004)"},
    ),
    "AE": Regels(
        "CTL",
        ("CommTL", "CPL", "Penal Code", "CPrL", "Companies Law"),
        namen={"CTL": "Civil Transactions Law (decreet-wet 25/2025)", "CommTL": "Commercial Transactions Law (decreet-wet 50/2022)",
               "CPL": "Consumer Protection Law (federale wet 15/2020)", "Penal Code": "Federal Penal Code (decreet-wet 31/2021)",
               "CPrL": "Civil Procedure Law (decreet-wet 42/2022)", "Companies Law": "Commercial Companies Law (decreet-wet 32/2021)"},
    ),
    "ZA": Regels(
        None,
        ("Constitution 1996", "CPA 2008", "Companies Act 2008", "NCA 2005", "ALA 1981", "Prescription Act 1969",
         "Conventional Penalties Act 1962", "Matrimonial Property Act 1984"),
        stijl="s",
        nummer=r"\d+[A-Z]{0,2}",
        namen={"Constitution 1996": "Constitution of the Republic of South Africa, 1996", "CPA 2008": "Consumer Protection Act 68 of 2008",
               "Companies Act 2008": "Companies Act 71 of 2008", "NCA 2005": "National Credit Act 34 of 2005",
               "ALA 1981": "Alienation of Land Act 68 of 1981", "Prescription Act 1969": "Prescription Act 68 of 1969",
               "Conventional Penalties Act 1962": "Conventional Penalties Act 15 of 1962",
               "Matrimonial Property Act 1984": "Matrimonial Property Act 88 of 1984"},
    ),
    "TR": Regels(
        "TMK",
        ("TBK", "TTK", "HMK", "TCK", "TKHK", "MÖHUK", "AY"),
        nummer=r"(?:Geçici\s|Ek\s)?\d+(?:/[A-Z])?",
        namen={"TMK": "Türk Medeni Kanunu (4721)", "TBK": "Türk Borçlar Kanunu (6098)", "TTK": "Türk Ticaret Kanunu (6102)",
               "HMK": "Hukuk Muhakemeleri Kanunu (6100)", "TCK": "Türk Ceza Kanunu (5237)",
               "TKHK": "Tüketicinin Korunması Hakkında Kanun (6502)", "MÖHUK": "Milletlerarası Özel Hukuk ve Usul Hukuku Hakkında Kanun (5718)",
               "AY": "Türkiye Cumhuriyeti Anayasası (1982)"},
    ),
}
