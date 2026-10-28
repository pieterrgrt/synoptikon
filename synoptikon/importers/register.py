"""Register van alle wetboeken en wetten die Synoptikon per stelsel ophaalt.

Eén regel per wet: stelsel, citeerafkorting (`None` = de hoofdcodificatie,
die uit meer delen kan bestaan, zoals de boeken van het BW), importer, id bij
de bron, titel en of de systematiekboom uit de import mag worden aangevuld.
`synoptikon import-alles` loopt dit register af; `synoptikon import` blijft
voor losse wetten.

Bronnen per stelsel en waarom:

* NL: wetten.overheid.nl (BWB-XML), geconsolideerd.
* DE: gesetze-im-internet.de (XML), geconsolideerd.
* FR: LEGI-dump van de DILA (licence ouverte), geconsolideerd; Légifrance
  zelf weigert geautomatiseerde toegang en de PISTE-API vraagt een sleutel.
* IT: Normattiva (Akoma Ntoso), geconsolideerd ("multivigente" op vandaag).
* ES: BOE, open-data-API, geconsolideerd.
* CH: Fedlex (Akoma Ntoso), geconsolideerd, laatste stand die vandaag geldt.
* BE: Belgisch Staatsblad via de spiegel etaamb.openjustice.be, *niet*
  geconsolideerd (Justel weigert geautomatiseerde toegang). Boek 6
  (wet van 7 februari 2024) staat niet in de spiegel; Boek 7, 9 en 10 en
  het oud BW ontbreken ook.
* EN: legislation.gov.uk (CLML), geconsolideerd ("latest available").
* GR: lawspot.gr, geconsolideerd (de enige open bron met verwerkte wijzigingen; het Staatsblad geeft alleen de
  oorspronkelijke ΦΕΚ als pdf). ΚΠολΔ en ΚΠΔ staan daar achter een login en ontbreken dus.
* US en AU: geen open, machineleesbare bron voor UCC, Restatements of ACL
  die zonder scraping werkt; alleen de systematiek.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Wet:
    stelsel: str
    wet: str | None
    importer: str  # bwb · gii · legi · normattiva · boe · fedlex · etaamb · uk · lawspot
    id: str
    titel: str
    systematiek: bool = False


WETTEN: list[Wet] = [
    # NL: de tien boeken van het BW
    *[Wet("NL", None, "bwb", i, f"Burgerlijk Wetboek Boek {b}") for b, i in [
        ("1", "BWBR0002656"), ("2", "BWBR0003045"), ("3", "BWBR0005291"), ("4", "BWBR0002761"), ("5", "BWBR0005288"),
        ("6", "BWBR0005289"), ("7", "BWBR0005290"), ("7A", "BWBR0006000"), ("8", "BWBR0005034"), ("10", "BWBR0030068")]],
    # DE
    Wet("DE", None, "gii", "bgb", "Bürgerliches Gesetzbuch"),
    Wet("DE", "EGBGB", "gii", "bgbeg", "Einführungsgesetz zum Bürgerlichen Gesetzbuche", systematiek=True),
    Wet("DE", "HGB", "gii", "hgb", "Handelsgesetzbuch", systematiek=True),
    Wet("DE", "ProdHaftG", "gii", "prodhaftg", "Produkthaftungsgesetz", systematiek=True),
    Wet("DE", "UWG", "gii", "uwg_2004", "Gesetz gegen den unlauteren Wettbewerb", systematiek=True),
    # FR
    Wet("FR", None, "legi", "LEGITEXT000006070721", "Code civil", systematiek=True),
    Wet("FR", "C. consom.", "legi", "LEGITEXT000006069565", "Code de la consommation", systematiek=True),
    Wet("FR", "C. com.", "legi", "LEGITEXT000005634379", "Code de commerce", systematiek=True),
    # IT
    Wet("IT", None, "normattiva", "urn:nir:stato:regio.decreto:1942-03-16;262", "Codice civile"),
    Wet("IT", "c. cons.", "normattiva", "urn:nir:stato:decreto.legislativo:2005-09-06;206", "Codice del consumo", systematiek=True),
    # ES
    Wet("ES", None, "boe", "BOE-A-1889-4763", "Código Civil"),
    Wet("ES", "TRLGDCU", "boe", "BOE-A-2007-20555", "Texto refundido de la Ley General para la Defensa de los Consumidores y Usuarios", systematiek=True),
    Wet("ES", "CCom", "boe", "BOE-A-1885-6627", "Código de Comercio", systematiek=True),
    # CH
    Wet("CH", None, "fedlex", "cc/24/233_245_233", "Schweizerisches Zivilgesetzbuch"),
    Wet("CH", "OR", "fedlex", "cc/27/317_321_377", "Obligationenrecht"),
    Wet("CH", "IPRG", "fedlex", "cc/1988/1776_1776_1776", "Bundesgesetz über das Internationale Privatrecht", systematiek=True),
    Wet("CH", "PrHG", "fedlex", "cc/1993/3122_3122_3122", "Produktehaftpflichtgesetz", systematiek=True),
    # GR: de ΑΚ en de wetten eromheen (lawspot.gr)
    Wet("GR", None, "lawspot", "astikos-kodikas", "Αστικός Κώδικας"),
    *[Wet("GR", afk, "lawspot", slug, t, systematiek=True) for afk, slug, t in [
        ("Συντ.", "syntagma-tis-ellados", "Σύνταγμα της Ελλάδος"),
        ("ν. 2251/1994", "nomos-2251-1994", "Ν. 2251/1994 για την προστασία των καταναλωτών"),
        ("ν. 4548/2018", "nomos-4548-2018", "Ν. 4548/2018 Αναμόρφωση του δικαίου των ανωνύμων εταιρειών"),
        ("ν. 3190/1955", "nomos-3190-1955", "Ν. 3190/1955 περί εταιρειών περιωρισμένης ευθύνης"),
        ("ν. 4072/2012", "nomos-4072-2012", "Ν. 4072/2012 (ΙΚΕ, προσωπικές εταιρείες, σήματα)"),
        ("ν. 2190/1920", "nomos-2190-1920", "Κ.Ν. 2190/1920 περί ανωνύμων εταιρειών"),
        ("ΕμπΝ", "emporikos-nomos", "Εμπορικός Νόμος"),
        ("ν. 3869/2010", "nomos-3869-2010", "Ν. 3869/2010 Ρύθμιση των οφειλών υπερχρεωμένων φυσικών προσώπων"),
        ("ν. 4624/2019", "nomos-4624-2019", "Ν. 4624/2019 Αρχή Προστασίας Δεδομένων Προσωπικού Χαρακτήρα"),
        ("ΠΚ", "poinikos-kodikas", "Ποινικός Κώδικας"),
    ]],
    # BE: het nieuwe BW, boek voor boek (tekst zoals bekendgemaakt)
    Wet("BE", None, "etaamb", "wet-van-28-april-2022_n2022032057", "Burgerlijk Wetboek Boek 1 · Algemene bepalingen", systematiek=True),
    Wet("BE", None, "etaamb", "wet-van-19-januari-2022_n2022030600", "Burgerlijk Wetboek Boek 2 titel 3 en Boek 4 · Relatievermogensrecht, nalatenschappen", systematiek=True),
    Wet("BE", None, "etaamb", "wet-van-04-februari-2020_n2020020347", "Burgerlijk Wetboek Boek 3 · Goederen", systematiek=True),
    Wet("BE", None, "etaamb", "wet-van-28-april-2022_n2022032058", "Burgerlijk Wetboek Boek 5 · Verbintenissen", systematiek=True),
    Wet("BE", None, "etaamb", "wet-van-13-april-2019_n2019012168", "Burgerlijk Wetboek Boek 8 · Bewijs", systematiek=True),
    # EN: de wetten die het contracten-, goederen- en aansprakelijkheidsrecht dragen
    *[Wet("EN", afk, "uk", i, t, systematiek=True) for afk, i, t in [
        ("SGA 1979", "ukpga/1979/54", "Sale of Goods Act 1979"),
        ("SGSA 1982", "ukpga/1982/29", "Supply of Goods and Services Act 1982"),
        ("CRA 2015", "ukpga/2015/15", "Consumer Rights Act 2015"),
        ("UCTA 1977", "ukpga/1977/50", "Unfair Contract Terms Act 1977"),
        ("MA 1967", "ukpga/1967/7", "Misrepresentation Act 1967"),
        ("C(RTP)A 1999", "ukpga/1999/31", "Contracts (Rights of Third Parties) Act 1999"),
        ("LR(FC)A 1943", "ukpga/Geo6/6-7/40", "Law Reform (Frustrated Contracts) Act 1943"),
        ("LA 1980", "ukpga/1980/58", "Limitation Act 1980"),
        ("CPA 1987", "ukpga/1987/43", "Consumer Protection Act 1987"),
        ("OLA 1957", "ukpga/Eliz2/5-6/31", "Occupiers' Liability Act 1957"),
        ("LPA 1925", "ukpga/Geo5/15-16/20", "Law of Property Act 1925"),
    ]],
]


def haal_op(w: Wet, legi_map: str | None = None):
    """Geparseerd object voor één registerregel."""
    if w.importer == "bwb":
        from . import bwb
        return bwb.haal_op(w.id)
    if w.importer == "gii":
        from . import gii
        return gii.haal_op(w.id)
    if w.importer == "legi":
        from pathlib import Path

        from . import ImportOvergeslagen, legi
        if not legi_map:
            raise ImportOvergeslagen(f"{w.titel}: geef --legi <map> (eerst scripts/legi_ophalen.sh <map>)")
        return legi.parse_map(Path(legi_map), w.id, titel=w.titel)
    if w.importer == "normattiva":
        from . import normattiva
        return normattiva.haal_op(w.id, titel=w.titel, deel="CODICE CIVILE" if w.wet is None else None)
    if w.importer == "boe":
        from . import boe
        return boe.haal_op(w.id, titel=w.titel)
    if w.importer == "fedlex":
        from . import fedlex
        return fedlex.haal_op(w.id, titel=w.titel)
    if w.importer == "etaamb":
        from . import etaamb
        return etaamb.haal_op(w.id, titel=w.titel)
    if w.importer == "lawspot":
        from . import lawspot
        g = lawspot.haal_op(w.id)
        g.titel = w.titel
        return g
    if w.importer == "uk":
        from . import legislation_uk
        return legislation_uk.haal_op(w.id, titel=w.titel)
    # Importers van de regio-uitbreidingen (register_<regio>.py): elke module heeft `haal_op(id, titel=…)`.
    from ..plugins import importer
    try:
        mod = importer(w.importer)
    except ModuleNotFoundError:
        raise ValueError(f"Onbekende importer {w.importer}") from None
    return mod.haal_op(w.id, titel=w.titel)


def _uitbreidingen() -> None:
    """Registerregels uit `register_<regio>.py` (elk met een lijst `WETTEN`) achter de vaste regels."""
    from ..plugins import modules
    for m in modules(__package__, "register_"):
        WETTEN.extend(m.WETTEN)


_uitbreidingen()
