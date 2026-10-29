"""Stelsels in Azië en Oceanië (regio-uitbreiding, zie `plugins.py`). Bronnen per stelsel: `importers/register_azie.py`."""

from .systematiek_azie import JP

# code, naam, taal, toelichting, actief, rechtsfamilie (zelfde vorm als seed/stelsels.py)
STELSELS = [
    ("JP", "Japan", "ja", "民法 (1896/1898): pandektistisch naar het Duitse ontwerp, met Franse sporen (eigendom gaat over bij de overeenkomst); schuldrecht herzien in 2017", True, "oost_aziatisch"),
]

SYSTEMATIEK = {
    "JP": JP,
}
