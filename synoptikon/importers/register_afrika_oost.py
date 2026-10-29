"""Register voor Oost-Europa, Turkije, het Midden-Oosten en Afrika (zelfde vorm als `register.py`).

Bronnen per stelsel en waarom:

* TR: mevzuat.gov.tr (Mevzuat Bilgi Sistemi van het presidentschap), geconsolideerd; de Word-HTML die de site in
  een iframe toont (importer `mevzuat`). robots.txt beperkt alleen Googlebot.
* RU: geen. pravo.gov.ru (en publication.pravo.gov.ru) weigert verbindingen van buiten Rusland; ConsultantPlus en
  Garant zijn commercieel en worden niet gescrapet. Alleen stelsel, systematiek en citeerregels.
"""
from __future__ import annotations

from .register import Wet

WETTEN: list[Wet] = [
    # TR: de TMK als hoofdcodificatie, de TBK (het OR) en de wetten eromheen
    Wet("TR", None, "mevzuat", "4721", "Türk Medeni Kanunu"),
    *[Wet("TR", afk, "mevzuat", nr, t, systematiek=True) for afk, nr, t in [
        ("TBK", "6098", "Türk Borçlar Kanunu"),
        ("AY", "2709", "Türkiye Cumhuriyeti Anayasası"),
        ("TTK", "6102", "Türk Ticaret Kanunu"),
        ("TKHK", "6502", "Tüketicinin Korunması Hakkında Kanun"),
        ("HMK", "6100", "Hukuk Muhakemeleri Kanunu"),
        ("TCK", "5237", "Türk Ceza Kanunu"),
        ("MÖHUK", "5718", "Milletlerarası Özel Hukuk ve Usul Hukuku Hakkında Kanun"),
    ]],
]
