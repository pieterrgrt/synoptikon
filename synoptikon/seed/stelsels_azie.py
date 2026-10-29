"""Stelsels in Azië en Oceanië (regio-uitbreiding, zie `plugins.py`). Bronnen per stelsel: `importers/register_azie.py`."""

from .systematiek_azie import HK, JP, NZ, TW

# code, naam, taal, toelichting, actief, rechtsfamilie (zelfde vorm als seed/stelsels.py)
STELSELS = [
    ("JP", "Japan", "ja", "民法 (1896/1898): pandektistisch naar het Duitse ontwerp, met Franse sporen (eigendom gaat over bij de overeenkomst); schuldrecht herzien in 2017", True, "oost_aziatisch"),
    ("TW", "Taiwan", "zh", "民法 (1929/1930) van de Republiek China: naar het BGB en het Zwitserse ZGB/OR, deels via Japan; sinds 1949 in Taiwan, sindsdien herzien", True, "oost_aziatisch"),
    ("HK", "Hongkong", "en", "Common law naar Engels voorbeeld, onder de Basic Law (1997) voortgezet; geen wetboek, ordinances naast de rechtspraak", True, "common_law"),
    ("NZ", "Nieuw-Zeeland", "en", "Common law naar Engels voorbeeld, contractenrecht grotendeels in de Contract and Commercial Law Act 2017; geen tekst: legislation.govt.nz weigert geautomatiseerde verzoeken en de API vraagt een sleutel", True, "common_law"),
]

SYSTEMATIEK = {
    "JP": JP,
    "TW": TW,
    "HK": HK,
    "NZ": NZ,
}
