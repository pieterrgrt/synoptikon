"""Citeerregels voor Oost-Europa, Turkije, het Midden-Oosten en Afrika.

* **RU** (ГК РФ): `ст. 10 ГК РФ`, met punt-nummers voor ingevoegde artikelen (`ст. 434.1`). Leden heten `п.`
  (пункт) en `ч.` (часть) en staan vóór het artikel ("п. 1 ст. 10"): het nummer na `п.`/`ч.` is geen artikel.
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
}
