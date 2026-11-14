"""Verwijzingen vinden in lopende tekst: "… aus §§ 280 I, III, 281 BGB, hilfsweise § 823 Abs. 1 …".

`artikelen.herken` leest één verwijzing die iemand intypt; hier gaat het om een hele tekst (een Gutachten, een memo, de
feedback van Claude). `vind` loopt de tekst af, leest bij elk "§", "Art." of "artikel" de keten die volgt en zoekt de wet
die erachter staat. Elke schakel wordt een `Ref`, met de leden, zinnen en nummers apart (`Detail`), zodat de
citatiecontrole kan nagaan of Abs. 3 bestaat en de citeerfunctie de keten in een andere stijl kan schrijven.

Wat de scanner kent:

* DE: "§ 433 Abs. 2", "§ 433 II", "§ 812 I 1 Alt. 1", "§§ 280 Abs. 1, 3, 281", "§§ 987 ff.", "§§ 929 bis 931",
  "§ 437 Nr. 2", "§§ 280 I, 311 II, 241 II", "§ 7 I StVG", "Art. 2 Abs. 1 GG", "§ 280 I i.V.m. § 241 II".
* NL: "art. 6:162 lid 2 BW", "artikel 6:74 jo. 6:81 BW", "artt. 3:296 en 3:297 BW", "art. 7:17 lid 2 en 5 BW",
  "art. 3:40 Awb", "art. 6:74 e.v. BW".
* FR: "art. 1240 C. civ.", "articles 1231-1 et 1231-2 du Code civil", "art. L. 217-3 C. consom.", "al. 2".
* EU: "Art. 6 Abs. 1 lit. a DSGVO", "art. 6 lid 1 onder a AVG", "Article 6(1)(a) GDPR", "Art. 101 AEUV".

Staat er geen wet achter, dan geldt de wet van de vorige verwijzing in dezelfde alinea (als de schrijfwijze daarbij
past), anders het stelsel dat de aanroeper meegeeft ("§ 433 II" in een Duitse Klausur is het BGB). Zo'n verwijzing
draagt `aangenomen=True`. Een afkorting die geen bekende wet is ("§ 2 FantasieG") geeft een vondst zonder Ref en met
`onbekend`: liever geen verwijzing dan een foute.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..i18n import rechtstaal
from . import artikelen
from .artikelen import HOOFDWET, Ref, _LAT

_ROMEINS = {"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10, "XI": 11, "XII": 12}


@dataclass(frozen=True)
class Detail:
    """Eén aangehaald onderdeel van een artikel: lid (Abs., al.), zin (S.), nummer (Nr.), letter (lit., onder a)."""

    lid: str | None = None
    zin: str | None = None
    nr: str | None = None
    letter: str | None = None
    extra: str | None = None  # "Alt. 1", "Hs. 2", "Var. 2", "Fall 1", "UAbs. 2"

    @property
    def leeg(self) -> bool:
        return not (self.lid or self.zin or self.nr or self.letter or self.extra)


@dataclass
class Element:
    """Eén schakel in een keten: een artikel (of bereik) met zijn onderdelen, en waar het in de tekst staat."""

    nummer: str
    start: int
    eind: int
    tot: str | None = None
    details: list[Detail] = field(default_factory=list)
    ff: bool = False  # "ff.", "e.v.", "et seq."
    ref: Ref | None = None


@dataclass
class Vondst:
    start: int
    eind: int
    ruw: str
    elementen: list[Element] = field(default_factory=list)
    soort: str = "artikel"  # artikel | ecli | celex | roepnaam | handeling (de laatste vier: services/citatiecontrole.py)
    stelsel: str | None = None
    wet: str | None = None  # None = hoofdcodificatie
    wet_tekst: str | None = None  # zoals de wet in de tekst staat ("BGB", "du Code civil")
    aangenomen: bool = False  # geen wet genoemd: overgenomen van de vorige verwijzing of van het standaardstelsel
    onbekend: str | None = None  # een afkorting die geen bekende wet is
    stijl: str = "§"  # "§" of "art": waarmee de verwijzing begint
    meervoud: bool = False

    @property
    def refs(self) -> list[Ref]:
        return [e.ref for e in self.elementen if e.ref is not None]


# --- opmaak van onderdelen per stelsel -----------------------------------------------------------------------------

_LID_WOORD = {"NL": "lid", "BE": "lid", "FR": "al.", "QC": "al.", "IT": "comma", "ES": "apartado"}


def detail_tekst(d: Detail, stelsel: str) -> str:
    """Een onderdeel zoals het stelsel het schrijft: "Abs. 1 S. 2 Nr. 3", "lid 2 onder a", "al. 2", "(1)(a)".
    Unierecht volgt de rechtstaal: "Abs. 1 lit. a" (de), "lid 1 onder a" (nl), "(1)(a)" (en)."""
    if stelsel == "EU":
        stelsel = {"nl": "NL", "de": "DE", "en": "EN"}.get(rechtstaal(), "EU")
    if stelsel in ("EN", "US", "AU", "CA", "HK", "NZ"):
        return "".join(f"({x})" for x in (d.lid, d.nr, d.letter) if x)
    if stelsel == "EU":
        delen = [f"par. {d.lid}" if d.lid else "", f"{d.letter})" if d.letter else "", f"{d.nr}°" if d.nr else "", d.extra or ""]
    elif stelsel in _LID_WOORD:
        delen = [f"{_LID_WOORD[stelsel]} {d.lid}" if d.lid else "", f"zin {d.zin}" if d.zin and stelsel in ("NL", "BE") else "",
                 (f"onder {d.letter}" if stelsel in ("NL", "BE") else f"{d.letter})") if d.letter else "", f"{d.nr}°" if d.nr else "", d.extra or ""]
    else:
        delen = [f"Abs. {d.lid}" if d.lid else "", f"S. {d.zin}" if d.zin else "", f"Nr. {d.nr}" if d.nr else "",
                 f"lit. {d.letter}" if d.letter else "", d.extra or ""]
    return " ".join(x for x in delen if x)


# --- lezen van een keten -------------------------------------------------------------------------------------------

_ANKER = re.compile(r"(?<![\w§])(§§?|(?:Artikel[ns]?|Artikelen|Art(?:t)?\.?|artikel(?:en)?|artt?\.?|articles?|Articles?|art[íi]culos?)(?=\s*(?:[LRD]\.?\s?)?\d))")
_SPATIE = re.compile(r"[ \t  ]*")
_NR_PAR = re.compile(r"(\d+[a-z]{0,3})(?![\w])")
_NR_ART = re.compile(
    r"((?:[LRD]\.?\s?(?=\d))?\d+[A-Za-z]?(?::\d+[a-z]{0,3}|(?:\.\d+[a-z]?)+(?![\d])|(?:-\d+)+)?"
    rf"(?:-?(?:{_LAT})(?![\w])|[a-z]{{1,3}}(?![\w]))?)(?![\w:])")
_ROM = re.compile(r"(X{0,1}(?:IX|IV|V?I{0,3}))(?![\w])(?!\.\w)")
_GETAL = re.compile(r"(\d+[a-z]?)(?![\w:])")
_LETTER = re.compile(r"([a-z]{1,2})\)?(?![\w])")
_HAAK = re.compile(r"\((\d+[a-z]?|[a-z]{1,2}|[ivx]+)\)")
_FF = re.compile(r"(ff?\.|e\.\s?v\.|et\s+seq\.?|et\s+s\.|et\s+suivants|en\s+verder|y\s+ss\.)(?![\w])", re.I)
_SOORT = [
    ("lid", re.compile(r"(Abs(?:atz|ätze[n]?|\.)?|lid|leden|al(?:inéas?|\.)|para(?:graph)?s?\.?|par\.|comma|apartado)(?![\w])\s*", re.I)),
    ("zin", re.compile(r"(S(?:atz|ätze[n]?|\.)|(?:vol)?zin|phrase|sentence)(?![\w])\s*")),
    ("nr", re.compile(r"(Nrn?\.|Nummer[n]?|Ziff(?:er|\.)|n°|no\.)\s*", re.I)),
    ("letter", re.compile(r"(lit\.|Buchst(?:abe[n]?|\.)|onder(?:deel)?|sub|letter|point|lettre)(?![\w])\s*", re.I)),
    ("extra", re.compile(r"(Alt(?:ernative|\.)|Var(?:iante|\.)|Hs\.|Halbs(?:atz|\.)|Fall|UAbs\.|Unterabs(?:atz|\.))\s*(\d+)(?![\w])")),
]
_SCHEIDING = re.compile(r"\s*(,|/|\b(?:und|oder|sowie|bzw\.|en|of|et|ou|and|or|e|y|o)\b)\s*")
_BEREIK = re.compile(r"\s*(–|—|-|\bbis(?:\s+einschließlich)?\b|\btot\s+en\s+met\b|\bt/m\b|\bà\b|\bto\b)\s*")
_VERBAND = re.compile(r"\s*,?\s*(i\.\s?V\.\s?m\.|iVm|in\s+Verbindung\s+mit|jo\.?|j°|jis\.|juncto|in\s+verbinding\s+met)\s*", re.I)
_LIDWOORD = re.compile(r"(des|der|dem|vom|van\s+het|van\s+de|van|du|de\s+la|de\s+l['’]|of\s+the|of)\s+", re.I)
_WET_BEGIN = {"oud", "code", "loi", "wet", "disp", "legge", "ley", "codice", "código", "codigo"}
_AFKORTING = re.compile(r"(?:[A-ZÄÖÜ][\w\-]*[A-ZÄÖÜ][\w\-]*|[a-zäöü]{1,3}[A-ZÄÖÜ]\w*[A-ZÄÖÜ]\w*)")


class _Lezer:
    """Leest vanaf een anker ("§§", "art.") de keten die volgt."""

    def __init__(self, tekst: str, pos: int, anker: str, meervoud: bool) -> None:
        self.t, self.pos, self.par, self.meervoud = tekst, pos, anker.startswith("§"), meervoud
        # Romeinse leden ("§ 433 II", "Art. 2 I GG") alleen bij § en bij het Duitse "Art."/"Artikel" met hoofdletter
        self.romeins_mag = self.par or anker.startswith("Art")
        self.elementen: list[Element] = []
        self.soort: str | None = None  # het laatst met een woord aangeduide onderdeel (lid, zin, nr, letter)
        self.romeins = False

    # -- hulpjes
    def _sla_over(self, pos: int | None = None) -> int:
        return _SPATIE.match(self.t, self.pos if pos is None else pos).end()

    def _nummer(self, pos: int):
        return (_NR_PAR if self.par else _NR_ART).match(self.t, pos)

    @property
    def _el(self) -> Element:
        return self.elementen[-1]

    def _detail(self, nieuw: bool = False) -> Detail:
        if nieuw or not self._el.details:
            self._el.details.append(Detail())
        return self._el.details[-1]

    def _zet(self, soort: str, waarde: str, nieuw: bool = False) -> None:
        """Zet een onderdeel; een tweede lid ("Abs. 1, 3") of een tweede zin onder hetzelfde lid wordt een nieuw Detail."""
        d = self._detail()
        if nieuw or getattr(d, soort) is not None:
            hoger = {"lid": {}, "zin": {"lid": d.lid}, "nr": {"lid": d.lid, "zin": d.zin}, "letter": {"lid": d.lid, "zin": d.zin, "nr": d.nr},
                     "extra": {"lid": d.lid, "zin": d.zin, "nr": d.nr, "letter": d.letter}}[soort]
            self._el.details.append(Detail(**hoger, **{soort: waarde}))
        else:
            self._el.details[-1] = Detail(**{**d.__dict__, soort: waarde})

    # -- de keten
    def lees(self) -> list[Element]:
        pos = self._sla_over()
        m = self._nummer(pos)
        if not m:
            return []
        self.elementen.append(Element(re.sub(r"\s+", "", m.group(1)), pos, m.end()))
        self.pos = m.end()
        while self._stap():
            pass
        return self.elementen

    def _waarde(self, soort: str, pos: int):
        """De waarde na een woord als "Abs." of "lit.": een getal, een Romeins cijfer of een letter."""
        if soort == "letter":
            return _LETTER.match(self.t, pos)
        return _GETAL.match(self.t, pos)

    def _onderdeel(self, pos: int) -> bool:
        """Een onderdeel direct na het artikel of het vorige onderdeel: "Abs. 1", "II", "1" (zin na Romeins lid), "(1)(a)"."""
        for soort, patroon in _SOORT:
            m = patroon.match(self.t, pos)
            if not m:
                continue
            if soort == "extra":
                self._zet("extra", f"{m.group(1)} {m.group(2)}".replace("Alternative", "Alt.").replace("Variante", "Var."))
                self.pos, self._el.eind = m.end(), m.end()
                return True
            w = self._waarde(soort, m.end())
            if not w:
                return False
            self._zet(soort, w.group(1))
            self.soort, self.romeins = soort, False
            self.pos, self._el.eind = w.end(), w.end()
            return True
        if m := _HAAK.match(self.t, pos) if pos == self.pos else None:  # "6(1)(a)": zonder spatie
            v = m.group(1)
            self._zet("lid" if v[0].isdigit() and not (self._el.details and self._el.details[-1].lid) else "nr" if v[0].isdigit() else "letter", v)
            self.pos, self._el.eind = m.end(), m.end()
            return True
        if self.romeins_mag:
            m = _ROM.match(self.t, pos)
            if m and m.group(1) in _ROMEINS and not (self._el.details and not self.romeins and self.soort):
                self._zet("lid", str(_ROMEINS[m.group(1)]))
                self.soort, self.romeins = "lid", True
                self.pos, self._el.eind = m.end(), m.end()
                return True
            if self.romeins and self._el.details and self._el.details[-1].zin is None and self._el.details[-1].nr is None:
                m = re.match(r"(\d{1,2})(?![\w.:/])", self.t[pos:])
                if m:  # "§ 812 I 1": zin 1 van lid 1
                    self._zet("zin", m.group(1))
                    self.pos = self._el.eind = pos + m.end()
                    return True
        return False

    def _stap(self) -> bool:
        pos = self._sla_over()
        if self._onderdeel(pos):
            return True
        if m := _FF.match(self.t, pos):
            self._el.ff = True
            self.pos = self._el.eind = m.end()
            return True
        # bereik: "§§ 929 bis 931", "art. 1112 à 1112-2", "Abs. 2 bis 4"
        if m := _BEREIK.match(self.t, self.pos):
            p = self._anker_over(m.end())
            if self.soort and not self.romeins and (w := _GETAL.match(self.t, p)) and p == m.end():
                d = self._el.details[-1]
                self._el.details[-1] = Detail(**{**d.__dict__, self.soort: f"{getattr(d, self.soort)}–{w.group(1)}"})
                self.pos = self._el.eind = w.end()
                return True
            n = self._nummer(p)
            if n and not self._el.details and self._el.tot is None:
                self._el.tot = re.sub(r"\s+", "", n.group(1))
                self.pos = self._el.eind = n.end()
                return True
            return False
        m = _VERBAND.match(self.t, self.pos) or _SCHEIDING.match(self.t, self.pos)
        if not m:
            return False
        p = m.end()
        na_anker = self._anker_over(p)
        if na_anker == p:  # zonder nieuw "§": kan een onderdeel van hetzelfde artikel zijn
            for soort, patroon in _SOORT:
                if patroon.match(self.t, p):
                    oud = self.pos
                    self.pos = p
                    self._detail(nieuw=soort == "lid")
                    if self._onderdeel(p):
                        return True
                    self._el.details.pop()
                    self.pos = oud
                    return False
            if self.romeins_mag:
                r = _ROM.match(self.t, p)
                if r and r.group(1) in _ROMEINS and self.romeins:
                    self._el.details.append(Detail(lid=str(_ROMEINS[r.group(1)])))
                    self.pos = self._el.eind = r.end()
                    return True
            if self.soort and not self.romeins and (w := self._waarde(self.soort, p)) and self._hoort_bij_onderdeel(w.group(1), p, w.end()):
                self._zet(self.soort, w.group(1), nieuw=self.soort == "lid")
                self.pos = self._el.eind = w.end()
                return True
        n = self._nummer(na_anker)
        if not n:
            return False
        if na_anker == p and not self._zelfde_vorm(n.group(1)):
            return False
        self.elementen.append(Element(re.sub(r"\s+", "", n.group(1)), na_anker, n.end()))
        self.soort, self.romeins = None, False
        self.pos = n.end()
        return True

    def _anker_over(self, pos: int) -> int:
        m = _ANKER.match(self.t, pos)
        return _SPATIE.match(self.t, m.end()).end() if m else pos

    def _zelfde_vorm(self, nummer: str) -> bool:
        """Een kaal getal na een komma is alleen een volgend artikel als het eruitziet als het vorige ("6:74, 6:81"; niet
        "art. 6:162, 3 jaar")."""
        vorm = lambda s: (":" in s, "-" in s, "." in s)  # noqa: E731
        return vorm(nummer) == vorm(self.elementen[0].nummer) and not re.match(r"\s*(?:Jahre|jaar|ans|years|Monat|maand|€|Euro|%)", self.t[self.pos:][len(nummer) + 2:][:12])

    def _hoort_bij_onderdeel(self, waarde: str, pos: int, eind: int) -> bool:
        """"§§ 280 Abs. 1, 3, 281": de 3 is Abs. 3, de 281 een nieuw artikel. Een kaal getal na "Abs. x," telt als nog een
        Absatz als er maar één § staat, of als het klein is, oploopt en kleiner is dan het artikelnummer."""
        if self.soort == "letter":
            return True
        if not waarde[0].isdigit():
            return False
        if not self._zelfde_vorm(waarde) or re.match(r"\s*(?:S\.|Satz|Nr\.|lit\.|Alt\.|Hs\.|zin|onder)", self.t[eind:]):
            return True
        vorige = getattr(self._el.details[-1], self.soort) if self._el.details else None
        try:
            n, v, art = int(re.match(r"\d+", waarde).group()), int(re.match(r"\d+", vorige or "0").group()), int(re.match(r"\d+", self._el.nummer).group())
        except (AttributeError, ValueError):
            return False
        if not self.meervoud:
            return n > v and n <= 30
        return v < n <= 20 and n < art


# --- de wet achter de keten ----------------------------------------------------------------------------------------


def _wet_na(tekst: str, pos: int, proef: str) -> tuple[str | None, int, str | None]:
    """De wet die na de keten staat: (tekst van de wet, eindpositie, onbekende afkorting).

    De kortste reeks woorden die een wet noemt wint ("BGB" in "BGB verlangen"), tenzij een woord meer een andere wet
    geeft ("SGB V" naast "SGB", "Rome II" naast "Rome I")."""
    begin = _SPATIE.match(tekst, pos).end()
    lw = _LIDWOORD.match(tekst, begin)
    begin_wet = lw.end() if lw else begin
    regel = tekst[begin_wet:begin_wet + 90].split("\n")[0]
    if volgende := _ANKER.search(regel):  # niet over de volgende verwijzing heen lezen
        regel = regel[:volgende.start()]
    woorden = list(re.finditer(r"\S+", regel))[:6]
    # Een wet begint met een hoofdletter of een afkorting ("c.c.", "oud BW"); een gewoon woord ("greift") is er geen.
    if woorden and re.fullmatch(r"[a-zäöüßàâéèêëïîôùûç]{3,}", woorden[0].group().strip(",;:.)(")) and woorden[0].group().strip(",;:.)(") not in _WET_BEGIN:
        woorden = []
    beste: tuple[str, tuple, int] | None = None  # (tekst, (stelsel, wet), aantal woorden)
    for k in range(1, len(woorden) + 1):
        if beste is not None and k > beste[2] + 2:
            break
        ruw = regel[:woorden[k - 1].end()].rstrip(",;:)]»”\"'")
        kaal = ruw.rstrip(".")
        # de punt hoort bij een afkorting met punten ("C. civ.", "c.c."), niet bij "BGB." aan het eind van een zin
        for kandidaat in dict.fromkeys((ruw if "." in kaal else kaal, kaal)):
            if not kandidaat or not artikelen.noemt_wet(kandidaat):
                continue
            gelezen = artikelen.herken(f"{proef} {kandidaat}")
            if not gelezen:
                continue
            sleutel = (gelezen[0].stelsel, gelezen[0].wet)
            if beste is None or sleutel != beste[1]:
                beste = (kandidaat, sleutel, k)
            break
    if beste is not None:
        return beste[0], begin_wet + len(beste[0]), None
    if woorden and begin_wet == begin:
        eerste = woorden[0].group().rstrip(",;:).")
        if _AFKORTING.fullmatch(eerste) and eerste not in _ROMEINS and artikelen.onbekende_wet(f"{proef} {eerste}"):
            return None, begin + len(eerste), eerste
    return None, pos, None


def _stelsel_past(stelsel: str, par: bool) -> bool:
    stijl = artikelen.regels(stelsel).stijl
    return (stijl == "§") == par or (not par and stelsel == "DE")


def _maak_refs(v: Vondst, wet_tekst: str | None, stelsel: str | None, wet: str | None) -> None:
    """Zet bij elk element de Ref: met de wet uit de tekst (via `artikelen.herken`), of met het aangenomen stelsel."""
    teken = "§" if v.stijl == "§" else "art."
    for e in v.elementen:
        nummer = e.nummer
        if wet_tekst is not None:
            refs = artikelen.herken(f"{teken} {nummer} {wet_tekst}")
            r = refs[0] if refs else None
        elif stelsel:
            r = artikelen.lees(stelsel, f"{teken} {nummer}")
            if r is not None and r.nummer and wet:
                r = Ref(r.stelsel, r.nummer, wet)
        else:
            r = None
        if r is None or not r.nummer:
            continue
        tot = e.tot
        # "Art. 5-7 DSGVO" is een bereik; alleen in stelsels met streepjes in het nummer (FR, IT …) hoort het erbij.
        if tot is None and "-" in nummer and r.stelsel not in ("FR", "IT", "QC", "US", "BE", "ES", "BR", "CL"):
            a, _s, b = nummer.partition("-")
            if b.isdigit() and a.isdigit() and int(b) > int(a):
                r, tot = Ref(r.stelsel, a, r.wet), b
        if tot:
            t = artikelen.lees(r.stelsel, f"{teken} {tot}")
            tot = t.nummer if t and t.nummer else tot
        d = next((x for x in e.details if not x.leeg), None)
        e.ref = Ref(r.stelsel, r.nummer, r.wet, tot, detail_tekst(d, r.stelsel) or None if d else None)
        v.stelsel, v.wet = r.stelsel, r.wet


def vind(tekst: str, stelsel: str | None = None, wet: str | None = None, draag_over: bool = True) -> list[Vondst]:
    """Alle artikelverwijzingen in `tekst`, in volgorde.

    `stelsel` (en `wet`): wat geldt als er geen wet achter een verwijzing staat. Met `draag_over` gaat de wet van de vorige
    verwijzing in dezelfde alinea daarvóór."""
    uit: list[Vondst] = []
    vorige: tuple[str, str | None, int] | None = None  # (stelsel, wet, eindpositie)
    pos = 0
    while True:
        m = _ANKER.search(tekst, pos)
        if not m:
            break
        par = m.group(1).startswith("§")
        meervoud = m.group(1) in ("§§",) or m.group(1).lower().rstrip(".") in ("artt", "artikelen", "articles", "artículos", "articulos")
        lezer = _Lezer(tekst, m.end(), m.group(1), meervoud)
        elementen = lezer.lees()
        if not elementen:
            pos = m.end()
            continue
        v = Vondst(m.start(), lezer.pos, "", elementen, stijl="§" if par else "art", meervoud=meervoud)
        proef = f"{'§' if par else 'art.'} {elementen[0].nummer}"
        wet_tekst, eind, onbekend = _wet_na(tekst, lezer.pos, proef)
        if onbekend:
            v.onbekend, v.eind = onbekend, eind
        elif wet_tekst is not None:
            v.wet_tekst, v.eind = wet_tekst, eind
            _maak_refs(v, wet_tekst, None, None)
        else:
            nl = all(re.fullmatch(r"\d+[A-Za-z]?:\d+[a-z]{0,3}", e.nummer) for e in elementen)
            if nl and not par:  # boek:nummer is zonder wet al het BW
                _maak_refs(v, None, "NL", None)
            elif draag_over and vorige and "\n\n" not in tekst[vorige[2]:v.start] and v.start - vorige[2] < 600 and _stelsel_past(vorige[0], par):
                _maak_refs(v, None, vorige[0], vorige[1])
            elif stelsel and _stelsel_past(stelsel, par):
                _maak_refs(v, None, stelsel, wet)
            elif par and stelsel is None:
                _maak_refs(v, None, "DE", None)
            v.aangenomen = True
        v.ruw = tekst[v.start:v.eind]
        uit.append(v)
        if v.refs and not v.aangenomen:
            vorige = (v.stelsel, v.wet, v.eind)
        elif v.refs and vorige:
            vorige = (vorige[0], vorige[1], v.eind)
        pos = max(v.eind, m.end())
    return uit


def refs(tekst: str, stelsel: str | None = None) -> list[Ref]:
    """Alle verwijzingen als platte lijst, zonder dubbelen (op stelsel, wet, nummer)."""
    uit, gezien = [], set()
    for v in vind(tekst, stelsel):
        for r in v.refs:
            if (r.stelsel, r.wet, r.nummer) not in gezien:
                gezien.add((r.stelsel, r.wet, r.nummer))
                uit.append(r)
    return uit


def koppel_md(tekst: str | None, bestaat=None, stelsel: str | None = "DE") -> str:
    """Markdown waarin elke verwijzing een link is naar het artikel in de lokale tekst.

    `bestaat(ref) -> bool`: alleen artikelen die er zijn worden een link (standaard: alles). Een keten krijgt een link per
    schakel: in "§§ 280 I, III, 281 BGB" leiden "280 I, III" en "281" elk naar hun eigen artikel."""
    if not tekst:
        return ""
    delen, laatste = [], 0
    for v in vind(tekst, stelsel):
        if tekst[max(0, v.start - 1):v.start] == "[" or tekst[v.eind:v.eind + 2] == "](":
            continue  # staat al in een link
        enkel = len(v.elementen) == 1
        for e in v.elementen:
            if e.ref is None or e.ref.url is None or (bestaat is not None and not bestaat(e.ref)):
                continue
            a, b = (v.start, v.eind) if enkel else (e.start, e.eind)
            if a < laatste:
                continue
            delen.append(tekst[laatste:a])
            delen.append(f"[{tekst[a:b]}]({e.ref.url.replace(' ', '%20')})")
            laatste = b
    delen.append(tekst[laatste:])
    return "".join(delen)


def hoofdwet_naam(stelsel: str) -> str:
    return HOOFDWET.get(stelsel, "")
