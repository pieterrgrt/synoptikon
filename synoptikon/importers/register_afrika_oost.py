"""Register voor Oost-Europa, Turkije, het Midden-Oosten en Afrika.

Bronnen per stelsel en waarom:

* RU: geen tekst. pravo.gov.ru (het officiële portaal) weigert verbindingen van buiten Rusland;
  ConsultantPlus en Garant zijn commercieel en worden niet gescrapet. Alleen stelsel, systematiek en citeerregels.
* TR: mevzuat.gov.tr (Mevzuat Bilgi Sistemi van het presidentschap), geconsolideerd, Word-HTML per wet; robots.txt
  beperkt alleen Googlebot.
"""
from __future__ import annotations

from .register import Wet

WETTEN = [
    Wet("TR", None, "mevzuat", "4721", "Türk Medeni Kanunu"),
    *[Wet("TR", afk, "mevzuat", nr, titel, systematiek=True) for afk, nr, titel in [
        ("TBK", "6098", "Türk Borçlar Kanunu"),
        ("Anayasa", "2709", "Türkiye Cumhuriyeti Anayasası"),
        ("TTK", "6102", "Türk Ticaret Kanunu"),
        ("TKHK", "6502", "Tüketicinin Korunması Hakkında Kanun"),
        ("HMK", "6100", "Hukuk Muhakemeleri Kanunu"),
        ("TCK", "5237", "Türk Ceza Kanunu"),
        ("MÖHUK", "5718", "Milletlerarası Özel Hukuk ve Usul Hukuku Hakkında Kanun"),
    ]],
]
