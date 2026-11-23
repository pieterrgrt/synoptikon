"""Claude in Synoptikon: een kleine agent-loop met de lokale wetteksten als gereedschap.

Twee taken gebruiken haar: opzoeken (`services/opzoeken.py`: "waar staat dit en wat staat er?") en rechtsvergelijkend
onderzoek bij een vraag (`services/onderzoek.py`). Claude leest wetteksten uitsluitend via de tools hieronder, dus
uit de geïmporteerde officiële versies; rechtspraak en literatuur zoekt het op het web (`web_search`). Het
eindresultaat is JSON volgens een schema (`output_config.format`).

- Sleutel en model: `SYNOPTIKON_ANTHROPIC_API_KEY`, `SYNOPTIKON_CLAUDE_MODEL` (standaard claude-opus-5-5).
- Budget: `SYNOPTIKON_LLM_BUDGET_USD` per kalendermaand (standaard 20) voor iedereen samen, en per profiel een grens
  (`Profiel.llm_grens_usd`, anders `SYNOPTIKON_LLM_PROFIEL_USD`, standaard 5; een beheerder zonder eigen grens heeft
  alleen het totaal). Elke aanroep komt in `llm_gebruik` op naam van het profiel dat erom vroeg; is het totaal of de
  grens van dat profiel op, dan weigert `loop` vóór de volgende aanroep.
- Weigeringen: server-side `fallbacks: "default"`; blijft het een weigering, dan een nette fout.
- Testen: zet `client_factory` op een nep-client.
"""
from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Bron, LlmGebruik, Profiel, Wettekst
from . import wetboek, zoeken
from .artikelen import Ref, herken
from .correspondentie import Context, wettekst_artikel

log = logging.getLogger(__name__)

# $ per miljoen tokens (in, uit); onbekend model: de duurste, zodat het budget niet te ruim uitvalt.
PRIJZEN = {
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-fable-5-1": (10.0, 50.0),
    "claude-fable-5-2": (8.0, 40.0),
}
ZOEKPRIJS = 0.01  # $ per webzoekactie
FALLBACK_BETA = "server-side-fallback-2026-07-01"
MAX_TEKST = 8000  # tekens wettekst per toolresultaat


class ClaudeFout(RuntimeError):
    pass


def _anthropic(api_key: str):
    import anthropic

    return anthropic.Anthropic(api_key=api_key, max_retries=2, timeout=600)


client_factory: Callable = _anthropic


def voor_wie(db: Session, profiel_id: int | None) -> str:
    """Voor wie Claude werkt, voor in een systeemprompt: naam en wat het profiel over studie en achtergrond zegt."""
    p = db.get(Profiel, profiel_id) if profiel_id else None
    if p is None:
        return "Je werkt voor een rechtenstudent."
    over = (p.achtergrond or "").strip()
    if not over:
        return f"Je werkt voor {p.naam}, een rechtenstudent. Over studie en achtergrond is niets bekend."
    return (f"Je werkt voor {p.naam}. Wat {p.naam} over studie en achtergrond opgeeft:\n<achtergrond>\n{over}\n</achtergrond>\n"
            "Stem uitleg en voorbeelden daarop af, bijvoorbeeld door verschillen met het recht te noemen dat al bekend is.")


def beschikbaar() -> bool:
    return bool(settings.anthropic_api_key)


def kosten(model: str, tokens_in: int, tokens_uit: int, zoekacties: int = 0) -> float:
    p_in, p_uit = PRIJZEN.get(model, (10.0, 50.0))
    return tokens_in / 1e6 * p_in + tokens_uit / 1e6 * p_uit + zoekacties * ZOEKPRIJS


def _maandbegin() -> datetime:
    return datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)


def maand_uitgaven(db: Session, profiel_id: int | None = None) -> float:
    """Uitgegeven deze kalendermaand: alles samen, of (met `profiel_id`) door dat profiel."""
    q = select(func.coalesce(func.sum(LlmGebruik.usd), 0.0)).where(LlmGebruik.aangemaakt >= _maandbegin())
    if profiel_id is not None:
        q = q.where(LlmGebruik.profiel_id == profiel_id)
    return float(db.scalar(q) or 0.0)


