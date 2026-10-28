"""Artikelverwijzingen herkennen, ordenen en in de systematiek plaatsen.

Elk stelsel heeft zijn eigen nummering en citeerwijze:

* **NL** (BW): `boek:nummer`, met letters (`6:230a`, `7A:1576`). Een
  bereik loopt nooit over een boekgrens.
* **BE** (nieuw BW, sinds 2020): `boek.nummer` (`5.69`, `3.94`; Boek 2
  Titel 3 drieledig: `2.3.16`). Het oud BW, nog geldend voor wat niet
  hercodificeerd is, telt doorlopend (`1582`, `2262bis`); het WER kent een
  Romeins boeknummer (`VI.37`), het WVV een dubbele punt (`2:56`).
* **DE** (BGB): `§ 929`, met letters (`§ 312k`). Leden heten `Abs.`, zinnen `S.`.
* **CH** (ZGB en OR, twee gelijkwaardige wetboeken): `Art. 41 OR`,
  `Art. 714 ZGB`, met letters (`Art. 6a`, `Art. 418v`).
* **FR** (Code civil): `1112`, `1112-1`, `1231-7`; andere codes ook met
  `L`/`R`/`D` vooraf (`L217-3`). Het streepje hoort bij het nummer, dus een
  bereik gebruikt altijd een en-dash (`1101–1231-7`).
* **IT** (Codice civile): `1337`, `1469-bis`, `2545-octiesdecies`.
* **ES** (Código civil): `1902`, `94 bis`.
* **EN**, **AU** (common law): geen codificatie; een `section` van een wet,
  `s 17 SGA 1979`, `s 18 ACL`, leden tussen haakjes (`s 2(1)(a)`).
* **US**: `UCC § 2-401`, `Rest. 2d Contracts § 90`, `La. C.C. art. 2315`.
* **EU**: `art. 6 Rome I`, `art. 101 VWEU`, `art. 2:301 PECL`, `art. II.-3:301 DCFR`.

Een `Ref` is (stelsel, wet, nummer[, tot], detail). `wet` is de afkorting
waaronder het artikel geciteerd wordt; `None` betekent de hoofdcodificatie
(BW, BGB, ZGB, C. civ., c.c., CC). Common-law-stelsels hebben geen
hoofdcodificatie en citeren altijd met een wet. Een systematiek bestaat per
(stelsel, wet): de boom van het BW, maar ook die van het OR, de UCC of de
Sale of Goods Act.
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Iterable
from urllib.parse import quote

from ..i18n import _ as vertaal
from ..i18n import taal as huidige_taal
from . import eunamen

_LATIJN = ["bis", "ter", "quater", "quinquies", "sexies", "septies", "octies", "novies", "decies",
           "undecies", "duodecies", "terdecies", "quaterdecies", "quinquiesdecies", "sexiesdecies",
           "septiesdecies", "octiesdecies"]
_LATIJN_WAARDE = {w: i + 2 for i, w in enumerate(_LATIJN)}
# Italiaanse codes tellen verder: 135-quindecies … 135-duodevicies, 135-vicies, 135-vicies-semel, 135-vicies-ter.
_LATIJN_WAARDE.update({"quindecies": 15, "sexdecies": 16, "duodevicies": 18, "undevicies": 19, "vicies": 20, "semel": 1})
_LAT = "|".join(sorted(_LATIJN_WAARDE, key=len, reverse=True))


@dataclass(frozen=True)
class Regels:
    """Citeerwijze en nummering van één stelsel."""

    hoofdwet: str | None  # None: geen codificatie (common law, EU)
    andere: tuple[str, ...] = ()  # bekende andere wetten, als afkorting
    stijl: str = "art"  # art · Art · § · s · us
    nummer: str = r"\d+[a-z]{0,3}"  # regex voor één artikelnummer
    namen: dict = field(default_factory=dict)  # afkorting → volledige titel


REGELS: dict[str, Regels] = {
    "NL": Regels("BW", ("Rv", "WvK", "Fw", "Aw", "Hw", "Wft", "Rome I")),
    "BE": Regels(
        "BW",
        ("oud BW", "WER", "WVV", "Ger.W.", "Hyp.W.", "Pandwet", "WIPR", "Woninghuurwet", "Handelshuurwet", "W.Verz."),
        nummer=rf"(?:[IVXL]+\.)?\d+(?:[.:/]\d+)*(?:\s?(?:{_LAT}))?",
        namen={"BW": "Burgerlijk Wetboek (2019)", "oud BW": "Oud Burgerlijk Wetboek (1804)", "WER": "Wetboek van economisch recht",
               "WVV": "Wetboek van vennootschappen en verenigingen", "Ger.W.": "Gerechtelijk Wetboek", "Hyp.W.": "Hypotheekwet 1851",
               "Pandwet": "Wet van 11 juli 2013 betreffende de zakelijke zekerheden op roerende goederen", "WIPR": "Wetboek van internationaal privaatrecht",
               "W.Verz.": "Wet van 4 april 2014 betreffende de verzekeringen"},
    ),
    "DE": Regels("BGB", ("HGB", "ZPO", "EGBGB", "ProdHaftG", "AnfG", "ErbbauRG", "InsO", "GmbHG", "AktG", "StVG", "UWG", "VVG", "WEG", "BeurkG"), stijl="§"),
    "CH": Regels(
        "ZGB",
        ("OR", "SchKG", "IPRG", "ZPO", "PrHG", "VVG", "KKG", "UWG", "SVG"),
        stijl="Art",
        nummer=rf"\d+[a-z]{{0,3}}(?:\s?(?:{_LAT}))?",
        namen={"ZGB": "Schweizerisches Zivilgesetzbuch", "OR": "Obligationenrecht", "SchKG": "Bundesgesetz über Schuldbetreibung und Konkurs",
               "IPRG": "Bundesgesetz über das Internationale Privatrecht", "PrHG": "Produktehaftpflichtgesetz", "KKG": "Konsumkreditgesetz"},
    ),
    "GR": Regels(
        "ΑΚ",
        ("ΕισΝΑΚ", "Συντ.", "ΠΚ", "ΕμπΝ", "ν. 2251/1994", "ν. 2190/1920", "ν. 3190/1955", "ν. 4548/2018", "ν. 4072/2012", "ν. 3869/2010",
         "ν. 4624/2019", "ΚΠολΔ"),
        nummer=r"\d+[Α-ΩA-Z]{0,2}",
        namen={"ΑΚ": "Αστικός Κώδικας (1946)", "Συντ.": "Σύνταγμα της Ελλάδος (1975)", "ΠΚ": "Ποινικός Κώδικας (2019)",
               "ΕμπΝ": "Εμπορικός Νόμος (1835)", "ν. 2251/1994": "Προστασία των καταναλωτών", "ν. 2190/1920": "Ανώνυμες εταιρείες (oud)",
               "ν. 3190/1955": "Εταιρείες περιορισμένης ευθύνης (ΕΠΕ)", "ν. 4548/2018": "Ανώνυμες εταιρείες",
               "ν. 4072/2012": "Ιδιωτική κεφαλαιουχική εταιρεία, προσωπικές εταιρείες, σήματα", "ν. 3869/2010": "Υπερχρεωμένα νοικοκυριά",
               "ν. 4624/2019": "Προστασία δεδομένων (uitvoering AVG)", "ΚΠολΔ": "Κώδικας Πολιτικής Δικονομίας", "ΕισΝΑΚ": "Εισαγωγικός Νόμος του Αστικού Κώδικα"},
    ),
    "FR": Regels("C. civ.", ("C. consom.", "C. com.", "C. trav.", "C. rur.", "C. proc. civ.", "C. assur.", "Loi 1901", "Loi 1985", "Loi 1987")),
    "IT": Regels(
        "c.c.",
        ("disp. att. c.c.", "c.p.c.", "c. cons.", "CCII", "c. ass.", "l. 218/1995", "l. 184/1983", "l. 898/1970", "l. 76/2016", "l. 392/1978", "Cost."),
        nummer=rf"\d+(?:\s?-?\s?(?:{_LAT})(?:-(?:{_LAT}))?)?",
        namen={"c.c.": "Codice civile (1942)", "c.p.c.": "Codice di procedura civile", "c. cons.": "Codice del consumo (d.lgs. 206/2005)",
               "CCII": "Codice della crisi d'impresa e dell'insolvenza (d.lgs. 14/2019)", "c. ass.": "Codice delle assicurazioni private",
               "l. 218/1995": "Riforma del sistema italiano di diritto internazionale privato", "l. 184/1983": "Diritto del minore ad una famiglia (adozione)",
               "l. 898/1970": "Disciplina dei casi di scioglimento del matrimonio", "l. 76/2016": "Unioni civili e convivenze (legge Cirinnà)"},
    ),
    "ES": Regels(
        "CC",
        ("CCom", "TRLGDCU", "LEC", "LH", "LPH", "LSC", "LAU", "LCGC", "LCS", "TRLC", "LJV", "CE"),
        nummer=rf"\d+(?:\s?(?:{_LAT}))?",
        namen={"CC": "Código Civil (1889)", "CCom": "Código de Comercio (1885)", "TRLGDCU": "Texto refundido de la Ley General para la Defensa de los Consumidores y Usuarios (RDL 1/2007)",
               "LEC": "Ley de Enjuiciamiento Civil (Ley 1/2000)", "LH": "Ley Hipotecaria (1946)", "LSC": "Ley de Sociedades de Capital (RDL 1/2010)",
               "LAU": "Ley de Arrendamientos Urbanos (Ley 29/1994)", "LCGC": "Ley sobre Condiciones Generales de la Contratación (Ley 7/1998)",
               "LCS": "Ley de Contrato de Seguro (Ley 50/1980)", "TRLC": "Texto refundido de la Ley Concursal (RDL 1/2020)"},
    ),
    "EN": Regels(
        None,
        ("SGA 1979", "SGSA 1982", "CRA 2015", "MA 1967", "UCTA 1977", "LA 1980", "CPA 1987", "C(RTP)A 1999", "LPA 1925", "LRA 2002",
         "LP(MP)A 1989", "TOLATA 1996", "MCA 1973", "CA 1989", "ACA 2002", "I(PFD)A 1975", "AEA 1925", "WA 1837", "CA 2006", "IA 1986",
         "PA 1890", "LR(FC)A 1943", "LR(CN)A 1945", "OLA 1957", "CL(C)A 1978", "FA 1889", "T(IG)A 1977", "MCA 2005", "FLRA 1969",
         "HFEA 2008", "LP(I)A 1998", "SCA 1981", "AA 1971", "FAA 1976", "CPA 2004", "DMPA 1973", "BEA 1882", "Statute of Frauds 1677"),
        stijl="s",
        nummer=r"\d+[A-Z]{0,3}",
        namen={"SGA 1979": "Sale of Goods Act 1979", "SGSA 1982": "Supply of Goods and Services Act 1982", "CRA 2015": "Consumer Rights Act 2015",
               "MA 1967": "Misrepresentation Act 1967", "UCTA 1977": "Unfair Contract Terms Act 1977", "LA 1980": "Limitation Act 1980",
               "CPA 1987": "Consumer Protection Act 1987", "C(RTP)A 1999": "Contracts (Rights of Third Parties) Act 1999",
               "LPA 1925": "Law of Property Act 1925", "LRA 2002": "Land Registration Act 2002",
               "LP(MP)A 1989": "Law of Property (Miscellaneous Provisions) Act 1989", "TOLATA 1996": "Trusts of Land and Appointment of Trustees Act 1996",
               "MCA 1973": "Matrimonial Causes Act 1973", "CA 1989": "Children Act 1989", "ACA 2002": "Adoption and Children Act 2002",
               "I(PFD)A 1975": "Inheritance (Provision for Family and Dependants) Act 1975", "AEA 1925": "Administration of Estates Act 1925",
               "WA 1837": "Wills Act 1837", "CA 2006": "Companies Act 2006", "IA 1986": "Insolvency Act 1986", "PA 1890": "Partnership Act 1890",
               "LR(FC)A 1943": "Law Reform (Frustrated Contracts) Act 1943", "LR(CN)A 1945": "Law Reform (Contributory Negligence) Act 1945",
               "OLA 1957": "Occupiers' Liability Act 1957", "CL(C)A 1978": "Civil Liability (Contribution) Act 1978", "FA 1889": "Factors Act 1889",
               "T(IG)A 1977": "Torts (Interference with Goods) Act 1977", "MCA 2005": "Mental Capacity Act 2005", "FLRA 1969": "Family Law Reform Act 1969",
               "HFEA 2008": "Human Fertilisation and Embryology Act 2008", "LP(I)A 1998": "Late Payment of Commercial Debts (Interest) Act 1998",
               "SCA 1981": "Senior Courts Act 1981", "AA 1971": "Animals Act 1971", "FAA 1976": "Fatal Accidents Act 1976",
               "CPA 2004": "Civil Partnership Act 2004", "DMPA 1973": "Domicile and Matrimonial Proceedings Act 1973", "BEA 1882": "Bills of Exchange Act 1882"},
    ),
    "US": Regels(
        None,
        ("UCC", "Rest. 2d Contracts", "Rest. 2d Torts", "Rest. 3d Torts: Prod. Liab.", "Rest. 3d Torts: PEH", "Rest. 3d Torts: Apport.",
         "Rest. 3d Restitution", "Rest. 3d Agency", "Rest. 3d Property: Wills", "Rest. 3d Trusts", "UPC", "UMDA", "UPA 2017",
         "Cal. Civ. Code", "Cal. Fam. Code", "La. C.C.", "11 U.S.C.", "15 U.S.C.", "RULLCA", "RUPA"),
        stijl="us",
        nummer=r"\d+[A-Z]?(?:[-.]\d+[A-Za-z]?)*",
        namen={"UCC": "Uniform Commercial Code (ALI/ULC)", "Rest. 2d Contracts": "Restatement (Second) of Contracts (1981)",
               "Rest. 2d Torts": "Restatement (Second) of Torts (1965–1979)", "Rest. 3d Torts: Prod. Liab.": "Restatement (Third) of Torts: Products Liability (1998)",
               "Rest. 3d Torts: PEH": "Restatement (Third) of Torts: Liability for Physical and Emotional Harm (2010–2012)",
               "Rest. 3d Torts: Apport.": "Restatement (Third) of Torts: Apportionment of Liability (2000)",
               "Rest. 3d Restitution": "Restatement (Third) of Restitution and Unjust Enrichment (2011)", "Rest. 3d Agency": "Restatement (Third) of Agency (2006)",
               "Rest. 3d Property: Wills": "Restatement (Third) of Property: Wills and Other Donative Transfers", "Rest. 3d Trusts": "Restatement (Third) of Trusts",
               "UPC": "Uniform Probate Code", "UMDA": "Uniform Marriage and Divorce Act", "UPA 2017": "Uniform Parentage Act (2017)",
               "Cal. Civ. Code": "California Civil Code", "Cal. Fam. Code": "California Family Code", "La. C.C.": "Louisiana Civil Code",
               "11 U.S.C.": "Bankruptcy Code (Title 11 U.S. Code)", "15 U.S.C.": "Title 15 U.S. Code (Commerce and Trade)",
               "RULLCA": "Revised Uniform Limited Liability Company Act", "RUPA": "Revised Uniform Partnership Act"},
    ),
    "AU": Regels(
        None,
        ("ACL", "CCA 2010 (Cth)", "Corporations Act 2001 (Cth)", "PPSA 2009 (Cth)", "Family Law Act 1975 (Cth)", "Bankruptcy Act 1966 (Cth)",
         "Sale of Goods Act 1923 (NSW)", "Civil Liability Act 2002 (NSW)", "Limitation Act 1969 (NSW)", "Succession Act 2006 (NSW)",
         "Conveyancing Act 1919 (NSW)", "Real Property Act 1900 (NSW)", "Frustrated Contracts Act 1978 (NSW)",
         "Minors (Property and Contracts) Act 1970 (NSW)", "Law Reform (Miscellaneous Provisions) Act 1965 (NSW)", "Adoption Act 2000 (NSW)"),
        stijl="s",
        nummer=r"\d+[A-Z]{0,3}",
        namen={"ACL": "Australian Consumer Law (Competition and Consumer Act 2010 (Cth) sch 2)", "CCA 2010 (Cth)": "Competition and Consumer Act 2010 (Cth)",
               "PPSA 2009 (Cth)": "Personal Property Securities Act 2009 (Cth)"},
    ),
    "EU": Regels(
        None,
        ("VWEU", "VEU", "Handvest", "Rome I", "Rome II", "Brussel I-bis", "Erfrechtverordening", "Insolventieverordening",
         "Richtlijn 85/374", "Richtlijn 93/13", "Richtlijn 2011/83", "Richtlijn 2019/770", "Richtlijn 2019/771", "Richtlijn 2011/7",
         "CISG", "PECL", "DCFR", "UNIDROIT PICC"),
        nummer=r"(?:[IVX]+\.-)?\d+(?::\d+)?[a-z]?",
        namen={"VWEU": "Verdrag betreffende de werking van de Europese Unie", "Rome I": "Verordening (EG) nr. 593/2008", "Rome II": "Verordening (EG) nr. 864/2007",
               "Brussel I-bis": "Verordening (EU) nr. 1215/2012", "Erfrechtverordening": "Verordening (EU) nr. 650/2012",
               "Insolventieverordening": "Verordening (EU) 2015/848", "Richtlijn 85/374": "Productaansprakelijkheidsrichtlijn",
               "Richtlijn 93/13": "Richtlijn oneerlijke bedingen", "Richtlijn 2011/83": "Richtlijn consumentenrechten",
               "Richtlijn 2019/770": "Richtlijn digitale inhoud", "Richtlijn 2019/771": "Richtlijn verkoop van goederen",
               "Richtlijn 2011/7": "Richtlijn betalingsachterstand", "CISG": "Weens Koopverdrag (1980)", "PECL": "Principles of European Contract Law",
               "DCFR": "Draft Common Frame of Reference (2009)", "UNIDROIT PICC": "UNIDROIT Principles of International Commercial Contracts (2016)"},
    ),
}

HOOFDWET = {code: r.hoofdwet for code, r in REGELS.items() if r.hoofdwet}

# Volledige namen die men intypt in plaats van de afkorting. Aangevuld met de
# volledige titels uit `Regels.namen` (zonder jaartal tussen haakjes).
_NAMEN_HAND = [
    ("Code civil suisse", "ZGB"), ("CC suisse", "ZGB"), ("CCS", "ZGB"), ("Zivilgesetzbuch", "ZGB"), ("Code des obligations", "OR"),
    ("Code de la consommation", "C. consom."), ("Code de commerce", "C. com."), ("Code du travail", "C. trav."),
    ("Code de procédure civile", "C. proc. civ."), ("Code des assurances", "C. assur."),
    ("Codice civile", "c.c."), ("Codice del consumo", "c. cons."), ("Codice di procedura civile", "c.p.c."),
    ("Código Civil", "CC"), ("Codigo Civil", "CC"), ("Código de Comercio", "CCom"), ("Codigo de Comercio", "CCom"),
    ("Ley General para la Defensa de los Consumidores y Usuarios", "TRLGDCU"),
    ("Bürgerliches Gesetzbuch", "BGB"), ("Handelsgesetzbuch", "HGB"), ("Produkthaftungsgesetz", "ProdHaftG"),
    ("Einführungsgesetz zum Bürgerlichen Gesetzbuche", "EGBGB"),
    ("Burgerlijk Wetboek", "BW"),
    ("Αστικός Κώδικας", "ΑΚ"), ("Αστικού Κώδικα", "ΑΚ"), ("Astikos Kodikas", "ΑΚ"), ("AK", "ΑΚ"), ("Σύνταγμα", "Συντ."), ("Ποινικός Κώδικας", "ΠΚ"),
    ("Εμπορικός Νόμος", "ΕμπΝ"), ("Wetboek van Koophandel", "WvK"), ("Wetboek van Burgerlijke Rechtsvordering", "Rv"), ("Faillissementswet", "Fw"),
]


def _namen() -> list[tuple[re.Pattern, str]]:
    paren = [*_NAMEN_HAND]
    for r in REGELS.values():
        for afk, naam in r.namen.items():
            naam = re.sub(r"\s*\([^()]*\)$", "", naam).strip()
            if len(naam) > 5 and naam.lower() != afk.lower():
                paren.append((naam, afk))
    gezien, uit = set(), []
    for naam, afk in sorted(paren, key=lambda p: len(p[0]), reverse=True):
        if naam.lower() not in gezien:
            gezien.add(naam.lower())
            uit.append((re.compile(r"(?<!\w)" + re.escape(naam).replace(r"\ ", r"\s+") + r"(?!\w)", re.I), afk))
    return uit


_NAMEN = _namen()


def vervang_namen(tekst: str) -> str:
    """Volledige wetsnamen als afkorting: "art. 33 Codice del consumo" → "art. 33 c. cons."."""
    for patroon, afk in _NAMEN:
        tekst = patroon.sub(afk, tekst)
    return tekst
ANDERE_WETTEN = {code: list(r.andere) for code, r in REGELS.items()}
_ONBEKEND = Regels(None)

_FR_HOOFD = re.compile(r"\b(C\.\s*civ\.?|Code\s+civil|Cc)\b", re.I)
_IT_HOOFD = re.compile(r"(?<![\w.])c\.\s?c\.(?!\w)", re.I)
_NL_NR = re.compile(r"(\d+[A-Za-z]?)\s*:\s*(\d+[a-z]{0,3})")
_DE_NR = re.compile(r"(\d+[a-z]{0,3})\b")
_FR_NR = re.compile(r"\b([LRD])?\.?\s?(\d+(?:-\d+)*)\b")
_DETAIL = re.compile(r"\b(lid|leden|onder|sub|Abs\.|S\.|Satz|Ziff\.|lit\.|Nr\.|al\.|alinéa|comma|apartado|párrafo|°)\s*.*$", re.I)
_HAAKJES = re.compile(r"^\s*((?:\([0-9A-Za-z]{1,5}\))+)")
_PREFIX = re.compile(r"^\s*(artt?\.|artikel|art[íi]culos?|art|άρθρ[οα]|αρθρ[οα]|άρθ\.|§§|§|ss?\.?(?=\s*\d)|secs?\.|sections?)\s*", re.I)
_STREEP = "–"


def regels(stelsel: str) -> Regels:
    return REGELS.get(stelsel, _ONBEKEND)


def wetnaam(stelsel: str, wet: str | None) -> str | None:
    """Volledige titel bij een afkorting, als die bekend is (EU: in de taal van de interface)."""
    r = regels(stelsel)
    if stelsel == "EU":
        t = huidige_taal()
        return eunamen.titel(wet, t) or (r.namen.get(wet or "") if t == "nl" else None)
    return r.namen.get(wet or r.hoofdwet or "")


def wet_kort(stelsel: str, wet: str | None) -> str | None:
    """De afkorting zoals ze getoond wordt: EU-wetten in de taal van de interface ("VWEU" → "AEUV")."""
    return eunamen.kort(wet, huidige_taal()) if stelsel == "EU" and wet else wet


# --- wetten uit de database (alle Duitse wetten, de EU-catalogus) ---------------------

_GELADEN = {"tijd": 0.0}
_DE_WETTEN: dict[str, str] = {}  # kleine letters → afkorting ("patg" → "PatG", "sgb v" → "SGB 5")
_DE_ART: set[str] = {"EGBGB", "GG"}  # Duitse wetten met artikelen in plaats van paragrafen (aangevuld uit de database)
# Een afkorting begint met een hoofdletter, of met een kleine letter gevolgd door een hoofdletter (eWpG, eIDKG).
_DE_TOKEN = re.compile(r"(?<![\w.])((?:\d{1,2}\.\s?|\d+-)?(?:[A-ZÄÖÜ]|[a-zäöü](?=[\wÄÖÜäöüß\-]*[A-ZÄÖÜ]))[\wÄÖÜäöüß\-]*(?:\.[A-Za-z]+)*(?:\s(?:\d{1,2}|[IVX]{1,4}))?)(?![\w-])")
_ROMEINS_NAAR = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V", 6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII", 14: "XIV"}


def laad_wetnamen(db=None) -> None:
    """Afkortingen van alle geïmporteerde Duitse wetten en de EU-catalogus in het geheugen (voor `herken`)."""
    from ..models import EuHandeling, Wettekst
    from sqlalchemy import select

    eigen = db is None
    if eigen:
        from ..db import session_factory
        db = session_factory()()
    try:
        de = db.scalars(select(Wettekst.wet).where(Wettekst.stelsel_code == "DE", Wettekst.wet.is_not(None)).distinct()).all()
        art = db.scalars(select(Wettekst.wet).where(Wettekst.stelsel_code == "DE", Wettekst.stijl == "Art")).all()
        eu = db.execute(select(EuHandeling.celex, EuHandeling.soort, EuHandeling.nummer)).all()
    finally:
        if eigen:
            db.close()
    namen: dict[str, str] = {}
    for w in de:
        namen.setdefault(w.lower(), w)
        m = re.fullmatch(r"(.*\D) (\d{1,2})", w)
        if m and int(m.group(2)) in _ROMEINS_NAAR:
            namen.setdefault(f"{m.group(1)} {_ROMEINS_NAAR[int(m.group(2))]}".lower(), w)
    _DE_WETTEN.clear()
    _DE_WETTEN.update(namen)
    _DE_ART.update(w for w in art if w)
    eunamen.laad([tuple(r) for r in eu])
    _GELADEN["tijd"] = time.time()


def _zorg_geladen() -> None:
    if time.time() - _GELADEN["tijd"] > 600:
        _GELADEN["tijd"] = time.time()  # ook bij een fout niet bij elke aanroep opnieuw proberen
        try:
            laad_wetnamen()
        except Exception:
            pass


def _de_wet(tekst: str) -> tuple[str | None, str]:
    _zorg_geladen()
    if not _DE_WETTEN:
        return None, tekst
    for m in _DE_TOKEN.finditer(tekst):
        for kandidaat in (m.group(1), m.group(1).split(" ")[0]):
            w = _DE_WETTEN.get(kandidaat.lower())
            if w:
                eind = m.start(1) + len(kandidaat)
                return w, tekst[: m.start(1)] + " " + tekst[eind:]
    return None, tekst


@dataclass(frozen=True)
class Ref:
    stelsel: str
    nummer: str | None  # None = geen wettelijke regeling in dit stelsel
    wet: str | None = None  # None = hoofdwet
    tot: str | None = None  # einde van een bereik
    detail: str | None = None  # "lid 4", "Abs. 2", "al. 5", "(1)(a)"

    @property
    def wet_label(self) -> str:
        return wet_kort(self.stelsel, self.wet) or HOOFDWET.get(self.stelsel, "")

    @property
    def wet_naam(self) -> str | None:
        return wetnaam(self.stelsel, self.wet)

    @property
    def citeer(self) -> str:
        return citeer(self.stelsel, self.nummer, self.wet, self.tot, self.detail)

    @property
    def url(self) -> str | None:
        if self.nummer is None:
            return None
        u = f"/artikelen/{self.stelsel}/{quote(self.nummer, safe=':-')}"
        return u + (f"?wet={quote(self.wet)}" if self.wet else "")


def citeer(stelsel: str, nummer: str | None, wet: str | None = None, tot: str | None = None, detail: str | None = None) -> str:
    if nummer is None:
        return vertaal("geen wettelijke regeling")
    w = wet_kort(stelsel, wet) or HOOFDWET.get(stelsel, "")
    nr = f"{nummer}{_STREEP}{tot}" if tot else nummer
    d = (detail if detail.startswith("(") else f" {detail}") if detail else ""
    if re.match(r"^(?:\(|[^\d\s(]{3,})", nummer):  # bijlage, preambule, protocol: "Anlage 2 1. BImSchV", "Protokoll 2 Art. 9 AEUV"
        return f"{nr}{d} {w}".strip()
    stijl = regels(stelsel).stijl
    if stelsel == "DE" and wet in _DE_ART:
        stijl = "Art"
    if stijl == "§":
        return f"{'§§' if tot else '§'} {nr}{d} {w}".strip()
    if stijl == "Art":
        return f"Art. {nr}{d} {w}".strip()
    if stijl == "s":
        return f"{'ss' if tot else 's'} {nr}{d} {w}".strip()
    if stelsel == "EU" and huidige_taal() not in ("nl", "fr"):
        return f"Art. {nr}{d} {w}".strip()
    if stijl == "us":
        teken = "art." if w == "La. C.C." else ("§§" if tot else "§")
        return f"{w} {teken} {nr}{d}".strip()
    return f"art. {nr}{d} {w}".strip()


# --- sorteersleutels en bereiken ---------------------------------------------


def _letters(s: str) -> str:
    return s.lower()


_ROMEINS = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}


def _romeins(s: str) -> int | None:
    if not re.fullmatch(r"[IVXLC]+", s):
        return None
    waarde, vorige = 0, 0
    for c in reversed(s):
        v = _ROMEINS[c]
        waarde, vorige = (waarde - v, vorige) if v < vorige else (waarde + v, v)
    return waarde


def _natuurlijk(nummer: str) -> tuple | None:
    """Natuurlijke sleutel: '40' < '40a' < '41', '94' < '94 bis' < '94 ter', '2-401' < '2-402', 'VI.37' < 'XII.1'."""
    delen = re.findall(r"\d+|[A-Za-z]+", nummer)
    if not delen or not any(d.isdigit() for d in delen):
        return None
    uit = []
    for i, d in enumerate(delen):
        if d.isdigit():
            uit.append((1, int(d), ""))
        elif i == 0 and _romeins(d) is not None:
            uit.append((0, _romeins(d), ""))
        else:
            uit.append((2, _LATIJN_WAARDE.get(d.lower(), 0), d.lower()))
    return tuple(uit)


def sleutel(stelsel: str, nummer: str) -> tuple | None:
    """Sorteersleutel binnen één stelsel. None als het nummer niet te lezen is."""
    nummer = nummer.strip()
    if stelsel == "NL":
        m = re.fullmatch(r"(\d+[A-Za-z]?):(\d+)([a-z]{0,3})", nummer)
        if not m:
            return None
        return (m.group(1).upper(), int(m.group(2)), m.group(3))
    if stelsel == "FR":
        m = re.fullmatch(r"([LRD]?)(\d+(?:-\d+)*)", nummer)
        if not m:
            return None
        delen = [int(x) for x in m.group(2).split("-")]
        return (m.group(1), *(delen + [0] * (4 - len(delen))))
    if stelsel == "DE":
        m = re.fullmatch(r"(\d+)([a-z]{0,3})", nummer)
        if not m:
            return None
        return (int(m.group(1)), _letters(m.group(2)))
    if not re.fullmatch(regels(stelsel).nummer, nummer):
        return None
    return _natuurlijk(nummer)


def parse_bereik(stelsel: str, bereik: str | None) -> tuple[tuple, tuple] | None:
    """`"art. 3:83–3:98"`, `"§§ 929–936"`, `"art. 1101–1231-7"`, `"ss 12–15"`, `"§§ 2-101–2-107"` → (laag, hoog)."""
    if not bereik:
        return None
    s = re.sub(r"^(art\.|artt\.|§§|§|ss?\b)\s*", "", bereik.strip(), flags=re.I)
    delen = [d.strip() for d in re.split(r"\s*–\s*|\s+-\s+", s)]
    lo, hi = sleutel(stelsel, delen[0]), sleutel(stelsel, delen[-1])
    if lo is None or hi is None:
        return None
    if stelsel == "NL" and lo[0] != hi[0]:
        return None
    return lo, hi


def formatteer_bereik(stelsel: str, nummers: Iterable[str]) -> str:
    gesorteerd = sorted({n for n in nummers if sleutel(stelsel, n) is not None}, key=lambda n: sleutel(stelsel, n))
    if not gesorteerd:
        return ""
    lo, hi = gesorteerd[0], gesorteerd[-1]
    enkel, meer = {"§": ("§", "§§"), "us": ("§", "§§"), "s": ("s", "ss"), "Art": ("Art.", "Art.")}.get(regels(stelsel).stijl, ("art.", "art."))
    return f"{enkel} {lo}" if lo == hi else f"{meer} {lo}{_STREEP}{hi}"


def bevat(stelsel: str, bereik: tuple[tuple, tuple], nummer: str) -> bool:
    k = sleutel(stelsel, nummer)
    if k is None:
        return False
    lo, hi = bereik
    if stelsel == "NL" and k[0] != lo[0]:
        return False
    try:
        return lo <= k <= hi
    except TypeError:
        return False


def ref_bevat(ref: Ref, stelsel: str, nummer: str, wet: str | None = None) -> bool:
    """Valt artikel `nummer` onder deze verwijzing (gelijk, of binnen het bereik)?"""
    if ref.nummer is None or ref.stelsel != stelsel or (ref.wet or None) != (wet or None):
        return False
    if ref.tot is None:
        return ref.nummer == nummer
    lo, hi = sleutel(stelsel, ref.nummer), sleutel(stelsel, ref.tot)
    return lo is not None and hi is not None and bevat(stelsel, (lo, hi), nummer)


# --- herkennen ---------------------------------------------------------------


def _wet_patroon(w: str) -> re.Pattern:
    return re.compile(r"(?<![\w.])" + re.escape(w).replace(r"\ ", r"\s*") + r"(?!\w)", re.I)


def _wet_uit(stelsel: str, tekst: str) -> tuple[str | None, str]:
    if stelsel == "EU":
        _zorg_geladen()
        w, rest = eunamen.herken_wet(tekst)
        if w:
            return w, rest
    for w in sorted(regels(stelsel).andere, key=len, reverse=True):
        patroon = _wet_patroon(w)
        if patroon.search(tekst):
            return w, patroon.sub(" ", tekst)
    if stelsel == "DE":
        w, rest = _de_wet(re.sub(r"(?<!\w)BGB(?!\w)", " ", tekst))
        if w:
            return w, rest
    hoofd = HOOFDWET.get(stelsel)
    if stelsel == "FR":
        tekst = _FR_HOOFD.sub(" ", tekst)
    elif stelsel == "IT":
        tekst = _IT_HOOFD.sub(" ", tekst)
    elif hoofd:
        tekst = re.sub(r"(?<!\w)" + re.escape(hoofd) + r"(?!\w)", " ", tekst)
    return None, tekst


def _detail(tekst: str) -> tuple[str | None, str]:
    m = _DETAIL.search(tekst)
    if not m:
        return None, tekst
    detail = re.sub(r"\s+", " ", re.split(r"[,;]", m.group(0))[0]).strip().rstrip(".,;")
    return (detail or None), tekst[: m.start()]


def _normaliseer(stelsel: str, nr: str) -> str:
    """Eén schrijfwijze per stelsel: '2262 bis' → '2262bis' (BE), '1469 bis' → '1469-bis' (IT), '94bis' → '94 bis' (ES)."""
    m = re.fullmatch(rf"(.*?\d)\s*-?\s*({_LAT})", nr, re.I)
    if not m:
        return nr
    basis, lat = m.group(1), m.group(2).lower()
    return {"IT": f"{basis}-{lat}", "ES": f"{basis} {lat}"}.get(stelsel, f"{basis}{lat}")


def lees(stelsel: str, tekst: str) -> Ref | None:
    """Leest een verwijzing binnen een bekend stelsel: "6:162", "§ 823 Abs. 1", "art. 1242 al. 5",
    "§ 1 ProdHaftG", "art. L217-3 C. consom.", "art. 1132–1136", "§§ 203–213", "art. 5.69 BW",
    "Art. 41 Abs. 1 OR", "art. 1469-bis c.c.", "s 2(1) SGA 1979", "UCC § 2-207(2)"."""
    tekst = tekst.strip()
    if tekst in ("", "—", "-"):
        return Ref(stelsel, None)
    wet, rest = _wet_uit(stelsel, tekst)
    rest = re.sub(r"\((?:oud|versie [^)]*|a\.F\.)\)", " ", rest)
    rest = _PREFIX.sub("", rest.strip())
    detail, rest = _detail(rest)
    if stelsel == "EU":
        rest = re.sub(r"\b([IVX]+)\.\s*[–-]\s*(?=\d)", r"\1.-", rest)
    stukken = [s.strip() for s in rest.split(_STREEP)]
    if stelsel == "NL":
        nrs = [_NL_NR.search(s) for s in stukken]
        if not nrs[0]:
            return None
        nummers = [f"{m.group(1).upper()}:{m.group(2)}" for m in nrs if m]
    elif stelsel == "FR":
        nrs = [_FR_NR.search(s) for s in stukken]
        if not nrs[0]:
            return None
        nummers = [f"{m.group(1) or ''}{m.group(2)}" for m in nrs if m]
    elif stelsel in REGELS and stelsel != "DE":
        patroon = re.compile(r"(?<![\w.])(" + regels(stelsel).nummer + r")(?![\w])")
        nrs = [patroon.search(s) for s in stukken]
        if not nrs[0]:
            return None
        if detail is None:
            h = _HAAKJES.match(stukken[-1][nrs[-1].end():] if nrs[-1] else "")
            detail = h.group(1) if h else None
        nummers = [_normaliseer(stelsel, re.sub(r"\s+", " ", m.group(1))) for m in nrs if m]
    else:
        nrs = [_DE_NR.search(s) for s in stukken]
        if not nrs[0]:
            return None
        nummers = [m.group(1) for m in nrs if m]
    tot = nummers[-1] if len(nummers) > 1 and nummers[-1] != nummers[0] else None
    return Ref(stelsel, nummers[0], wet, tot, detail)


def _wet_treffers(t: str) -> list[str]:
    """Stelsels waarvan een wet in de tekst genoemd wordt. Een specifieke wet ("La. C.C.", "oud BW")
    gaat voor de afkorting van een hoofdcodificatie die erin past ("c.c.", "BW")."""
    def patroon(w: str) -> str:
        return r"(?<![\w.])" + re.escape(w).replace(r"\ ", r"\s*") + r"(?!\w)"

    _zorg_geladen()
    uit, rest = [], t
    if eunamen.noemt_eu(t):
        uit.append("EU")
        rest = eunamen.herken_wet(rest)[1]
    for code, r in REGELS.items():
        for w in r.andere:
            if re.search(patroon(w), t):
                uit.append(code)
                rest = re.sub(patroon(w), " ", rest)
    if "DE" not in uit and _de_wet(rest)[0]:
        uit.append("DE")
    for code, r in REGELS.items():
        if code in uit:
            continue
        if (code == "FR" and _FR_HOOFD.search(rest)) or (code == "IT" and _IT_HOOFD.search(rest)):
            uit.append(code)
        elif r.hoofdwet and code not in ("FR", "IT") and re.search(patroon(r.hoofdwet), rest):
            uit.append(code)
    return sorted(set(uit), key=list(REGELS).index)


def herken(tekst: str, stelsel: str | None = None) -> list[Ref]:
    """Vrije invoer → mogelijke verwijzingen. Leeg als het geen artikelverwijzing lijkt.

    "3:84" en "art. 3:84 BW" → NL; "art. 5.69 BW" en "1382 oud BW" → BE; "§ 929", "929 BGB" → DE;
    "1196 C. civ." of "1112-1" → FR; "Art. 41 OR" → CH; "s 17 SGA 1979" → EN; "UCC § 2-401" → US.
    Een kaal nummer ("929") is dubbelzinnig: DE én FR; "art. 1902 CC" kan ES of FR zijn.
    """
    t = vervang_namen(tekst.strip())
    if not t or len(t) > 80 or not re.search(r"\d", t):
        return []
    if stelsel:
        r = lees(stelsel, t)
        return [r] if r and r.nummer else []
    if re.search(r"ECLI|\d{4}-\d{2}-\d{2}", t, re.I):
        return []
    kandidaten = _wet_treffers(t)
    if "NL" in kandidaten and "BE" in kandidaten:  # "BW" in beide: de nummering beslist
        kandidaten.remove("BE" if _NL_NR.search(t) and "WVV" not in t else "NL")
    if not kandidaten:
        if _NL_NR.search(t):
            kandidaten = ["NL"]
        elif re.search(r"\b\d+\.\d+\b", t) and not re.search(r"§", t):
            kandidaten = ["BE"]
        elif "§" in t and re.search(r"\d+-\d+", t):
            kandidaten = ["US"]
        elif "§" in t:
            kandidaten = ["DE"]
        elif re.search(r"\bC\.\s*(consom|com|trav|rur)\b", t, re.I) or re.search(r"\d+-\d+", t):
            kandidaten = ["FR"]
        elif re.match(r"art", t, re.I):
            kandidaten = ["FR"]
        elif re.fullmatch(r"\d+[a-z]{0,2}", t):
            kandidaten = ["DE", "FR"] if t.isdigit() else ["DE"]
    uit = []
    for s in kandidaten:
        r = lees(s, t)
        if r and r.nummer:
            uit.append(r)
    return uit


def noemt_wet(tekst: str) -> bool:
    """Of de invoer een wet noemt ("BGB", "c. cons.", "Code de commerce"), of alleen een nummer is."""
    return bool(_wet_treffers(vervang_namen(tekst)))


def kale_nummers(tekst: str) -> set[str]:
    """Schrijfwijzen waaronder een kaal nummer ("art. 1469 bis", "L. 217-3", "§ 929") in een wettekst kan staan."""
    t = _PREFIX.sub("", tekst.strip())
    _, t = _detail(t)
    m = re.fullmatch(rf"([LRD])?\.?\s?(\d+[a-z]{{0,3}}(?:-\d+)*)(?:\s?-?\s?({_LAT}))?\.?", t.strip(), re.I)
    if not m:
        return set()
    basis = (m.group(1) or "").upper() + m.group(2)
    if not m.group(3):
        return {basis}
    lat = m.group(3).lower()
    return {f"{basis}{lat}", f"{basis} {lat}", f"{basis}-{lat}"}


def ref_uit_bron(bron) -> Ref | None:
    """Een wetsbron ("art. 3:84 BW", "§ 311 BGB", "art. 1112 C. civ. (versie 2016)", "s 17 SGA 1979") als Ref."""
    if bron.soort != "wet" or bron.stelsel_code not in REGELS:
        return None
    r = lees(bron.stelsel_code, bron.citeertitel)
    return r if r and r.nummer else None


# --- plaatsen in de systematiek ------------------------------------------------

_NL_BOEKCODE = re.compile(r"^BW-(\d+[A-Z]?)$")


class Plaatser:
    """Plaatst artikelnummers van één wet in de systematiekboom van één stelsel.

    Alleen knopen van die wet doen mee (`wet` None: de hoofdcodificatie).
    Knopen zonder (leesbaar) bereik krijgen het omspannende bereik van hun
    kinderen; NL-boekknopen (`BW-3`) bevatten elk artikel van dat boek, en de
    wortel van een andere wet zonder bereik ("Sale of Goods Act 1979") elk
    artikel van die wet. Hangt de wet onder een knoop van een andere wet of
    een rubriek (EN: "Contract"), dan begint het pad bij die voorouders.
    """

    def __init__(self, stelsel: str, knopen: Iterable, wet: str | None = None) -> None:
        self.stelsel = stelsel
        self.wet = wet or None
        self.knopen = [k for k in knopen if (getattr(k, "wet", None) or None) == self.wet]
        self.ids = {k.id for k in self.knopen}
        self.kinderen: dict[int | None, list] = {}
        for k in self.knopen:
            self.kinderen.setdefault(k.parent_id if k.parent_id in self.ids else None, []).append(k)
        self.bereik: dict[int, tuple[tuple, tuple] | None] = {}
        for k in self.knopen:
            self._bereik(k)

    def _bereik(self, k):
        if k.id in self.bereik:
            return self.bereik[k.id]
        b = parse_bereik(self.stelsel, k.bereik)
        if b is None:
            sub = [self._bereik(c) for c in self.kinderen.get(k.id, [])]
            sub = [s for s in sub if s]
            if sub and (self.stelsel != "NL" or len({s[0][0] for s in sub}) == 1):
                try:
                    b = (min(s[0] for s in sub), max(s[1] for s in sub))
                except TypeError:
                    b = None
        self.bereik[k.id] = b
        return b

    def _bevat(self, k, nummer: str) -> bool:
        if self.stelsel == "NL" and self.wet is None:
            m = _NL_BOEKCODE.match(k.code or "")
            if m:
                s = sleutel("NL", nummer)
                return s is not None and s[0] == m.group(1)
        b = self.bereik.get(k.id)
        if b is None and self.wet is not None and k in self.kinderen.get(None, []):
            return True
        return b is not None and bevat(self.stelsel, b, nummer)

    def pad(self, nummer: str) -> list:
        """Pad van wortel tot de diepste knoop die het artikel bevat (leeg als onbekend)."""
        if sleutel(self.stelsel, nummer) is None:
            return []
        pad: list = []
        ouder = None
        while True:
            kandidaten = [k for k in self.kinderen.get(ouder, []) if self._bevat(k, nummer)]
            if not kandidaten:
                break
            # Bij overlap (zeldzaam) wint het smalste bereik.
            kandidaten.sort(key=lambda k: self._breedte(k))
            knoop = kandidaten[0]
            pad.append(knoop)
            ouder = knoop.id
        if pad:
            voor, p = [], getattr(pad[0], "parent", None)
            while p is not None and p.id not in self.ids:
                voor.append(p)
                p = getattr(p, "parent", None)
            pad = [*reversed(voor), *pad]
        return pad

    def _breedte(self, k) -> tuple:
        b = self.bereik.get(k.id)
        if not b:
            return (1,)
        return (0, *[_afstand(l, h) for l, h in zip(b[0], b[1])])

    def onder(self, knoop, nummer: str) -> bool:
        """Valt het artikel binnen (een afstammeling van) deze knoop?"""
        return knoop in self.pad(nummer)


def _afstand(l, h) -> int:
    if isinstance(l, int) and isinstance(h, int):
        return h - l
    if isinstance(l, tuple) and isinstance(h, tuple) and len(l) > 1 and len(h) > 1 and isinstance(l[1], int) and isinstance(h[1], int):
        return h[1] - l[1]
    return 0


def plaatser(db, stelsel: str, wet: str | None = None) -> Plaatser:
    from sqlalchemy import select

    from ..models import Systematiek

    return Plaatser(
        stelsel, db.scalars(select(Systematiek).where(Systematiek.stelsel_code == stelsel).order_by(Systematiek.volgorde)).all(), wet
    )
