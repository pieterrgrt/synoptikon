"""Citeerregels van de Europese stelsels buiten het basisregister (regio "europa").

* **AT** (ABGB): `§ 1295 ABGB`, met letters (`§ 1216e`); andere wetten met hun gangbare afkorting
  (`§ 6 KSchG`, `§ 1 UGB`). Het B-VG telt in artikelen (`Art. 7 B-VG`).
* **DK** (geen hoofdwet): `§ 36 aftl.`, `§ 4 a kbl.`, `§ 76, stk. 1, kbl.`; letters met een spatie (`§ 9 a`).
* **FI** (geen hoofdwet): `OikTL 36 §`, `36 § OikTL`; wetten die per hoofdstuk nummeren als hoofdstuk:paragraaf
  (`RL 21:1`, `KSL 7 a:14 a`, `OK 17:1`), de schrijfwijze van de Finse praktijk. "21 luku 1 §" wordt niet herkend.
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
    "DK": Regels(
        None,
        ("grl.", "aftl.", "kbl.", "forbrugeraftalel.", "EAL", "forældelsesl.", "selskabsl.", "rpl.", "strfl.", "DL", "renteloven",
         "markedsføringsl.", "gældsbrevsl.", "tinglysningsl.", "lejeloven", "ægteskabsl.", "arvel."),
        stijl="§",
        nummer=r"\d+(?:\s?[a-zæøå](?![\wæøå]))?",
        namen={"grl.": "Danmarks Riges Grundlov (1953)", "aftl.": "Aftaleloven", "kbl.": "Købeloven", "forbrugeraftalel.": "Forbrugeraftaleloven",
               "EAL": "Erstatningsansvarsloven", "forældelsesl.": "Forældelsesloven", "selskabsl.": "Selskabsloven", "rpl.": "Retsplejeloven",
               "strfl.": "Straffeloven", "DL": "Danske Lov (1683)", "markedsføringsl.": "Markedsføringsloven", "gældsbrevsl.": "Gældsbrevsloven",
               "tinglysningsl.": "Tinglysningsloven", "ægteskabsl.": "Ægteskabsloven", "arvel.": "Arveloven"},
    ),
    "FI": Regels(
        None,
        ("PL", "OikTL", "KL", "KSL", "VahL", "VanhL", "OYL", "OK", "RL", "MK", "PK", "AL", "TSL", "HolhTL", "KorkoL"),
        stijl="§",
        nummer=r"\d+(?:\s?[a-zäö](?![\wäö]))?(?::\d+(?:\s?[a-zäö](?![\wäö]))?)?",
        namen={"PL": "Suomen perustuslaki (731/1999)", "OikTL": "Oikeustoimilaki", "KL": "Kauppalaki", "KSL": "Kuluttajansuojalaki",
               "VahL": "Vahingonkorvauslaki", "VanhL": "Laki velan vanhentumisesta", "OYL": "Osakeyhtiölaki", "OK": "Oikeudenkäymiskaari",
               "RL": "Rikoslaki", "MK": "Maakaari", "PK": "Perintökaari", "AL": "Avioliittolaki",
               "TSL": "Työsopimuslaki", "HolhTL": "Laki holhoustoimesta", "KorkoL": "Korkolaki"},
    ),
}
