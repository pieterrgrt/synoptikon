"""Indeling van de stelsels naar werelddeel en regio, voor de stelselkiezer op /profiel en het overzicht op /stelsels.

Per ISO 3166-1-code (alle 249, ook die nog geen stelsel in de database hebben) plus de eigen codes van Synoptikon:
EN (Engeland & Wales), SC (Schotland; daarmee valt de Seychellen-code weg), QC (Québec), EU en de verdragen en soft
law. Een onbekende code met een streepje (`US-LA`, `CA-ON`) volgt het land ervoor; verder valt hij onder Overig.

De indeling is praktisch, niet de VN-geoschema's: de Baltische staten bij Noord-Europa (EU, eigen burgerlijk wetboek),
het voormalige Joegoslavië en Albanië bij Midden- en Oost-Europa, Mexico bij Latijns-Amerika, Turkije en Mauritanië
bij het Midden-Oosten en Noord-Afrika, Groenland en de Faeröer bij Noord-Europa (Deens rijk).
"""
from __future__ import annotations

# sleutel → naam, in de volgorde van de kiezer.
REGIOS: dict[str, str] = {
    "europa_west": "West-Europa",
    "europa_noord": "Noord-Europa",
    "europa_zuid": "Zuid-Europa",
    "europa_midden_oost": "Midden- en Oost-Europa",
    "post_sovjet": "Post-Sovjetstaten",
    "noord_amerika": "Noord-Amerika",
    "latijns_amerika": "Latijns-Amerika en het Caribisch gebied",
    "mona": "Midden-Oosten en Noord-Afrika",
    "afrika": "Afrika ten zuiden van de Sahara",
    "azie_oost": "Oost-Azië",
    "azie_zuid": "Zuid-Azië",
    "azie_zuidoost": "Zuidoost-Azië",
    "oceanie": "Oceanië",
    "supranationaal": "Europees en internationaal",
    "overig": "Overig",
}

_LEDEN: dict[str, str] = {
    "europa_west": "NL BE LU FR MC DE AT CH LI IE GB EN SC GG JE IM",
    "europa_noord": "DK SE NO FI IS FO GL AX SJ EE LV LT",
    "europa_zuid": "IT ES PT GR MT CY SM VA AD GI",
    "europa_midden_oost": "PL CZ SK HU RO BG SI HR BA RS ME MK AL XK",
    "post_sovjet": "RU BY UA MD GE AM AZ KZ UZ TM KG TJ",
    "noord_amerika": "US CA QC PM BM",
    "latijns_amerika": "MX GT BZ SV HN NI CR PA CU DO HT JM PR BS BB TT AG DM GD KN LC VC AW CW SX BQ KY TC VG VI AI MS "
                       "GP MQ BL MF CO VE EC PE BO CL AR UY PY BR GY SR GF FK GS",
    "mona": "MA DZ TN LY EG EH SD MR IL PS JO LB SY IQ IR SA AE QA BH KW OM YE TR",
    "afrika": "SN GM GW GN SL LR CI ML BF NE NG GH TG BJ CV ST GQ GA CG CD CM CF TD SS ET ER DJ SO KE UG RW BI TZ "
              "MZ MW ZM ZW AO NA BW ZA LS SZ MG MU KM RE YT SH",
    "azie_oost": "CN JP KR KP TW HK MO MN",
    "azie_zuid": "IN PK BD LK NP BT MV AF IO",
    "azie_zuidoost": "ID MY SG TH VN PH MM KH LA BN TL",
    "oceanie": "AU NZ PG FJ SB VU NC PF WS TO KI TV NR MH FM PW CK NU TK WF AS GU MP UM PN NF CC CX AQ BV HM TF",
    "supranationaal": "EU INT EVRM EHRM CISG PECL DCFR UNIDROIT OHADA UN",
}

REGIO: dict[str, str] = {code: sleutel for sleutel, codes in _LEDEN.items() for code in codes.split()}


def regio(code: str | None) -> str:
    """Regiosleutel van een stelselcode; `US-LA` volgt `US`, een onbekende code valt onder 'overig'."""
    code = (code or "").upper()
    if code in REGIO:
        return REGIO[code]
    return REGIO.get(code.split("-")[0], "overig")


# Voorstel bij de eerste keer inloggen, naar de taal van het profiel. Wat niet (actief) in de database staat valt weg;
# blijft er niets over, dan de stelsels in die taal.
VOORSTEL_PER_TAAL: dict[str, list[str]] = {
    "nl": ["NL", "BE", "DE", "FR", "EU"],
    "fr": ["FR", "BE", "CH", "LU", "QC", "EU"],
    "de": ["DE", "AT", "CH", "LI", "EU"],
    "it": ["IT", "CH", "FR", "EU"],
    "en": ["EN", "SC", "IE", "US", "CA", "AU", "EU"],
    "es": ["ES", "MX", "AR", "CL", "CO", "EU"],
}
