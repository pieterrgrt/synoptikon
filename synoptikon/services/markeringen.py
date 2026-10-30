"""Markeringen: stukken tekst in een artikel of uitspraak die je voor een vak aanwees.

Een markering bewaart `quote` met een stukje tekst ervoor en erna (`voor`, `na`), geen index: `vind` zoekt de quote in de
actuele tekst, en kiest bij meerdere plekken de plek waar de omgeving het best past. Spaties en regeleinden tellen niet mee
(de browser en de gerenderde tekst verschillen daarin). Staat de quote niet meer in de tekst (een nieuwe versie van de wet),
dan is de markering 'verweesd': ze blijft in de lijst staan maar kleurt niets.

Gebruik:
- `markeer_html`: de gerenderde tekst met `<mark>` om de gemarkeerde stukken (artikel- en brontekst);
- `markeer_md`: de tekst van een kaart met de kern en voorwaarden vetgedrukt;
- `kern_tekst`: de gemarkeerde kernstukken als voorstel voor de rechtsregel van een arrestkaart.
"""
from __future__ import annotations

import html as htmllib
import re
from collections import defaultdict

from markupsafe import Markup
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import MARKERINGSOORTEN, Markering

CONTEXT = 40  # tekens ervoor en erna die bewaard worden
MAX_QUOTE = 2000


def _strak(tekst: str) -> tuple[str, list[int]]:
    """De tekst zonder witruimte, met van elk teken de plek in het origineel."""
    plek = [i for i, c in enumerate(tekst) if not c.isspace()]
    return "".join(tekst[i] for i in plek), plek


def _vind_strak(stroom: str, m: Markering) -> tuple[int, int] | None:
    q = re.sub(r"\s+", "", m.quote)
    if not q:
        return None
    voor, na = re.sub(r"\s+", "", m.voor or ""), re.sub(r"\s+", "", m.na or "")
    beste, score, start = None, -1, stroom.find(q)
    while start != -1:
        s = 0
        for a, b in zip(reversed(stroom[:start]), reversed(voor)):
            if a != b:
                break
            s += 1
        for a, b in zip(stroom[start + len(q):], na):
            if a != b:
                break
            s += 1
        if s > score:
            beste, score = start, s
        start = stroom.find(q, start + 1)
    return None if beste is None else (beste, beste + len(q))


def vind(tekst: str, m: Markering) -> tuple[int, int] | None:
    """Begin en einde van de markering in `tekst`, of None als ze er niet (meer) in staat."""
    stroom, plek = _strak(tekst)
    r = _vind_strak(stroom, m)
    return None if r is None else (plek[r[0]], plek[r[1] - 1] + 1)


def verweesd(html: str, ms: list[Markering]) -> set[int]:
    """Id's van markeringen die niet meer in de (gerenderde) tekst staan."""
    stroom, _p = _strak(htmllib.unescape(re.sub(r"<[^>]*>", "", str(html or ""))))
    return {m.id for m in ms if _vind_strak(stroom, m) is None}


# --- gerenderde HTML ----------------------------------------------------------------------------------------------------

_TAG = re.compile(r"(<[^>]*>)")


def markeer_html(html: str, ms: list[Markering]) -> Markup:
    """Zet <mark> om de gemarkeerde stukken in gerenderde HTML (ook over tags heen, per tekstknoop)."""
    html = str(html)
    if not ms:
        return Markup(html)
    delen = _TAG.split(html)
    knopen = [(i, htmllib.unescape(d)) for i, d in enumerate(delen) if d and not d.startswith("<")]
    stroom, herkomst = [], []  # per teken zonder witruimte: (index in delen, plek in de tekstknoop)
    for i, t in knopen:
        for j, c in enumerate(t):
            if not c.isspace():
                stroom.append(c)
                herkomst.append((i, j))
    stroom = "".join(stroom)
    bereiken: dict[int, list[tuple[int, int, Markering]]] = defaultdict(list)
    for m in ms:
        r = _vind_strak(stroom, m)
        if r is None:
            continue
        per_knoop: dict[int, list[int]] = defaultdict(list)
        for k in range(*r):
            per_knoop[herkomst[k][0]].append(herkomst[k][1])
        for i, js in per_knoop.items():
            bereiken[i].append((min(js), max(js) + 1, m))
    for i, lijst in bereiken.items():
        tekst = dict(knopen)[i]
        uit, vanaf = [], 0
        for a, b, m in sorted(lijst, key=lambda x: x[0]):
            if a < vanaf:  # overlap met een eerdere markering: die wint
                continue
            titel = f' title="{htmllib.escape(m.notitie, quote=True)}"' if m.notitie else ""
            uit.append(htmllib.escape(tekst[vanaf:a], quote=False))
            uit.append(f'<mark class="markering m-{m.soort}" data-id="{m.id}"{titel}>{htmllib.escape(tekst[a:b], quote=False)}</mark>')
            vanaf = b
        uit.append(htmllib.escape(tekst[vanaf:], quote=False))
        delen[i] = "".join(uit)
    return Markup("".join(delen))