def per_profiel(db: Session) -> dict[int | None, float]:
    """Uitgaven deze maand per profiel (None: zonder profiel, zoals de CLI), voor het overzicht van de beheerder."""
    return {pid: float(usd) for pid, usd in db.execute(select(LlmGebruik.profiel_id, func.sum(LlmGebruik.usd))
                                                       .where(LlmGebruik.aangemaakt >= _maandbegin()).group_by(LlmGebruik.profiel_id))}


def grens(p: Profiel | None) -> float | None:
    """De maandgrens van dit profiel in $; None = geen eigen grens (alleen het totaal)."""
    if p is None:
        return None
    if p.llm_grens_usd is not None:
        return p.llm_grens_usd
    return None if p.is_beheerder else settings.llm_profiel_usd


def budget_over(db: Session) -> float:
    return max(0.0, settings.llm_budget_usd - maand_uitgaven(db))


def controleer_budget(db: Session, profiel_id: int | None) -> None:
    """ClaudeFout als het totaal of de grens van het profiel op is."""
    if budget_over(db) <= 0:
        raise ClaudeFout(f"Het maandbudget voor Claude (${settings.llm_budget_usd:.0f}) is op.")
    g = grens(db.get(Profiel, profiel_id)) if profiel_id else None
    if g is not None and maand_uitgaven(db, profiel_id) >= g:
        raise ClaudeFout(f"Je maandgrens voor Claude (${g:.2f}) is op.")


# --- gereedschap ----------------------------------------------------------------------------------------------------

STELSEL_EIGENSCHAP = {"type": "string", "description": "Stelselcode: NL, DE, FR, EU, BE, CH, IT, ES, EN, GR, US, AU. Leeg = alle."}

TOOLS = [
    {
        "name": "artikel_lezen",
        "description": (
            "Leest één artikel uit de lokaal geïmporteerde officiële wetteksten: de volledige tekst, het opschrift en "
            "de plaats in de wet (boek › titel › afdeling). Gebruik de citeerwijze van het stelsel: '§ 823 BGB', "
            "'Art. 2 GG', 'art. 6:162 BW', 'art. 1240 C. civ.', 'Art. 101 AEUV', 'Art. 6 DSGVO', 'art. 41 OR'. "
            "Gebruik dit voor elke wettekst die je citeert; citeer nooit een wettekst uit je geheugen."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"verwijzing": {"type": "string"}, "stelsel": STELSEL_EIGENSCHAP},
            "required": ["verwijzing"],
            "additionalProperties": False,
        },
    },
    {
        "name": "wet_zoeken",
        "description": "Zoekt een wet op titel of afkorting ('Grundgesetz', 'StGB', 'AVG', 'Rome I', '2019/771'); geeft afkorting en titel.",
        "input_schema": {
            "type": "object",
            "properties": {"naam": {"type": "string"}, "stelsel": STELSEL_EIGENSCHAP},
            "required": ["naam"],
            "additionalProperties": False,
        },
    },
    {
        "name": "wetteksten_doorzoeken",
        "description": (
            "Full-text zoeken in alle geïmporteerde wetsartikelen (accent-ongevoelig, woorden als prefix). Geeft per "
            "treffer de citeertitel, het opschrift en een fragment. Zoek in de taal van de wet: 'Übergabe Eigentum' "
            "voor DE, 'délivrance' voor FR, 'levering' voor NL."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "zoektermen": {"type": "string"},
                "stelsel": STELSEL_EIGENSCHAP,
                "wet": {"type": "string", "description": "Afkorting om binnen één wet te zoeken (BGB, GG, StGB, OR …); leeg = alle wetten."},
            },
            "required": ["zoektermen"],
            "additionalProperties": False,
        },
    },
    {
        "name": "eigen_bronnen_doorzoeken",
        "description": "Doorzoekt de bronnen die in Synoptikon zijn vastgelegd: rechtspraak (met kernoverweging), literatuur en wetsbronnen.",
        "input_schema": {
            "type": "object",
            "properties": {"zoektermen": {"type": "string"}},
            "required": ["zoektermen"],
            "additionalProperties": False,
        },
    },
]


