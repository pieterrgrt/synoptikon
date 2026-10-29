"""Register voor Azië en Oceanië (regio-uitbreiding, zie `plugins.py`).

Bronnen per stelsel en waarom:

* JP: e-Gov 法令検索, API v2 (open, zonder sleutel; XML volgens het 法令標準XMLスキーマ), geconsolideerd: de geldende
  stand, versie = inwerkingtreding van de laatste wijziging. De Engelse vertalingen (Japanese Law Translation) zijn
  niet opgenomen: die site weigert geautomatiseerde verzoeken (403), en een tweede taalversie onder dezelfde
  afkorting vraagt een `taal` in het register, dat `import-alles` nu niet doorgeeft.
* TW: 全國法規資料庫 (law.moj.gov.tw), de pagina LawAll.aspx per wet (HTML; robots.txt staat alleen die toe, de
  open-databestanden onder /api/ zijn één grote zip van alle wetten), geconsolideerd, versie = 修正日期. De Engelse
  vertalingen (/ENG/) vallen onder `Disallow` en zijn niet opgenomen.
* HK: Hong Kong e-Legislation, de open data van het DoJ op data.gov.hk (HKLM-XML, current version, Engels; de
  Chinese tekst staat in eigen zips). Per wet alleen het ene bestand uit de grote zip, met Range-verzoeken.
  elegislation.gov.hk zelf sluit robots.txt af. Geen wetboek: de ordinances rond contract en koop, de
  Companies Ordinance, de Crimes Ordinance en de Basic Law, met het chapter als afkorting ("Cap. 26").
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
    # HK: common law; de ordinances rond contract en koop en de Basic Law (DoJ open data)
    *[Wet("HK", afk, "hkel", i, t, systematiek=True) for afk, i, t in [
        ("BL", "A101", "Basic Law of the Hong Kong Special Administrative Region"),
        ("Cap. 26", "cap26", "Sale of Goods Ordinance"),
        ("Cap. 71", "cap71", "Control of Exemption Clauses Ordinance"),
        ("Cap. 284", "cap284", "Misrepresentation Ordinance"),
        ("Cap. 457", "cap457", "Supply of Services (Implied Terms) Ordinance"),
        ("Cap. 623", "cap623", "Contracts (Rights of Third Parties) Ordinance"),
        ("Cap. 347", "cap347", "Limitation Ordinance"),
        ("Cap. 622", "cap622", "Companies Ordinance"),
        ("Cap. 200", "cap200", "Crimes Ordinance"),
    ]],
]
