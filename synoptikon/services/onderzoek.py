"""Rechtsvergelijkend onderzoek door Claude bij een vraag.

Je schrijft de vraag (het tertium comparationis) en kiest de stelsels; Claude onderzoekt per stelsel hoe het recht die
vraag beantwoordt, leest daarvoor de wetteksten uit de lokale import, zoekt de leidende rechtspraak op het web, en
schrijft een functionele vergelijking. Het resultaat:

- per stelsel `kern` (één zin) en `analyse` (markdown) in het Antwoord, maar alleen waar die nog leeg zijn: wat je zelf
  schreef blijft staan; Claudes versie staat dan nog in het onderzoek zelf (de pagina toont haar);
- de genoemde artikelen en uitspraken als Bron (wetsartikelen met de lokale tekst en een koppeling aan het
  geïmporteerde artikel), gekoppeld aan het Antwoord met hun rol;
- een synthese: overeenkomsten, verschillen, en waar de stelsels functioneel uitkomen.

Alles staat gemarkeerd als "Claude, niet geverifieerd" (in de analyse en in de opmerking bij de bron).
"""
from __future__ import annotations

import logging
import threading

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..config import settings
from ..models import Antwoord, AntwoordBron, Bron, Onderzoek, Stelsel, Vraag, now
from . import claude
from .artikelen import herken
from .correspondentie import Context, wettekst_artikel

log = logging.getLogger(__name__)
MARKERING = "*Onderzoek door Claude (niet geverifieerd).*"

SYSTEEM = """Je doet rechtsvergelijkend onderzoek voor Synoptikon, de werkomgeving van een jurist (Nederlands recht, \
Europees recht; nu rechtenstudie in Duitsland). Werk volgens de functionele methode (Zweigert/Kötz): vertrek van het \
probleem, niet van de begrippen van één stelsel; laat per stelsel zien welke regels, leerstukken en uitspraken dat \
probleem oplossen, ook als ze in een ander rechtsgebied of onder een andere naam staan; let op faux amis.

Werkwijze:
- Lees elk wetsartikel dat je noemt met `artikel_lezen`. Zoek artikelen met `wetteksten_doorzoeken` in de taal van \
het stelsel. Citeer een wettekst nooit uit je geheugen.
- Zoek leidende rechtspraak op het web (bij voorkeur officiële bronnen) en kijk ook in `eigen_bronnen_doorzoeken`. \
Geef per uitspraak gerecht, datum, vindplaats (ECLI, NJ, BGHZ, NJW, Bull. civ., Slg.) en de kern. Een letterlijke \
kernoverweging alleen als je haar uit een bron hebt.
- Schrijf in het Nederlands, als een zorgvuldige rechtswetenschapper: precies, met vindplaatsen, zonder opvulling. \
Wat je afleidt zonder bron markeer je met (niet geverifieerd). Onzekerheid benoem je.
- Per stelsel: `kern` is één zin met het antwoord; `analyse` is markdown (geen koppen hoger dan ###) met de regeling, \
de leerstukken, de rechtspraak, en de systematische plaats.
- `bronnen` per stelsel: de wetsartikelen (soort wet, `citeer` precies in de citeerwijze die `artikel_lezen` \
accepteerde) en uitspraken (soort rechtspraak) waarop de analyse rust, met hun `rol` (hoofdregel, uitzondering, \
rechtspraak, literatuur, conflictenrecht, bescherming derden …) en een korte `notitie` waarom ze ertoe doen.
- `synthese`: markdown, de eigenlijke vergelijking: waar komen de stelsels functioneel op hetzelfde uit, waar niet, \
en waarom (systematiek, dogmatiek, beleid). Sluit af met open punten voor verder onderzoek."""

