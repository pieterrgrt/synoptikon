"""Register voor Azië en Oceanië (regio-uitbreiding, zie `plugins.py`).

Bronnen per stelsel en waarom:

* JP: e-Gov 法令検索, API v2 (open, zonder sleutel; XML volgens het 法令標準XMLスキーマ), geconsolideerd: de geldende
  stand, versie = inwerkingtreding van de laatste wijziging. De Engelse vertalingen (Japanese Law Translation) zijn
  niet opgenomen: die site weigert geautomatiseerde verzoeken (403), en een tweede taalversie onder dezelfde
  afkorting vraagt een `taal` in het register, dat `import-alles` nu niet doorgeeft.
* TW: 全國法規資料庫 (law.moj.gov.tw), de pagina LawAll.aspx per wet (HTML; robots.txt staat alleen die toe, de
  open-databestanden onder /api/ zijn één grote zip van alle wetten), geconsolideerd, versie = 修正日期. De Engelse
  vertalingen (/ENG/) vallen onder `Disallow` en zijn niet opgenomen.
"""
from __future__ import annotations

from .register import Wet

WETTEN: list[Wet] = [
    # JP: het 民法 en de wetten eromheen (e-Gov)
    Wet("JP", None, "egov", "129AC0000000089", "民法"),
    *[Wet("JP", afk, "egov", i, t, systematiek=True) for afk, i, t in [
        ("憲法", "321CONSTITUTION", "日本国憲法"),
        ("商法", "132AC0000000048", "商法"),
        ("会社法", "417AC0000000086", "会社法"),
        ("消契法", "412AC0000000061", "消費者契約法"),
        ("民訴法", "408AC0000000109", "民事訴訟法"),
        ("刑法", "140AC0000000045", "刑法"),
        ("通則法", "418AC0000000078", "法の適用に関する通則法"),
    ]],
    # TW: het 民法 van de Republiek China en de wetten eromheen (law.moj.gov.tw)
    Wet("TW", None, "lawmoj", "B0000001", "民法"),
    *[Wet("TW", afk, "lawmoj", i, t, systematiek=True) for afk, i, t in [
        ("憲法", "A0000001", "中華民國憲法"),
        ("公司法", "J0080001", "公司法"),
        ("消保法", "J0170001", "消費者保護法"),
        ("民訴法", "B0010001", "民事訴訟法"),
        ("刑法", "C0000001", "中華民國刑法"),
        ("涉民法", "B0000007", "涉外民事法律適用法"),
    ]],
]
