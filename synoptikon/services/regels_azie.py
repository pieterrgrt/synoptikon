"""Citeerregels voor Azië en Oceanië (regio-uitbreiding, zie `plugins.py`).

* **JP**: 民法709条, 第709条の2, 会社法第429条第1項. Nummers met の voor ingevoegde artikelen (`709の2`).
* **TW**: 民法第184條第1項, 第7條之1 (ingevoegd artikel, bij de bron `7-1`), 消保法 voor 消費者保護法.
* **HK**: common law zonder wetboek, ordinances naar hun chapter: "s 14 Cap. 26", "section 3 of the Misrepresentation
  Ordinance", "art. 8 BL" (Basic Law).

Dezelfde wetsnaam in twee stelsels ("民法第709条": JP of TW) geeft, zoals "art. 1902 CC" (ES of FR), beide.

`cjk` (in `VOORBEWERKING`) maakt van "第七百九条" of "709条" een gewone verwijzing ("art. 709") vóór de herkenning;
`NAMEN` zijn de volledige wetsnamen, die korter zijn dan de vijf tekens die `artikelen._namen` voor titels eist.
"""
from __future__ import annotations

import re

from .artikelen import Regels

REGELS: dict[str, Regels] = {
    "JP": Regels(
        "民法",
        ("憲法", "商法", "会社法", "消契法", "民訴法", "刑法", "通則法"),
        nummer=r"\d+(?:の\d+)*",
        namen={"民法": "民法 (明治29年法律第89号)", "憲法": "日本国憲法", "消契法": "消費者契約法", "民訴法": "民事訴訟法",
               "通則法": "法の適用に関する通則法", "会社法": "会社法 (平成17年法律第86号)", "商法": "商法 (明治32年法律第48号)",
               "刑法": "刑法 (明治40年法律第45号)"},
    ),
    "TW": Regels(
        "民法",
        ("憲法", "公司法", "消保法", "民訴法", "刑法", "涉民法"),
        nummer=r"\d+(?:-\d+)?",
        namen={"民法": "民法 (1929/1930)", "憲法": "中華民國憲法", "公司法": "公司法 (1929)", "消保法": "消費者保護法",
               "民訴法": "民事訴訟法", "刑法": "中華民國刑法", "涉民法": "涉外民事法律適用法"},
    ),
    "HK": Regels(
        None,
        ("BL", "Cap. 26", "Cap. 71", "Cap. 284", "Cap. 457", "Cap. 623", "Cap. 347", "Cap. 622", "Cap. 200"),
        stijl="s",
        nummer=r"\d+[A-Z]{0,3}",
        namen={"BL": "Basic Law of the Hong Kong Special Administrative Region", "Cap. 26": "Sale of Goods Ordinance", "Cap. 71": "Control of Exemption Clauses Ordinance", "Cap. 284": "Misrepresentation Ordinance", "Cap. 457": "Supply of Services (Implied Terms) Ordinance", "Cap. 623": "Contracts (Rights of Third Parties) Ordinance", "Cap. 347": "Limitation Ordinance", "Cap. 622": "Companies Ordinance", "Cap. 200": "Crimes Ordinance"},
    ),
}

NAMEN = [
    ("日本国憲法", "憲法"), ("消費者契約法", "消契法"), ("民事訴訟法", "民訴法"), ("法の適用に関する通則法", "通則法"),
    ("中華民國憲法", "憲法"), ("消費者保護法", "消保法"), ("中華民國刑法", "刑法"), ("涉外民事法律適用法", "涉民法"),
    ("Basic Law", "BL"), *[(f"Cap {n}", f"Cap. {n}") for n in (26, 71, 284, 457, 623, 347, 622, 200)],
]


# Oost-Aziatische citeerwijze: "第709条の2", "제750조의2", "第 184 條", "第一千一百六十五条". Het nummer staat
# tussen 第/제 en 条/條/조, zonder spatie tegen de wetsnaam ("民法第709条"). Python telt CJK-tekens als \w, dus
# de grenzen (?<!\w) rond wetsnamen en nummers werken pas als `cjk` er "art. 709の2" van maakt.
_CJK = re.compile(r"[぀-ヿ㐀-鿿가-힯]")
_CJK_CIJFER = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
_CJK_NR = "[0-9０-９〇零一二三四五六七八九十百千]+"
_CJK_ART = re.compile(rf"[第제]?\s*({_CJK_NR}(?:-\d+)?)\s*[条條조]((?:\s*(?:の|의|之)\s*{_CJK_NR})*)")


def _getal(s: str) -> str:
    """"七百九" → "709", "一千一百六十五" → "1165", "７０９" → "709"; Arabische cijfers blijven staan."""
    s = s.translate({0xFF10 + i: str(i) for i in range(10)})
    if s[:1].isdigit():
        return s
    if not re.search("[十百千]", s):
        return "".join(str(_CJK_CIJFER[c]) for c in s)
    totaal, cijfer = 0, 0
    for c in s:
        if c in _CJK_CIJFER:
            cijfer = _CJK_CIJFER[c]
        else:
            totaal += (cijfer or 1) * {"十": 10, "百": 100, "千": 1000}[c]
            cijfer = 0
    return str(totaal + cijfer)


def cjk(tekst: str) -> str:
    """"民法第709条の2" → "民法 art. 709の2 ", "민법 제750조의2" → "민법  art. 750의2 ", "第一百二十条之一" → " art. 120-1 "."""
    if not _CJK.search(tekst):
        return tekst

    def vervang(m: re.Match) -> str:
        nr = _getal(m.group(1))
        for verbinder, getal in re.findall(rf"(の|의|之)\s*({_CJK_NR})", m.group(2)):
            nr += ("-" if verbinder == "之" else verbinder) + _getal(getal)
        return f" art. {nr} "

    return _CJK_ART.sub(vervang, tekst)


VOORBEWERKING = [cjk]
