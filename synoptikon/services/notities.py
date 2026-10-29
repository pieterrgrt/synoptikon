"""Kaarten uit notities: Claude leest een notitie, Synoptikon levert de wettekst.

De notities (Obsidian, map Humboldt) staan als kopie in `settings.notities_dir`; `scripts/notities.sh` werkt die kopie
bij en roept daarna `synoptikon notities` aan. Per map hoort een vak (`SYNOPTIKON_NOTITIES_VAKKEN`, of `vak:` in de
frontmatter); mappen zonder vak blijven buiten beschouwing.

Een notitie is aan de beurt als ze nieuw is of haar inhoud veranderd is (sha256). Claude leest haar, controleert elke
norm met `artikel_lezen` en stelt kaarten voor: artikel → inhoud, inhoud → artikel, arrest → rechtsregel en vrije
kaarten voor begrippen, schema's en Streitstände. Ze komen als *voorstel* (inactief) in de leerlijst
"Notities · <vak>"; pas wat je overneemt gaat naar Wunderkammer. Wat er al is (ook afgewezen) gaat mee in de opdracht,
zodat een gewijzigde notitie alleen nieuwe kaarten oplevert.
"""
from __future__ import annotations

import hashlib
import logging
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Kaart, Leerlijst, NotitieBestand, now
from . import claude, leren
from .artikelen import HOOFDWET, herken
from .correspondentie import wettekst_artikel

log = logging.getLogger(__name__)

MIN_TEKENS = 200  # lege of bijna lege notities ("Naamloos") overslaan
MAX_TEKENS = 60000  # langer: afkappen; zo blijft één notitie onder een paar dollar
MAX_KAARTEN = 15
LIJST_PREFIX = "Notities · "

_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?", re.S)


@dataclass
class Bestand:
    pad: str  # relatief, met /
    vak: str
    tekst: str  # zonder frontmatter
    hash: str


def vakken(instelling: str | None = None) -> dict[str, str]:
    """"Zivilrecht 1A=ZR Ia; Kapitalmarktrecht=W" → {"Zivilrecht 1A": "ZR Ia", …}."""
    uit = {}
    for deel in (instelling if instelling is not None else settings.notities_vakken or "").split(";"):
        if "=" in deel:
            map_, vak = (x.strip() for x in deel.split("=", 1))
            if map_ and vak:
                uit[map_] = vak
    return uit


def _frontmatter(tekst: str) -> tuple[dict[str, str], str]:
    m = _FRONTMATTER.match(tekst)
    if not m:
        return {}, tekst
    velden = {}
    for regel in m.group(1).splitlines():
        if ":" in regel and not regel.startswith((" ", "-")):
            k, v = regel.split(":", 1)
            velden[k.strip().lower()] = v.strip().strip("\"'")
    return velden, tekst[m.end():]


def bestanden(root: Path | None = None, per_map: dict[str, str] | None = None) -> Iterator[Bestand]:
    root = root or settings.notities_dir
    per_map = vakken() if per_map is None else per_map
    if not root.is_dir():
        return
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        if any(d.startswith(".") for d in p.relative_to(root).parts) or p.name == "CLAUDE.md":
            continue
        try:
            ruw = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            log.warning("notitie %s niet leesbaar", rel)
            continue
        velden, tekst = _frontmatter(ruw)
        if velden.get("synoptikon", "").lower() in ("nee", "no", "false", "uit"):
            continue
        vak = velden.get("vak") or ("/" in rel and per_map.get(rel.split("/", 1)[0])) or None
        if not vak or len(tekst.strip()) < MIN_TEKENS:
            continue
        yield Bestand(rel, vak, tekst.strip(), hashlib.sha256(ruw.encode()).hexdigest())


def lijst_voor(db: Session, profiel_id: int, vak: str) -> Leerlijst:
    naam = LIJST_PREFIX + vak
    lijst = db.scalar(select(Leerlijst).where(Leerlijst.profiel_id == profiel_id, Leerlijst.naam == naam))
    if lijst is None:
        lijst = Leerlijst(profiel_id=profiel_id, naam=naam, vak=vak, naar_wk=True,
                          omschrijving="Voorstellen uit je notities; wat je overneemt gaat naar Wunderkammer.")
        db.add(lijst)
        db.flush()
    return lijst


# --- Claude ---------------------------------------------------------------------------------------------------------

