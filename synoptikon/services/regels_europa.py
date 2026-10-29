"""Citeerregels van de Europese stelsels buiten het basisregister (regio "europa").

* **AT** (ABGB): `§ 1295 ABGB`, met letters (`§ 1216e`); andere wetten met hun gangbare afkorting
  (`§ 6 KSchG`, `§ 1 UGB`). Het B-VG telt in artikelen (`Art. 7 B-VG`).
"""
from __future__ import annotations

from .artikelen import Regels

REGELS: dict[str, Regels] = {
    "AT": Regels(
        "ABGB",
        ("UGB", "KSchG", "ZPO", "StGB", "B-VG", "IPRG", "IO", "EO", "MRG", "WEG 2002", "EheG", "GmbHG", "AktG", "PHG", "VersVG",
         "FAGG", "VGG", "ECG", "AußStrG", "JN", "UWG", "EGZPO"),
        stijl="§",
        nummer=r"\d+[a-z]{0,3}",
        namen={"ABGB": "Allgemeines bürgerliches Gesetzbuch (1811)", "UGB": "Unternehmensgesetzbuch", "KSchG": "Konsumentenschutzgesetz",
               "ZPO": "Zivilprozessordnung", "StGB": "Strafgesetzbuch", "B-VG": "Bundes-Verfassungsgesetz", "IPRG": "IPR-Gesetz",
               "IO": "Insolvenzordnung", "EO": "Exekutionsordnung", "MRG": "Mietrechtsgesetz", "WEG 2002": "Wohnungseigentumsgesetz 2002",
               "EheG": "Ehegesetz", "PHG": "Produkthaftungsgesetz", "VersVG": "Versicherungsvertragsgesetz",
               "FAGG": "Fern- und Auswärtsgeschäfte-Gesetz", "VGG": "Verbrauchergewährleistungsgesetz", "AußStrG": "Außerstreitgesetz",
               "JN": "Jurisdiktionsnorm"},
    ),
}
