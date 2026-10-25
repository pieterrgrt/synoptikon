"""Artikelverwijzingen herkennen, ordenen en in de systematiek plaatsen.

Drie nummeringen, elk met eigen regels:

* **NL** (BW): `boek:nummer`, met letters (`6:230a`, `7A:1576`). Een
  bereik loopt nooit over een boekgrens.
* **DE** (BGB): `§ 929`, met letters (`§ 312k`). Leden heten `Abs.`, zinnen `S.`.
* **FR** (Code civil): `1112`, `1112-1`, `1231-7`; andere codes ook met
  `L`/`R`/`D` vooraf (`L217-3`). Het streepje hoort bij het nummer, dus een
  bereik gebruikt altijd een en-dash (`1101–1231-7`).

Een `Ref` is (stelsel, wet, nummer[, tot], detail). `wet` is de afkorting
waaronder het artikel geciteerd wordt; `None` betekent de hoofdcodificatie
(BW, BGB, C. civ.). Alleen voor de hoofdcodificatie bestaat een systematiek.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable
from urllib.parse import quote

HOOFDWET = {"NL": "BW", "DE": "BGB", "FR": "C. civ."}

# Bekende andere wetten per stelsel, langste eerst zodat "C. consom." niet als "C. c" wordt gelezen.
ANDERE_WETTEN = {
    "NL": ["Rv", "WvK", "Fw", "Aw", "Hw"],
    "DE": ["HGB", "ZPO", "EGBGB", "ProdHaftG", "AnfG", "ErbbauRG", "InsO", "GmbHG", "AktG", "StVG", "UWG"],
    "FR": ["C. consom.", "C. com.", "C. trav.", "C. rur.", "C. proc. civ.", "C. assur.", "Loi 1901", "Loi 1985"],
}

_FR_HOOFD = re.compile(r"\b(C\.\s*civ\.?|Code\s+civil|Cc)\b", re.I)
_NL_NR = re.compile(r"(\d+[A-Za-z]?)\s*:\s*(\d+[a-z]{0,3})")
_DE_NR = re.compile(r"(\d+[a-z]{0,3})\b")
_FR_NR = re.compile(r"\b([LRD])?\.?\s?(\d+(?:-\d+)*)\b")
_DETAIL = re.compile(r"\b(lid|leden|onder|sub|Abs\.|S\.|Satz|Nr\.|al\.|alinéa|°)\s*.*$", re.I)
_STREEP = "–"


@dataclass(frozen=True)
class Ref:
    stelsel: str
    nummer: str | None  # None = geen wettelijke regeling in dit stelsel
    wet: str | None = None  # None = hoofdwet
    tot: str | None = None  # einde van een bereik
    detail: str | None = None  # "lid 4", "Abs. 2", "al. 5"

    @property
    def wet_label(self) -> str:
        return self.wet or HOOFDWET.get(self.stelsel, "")

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
        return "geen wettelijke regeling"
    w = wet or HOOFDWET.get(stelsel, "")
    nr = f"{nummer}{_STREEP}{tot}" if tot else nummer
    d = f" {detail}" if detail else ""
    if stelsel == "DE":
        return f"{'§§' if tot else '§'} {nr}{d} {w}".strip()
    return f"art. {nr}{d} {w}".strip()


# --- sorteersleutels en bereiken ---------------------------------------------


def _letters(s: str) -> str:
    return s.lower()


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
    m = re.fullmatch(r"(\d+)([a-z]{0,3})", nummer)
    if not m:
        return None
    return (int(m.group(1)), _letters(m.group(2)))


def parse_bereik(stelsel: str, bereik: str | None) -> tuple[tuple, tuple] | None:
    """`"art. 3:83–3:98"`, `"§§ 929–936"`, `"art. 1101–1231-7"`, `"art. 6:212"` → (laag, hoog)."""
    if not bereik:
        return None
    s = re.sub(r"^(art\.|artt\.|§§|§)\s*", "", bereik.strip(), flags=re.I)
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
    if stelsel == "DE":
        return f"§ {lo}" if lo == hi else f"§§ {lo}{_STREEP}{hi}"
    return f"art. {lo}" if lo == hi else f"art. {lo}{_STREEP}{hi}"


def bevat(stelsel: str, bereik: tuple[tuple, tuple], nummer: str) -> bool:
    k = sleutel(stelsel, nummer)
    if k is None:
        return False
    lo, hi = bereik
    if stelsel == "NL" and k[0] != lo[0]:
        return False
    return lo <= k <= hi


def ref_bevat(ref: Ref, stelsel: str, nummer: str, wet: str | None = None) -> bool:
    """Valt artikel `nummer` onder deze verwijzing (gelijk, of binnen het bereik)?"""
    if ref.nummer is None or ref.stelsel != stelsel or (ref.wet or None) != (wet or None):
        return False
    if ref.tot is None:
        return ref.nummer == nummer
    lo, hi = sleutel(stelsel, ref.nummer), sleutel(stelsel, ref.tot)
    return lo is not None and hi is not None and bevat(stelsel, (lo, hi), nummer)


# --- herkennen ---------------------------------------------------------------


def _wet_uit(stelsel: str, tekst: str) -> tuple[str | None, str]:
    for w in ANDERE_WETTEN.get(stelsel, []):
        patroon = re.compile(r"(?<!\w)" + re.escape(w).replace(r"\ ", r"\s*") + r"(?!\w)", re.I)
        if patroon.search(tekst):
            return w, patroon.sub(" ", tekst)
    hoofd = HOOFDWET.get(stelsel)
    if stelsel == "FR":
        tekst = _FR_HOOFD.sub(" ", tekst)
    elif hoofd:
        tekst = re.sub(r"(?<!\w)" + re.escape(hoofd) + r"(?!\w)", " ", tekst)
    return None, tekst


def _detail(tekst: str) -> tuple[str | None, str]:
    m = _DETAIL.search(tekst)
    if not m:
        return None, tekst
    detail = re.sub(r"\s+", " ", re.split(r"[,;]", m.group(0))[0]).strip().rstrip(".,;")
    return (detail or None), tekst[: m.start()]


def lees(stelsel: str, tekst: str) -> Ref | None:
    """Leest een verwijzing binnen een bekend stelsel: "6:162", "§ 823 Abs. 1", "art. 1242 al. 5",
    "§ 1 ProdHaftG", "art. L217-3 C. consom.", "art. 1132–1136", "§§ 203–213"."""
    tekst = tekst.strip()
    if tekst in ("", "—", "-"):
        return Ref(stelsel, None)
    wet, rest = _wet_uit(stelsel, tekst)
    rest = re.sub(r"\((?:oud|versie [^)]*|a\.F\.)\)", " ", rest)
    rest = re.sub(r"^\s*(artt?\.|artikel|art|§§|§)\s*", "", rest.strip(), flags=re.I)
    detail, rest = _detail(rest)
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
    else:
        nrs = [_DE_NR.search(s) for s in stukken]
        if not nrs[0]:
            return None
        nummers = [m.group(1) for m in nrs if m]
    tot = nummers[-1] if len(nummers) > 1 and nummers[-1] != nummers[0] else None
    return Ref(stelsel, nummers[0], wet, tot, detail)


def herken(tekst: str, stelsel: str | None = None) -> list[Ref]:
    """Vrije invoer → mogelijke verwijzingen. Leeg als het geen artikelverwijzing lijkt.

    "3:84" en "art. 3:84 BW" → NL; "§ 929", "929 BGB" → DE; "1196 C. civ." of
    "1112-1" → FR. Een kaal nummer ("929") is dubbelzinnig: DE én FR.
    """
    t = tekst.strip()
    if not t or len(t) > 80 or not re.search(r"\d", t):
        return []
    if stelsel:
        r = lees(stelsel, t)
        return [r] if r and r.nummer else []
    if re.search(r"ECLI|\d{4}-\d{2}-\d{2}", t, re.I):
        return []
    kandidaten: list[str] = []
    if _NL_NR.search(t) or re.search(r"\bBW\b", t):
        kandidaten = ["NL"]
    elif "§" in t or re.search(r"\b(BGB|HGB|ZPO|ProdHaftG|AnfG|ErbbauRG|EGBGB)\b", t):
        kandidaten = ["DE"]
    elif _FR_HOOFD.search(t) or re.search(r"\bC\.\s*(consom|com|trav|rur)\b", t, re.I) or re.search(r"\d+-\d+", t):
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


def ref_uit_bron(bron) -> Ref | None:
    """Een wetsbron ("art. 3:84 BW", "§ 311 BGB", "art. 1112 C. civ. (versie 2016)") als Ref."""
    if bron.soort != "wet" or bron.stelsel_code not in HOOFDWET:
        return None
    r = lees(bron.stelsel_code, bron.citeertitel)
    return r if r and r.nummer else None


# --- plaatsen in de systematiek ------------------------------------------------


_NL_BOEKCODE = re.compile(r"^BW-(\d+[A-Z]?)$")


class Plaatser:
    """Plaatst artikelnummers in de systematiekboom van één stelsel.

    Knopen zonder (leesbaar) bereik krijgen het omspannende bereik van hun
    kinderen; NL-boekknopen (`BW-3`) bevatten elk artikel van dat boek.
    """

    def __init__(self, stelsel: str, knopen: Iterable) -> None:
        self.stelsel = stelsel
        self.knopen = list(knopen)
        self.kinderen: dict[int | None, list] = {}
        for k in self.knopen:
            self.kinderen.setdefault(k.parent_id, []).append(k)
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
                b = (min(s[0] for s in sub), max(s[1] for s in sub))
        self.bereik[k.id] = b
        return b

    def _bevat(self, k, nummer: str) -> bool:
        if self.stelsel == "NL":
            m = _NL_BOEKCODE.match(k.code or "")
            if m:
                s = sleutel("NL", nummer)
                return s is not None and s[0] == m.group(1)
        b = self.bereik.get(k.id)
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
                return pad
            # Bij overlap (zeldzaam) wint het smalste bereik.
            kandidaten.sort(key=lambda k: self._breedte(k))
            knoop = kandidaten[0]
            pad.append(knoop)
            ouder = knoop.id

    def _breedte(self, k) -> tuple:
        b = self.bereik.get(k.id)
        if not b:
            return (1,)
        return (0, *[h - l if isinstance(h, int) and isinstance(l, int) else 0 for l, h in zip(b[0], b[1])])

    def onder(self, knoop, nummer: str) -> bool:
        """Valt het artikel binnen (een afstammeling van) deze knoop?"""
        return knoop in self.pad(nummer)


def plaatser(db, stelsel: str) -> Plaatser:
    from sqlalchemy import select

    from ..models import Systematiek

    return Plaatser(stelsel, db.scalars(select(Systematiek).where(Systematiek.stelsel_code == stelsel).order_by(Systematiek.volgorde)).all())
