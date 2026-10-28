"""Namen van EU-handelingen in de taal van de interface.

Intern heeft elke EU-wet één sleutel, de Nederlandse afkorting waaronder ze in Synoptikon geciteerd wordt: "VWEU",
"Rome I", "Richtlijn 93/13", "Verordening 2016/679". Die sleutel staat in `Wettekst.wet` en in de correspondentietabel.
Getoond wordt de naam in de taal van het verzoek (AEUV, TFUE, TFEU; DSGVO, RGPD, GDPR), en bij invoer wordt elke
schrijfwijze weer naar de sleutel teruggebracht ("Art. 34 AEUV", "Art. 6 DSGVO", "Verordnung (EG) Nr. 593/2008").
"""
from __future__ import annotations

import re

TALEN = ("nl", "de", "fr", "it", "en", "es")

# CELEX van de geconsolideerde verdragen (2016) → sleutel. De tekst komt als één document ("…/TXT").
VERDRAGEN = {"12016E": "VWEU", "12016M": "VEU", "12016P": "Handvest"}
VERDRAG_DATUM = "2016-06-07"  # PB C 202 (geconsolideerde versie; sindsdien niet gewijzigd)

# sleutel → korte naam per taal (ontbreekt een taal, dan de sleutel zelf)
KORT: dict[str, dict[str, str]] = {
    "VWEU": dict(nl="VWEU", de="AEUV", fr="TFUE", it="TFUE", en="TFEU", es="TFUE"),
    "VEU": dict(nl="VEU", de="EUV", fr="TUE", it="TUE", en="TEU", es="TUE"),
    "Handvest": dict(nl="Handvest", de="GRCh", fr="Charte", it="Carta", en="Charter", es="Carta"),
    "Rome I": dict(nl="Rome I", de="Rom I-VO", fr="Rome I", it="Roma I", en="Rome I", es="Roma I"),
    "Rome II": dict(nl="Rome II", de="Rom II-VO", fr="Rome II", it="Roma II", en="Rome II", es="Roma II"),
    "Brussel I-bis": dict(nl="Brussel I-bis", de="Brüssel Ia-VO", fr="Bruxelles I bis", it="Bruxelles I bis", en="Brussels I bis",
                          es="Bruselas I bis"),
    "Erfrechtverordening": dict(nl="Erfrechtverordening", de="EuErbVO", fr="Règlement successions", it="Regolamento successioni",
                                en="Succession Regulation", es="Reglamento de sucesiones"),
    "Insolventieverordening": dict(nl="Insolventieverordening", de="EuInsVO", fr="Règlement insolvabilité", it="Regolamento insolvenza",
                                   en="Insolvency Regulation", es="Reglamento de insolvencia"),
    "CISG": dict(nl="CISG", de="CISG", fr="CVIM", it="CISG", en="CISG", es="CISG"),
}

# Volledige titel van de verdragen per taal (de andere handelingen hebben hun titel uit de Cellar, `eu_titel`).
TITEL: dict[str, dict[str, str]] = {
    "VWEU": dict(nl="Verdrag betreffende de werking van de Europese Unie", de="Vertrag über die Arbeitsweise der Europäischen Union",
                 fr="Traité sur le fonctionnement de l'Union européenne", it="Trattato sul funzionamento dell'Unione europea",
                 en="Treaty on the Functioning of the European Union", es="Tratado de Funcionamiento de la Unión Europea"),
    "VEU": dict(nl="Verdrag betreffende de Europese Unie", de="Vertrag über die Europäische Union", fr="Traité sur l'Union européenne",
                it="Trattato sull'Unione europea", en="Treaty on European Union", es="Tratado de la Unión Europea"),
    "Handvest": dict(nl="Handvest van de grondrechten van de Europese Unie", de="Charta der Grundrechte der Europäischen Union",
                     fr="Charte des droits fondamentaux de l'Union européenne", it="Carta dei diritti fondamentali dell'Unione europea",
                     en="Charter of Fundamental Rights of the European Union", es="Carta de los Derechos Fundamentales de la Unión Europea"),
}

# Handelingen met een eigen sleutel in Synoptikon (de rest: soort + nummer).
BIJNAAM = {"32008R0593": "Rome I", "32007R0864": "Rome II", "32012R1215": "Brussel I-bis", "32012R0650": "Erfrechtverordening",
           "32015R0848": "Insolventieverordening"}