BRON_SCHEMA = {
    "type": "object",
    "properties": {
        "soort": {"type": "string", "enum": ["wet", "rechtspraak", "literatuur", "softlaw"]},
        "citeer": {"type": "string"},
        "titel": {"type": "string", "description": "Opschrift of zaaknaam; leeg als onbekend"},
        "vindplaats": {"type": "string", "description": "ECLI, NJ, BGHZ …; leeg bij wetsartikelen"},
        "url": {"type": "string"},
        "tekst": {"type": "string", "description": "Bij rechtspraak de kernoverweging als die letterlijk uit een bron komt, anders leeg; bij wetten leeg (de app haalt de tekst zelf)"},
        "rol": {"type": "string"},
        "notitie": {"type": "string"},
    },
    "required": ["soort", "citeer", "titel", "vindplaats", "url", "tekst", "rol", "notitie"],
    "additionalProperties": False,
}

SCHEMA = {
    "type": "object",
    "properties": {
        "stelsels": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "kern": {"type": "string"},
                    "analyse": {"type": "string"},
                    "bronnen": {"type": "array", "items": BRON_SCHEMA},
                },
                "required": ["code", "kern", "analyse", "bronnen"],
                "additionalProperties": False,
            },
        },
        "synthese": {"type": "string"},
    },
    "required": ["stelsels", "synthese"],
    "additionalProperties": False,
}


def laatste(db: Session, vraag: Vraag) -> Onderzoek | None:
    return db.scalar(select(Onderzoek).where(Onderzoek.vraag_id == vraag.id).order_by(Onderzoek.id.desc()).limit(1))


def start(db: Session, vraag: Vraag, codes: list[str], opdracht: str = "", achtergrond: bool = True) -> Onderzoek:
    o = Onderzoek(vraag_id=vraag.id, stelsels=",".join(codes), opdracht=opdracht.strip() or None, status="wacht")
    db.add(o)
    db.commit()
    if achtergrond:
        threading.Thread(target=_voer_uit, args=(o.id,), daemon=True).start()
    else:
        _voer_uit(o.id, db)
    return o


def _prompt(db: Session, vraag: Vraag, codes: list[str], opdracht: str | None) -> str:
    namen = {s.code: s.naam for s in db.scalars(select(Stelsel)).all()}
    delen = [f"# Vraag\n\n{vraag.titel}"]
    if vraag.omschrijving:
        delen.append(vraag.omschrijving)
    if vraag.rechtsgebied:
        delen.append(f"Rechtsgebied: {vraag.rechtsgebied}")
    delen.append("# Stelsels\n\n" + "\n".join(f"- {c}: {namen.get(c, c)}" for c in codes))
    # Wat er al staat, zodat Claude aanvult in plaats van overdoet.
    al = []
    for a in vraag.antwoorden:
        if a.stelsel_code in codes and (a.kern or a.analyse or a.bronnen):
            al.append(f"## {a.stelsel_code}\nKern: {a.kern or '—'}\nBronnen: " + "; ".join(ab.bron.citeertitel for ab in a.bronnen))
    if al:
        delen.append("# Wat er al in de synopse staat\n\n" + "\n\n".join(al))
    if opdracht:
        delen.append(f"# Aanwijzingen\n\n{opdracht}")
    delen.append("Onderzoek de vraag voor elk van deze stelsels en lever het resultaat volgens het schema.")
    return "\n\n".join(delen)


def _voer_uit(oid: int, db: Session | None = None) -> None:
    from ..db import session_factory

    eigen = db is None
    db = db or session_factory()()
    try:
        o = db.get(Onderzoek, oid)
        vraag = db.scalar(select(Vraag).where(Vraag.id == o.vraag_id).options(
            selectinload(Vraag.antwoorden).selectinload(Antwoord.bronnen).selectinload(AntwoordBron.bron)))
        codes = [c for c in o.stelsels.split(",") if c]
        o.status, o.model = "bezig", settings.claude_model
        db.commit()

        def voortgang(stap: str) -> None:
            o.voortgang = stap
            db.commit()

        try:
            r, usd = claude.loop(db, "onderzoek", SYSTEEM, _prompt(db, vraag, codes, o.opdracht), SCHEMA, effort="high",
                                 max_rondes=30, max_zoekacties=12, max_tokens=64000, voortgang=voortgang)
            o.resultaat, o.usd = r, usd
            verwerk(db, vraag, r, codes)
            o.status, o.voortgang = "klaar", None
        except claude.ClaudeFout as e:
            o.status, o.fout = "fout", str(e)
        except Exception as e:
            log.exception("onderzoek")
            o.status, o.fout = "fout", f"{type(e).__name__}: {e}"
        o.klaar = now()
        db.commit()
    finally:
        if eigen:
            db.close()


