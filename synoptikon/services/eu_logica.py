"""Europese rechtslogica: wat een handeling *is* en wat dat betekent voor het nationale recht.

De catalogus (Cellar) zegt welke handelingen gelden; deze module zegt wat
daaruit volgt. Per soort (art. 288 VWEU) en variant (art. 290/291 VWEU) de
werking in de nationale rechtsorde, met de arresten waarop die regels
rusten; per handeling de afgeleide status: termijn verstreken, welke
lidstaten maatregelen meldden, en wat er voor de niet-lidstaten in
Synoptikon geldt (Brexit voor EN, autonome navolging voor CH).

Alles hier is algemeen leerstuk; het harmonisatieniveau per richtlijn
(`HARMONISATIE`) is een eigen aantekening met de bepaling waaruit het volgt.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from ..i18n import _, n_
from ..importers.cellar import LANDEN

BREXIT = date(2020, 12, 31)  # einde overgangsperiode: daarna geen omzettingsplicht meer voor het VK


@dataclass(frozen=True)
class Regel:
    tekst: str
    bron: str | None = None  # arrest of verdragsbepaling
    url: str | None = None


def _hvj(naam: str, zaak: str, ecli: str) -> tuple[str, str]:
    return f"HvJ {naam}, {zaak}, {ecli}", f"https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=ecli:{ecli}"


_VAN_GEND = _hvj("Van Gend & Loos", "26/62", "ECLI:EU:C:1963:1")
_COSTA = _hvj("Costa/ENEL", "6/64", "ECLI:EU:C:1964:66")
_VARIOLA = _hvj("Variola", "34/73", "ECLI:EU:C:1973:101")
_POLITI = _hvj("Politi", "43/71", "ECLI:EU:C:1971:122")
_MUNOZ = _hvj("Muñoz", "C-253/00", "ECLI:EU:C:2002:497")
_RATTI = _hvj("Ratti", "148/78", "ECLI:EU:C:1979:110")
_MARSHALL = _hvj("Marshall", "152/84", "ECLI:EU:C:1986:84")
_FACCINI = _hvj("Faccini Dori", "C-91/92", "ECLI:EU:C:1994:292")
_VON_COLSON = _hvj("Von Colson", "14/83", "ECLI:EU:C:1984:153")
_MARLEASING = _hvj("Marleasing", "C-106/89", "ECLI:EU:C:1990:395")
_PFEIFFER = _hvj("Pfeiffer", "C-397/01 e.a.", "ECLI:EU:C:2004:584")
_FRANCOVICH = _hvj("Francovich", "C-6/90 en C-9/90", "ECLI:EU:C:1991:428")
_WALLONIE = _hvj("Inter-Environnement Wallonie", "C-129/96", "ECLI:EU:C:1997:628")
_CIA = _hvj("CIA Security", "C-194/94", "ECLI:EU:C:1996:172")
_PUPINO = _hvj("Pupino", "C-105/03", "ECLI:EU:C:2005:386")
_POPLAWSKI = _hvj("Popławski II", "C-573/17", "ECLI:EU:C:2019:530")
_KOMMISSION_FR = _hvj("Commissie/Frankrijk", "C-52/00", "ECLI:EU:C:2002:252")

_VWEU288 = "https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:12016E288"

WERKING: dict[str, list[Regel]] = {
    "verordening": [
        Regel("Algemene strekking, verbindend in al haar onderdelen en rechtstreeks toepasselijk in elke lidstaat.", "art. 288 lid 2 VWEU", _VWEU288),
        Regel("Geen omzetting: de verordening geldt uit zichzelf. Nationale herhaling of omzetting is zelfs verboden, omdat zij de Europese herkomst en de uitlegbevoegdheid van het Hof verhult.", *_VARIOLA),
        Regel("Particulieren kunnen zich er rechtstreeks op beroepen, ook tegenover elkaar (horizontaal), voor zover de bepaling duidelijk en onvoorwaardelijk is.", *_POLITI),
        Regel("Nationale wetgeving is alleen nodig waar de verordening dat vraagt of ruimte laat: aanwijzen van toezichthouders, sancties, procedure en gebruik van open keuzes ('uitvoeringswet').", *_MUNOZ),
        Regel("Voorrang: strijdig nationaal recht blijft buiten toepassing, ook later recht.", *_COSTA),
    ],
    "richtlijn": [
        Regel("Verbindend ten aanzien van het te bereiken resultaat; vorm en middelen kiest de lidstaat.", "art. 288 lid 3 VWEU", _VWEU288),
        Regel("Omzetting vereist binnen de termijn, in bindende nationale voorschriften met voldoende rechtszekerheid; waar de richtlijn het voorschrijft, met een verwijzing naar de richtlijn.", None),
        Regel("Al vóór het einde van de termijn mag de lidstaat geen maatregelen nemen die het resultaat ernstig in gevaar brengen.", *_WALLONIE),
        Regel("Richtlijnconforme uitleg: de rechter legt het nationale recht zoveel mogelijk uit in het licht van tekst en doel van de richtlijn, het hele nationale recht in aanmerking genomen; niet contra legem.", *_VON_COLSON),
        Regel("Dat geldt ook voor nationaal recht dat ouder is dan de richtlijn.", *_MARLEASING),
        Regel("…en de rechter moet daarvoor de volle reikwijdte van de nationale uitlegmethoden benutten.", *_PFEIFFER),
        Regel("Na de termijn: verticale directe werking van duidelijke, onvoorwaardelijke bepalingen tegenover de staat (in ruime zin).", *_RATTI),
        Regel("Geen horizontale directe werking: een richtlijn schept uit zichzelf geen verplichtingen voor particulieren.", *_FACCINI),
        Regel("…ook niet als de wederpartij een particulier is en de staat te laat heeft omgezet.", *_MARSHALL),
        Regel("Uitzondering op het vorige: een bepaling die alleen het nationale recht onverbindend maakt (technische voorschriften die niet zijn gemeld) kan ook tussen particulieren worden ingeroepen.", *_CIA),
        Regel("Staatsaansprakelijkheid bij niet of onjuist omzetten, als de regel rechten verleent, de schending voldoende gekwalificeerd is en er causaal verband is.", *_FRANCOVICH),
    ],
    "kaderbesluit": [
        Regel("Derde pijler (oud art. 34 lid 2 sub b VEU): verbindend ten aanzien van het resultaat, uitdrukkelijk zonder rechtstreekse werking.", "oud art. 34 VEU", None),
        Regel("Wel kaderbesluitconforme uitleg van het nationale recht.", *_PUPINO),
        Regel("…maar die mag niet leiden tot uitleg contra legem; de rechter laat strijdig nationaal recht niet op grond van het kaderbesluit buiten toepassing.", *_POPLAWSKI),
        Regel("Na het Verdrag van Lissabon blijven kaderbesluiten gelden tot zij worden ingetrokken of gewijzigd; sinds 1-12-2014 volle bevoegdheid van Commissie en Hof.", "Protocol nr. 36, art. 9–10", None),
    ],
}

VARIANT: dict[str, Regel] = {
    "gedelegeerd": Regel(
        "Gedelegeerde handeling van de Commissie: vult niet-essentiële onderdelen van de basishandeling aan of wijzigt die, binnen de delegatie; "
        "Parlement en Raad kunnen bezwaar maken of de delegatie intrekken. Werkt verder als de soort waartoe ze behoort.",
        "art. 290 VWEU", "https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:12016E290"),
    "uitvoering": Regel(
        "Uitvoeringshandeling: waar eenvormige uitvoering nodig is, verleent de basishandeling de Commissie (of de Raad) uitvoeringsbevoegdheid, "
        "onder toezicht van comités van de lidstaten (comitologie, Verordening 182/2011). Uitvoering door de lidstaten blijft de regel.",
        "art. 291 VWEU", "https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX:12016E291"),
}

# Harmonisatieniveau van richtlijnen die in Synoptikon een rol spelen: celex → (niveau, grondslag).
# Eigen aantekening, niet uit Cellar.
HARMONISATIE: dict[str, tuple[str, str]] = {
    "31985L0374": ("maximum", "HvJ C-52/00 (Commissie/Frankrijk): de richtlijn laat buiten art. 15 en 16 geen ruimte voor strengere regels"),
    "31993L0013": ("minimum", "art. 8: strengere bepalingen toegestaan"),
    "32011L0083": ("maximum", "art. 4, met uitzonderingen die de richtlijn zelf noemt"),
    "32019L0771": ("maximum", "art. 4, met keuzes o.a. art. 10 lid 3 en 6, art. 12"),
    "32019L0770": ("maximum", "art. 4"),
    "32005L0029": ("maximum", "art. 3 lid 5 en art. 4 (volledige harmonisatie)"),
    "32008L0048": ("maximum", "art. 22 lid 1, voor wat de richtlijn regelt"),
    "32023L2225": ("maximum", "art. 42 lid 1, voor wat de richtlijn regelt"),
    "32015L2302": ("maximum", "art. 4"),
    "32011L0007": ("minimum", "art. 12 lid 3: gunstiger bepalingen voor de schuldeiser toegestaan"),
    "31986L0653": ("gemengd", "maximum, behalve de keuze tussen vergoeding en schadeloosstelling (art. 17)"),
    "32016L0943": ("minimum", "art. 1 lid 1: verdergaande bescherming toegestaan, behalve de opgesomde bepalingen"),
    "32000L0031": ("gemengd", "coördinatie; art. 3 (land van oorsprong) en art. 12–15 (aansprakelijkheid tussenpersonen) zijn dwingend"),
    "32014L0104": ("minimum", "art. 1 en overweging 4; regels over openbaarmaking (art. 5–8) deels maximum"),
    "32001L0023": ("minimum", "art. 8: gunstiger bepalingen voor werknemers toegestaan"),
    "32020L1828": ("minimum", "art. 1 lid 2: lidstaten mogen andere procedures behouden of invoeren"),
}


@dataclass
class Status:
    """Afgeleide status van één handeling in de stelsels van Synoptikon."""

    werking: list[Regel]
    variant: Regel | None
    harmonisatie: tuple[str, str] | None
    termijn_verstreken: bool | None
    per_stelsel: dict[str, str] = field(default_factory=dict)  # stelsel → één zin


def status(h, nims_per_stelsel: dict[str, int], omzet_per_stelsel: dict[str, int], vandaag: date | None = None) -> Status:
    vandaag = vandaag or date.today()
    omzetten = h.soort in ("richtlijn", "kaderbesluit")
    verstreken = (h.omzettingstermijn < vandaag) if (omzetten and h.omzettingstermijn) else None
    per: dict[str, str] = {}
    for land, code in LANDEN.items():
        n, eigen = nims_per_stelsel.get(code, 0), omzet_per_stelsel.get(code, 0)
        if code == "EN":
            per[code] = _brexit(h, n)
            continue
        if omzetten:
            if n:
                per[code] = n_("{n} omzettingsmaatregel gemeld", "{n} omzettingsmaatregelen gemeld", n)
            elif verstreken:
                per[code] = _("geen omzetting gemeld, terwijl de termijn verstreken is (of omzetting was niet nodig)")
            else:
                per[code] = _("nog geen omzetting gemeld; de termijn loopt")
        else:
            per[code] = n_("rechtstreeks toepasselijk; {n} uitvoeringsmaatregel gemeld", "rechtstreeks toepasselijk; {n} uitvoeringsmaatregelen gemeld", n) if n \
                else _("rechtstreeks toepasselijk; geen uitvoeringsmaatregelen gemeld")
        if eigen:
            per[code] += " · " + n_("{n} artikelkoppeling in Synoptikon", "{n} artikelkoppelingen in Synoptikon", eigen)
    per["CH"] = (_("geen lidstaat (ook niet van de EER); Unierecht geldt alleen via bilaterale verdragen of als 'autonomer Nachvollzug'")
                 + (" · " + n_("{n} artikelkoppeling in Synoptikon", "{n} artikelkoppelingen in Synoptikon", omzet_per_stelsel["CH"]) if omzet_per_stelsel.get("CH") else ""))
    return Status(WERKING.get(h.soort, []), VARIANT.get(h.variant), HARMONISATIE.get(h.celex), verstreken, per)


def _brexit(h, n: int) -> str:
    """Engeland & Wales: lidstaat tot 31-1-2020, gebonden tot het einde van de overgangsperiode (31-12-2020)."""
    datum = h.omzettingstermijn if h.soort != "verordening" else h.in_werking
    if datum and datum > BREXIT and not n:
        return _("na de Brexit vastgesteld of omgezet: geen gelding in het VK")
    if h.soort == "verordening":
        return _("als 'retained EU law' overgenomen op 31-12-2020, sinds 2024 'assimilated law' (Retained EU Law (Revocation and Reform) Act 2023), "
                 "tenzij ingetrokken; latere Europese wijzigingen gelden niet")
    if n:
        return n_("{n} omzettingsmaatregel van vóór de Brexit; die geldt als nationaal recht door, los van latere Europese wijzigingen",
                  "{n} omzettingsmaatregelen van vóór de Brexit; die gelden als nationaal recht door, los van latere Europese wijzigingen", n)
    return _("geen omzetting door het VK gemeld")