def _kort(s: str | None, n: int) -> str:
    s = s or ""
    return s if len(s) <= n else s[:n] + " […]"


def _artikel_lezen(db: Session, verwijzing: str, stelsel: str = "") -> dict:
    ctx = Context(db)
    refs = herken(verwijzing, stelsel.upper() or None)
    if not refs:
        return {"fout": f"'{verwijzing}' herken ik niet als artikelverwijzing. Gebruik de citeerwijze, bijv. '§ 823 BGB'."}
    uit = []
    for r in refs[:3]:
        wa = wettekst_artikel(db, r)
        if wa is None:
            uit.append({"citeer": r.citeer, "gevonden": False})
            continue
        pad = wa.pad or " › ".join(k.label for k in ctx.pad(r))
        uit.append({
            "citeer": r.citeer, "gevonden": True, "stelsel": r.stelsel, "wet": wetboek.toon_titel(wa.wettekst),
            "afkorting": r.wet, "nummer": r.nummer, "opschrift": wa.opschrift, "plaats": pad,
            "versie": wa.wettekst.versie, "tekst": _kort(wa.tekst, MAX_TEKST),
        })
    return {"artikelen": uit}


def _wet_zoeken(db: Session, naam: str, stelsel: str = "") -> dict:
    codes = [stelsel.upper()] if stelsel else [c for c, in db.execute(select(Wettekst.stelsel_code).distinct())]
    uit = []
    for c in codes:
        ws, _n = wetboek.zoek_wetten(db, c, naam, per_pagina=5)
        uit += [{"stelsel": c, "afkorting": w.wet or "(hoofdwet)", "titel": wetboek.toon_titel(w), "versie": w.versie} for w in ws]
    return {"wetten": uit[:15]} if uit else {"wetten": [], "opmerking": "Geen wet met die naam geïmporteerd."}


def _wetteksten_doorzoeken(db: Session, zoektermen: str, stelsel: str = "", wet: str = "") -> dict:
    treffers = zoeken.wetsartikelen(db, zoektermen, stelsel.upper(), limiet=15, wet=wet or None)
    return {"treffers": [{
        "citeer": Ref(wa.wettekst.stelsel_code, wa.nummer, wa.wettekst.wet).citeer, "opschrift": wa.opschrift,
        "fragment": s.replace("<mark>", "").replace("</mark>", ""),
    } for wa, s in treffers]}


def _eigen_bronnen(db: Session, zoektermen: str) -> dict:
    from sqlalchemy import text

    m = zoeken.fts_query(zoektermen)
    if not m:
        return {"bronnen": []}
    ids = [r[0] for r in db.execute(text("SELECT rowid FROM bron_fts WHERE bron_fts MATCH :m ORDER BY rank LIMIT 10"), {"m": m})]
    return {"bronnen": [{
        "stelsel": b.stelsel_code, "soort": b.soort, "citeertitel": b.citeertitel, "titel": b.titel, "vindplaats": b.vindplaats,
        "url": b.url, "tekst": _kort(b.tekst, 2000),
    } for b in (db.get(Bron, i) for i in ids) if b]}


def voer_uit(db: Session, naam: str, invoer: dict) -> dict:
    try:
        if naam == "artikel_lezen":
            return _artikel_lezen(db, str(invoer.get("verwijzing", "")), str(invoer.get("stelsel") or ""))
        if naam == "wet_zoeken":
            return _wet_zoeken(db, str(invoer.get("naam", "")), str(invoer.get("stelsel") or ""))
        if naam == "wetteksten_doorzoeken":
            return _wetteksten_doorzoeken(db, str(invoer.get("zoektermen", "")), str(invoer.get("stelsel") or ""), str(invoer.get("wet") or ""))
        if naam == "eigen_bronnen_doorzoeken":
            return _eigen_bronnen(db, str(invoer.get("zoektermen", "")))
    except Exception as e:  # een kapotte zoekopdracht mag de hele loop niet stoppen
        log.exception("tool %s", naam)
        return {"fout": str(e)}
    return {"fout": f"onbekende tool {naam}"}


# --- de loop --------------------------------------------------------------------------------------------------------


