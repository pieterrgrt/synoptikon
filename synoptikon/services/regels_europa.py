"""Citeerregels van de Europese stelsels buiten het basisregister (regio "europa").

* **AT** (ABGB): `§ 1295 ABGB`, met letters (`§ 1216e`); andere wetten met hun gangbare afkorting
  (`§ 6 KSchG`, `§ 1 UGB`). Het B-VG telt in artikelen (`Art. 7 B-VG`).
* **DK** (geen hoofdwet): `§ 36 aftl.`, `§ 4 a kbl.`, `§ 76, stk. 1, kbl.`; letters met een spatie (`§ 9 a`).
* **FI** (geen hoofdwet): `OikTL 36 §`, `36 § OikTL`; wetten die per hoofdstuk nummeren als hoofdstuk:paragraaf
  (`RL 21:1`, `KSL 7 a:14 a`, `OK 17:1`), de schrijfwijze van de Finse praktijk. "21 luku 1 §" wordt niet herkend.
* **NO** (geen hoofdwet): `avtl. § 36`, `tvl. § 1-1` (nieuwere wetten nummeren per hoofdstuk met een streepje),
  `§ 38 a`.
* **SE** (geen hoofdwet): `36 § AvtL`, `AvtL 36 §`; de balkar en andere wetten die per hoofdstuk nummeren als
  hoofdstuk:paragraaf (`BrB 3:1`, `RB 17:3`). "3 kap. 1 § BrB" wordt niet herkend.
* **PL** (KC): `art. 415 KC`, `art. 22¹ KC` (of `22^1`), andere kodeksy met hun hoofdletterafkorting (`art. 299 KSH`,
  `art. 148 KK`); de gangbare kleine letters (`k.c.`) zijn niet opgenomen, omdat ze als eigen wet zouden tellen.
* **PT** (CC): `art. 405.º CC`, `artigo 483.º do Código Civil`; letters met een streepje (`1305-A`; "1305.º-A" verliest
  de letter). "CC" deelt PT met ES.
* **CZ** (OZ): `§ 2910 OZ`, `§ 1 ZOK`; **HU** (Ptk.): `Ptk. 6:519`, nummer boek:paragraaf; **RO** (NCC): `art. 1350 NCC`
  ("C. civ." is al van FR).
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
    "NO": Regels(
        None,
        ("Grl.", "avtl.", "kjl.", "fkjl.", "skl.", "foreldelsesl.", "asl.", "tvl.", "strl.", "husleieloven", "ekteskapsl.",
         "arvel.", "tingl.", "panteloven", "markedsføringsl.", "angrerettl.", "finansavtalel.", "asal.", "deknl.", "konkursl."),
        stijl="§",
        nummer=r"\d+(?:-\d+)?(?:\s?[a-zæøå](?![\wæøå]))?",
        namen={"Grl.": "Kongeriket Norges Grunnlov (1814)", "avtl.": "Avtaleloven", "kjl.": "Kjøpsloven", "fkjl.": "Forbrukerkjøpsloven",
               "skl.": "Skadeserstatningsloven", "foreldelsesl.": "Foreldelsesloven", "asl.": "Aksjeloven", "tvl.": "Tvisteloven",
               "strl.": "Straffeloven", "ekteskapsl.": "Ekteskapsloven", "arvel.": "Arveloven",
               "tingl.": "Tinglysingsloven", "markedsføringsl.": "Markedsføringsloven", "angrerettl.": "Angrerettloven",
               "finansavtalel.": "Finansavtaleloven", "asal.": "Allmennaksjeloven", "deknl.": "Dekningsloven", "konkursl.": "Konkursloven"},
    ),
    "SE": Regels(
        None,
        ("RF", "AvtL", "KöpL", "KKL", "SkL", "PreskL", "ABL", "RB", "BrB", "JB", "ÄB", "ÄktB", "FB", "HB", "KtjL", "KkrL", "MFL", "KonkL",
         "SamboL", "HBL", "IPRL"),
        stijl="§",
        nummer=r"\d+(?:\s?[a-zåäö](?![\wåäö]))?(?::\d+(?:\s?[a-zåäö](?![\wåäö]))?)?",
        namen={"RF": "Regeringsformen (1974:152)", "AvtL": "Avtalslagen", "KöpL": "Köplagen", "KKL": "Konsumentköplagen", "SkL": "Skadeståndslagen",
               "PreskL": "Preskriptionslagen", "ABL": "Aktiebolagslagen", "RB": "Rättegångsbalken", "BrB": "Brottsbalken", "JB": "Jordabalken",
               "ÄB": "Ärvdabalken", "ÄktB": "Äktenskapsbalken", "FB": "Föräldrabalken", "HB": "Handelsbalken (1734)", "KtjL": "Konsumenttjänstlagen",
               "KkrL": "Konsumentkreditlagen", "MFL": "Marknadsföringslagen", "KonkL": "Konkurslagen", "SamboL": "Sambolagen",
               "HBL": "Lagen om handelsbolag och enkla bolag"},
    ),
    "PL": Regels(
        "KC",
        ("KSH", "KPC", "KK", "KPK", "KRO", "KP", "KW", "Konstytucja RP", "UPK", "PPM", "UOKiK"),
        nummer=r"\d+(?:[¹²³⁴⁵⁶⁷⁸⁹⁰]+|\^\d+)?",
        namen={"KC": "Kodeks cywilny (1964)", "KSH": "Kodeks spółek handlowych", "KPC": "Kodeks postępowania cywilnego", "KK": "Kodeks karny",
               "KPK": "Kodeks postępowania karnego", "KRO": "Kodeks rodzinny i opiekuńczy", "KP": "Kodeks pracy", "KW": "Kodeks wykroczeń",
               "Konstytucja RP": "Konstytucja Rzeczypospolitej Polskiej (1997)", "UPK": "Ustawa o prawach konsumenta (2014)",
               "PPM": "Prawo prywatne międzynarodowe (2011)", "UOKiK": "Ustawa o ochronie konkurencji i konsumentów"},
    ),
    "PT": Regels(
        "CC",
        ("CRP", "CSC", "LDC", "CPC", "CP", "CCom", "RJCCG", "CT", "CIRE"),
        nummer=r"\d+(?:-[A-Z])?",
        namen={"CC": "Código Civil (1966)", "CRP": "Constituição da República Portuguesa (1976)", "CSC": "Código das Sociedades Comerciais",
               "LDC": "Lei de Defesa do Consumidor", "CPC": "Código de Processo Civil", "CP": "Código Penal",
               "RJCCG": "Regime jurídico das cláusulas contratuais gerais (DL 446/85)", "CT": "Código do Trabalho",
               "CIRE": "Código da Insolvência e da Recuperação de Empresas"},
    ),
    "CZ": Regels(
        "OZ",
        ("ZOK", "OSŘ", "TZ", "ZMPS", "Ústava", "ZOS"),
        stijl="§",
        nummer=r"\d+[a-z]?",
        namen={"OZ": "Občanský zákoník (zákon č. 89/2012 Sb.)", "ZOK": "Zákon o obchodních korporacích (č. 90/2012 Sb.)",
               "OSŘ": "Občanský soudní řád (č. 99/1963 Sb.)", "TZ": "Trestní zákoník (č. 40/2009 Sb.)",
               "ZMPS": "Zákon o mezinárodním právu soukromém (č. 91/2012 Sb.)", "Ústava": "Ústava České republiky (1993)",
               "ZOS": "Zákon o ochraně spotřebitele (č. 634/1992 Sb.)"},
    ),
    "HU": Regels(
        "Ptk.",
        ("Pp.", "Btk.", "Alaptörvény", "Nmjtv.", "Fgytv."),
        stijl="§",
        nummer=r"\d:\d+(?:/[A-Z])?|\d+",
        namen={"Ptk.": "Polgári Törvénykönyv (2013. évi V. törvény)", "Pp.": "Polgári perrendtartás (2016. évi CXXX. törvény)",
               "Btk.": "Büntető Törvénykönyv (2012. évi C. törvény)", "Alaptörvény": "Magyarország Alaptörvénye (2011)",
               "Nmjtv.": "A nemzetközi magánjogról szóló 2017. évi XXVIII. törvény", "Fgytv.": "A fogyasztóvédelemről szóló 1997. évi CLV. törvény"},
    ),
    "RO": Regels(
        "NCC",
        ("NCPC", "NCP", "Constituția României", "Legea 31/1990"),
        nummer=r"\d+(?:\^\d+|[¹²³⁴⁵⁶⁷⁸⁹])?",
        namen={"NCC": "Noul Cod civil (Legea nr. 287/2009)", "NCPC": "Noul Cod de procedură civilă (Legea nr. 134/2010)",
               "NCP": "Noul Cod penal (Legea nr. 286/2009)", "Constituția României": "Constituția României (1991)",
               "Legea 31/1990": "Legea societăților nr. 31/1990"},
    ),
}