SYSTEM = """Je maakt leerkaarten uit de collegeaantekeningen van Pieter, rechtenstudent aan de HU Berlin (LL.M.
Europäisches Recht und Rechtsvergleich). Hij herhaalt ze met spaced repetition in Wunderkammer.

Werkwijze:
- Lees de notitie en kies wat examenstof is: centrale normen, definities, Tatbestandsmerkmale, Prüfungsschemata,
  Streitstände met de heersende mening, en uitspraken met hun rechtsregel. Laat organisatorische zaken, losse
  gedachten en wat al in de lijst staat weg.
- Controleer elke norm met artikel_lezen voordat je er een kaart van maakt; citeer nooit uit je geheugen. Een norm
  die artikel_lezen niet vindt, wordt een vrije kaart of valt weg.
- Kaartsoorten:
  - artikel: de wettekst is het antwoord (Synoptikon vult die zelf in). `verwijzing` in citeerwijze ('§ 929 BGB',
    'Art. 49 AEUV'); `vraag` mag leeg (dan "Was steht in § 929 BGB?") of een gerichtere vraag zijn.
  - kern: een omschrijving van wat de norm regelt in `vraag` (zonder het nummer te verraden); antwoord is de norm.
  - arrest: `zaak` (naam, gericht, datum), `vindplaats` (ECLI, BGHZ, Slg.), `antwoord` = de rechtsregel, `feiten` kort.
  - vrij: `vraag` en `antwoord`, voor begrippen, schema's (stappen genummerd), Streitstände en verbanden.
- Schrijf in de taal van de notitie (meestal juristisches Deutsch). Eén ding per kaart; antwoorden kort (hooguit
  zo'n 80 woorden), schema's als genummerde lijst. Markdown mag.
- Hoogstens {max} kaarten; liever minder en goed. Lege velden als lege string.
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "kaarten": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "soort": {"type": "string", "enum": ["artikel", "kern", "arrest", "vrij"]},
                    "verwijzing": {"type": "string"},
                    "vraag": {"type": "string"},
                    "antwoord": {"type": "string"},
                    "zaak": {"type": "string"},
                    "vindplaats": {"type": "string"},
                    "feiten": {"type": "string"},
                },
                "required": ["soort", "verwijzing", "vraag", "antwoord", "zaak", "vindplaats", "feiten"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["kaarten"],
    "additionalProperties": False,
}


def _bestaand(lijst: Leerlijst) -> str:
    regels = []
    for k in lijst.kaarten:
        ref = leren.ref_van(k)
        onderwerp = ref.citeer if ref else (k.zaak or k.vraag or "")
        regels.append(f"- {k.soort}: {onderwerp[:150]}" + (" (afgewezen)" if k.status == "afgewezen" else ""))
    return "\n".join(regels) or "(nog leeg)"


def _opdracht(b: Bestand, lijst: Leerlijst) -> str:
    tekst = b.tekst if len(b.tekst) <= MAX_TEKENS else b.tekst[:MAX_TEKENS] + "\n\n[…afgekapt]"
    return (f"Vak: {b.vak}\nNotitie: {b.pad}\n\nAl in de leerlijst (niet opnieuw voorstellen):\n{_bestaand(lijst)}\n\n"
            f"<notitie>\n{tekst}\n</notitie>")


_GEEN_WET = {"§", "§§", "art", "artt", "abs", "s", "satz", "nr", "lit", "alt", "hs", "halbs", "uabs", "var", "f", "ff"}


def _klopt(db: Session, ref, verwijzing: str) -> bool:
    """Het artikel staat in de lokale wettekst, en een onbekende wet is niet stilletjes de hoofdwet geworden
    ('§ 2 FantasieG' mag geen § 2 BGB worden)."""
    if ref.wet is None:
        hoofdwet = (HOOFDWET.get(ref.stelsel) or "").replace(".", "").replace(" ", "").lower()
        for w in re.findall(r"[^\W\d_][\w.]*", verwijzing):
            w = w.replace(".", "").lower()
            if w not in _GEEN_WET and w != hoofdwet and not re.fullmatch(r"[ivx]+|[a-z]", w):
                return False
    return wettekst_artikel(db, ref) is not None


def _kaarten_uit(db: Session, lijst: Leerlijst, b: Bestand, voorstel: list[dict]) -> list[Kaart]:
    nieuw = []
    for v in voorstel[:MAX_KAARTEN]:
        soort = v.get("soort")
        velden = dict(vraag=v.get("vraag", ""), antwoord=v.get("antwoord", ""), status="voorstel", actief=False, herkomst=b.pad[:300])
        if soort in ("artikel", "kern"):
            refs = [r for r in herken(v.get("verwijzing", "")) if _klopt(db, r, v.get("verwijzing", ""))]
            if refs:
                if soort == "artikel":
                    velden["antwoord"] = ""  # de wettekst is het antwoord
                nieuw += leren.maak_kaarten(db, lijst, [soort], ref=refs[0], **velden)
                continue
            soort = "vrij"  # norm niet herkend: als vrije kaart, als er een vraag en antwoord is
        if soort == "arrest" and (v.get("zaak") or "").strip():
            nieuw += leren.maak_kaarten(db, lijst, ["arrest"], zaak=v["zaak"][:300], vindplaats=(v.get("vindplaats") or "")[:200],
                                        feiten=v.get("feiten", ""), **velden)
        elif (v.get("vraag") or "").strip() and (v.get("antwoord") or "").strip():
            nieuw += leren.maak_kaarten(db, lijst, ["vrij"], **velden)
    return nieuw


def verwerk_notitie(db: Session, profiel_id: int, b: Bestand) -> list[Kaart]:
    lijst = lijst_voor(db, profiel_id, b.vak)
    antwoord, _kosten = claude.loop(db, "notities", SYSTEM.format(max=MAX_KAARTEN), _opdracht(b, lijst), SCHEMA,
                                    effort="medium", max_rondes=15, max_zoekacties=0)
    return _kaarten_uit(db, lijst, b, antwoord.get("kaarten") or [])


@dataclass
class Uitkomst:
    notities: int = 0
    voorstellen: int = 0
    ongewijzigd: int = 0
    over: int = 0  # wachten op een volgende ronde (--max)
    fouten: int = 0


def verwerk(db: Session, profiel_id: int = 1, maximum: int = 10, droog: bool = False) -> Uitkomst:
    """Nieuwe en gewijzigde notities verwerken, hoogstens `maximum` per ronde. `droog`: alleen tellen."""
    uit = Uitkomst()
    gezien = {n.pad: n for n in db.scalars(select(NotitieBestand).where(NotitieBestand.profiel_id == profiel_id))}
    for b in bestanden():
        n = gezien.get(b.pad)
        if n is not None and n.hash == b.hash and not n.fout:
            uit.ongewijzigd += 1
            continue
        if uit.notities >= maximum:
            uit.over += 1
            continue
        uit.notities += 1
        if droog:
            print(f"  {b.vak:<12} {b.pad}")
            continue
        if n is None:
            n = NotitieBestand(profiel_id=profiel_id, pad=b.pad, hash=b.hash)
            db.add(n)
        n.vak, n.hash, n.verwerkt = b.vak, b.hash, now()
        try:
            kaarten = verwerk_notitie(db, profiel_id, b)
            n.voorstellen, n.fout = len(kaarten), None
            uit.voorstellen += len(kaarten)
        except Exception as e:  # ClaudeFout, of de API zelf; de volgende ronde probeert het opnieuw
            log.exception("notitie %s", b.pad)
            db.rollback()
            n = db.scalar(select(NotitieBestand).where(NotitieBestand.profiel_id == profiel_id, NotitieBestand.pad == b.pad)) or NotitieBestand(
                profiel_id=profiel_id, pad=b.pad, vak=b.vak)
            n.hash, n.fout, n.verwerkt = b.hash, str(e)[:2000] or type(e).__name__, now()
            db.add(n)
            db.commit()
            uit.fouten += 1
            if isinstance(e, claude.ClaudeFout) and "budget" in str(e):
                break
            continue
        db.commit()
    return uit


def besluit(k: Kaart, wat: str) -> None:
    """Eén voorstel: `over` (actief, naar Wunderkammer), `af`, of `terug` naar voorstel (ongedaan maken)."""
    if wat == "over":
        k.status, k.actief = None, True
    elif wat == "af":
        k.status, k.actief = "afgewezen", False
    elif wat == "terug":
        k.status, k.actief = "voorstel", False


def beoordeel(lijst: Leerlijst, over: set[int]) -> tuple[int, int]:
    """Voorstellen in de lijst: aangevinkte overnemen (actief, naar Wunderkammer), de rest afwijzen. → (over, af)."""
    n_over = n_af = 0
    for k in lijst.kaarten:
        if k.status != "voorstel":
            continue
        if k.id in over:
            k.status, k.actief = None, True
            n_over += 1
        else:
            k.status, k.actief = "afgewezen", False
            n_af += 1
    return n_over, n_af