# Gangbare afkortingen van handelingen zonder eigen sleutel: CELEX → naam per taal.
ROEPNAAM: dict[str, dict[str, str]] = {
    "32016R0679": dict(nl="AVG", de="DSGVO", fr="RGPD", it="GDPR", en="GDPR", es="RGPD"),
    "32024R1689": dict(nl="AI-verordening", de="KI-VO", fr="RIA", it="AI Act", en="AI Act", es="RIA"),
    "32022R2065": dict(nl="DSA", de="DSA", fr="DSA", it="DSA", en="DSA", es="DSA"),
    "32022R1925": dict(nl="DMA", de="DMA", fr="DMA", it="DMA", en="DMA", es="DMA"),
    "32022R2554": dict(nl="DORA", de="DORA", fr="DORA", it="DORA", en="DORA", es="DORA"),
    "32023R2854": dict(nl="Dataverordening", de="Data Act", fr="Data Act", it="Data Act", en="Data Act", es="Data Act"),
    "32022R0868": dict(nl="DGA", de="DGA", fr="DGA", it="DGA", en="DGA", es="DGA"),
    "32023R1114": dict(nl="MiCA", de="MiCAR", fr="MiCA", it="MiCA", en="MiCA", es="MiCA"),
    "32014R0910": dict(nl="eIDAS", de="eIDAS-VO", fr="eIDAS", it="eIDAS", en="eIDAS", es="eIDAS"),
    "32022L2555": dict(nl="NIS2", de="NIS-2-RL", fr="NIS 2", it="NIS 2", en="NIS2", es="NIS2"),
    "32019L0790": dict(nl="DSM-richtlijn", de="DSM-RL", fr="Directive DAMUN", it="Direttiva DSM", en="DSM Directive", es="Directiva DAMUD"),
    "32006L0123": dict(nl="Dienstenrichtlijn", de="DLRL", fr="Directive services", it="Direttiva servizi", en="Services Directive",
                       es="Directiva de servicios"),
    "32004R0805": dict(nl="EET-verordening", de="EuVTVO", fr="Règlement TEE", it="Regolamento TEE", en="EEO Regulation", es="Reglamento TEE"),
    "32007R1393": dict(nl="Betekeningsverordening", de="EuZVO", fr="Règlement signification", it="Regolamento notificazione",
                       en="Service Regulation", es="Reglamento de notificación"),
    "32019R1111": dict(nl="Brussel II-ter", de="Brüssel IIb-VO", fr="Bruxelles II ter", it="Bruxelles II ter", en="Brussels II ter",
                       es="Bruselas II ter"),
    "32001R0044": dict(nl="Brussel I", de="EuGVVO a.F.", fr="Bruxelles I", it="Bruxelles I", en="Brussels I", es="Bruselas I"),
}

SOORT = {
    "verordening": dict(nl="Verordening", de="Verordnung", fr="Règlement", it="Regolamento", en="Regulation", es="Reglamento"),
    "richtlijn": dict(nl="Richtlijn", de="Richtlinie", fr="Directive", it="Direttiva", en="Directive", es="Directiva"),
    "kaderbesluit": dict(nl="Kaderbesluit", de="Rahmenbeschluss", fr="Décision-cadre", it="Decisione quadro", en="Framework Decision",
                         es="Decisión marco"),
}
_SOORT_KORT = {"verordening": dict(de="VO"), "richtlijn": dict(de="RL")}
SLEUTEL_SOORT = {v["nl"]: k for k, v in SOORT.items()}  # "Verordening" → "verordening"

PREAMBULE = dict(nl="Preambule", de="Präambel", fr="Préambule", it="Preambolo", en="Preamble", es="Preámbulo")


def sleutel(celex: str, soort: str | None, nummer: str | None) -> str:
    """De sleutel van een handeling: verdrag, bijnaam, of "Verordening 2016/679"."""
    if celex[:6] in VERDRAGEN:
        return VERDRAGEN[celex[:6]]
    if celex in BIJNAAM:
        return BIJNAAM[celex]
    if soort in SOORT and nummer:
        return f"{SOORT[soort]['nl']} {nummer}"
    return celex


def _soort_nummer(wet: str) -> tuple[str, str] | None:
    m = re.fullmatch(r"(Verordening|Richtlijn|Kaderbesluit) (\d+/\d+)", wet or "")
    return (SLEUTEL_SOORT[m.group(1)], m.group(2)) if m else None


_CELEX_VAN: dict[str, str] = {}  # sleutel → CELEX, gevuld door `laad`


def celex_van(wet: str) -> str | None:
    return _CELEX_VAN.get(wet)


def kort(wet: str | None, taal: str) -> str | None:
    """Korte naam in de gevraagde taal: "VWEU" → "AEUV" (de), "Verordening 2016/679" → "DSGVO" (de)."""
    if not wet:
        return wet
    if wet in KORT:
        return KORT[wet].get(taal, wet)
    celex = _CELEX_VAN.get(wet)
    if celex in ROEPNAAM:
        return ROEPNAAM[celex].get(taal, wet)
    sn = _soort_nummer(wet)
    if sn:
        soort, nummer = sn
        woord = _SOORT_KORT.get(soort, {}).get(taal) or SOORT[soort].get(taal, SOORT[soort]["nl"])
        return f"{woord} {nummer}"
    return wet