def _bron(db: Session, stelsel: str, b: dict) -> Bron | None:
    """Zoekt of maakt de bron. Een wetsartikel krijgt de lokale tekst en de koppeling aan het geïmporteerde artikel."""
    citeer = (b.get("citeer") or "").strip()
    if not citeer:
        return None
    if b.get("soort") == "wet":
        for ref in herken(citeer, stelsel) or herken(citeer):
            wa = wettekst_artikel(db, ref)
            if wa is None:
                continue
            bestaand = db.scalar(select(Bron).where(Bron.wettekst_artikel_id == wa.id))
            if bestaand is None:
                bestaand = db.scalar(select(Bron).where(Bron.stelsel_code == ref.stelsel, Bron.citeertitel == ref.citeer))
            if bestaand:
                return bestaand
            pad = Context(db).pad(ref)
            nieuw = Bron(stelsel_code=ref.stelsel, soort="wet", citeertitel=ref.citeer, titel=wa.opschrift, tekst=wa.tekst,
                         taal=wa.wettekst.taal or db.get(Stelsel, ref.stelsel).taal, url=wa.wettekst.bron_url,
                         wettekst_artikel_id=wa.id, systematiek_id=pad[-1].id if pad else None,
                         opmerking=f"Tekst uit de geïmporteerde versie {wa.wettekst.versie}; gekozen door Claude.")
            db.add(nieuw)
            db.flush()
            return nieuw
    vindplaats = (b.get("vindplaats") or "").strip() or None
    bestaand = db.scalar(select(Bron).where(Bron.vindplaats == vindplaats)) if vindplaats else None
    bestaand = bestaand or db.scalar(select(Bron).where(Bron.stelsel_code == stelsel, Bron.citeertitel == citeer[:200]))
    if bestaand:
        return bestaand
    st = db.get(Stelsel, stelsel)
    nieuw = Bron(stelsel_code=stelsel, soort=b.get("soort") if b.get("soort") in ("rechtspraak", "literatuur", "softlaw", "wet") else "literatuur",
                 citeertitel=citeer[:200], titel=(b.get("titel") or None) and b["titel"][:300], tekst=b.get("tekst") or None,
                 taal=st.taal if st else "nl", vindplaats=vindplaats and vindplaats[:200],
                 vindplaats_type="ECLI" if vindplaats and vindplaats.upper().startswith("ECLI") else None,
                 url=(b.get("url") or None) and b["url"][:500], opmerking="Gevonden door Claude (niet geverifieerd).")
    db.add(nieuw)
    db.flush()
    return nieuw


def verwerk(db: Session, vraag: Vraag, r: dict, codes: list[str]) -> None:
    """Zet het resultaat in de synopse: lege kern en analyse invullen, bronnen koppelen."""
    for s in r.get("stelsels") or []:
        code = (s.get("code") or "").upper()
        if code not in codes:
            continue
        a = vraag.antwoord_voor(code)
        if a is None:
            a = Antwoord(stelsel_code=code)
            vraag.antwoorden.append(a)
            db.flush()
        if not a.kern and s.get("kern"):
            a.kern = s["kern"][:400]
        if not a.analyse and s.get("analyse"):
            a.analyse = f"{MARKERING}\n\n{s['analyse']}"
        gekoppeld = {ab.bron_id for ab in a.bronnen}
        volgorde = max([ab.volgorde for ab in a.bronnen] or [0])
        for b in s.get("bronnen") or []:
            bron = _bron(db, code, b)
            if bron is None or bron.id in gekoppeld:
                continue
            volgorde += 10
            a.bronnen.append(AntwoordBron(bron_id=bron.id, volgorde=volgorde, rol=(b.get("rol") or None) and b["rol"][:60],
                                          notitie=b.get("notitie") or None))
            gekoppeld.add(bron.id)
    db.flush()