# --- markdown van een kaart ---------------------------------------------------------------------------------------------


def markeer_md(tekst: str, ms: list[Markering]) -> str:
    """De kern en voorwaarden vetgedrukt in de (markdown)tekst van een kaart. Wat er niet in te vinden is, blijft weg."""
    gevonden = []
    for m in ms:
        if m.soort in ("kern", "voorwaarde") and (r := vind(tekst, m)):
            gevonden.append(r)
    uit, vanaf = [], 0
    for a, b in sorted(gevonden):
        if a < vanaf:
            continue
        uit += [tekst[vanaf:a], "**", tekst[a:b].strip(), "**"]
        vanaf = b
    uit.append(tekst[vanaf:])
    return "".join(uit)


# --- opslaan en ophalen -------------------------------------------------------------------------------------------------


def maak(db: Session, profiel_id: int, quote: str, voor: str = "", na: str = "", soort: str = "kern", vak: str | None = None,
         notitie: str | None = None, bron_id: int | None = None, stelsel: str | None = None, wet: str | None = None,
         nummer: str | None = None) -> Markering | None:
    """Een markering van een bron of een artikel; None bij een lege of te lange quote of zonder doel."""
    quote = (quote or "").strip()
    if not quote or len(quote) > MAX_QUOTE or not (bron_id or (stelsel and nummer)):
        return None
    artikel = not bron_id  # een markering hoort bij een bron of bij een artikel, niet bij allebei
    m = Markering(profiel_id=profiel_id, bron_id=bron_id or None, stelsel_code=(stelsel.upper() if artikel and stelsel else None),
                  wet=(wet or None) if artikel else None, nummer=(nummer or None) if artikel else None, quote=quote,
                  voor=(voor or "")[-CONTEXT:], na=(na or "")[:CONTEXT], vak=(vak or "").strip() or None,
                  soort=soort if soort in MARKERINGSOORTEN else "kern", notitie=(notitie or "").strip() or None)
    db.add(m)
    db.flush()
    return m


def van_bron(db: Session, profiel_id: int, bron_id: int) -> list[Markering]:
    return list(db.scalars(select(Markering).where(Markering.profiel_id == profiel_id, Markering.bron_id == bron_id)
                           .order_by(Markering.id)).all())


def van_artikel(db: Session, profiel_id: int, stelsel: str, wet: str | None, nummer: str) -> list[Markering]:
    q = select(Markering).where(Markering.profiel_id == profiel_id, Markering.stelsel_code == stelsel, Markering.nummer == nummer)
    return [m for m in db.scalars(q.order_by(Markering.id)).all() if (m.wet or None) == (wet or None)]


def voor_vak(ms: list[Markering], vak: str | None) -> list[Markering]:
    """Wat bij dit vak hoort: markeringen voor dat vak en die voor elk vak. Zonder vak: alle."""
    return [m for m in ms if not vak or not m.vak or m.vak.lower() == vak.lower()]


def kern_tekst(db: Session, profiel_id: int, bron_id: int, vak: str | None = None) -> str:
    """De gemarkeerde kernstukken van een uitspraak, in de volgorde waarin je ze aanwees: het voorstel voor de rechtsregel."""
    ms = [m for m in voor_vak(van_bron(db, profiel_id, bron_id), vak) if m.soort == "kern"]
    return "\n\n".join(re.sub(r"\s+", " ", m.quote) for m in ms)