def titel(wet: str | None, taal: str) -> str | None:
    """Volledige titel van een verdrag in de gevraagde taal (andere handelingen: `eu_titel`)."""
    return TITEL.get(wet or "", {}).get(taal)


# --- herkennen bij invoer ---------------------------------------------------------

_SOORT_WOORDEN = {
    "verordening": r"Verordening|Verordnung|VO|Règlement|Reglement|Regolamento|Regulation|Reglamento",
    "richtlijn": r"Richtlijn|Richtlinie|RL|Directive|Direttiva|Directiva",
    "kaderbesluit": r"Kaderbesluit|Rahmenbeschluss|Décision-cadre|Decisione quadro|Framework Decision|Decisión marco",
}
_NUMMER = r"(?:\((?:EU|EG|EWG|EEG|CE|CEE|UE|EC|EEC)\)\s*)?(?:(?:Nr\.|nr\.|n[°o.]|No\.?|n\.)\s*)?(\d{1,4})\s*/\s*(\d{1,4})(?:\s*/\s*(?:EU|EG|EWG|EEG|CE|CEE|UE|EC|EEC|JBZ|JI|JAI))?"
_GENERIEK = [(soort, re.compile(rf"(?<!\w)(?:{woorden})\s*{_NUMMER}(?!\d)", re.I)) for soort, woorden in _SOORT_WOORDEN.items()]
_ALIASSEN: list[tuple[re.Pattern, str]] = []
_NUMMERS: dict[tuple[str, str], str] = {}  # (soort, nummer) → sleutel, gevuld door `laad`


def _bouw_aliassen() -> None:
    namen: dict[str, str] = {}
    for wet, per_taal in KORT.items():
        namen[wet.lower()] = wet
        for n in per_taal.values():
            namen.setdefault(n.lower(), wet)
    for celex, per_taal in ROEPNAAM.items():
        wet = next((w for w, c in _CELEX_VAN.items() if c == celex), None)
        if wet:
            for n in per_taal.values():
                namen.setdefault(n.lower(), wet)
    # oude schrijfwijzen en volledige verdragsnamen
    for wet, per_taal in TITEL.items():
        for n in per_taal.values():
            namen.setdefault(n.lower(), wet)
    for n, wet in (("EG-Vertrag", "VWEU"), ("Charta", "Handvest"), ("Grundrechtecharta", "Handvest"), ("EU-Grundrechtecharta", "Handvest"),
                   ("Rom I", "Rome I"), ("Rom II", "Rome II"), ("Brüssel Ia", "Brussel I-bis"), ("EuGVVO", "Brussel I-bis"),
                   ("Brussels Ia", "Brussel I-bis"), ("Bruxelles Ibis", "Brussel I-bis")):
        namen.setdefault(n.lower(), wet)
    _ALIASSEN[:] = [(re.compile(r"(?<![\w.])" + re.escape(n).replace(r"\ ", r"\s*") + r"(?![\w-])", re.I), wet)
                    for n, wet in sorted(namen.items(), key=lambda p: len(p[0]), reverse=True)]


def laad(paren: list[tuple[str, str | None, str | None]]) -> None:
    """Zet de catalogus (celex, soort, nummer) in het geheugen, voor `kort` en het herkennen van nummers."""
    _CELEX_VAN.clear()
    _NUMMERS.clear()
    for celex, soort, nummer in paren:
        w = sleutel(celex, soort, nummer)
        _CELEX_VAN.setdefault(w, celex)
        if soort and nummer:
            _NUMMERS.setdefault((soort, nummer), w)
    for celex, w in BIJNAAM.items():
        _CELEX_VAN.setdefault(w, celex)
    for celex, w in VERDRAGEN.items():
        _CELEX_VAN.setdefault(w, celex)
    _bouw_aliassen()


def herken_wet(tekst: str) -> tuple[str | None, str]:
    """Zoekt een EU-wet in de tekst; geeft (sleutel, tekst zonder de wet) of (None, tekst)."""
    if not _ALIASSEN:
        _bouw_aliassen()
    for soort, patroon in _GENERIEK:
        m = patroon.search(tekst)
        if m:
            a, b = m.group(1), m.group(2)
            # vóór 2015 bij verordeningen nummer/jaar, daarna jaar/nummer; richtlijnen altijd jaar/nummer
            kandidaten = [f"{a}/{b}", f"{b}/{a}"]
            wet = next((_NUMMERS[(soort, k)] for k in kandidaten if (soort, k) in _NUMMERS), None)
            if wet is None:
                wet = f"{SOORT[soort]['nl']} {a}/{b}"
            return wet, tekst[: m.start()] + " " + tekst[m.end():]
    for patroon, wet in _ALIASSEN:
        m = patroon.search(tekst)
        if m:
            return wet, tekst[: m.start()] + " " + tekst[m.end():]
    return None, tekst


def noemt_eu(tekst: str) -> bool:
    return herken_wet(tekst)[0] is not None