def _noteer(db: Session, doel: str, model: str, usage, profiel_id: int | None = None) -> float:
    zoek = getattr(getattr(usage, "server_tool_use", None), "web_search_requests", 0) or 0
    t_in = (usage.input_tokens or 0) + (getattr(usage, "cache_creation_input_tokens", 0) or 0) + (getattr(usage, "cache_read_input_tokens", 0) or 0)
    usd = kosten(model, t_in, usage.output_tokens or 0, zoek)
    db.add(LlmGebruik(profiel_id=profiel_id, doel=doel, model=model, tokens_in=t_in, tokens_uit=usage.output_tokens or 0, zoekacties=zoek, usd=usd))
    db.commit()
    return usd


def loop(
    db: Session,
    doel: str,
    system: str,
    prompt: str,
    schema: dict,
    effort: str = "medium",
    max_rondes: int = 12,
    max_zoekacties: int = 5,
    max_tokens: int = 32000,
    voortgang: Callable[[str], None] | None = None,
    profiel_id: int | None = None,
) -> tuple[dict, float]:
    """Laat Claude met de tools werken tot het een antwoord volgens `schema` geeft. → (antwoord, kosten in $).
    `profiel_id`: wie erom vroeg; daarop wordt geboekt en diens grens geldt (None: alleen het totaal, zoals de CLI)."""
    if not beschikbaar():
        raise ClaudeFout("Claude staat uit: er is geen SYNOPTIKON_ANTHROPIC_API_KEY ingesteld.")
    client = client_factory(settings.anthropic_api_key)
    model = settings.claude_model
    tools = [*TOOLS, {"type": "web_search_20260209", "name": "web_search", "max_uses": max_zoekacties}] if max_zoekacties else list(TOOLS)
    berichten: list[dict] = [{"role": "user", "content": prompt}]
    totaal = 0.0
    for ronde in range(max_rondes + 1):
        controleer_budget(db, profiel_id)
        laatste = ronde == max_rondes
        params = dict(
            model=model, max_tokens=max_tokens, system=system, messages=berichten,
            tools=tools, tool_choice={"type": "none"} if laatste else {"type": "auto"},
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": schema}},
            betas=[FALLBACK_BETA], fallbacks="default", cache_control={"type": "ephemeral"},
        )
        with client.beta.messages.stream(**params) as stream:
            antwoord = stream.get_final_message()
        totaal += _noteer(db, doel, model, antwoord.usage, profiel_id)
        if antwoord.stop_reason == "refusal":
            raise ClaudeFout("Claude weigerde deze opdracht.")
        if antwoord.stop_reason == "max_tokens":
            raise ClaudeFout("Het antwoord werd te lang en is afgebroken.")
        berichten.append({"role": "assistant", "content": antwoord.content})
        if antwoord.stop_reason == "pause_turn":
            continue
        gebruik = [b for b in antwoord.content if b.type == "tool_use"]
        if not gebruik:
            tekst = "".join(b.text for b in antwoord.content if b.type == "text").strip()
            try:
                return json.loads(tekst), totaal
            except json.JSONDecodeError as e:
                raise ClaudeFout(f"Claude gaf geen geldig antwoord ({e}).") from e
        resultaten = []
        for b in gebruik:
            if voortgang:
                voortgang(_stap(b.name, b.input))
            uit = voer_uit(db, b.name, b.input if isinstance(b.input, dict) else {})
            resultaten.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(uit, ensure_ascii=False)})
        berichten.append({"role": "user", "content": resultaten})
    raise ClaudeFout("Claude kwam niet tot een antwoord.")


def _stap(naam: str, invoer) -> str:
    invoer = invoer if isinstance(invoer, dict) else {}
    if naam == "artikel_lezen":
        return f"leest {invoer.get('verwijzing', '')}"
    if naam == "wet_zoeken":
        return f"zoekt wet {invoer.get('naam', '')}"
    if naam == "wetteksten_doorzoeken":
        return f"doorzoekt wetteksten: {invoer.get('zoektermen', '')}" + (f" ({invoer['stelsel']})" if invoer.get("stelsel") else "")
    return f"doorzoekt eigen bronnen: {invoer.get('zoektermen', '')}"
