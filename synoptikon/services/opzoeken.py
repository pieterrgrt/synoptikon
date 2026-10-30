"""Opzoeken: één invulveld voor alles wat je in een college of tekst tegenkomt.

Typ een artikel ("§ 823 BGB", "Art. 2 GG", "6:162 BW", "Art. 6 DSGVO"), een wet ("Grundgesetz", "StGB", "AVG") of
een uitspraak ("Baris/Riezenkamp", "Costa/ENEL", "BGHZ 63, 369", een ECLI). Eerst zoekt Synoptikon zelf:

1. artikelverwijzingen → de tekst uit de geïmporteerde wet, met de plaats in de wet;
2. wetten op titel of afkorting, in alle stelsels;
3. uitspraken onder de eigen bronnen;
4. EU-handelingen op roepnaam, nummer of titel.

Een ECLI of CELEX-nummer wordt eerst deterministisch opgehaald (`herkennen`: Cellar voor EU, rechtspraak.nl voor NL).
Vindt het geen artikel, of gaat het om rechtspraak die er niet in staat, dan zoekt Claude het op (`met_claude`): waar het
staat, wat er staat, en een korte toelichting. Wettekst komt dan nog steeds uit de lokale import; alleen bij een
uitspraak komt de tekst van het web, gemarkeerd als niet geverifieerd.

Wat je opzoekt komt in het logboek (`Opzoeking`), zodat je na het college terugziet wat langskwam; met één tik gaat
het als kaart naar een leerlijst, en zo naar Wunderkammer.
"""
from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select, text
from sqlalchemy.orm import Session

from ..models import Bron, EuHandeling, Opzoeking, Wettekst, WettekstArtikel
from . import claude, eu, eunamen, herkennen, wetboek
from .artikelen import Ref, herken
from .correspondentie import Context, wettekst_artikel, zoek_artikel
from .zoeken import fts_query

log = logging.getLogger(__name__)


@dataclass
class Gevonden:
    soort: str  # artikel | wet | uitspraak | eu
    titel: str
    url: str | None
    stelsel: str | None = None
    ref: Ref | None = None
    artikel: WettekstArtikel | None = None
    plaats: list[str] = field(default_factory=list)
    wettekst: Wettekst | None = None
    bron: Bron | None = None
    handeling: EuHandeling | None = None


def _plaats(ctx: Context, r: Ref, wa: WettekstArtikel | None) -> list[str]:
    if wa is not None and wa.pad:
        return [re.sub(r"\s+", " ", p).strip() for p in wa.pad.split("›") if p.strip()]
    return [k.label for k in ctx.pad(r)]


def _binnen(stelsel: str | None, stelsels: list[str] | None) -> bool:
    """Valt een treffer binnen de gekozen stelsels (None of leeg = alle)?"""
    return not stelsels or stelsel in stelsels


def artikelen(db: Session, q: str, stelsel: str = "", stelsels: list[str] | None = None) -> list[Gevonden]:
    ctx = Context(db)
    uit = []
    gevonden = zoek_artikel(db, q, stelsel or None, stelsels=stelsels)
    for r, wa in [(r, wa) for r, wa in gevonden if _binnen(r.stelsel, stelsels)][:6]:
        uit.append(Gevonden("artikel", r.citeer, wetboek.lees_url(db, r, wa), r.stelsel, r, wa, _plaats(ctx, r, wa),
                            wa.wettekst if wa else None))
    return uit


def _woorden(s: str) -> set[str]:
    return set(re.findall(r"\w+", s.casefold()))


def wetten(db: Session, q: str, stelsel: str = "", n: int = 6, stelsels: list[str] | None = None) -> list[Gevonden]:
    """Wetten waarvan de afkorting de invoer is, of waarvan de titel alle woorden bevat (in alle stelsels in één query)."""
    q = q.strip()
    if len(q) < 2 or len(q) > 120:
        return []
    codes = [stelsel] if stelsel else list(stelsels or [])
    gezocht = _woorden(q)
    kandidaten: list[tuple[tuple, Wettekst]] = []
    ws, _n = wetboek.zoek_wetten(db, "", q, per_pagina=40, stelsels=codes, tel=False)
    for w in ws:
        afk = (wetboek.toon_afkorting(w) or w.wet or "").casefold()
        titel = wetboek.toon_titel(w)
        exact = afk == q.casefold() or (w.wet or "").casefold() == q.casefold()
        if not exact and not gezocht <= _woorden(titel) | _woorden(afk) and not titel.casefold().startswith(q.casefold()):
            continue
        kandidaten.append(((not exact, not w.kern, len(titel)), w))
    # EU-wetten onder elke naam en in elke taal: DSGVO, RGPD, GDPR, AVG, Rom I-VO, Richtlinie 93/13 …
    if not codes or "EU" in codes:
        sleutel, rest = eunamen.herken_wet(q)
        if sleutel and not rest.strip():
            ws = wetboek._kies_taal(list(db.scalars(select(Wettekst).where(Wettekst.stelsel_code == "EU", Wettekst.wet == sleutel)).all()))
            gezien = {w.id for _s, w in kandidaten}
            kandidaten += [((False, False, 0), w) for w in ws if w.id not in gezien]
    kandidaten.sort(key=lambda p: p[0])
    if any(not s[0] for s, _w in kandidaten):  # een precieze afkorting: alleen die
        kandidaten = [(s, w) for s, w in kandidaten if not s[0]]
    return [Gevonden("wet", wetboek.toon_titel(w), f"/stelsels/{w.stelsel_code}/wet/{w.id}", w.stelsel_code, wettekst=w)
            for _s, w in kandidaten[:n]]


def uitspraken(db: Session, q: str, n: int = 6, stelsels: list[str] | None = None) -> list[Gevonden]:
    """Rechtspraak onder de eigen bronnen: op ECLI of vindplaats, anders full-text."""
    stmt = select(Bron).where(Bron.soort == "rechtspraak")
    if stelsels:
        stmt = stmt.where(Bron.stelsel_code.in_(stelsels))
    exact = db.scalars(stmt.where(or_(Bron.vindplaats.ilike(q.strip()), Bron.citeertitel.ilike(f"%{q.strip()}%"))).limit(n)).all()
    ids = {b.id for b in exact}
    gevonden = list(exact)
    m = fts_query(q)
    if m and len(gevonden) < n:
        for (rowid,) in db.execute(text("SELECT rowid FROM bron_fts WHERE bron_fts MATCH :m ORDER BY rank LIMIT 20"), {"m": m}):
            b = db.get(Bron, rowid)
            if b and b.soort == "rechtspraak" and b.id not in ids and _binnen(b.stelsel_code, stelsels):
                gevonden.append(b)
                ids.add(b.id)
            if len(gevonden) >= n:
                break
    return [Gevonden("uitspraak", b.citeertitel, f"/bronnen/{b.id}", b.stelsel_code, bron=b) for b in gevonden]


def eu_handelingen(db: Session, q: str, n: int = 4) -> list[Gevonden]:
    try:
        hs, _t = eu.zoek(db, q, per_pagina=n, tel=False)
    except Exception:  # FTS-syntax bij vreemde invoer
        return []
    teksten = dict(db.execute(select(Wettekst.wet_id, Wettekst.id).where(Wettekst.wet_id.in_([h.celex for h in hs]))).all())
    return [Gevonden("eu", h.roepnaam or h.citeer, f"/stelsels/EU/wet/{teksten[h.celex]}" if h.celex in teksten else f"/eu/{h.celex}",
                     "EU", handeling=h) for h in hs]


@dataclass
class Uitkomst:
    q: str
    artikelen: list[Gevonden]
    wetten: list[Gevonden]
    uitspraken: list[Gevonden]
    eu: list[Gevonden]

    @property
    def raak(self) -> bool:
        """Is er iets gevonden dat precies past (een artikel met tekst, een wet op afkorting)?"""
        return any(g.artikel for g in self.artikelen) or bool(self.wetten) or bool(self.uitspraken)


def lokaal(db: Session, q: str, stelsel: str = "", stelsels: list[str] | None = None) -> Uitkomst:
    """Alles wat precies past. `stelsels` beperkt tot die stelsels (None of leeg = alle; `stelsel` gaat voor)."""
    if stelsel:
        stelsels = [stelsel]
    arts = artikelen(db, q, stelsel, stelsels)
    met_tekst = any(g.artikel for g in arts)
    u = Uitkomst(
        q,
        arts,
        [] if met_tekst else wetten(db, q, stelsel, stelsels=stelsels),
        [] if met_tekst else uitspraken(db, q, stelsels=stelsels),
        [],
    )
    if not met_tekst and not u.wetten and _binnen("EU", stelsels):
        u.eu = eu_handelingen(db, q)
    return u


# --- logboek -------------------------------------------------------------------------------------------------------


def vandaag(db: Session, profiel_id: int, dagen: int = 1) -> list[Opzoeking]:
    sinds = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=dagen)
    return list(db.scalars(select(Opzoeking).where(Opzoeking.profiel_id == profiel_id, Opzoeking.aangemaakt >= sinds)
                           .order_by(Opzoeking.aangemaakt.desc()).limit(60)).all())


def samenvatting(g: Gevonden) -> dict:
    """Wat van een lokale treffer in het logboek komt (en waaruit later een kaart wordt gemaakt)."""
    d = dict(soort=g.soort, titel=g.titel, url=g.url, stelsel=g.stelsel, bron="lokaal")
    if g.ref:
        d.update(citeer=g.ref.citeer, wet=g.ref.wet, nummer=g.ref.nummer, plaats=" › ".join(g.plaats),
                 opschrift=g.artikel.opschrift if g.artikel else None)
    if g.bron:
        d.update(bron_id=g.bron.id, vindplaats=g.bron.vindplaats)
    return d


def log_lokaal(db: Session, profiel_id: int, q: str, u: Uitkomst) -> Opzoeking | None:
    """Het eerste wat precies past komt in het logboek; dezelfde invoer op dezelfde dag één keer."""
    eerste = next((g for g in [*u.artikelen, *u.uitspraken, *u.wetten] if g.artikel or g.soort != "artikel"), None)
    if eerste is None:
        return None
    bestaand = next((o for o in vandaag(db, profiel_id) if o.invoer.casefold() == q.strip().casefold()), None)
    if bestaand:
        return bestaand
    o = Opzoeking(profiel_id=profiel_id, invoer=q.strip()[:400], resultaat=samenvatting(eerste))
    db.add(o)
    db.flush()
    return o


# --- Claude ---------------------------------------------------------------------------------------------------------

SYSTEEM = """Je bent de juridische opzoekhulp in Synoptikon, de rechtsvergelijkingsapp van een jurist (Nederlands \
recht, Europees recht, nu rechtenstudie in Duitsland). Hij typt tijdens een college iets in wat hij hoort: een \
wetsartikel, een wet, een uitspraak of een verdrag, vaak afgekort of half. Zoek uit wat het precies is, waar het \
staat en wat er staat.

- Wetteksten: lees ze met `artikel_lezen` (de lokale officiële teksten). Citeer een wettekst nooit uit je geheugen. \
Vind je een wet niet, probeer `wet_zoeken` en `wetteksten_doorzoeken`.
- Uitspraken: kijk eerst met `eigen_bronnen_doorzoeken`; anders zoek op het web, bij voorkeur op officiële bronnen \
(curia.europa.eu, eur-lex.europa.eu, rechtspraak.nl, bundesgerichtshof.de, bundesverfassungsgericht.de, \
legifrance.gouv.fr, hudoc.echr.coe.int). Geef ECLI of de gebruikelijke vindplaats (NJ, BGHZ, NJW, Slg., Bull. civ.).
- `tekst`: bij een artikel de tekst precies zoals `artikel_lezen` hem gaf (zonder iets weg te laten); bij een \
uitspraak alleen de kernoverweging als je die letterlijk uit een bron hebt, anders leeg. Nooit verzinnen.
- `toelichting`: twee tot vier zinnen in het Nederlands: waar gaat het over, waarom doet het ertoe, met welke \
regeling of leer het samenhangt. Wat niet uit een bron komt, markeer je met (niet geverifieerd).
- `artikelverwijzing`: bij een artikel de citeerwijze zoals `artikel_lezen` die accepteert, anders leeg.
- Ben je onzeker wat bedoeld is, kies dan de meest waarschijnlijke lezing, zet `zekerheid` op laag en noem \
alternatieven in de toelichting."""

SCHEMA = {
    "type": "object",
    "properties": {
        "soort": {"type": "string", "enum": ["artikel", "wet", "uitspraak", "verdrag", "literatuur", "onbekend"]},
        "stelsel": {"type": "string", "description": "NL, DE, FR, EU, EVRM, BE, CH, IT, ES, EN, US, INT …"},
        "citeer": {"type": "string", "description": "Volledige citeerwijze, bijv. '§ 823 Abs. 1 BGB' of 'HR 15 november 1957, NJ 1958/67 (Baris/Riezenkamp)'"},
        "titel": {"type": "string", "description": "Opschrift van het artikel, titel van de wet, of de zaaknaam"},
        "vindplaats": {"type": "string", "description": "ECLI, CELEX, NJ/BGHZ/NJW-vindplaats; leeg als niet van toepassing"},
        "url": {"type": "string", "description": "Officiële bron; leeg als onbekend"},
        "plaats": {"type": "string", "description": "Waar het staat: wet › boek › titel › afdeling, of gerecht, datum en zaaknummer"},
        "tekst": {"type": "string"},
        "tekst_herkomst": {"type": "string", "enum": ["lokaal", "web", "geen"]},
        "toelichting": {"type": "string"},
        "artikelverwijzing": {"type": "string"},
        "zekerheid": {"type": "string", "enum": ["hoog", "middel", "laag"]},
    },
    "required": ["soort", "stelsel", "citeer", "titel", "vindplaats", "url", "plaats", "tekst", "tekst_herkomst",
                 "toelichting", "artikelverwijzing", "zekerheid"],
    "additionalProperties": False,
}


def _verrijk(db: Session, r: dict) -> dict:
    """Een artikel dat Claude noemt, koppelen aan de lokale tekst (die gaat altijd voor)."""
    verwijzing = r.get("artikelverwijzing") or (r.get("citeer") if r.get("soort") == "artikel" else "")
    refs = herken(verwijzing, None) if verwijzing else []
    for ref in refs:
        wa = wettekst_artikel(db, ref)
        if wa is None:
            continue
        ctx = Context(db)
        r.update(stelsel=ref.stelsel, wet=ref.wet, nummer=ref.nummer, citeer=ref.citeer, opschrift=wa.opschrift,
                 tekst=wa.tekst, tekst_herkomst="lokaal", url=wetboek.lees_url(db, ref, wa),
                 plaats=" › ".join(_plaats(ctx, ref, wa)) or r.get("plaats"))
        break
    return r


def met_claude(db: Session, profiel_id: int, q: str, achtergrond: bool = True) -> Opzoeking:
    """Maakt een Opzoeking en laat haar invullen (standaard in een eigen thread; de pagina vraagt de stand op).

    Een ECLI of CELEX gaat eerst naar de bron zelf (`herkennen`); Claude komt pas als die niets geeft."""
    o = Opzoeking(profiel_id=profiel_id, invoer=q.strip()[:400], status="bezig")
    db.add(o)
    db.commit()
    if achtergrond:
        threading.Thread(target=_vul, args=(o.id,), daemon=True).start()
    else:
        _vul(o.id, db)
    return o


def _vul(oid: int, db: Session | None = None) -> None:
    from ..db import session_factory

    eigen = db is None
    db = db or session_factory()()
    try:
        o = db.get(Opzoeking, oid)
        if (i := herkennen.herken_id(o.invoer)) and (feiten := herkennen.zoek(i)):
            o.resultaat, o.status = feiten, "klaar"
            db.commit()
            return
        try:
            r, _usd = claude.loop(db, "opzoeken", SYSTEEM, f"Opzoeken: {o.invoer}", SCHEMA, effort="low", max_rondes=6,
                                  max_zoekacties=3, max_tokens=16000)
            r = _verrijk(db, r)
            r["bron"] = "claude"
            o.resultaat, o.status = r, "klaar"
        except claude.ClaudeFout as e:
            o.status, o.fout = "fout", str(e)
        except Exception as e:  # netwerk, API
            log.exception("opzoeken")
            o.status, o.fout = "fout", f"{type(e).__name__}: {e}"
        db.commit()
    finally:
        if eigen:
            db.close()


OPMERKING = {"claude": "Opgezocht door Claude (niet geverifieerd). ", "cellar": "Opgehaald bij EUR-Lex (Cellar). ",
             "rechtspraak": "Opgehaald bij rechtspraak.nl. ", "eigen": "Zelf nagekeken. "}


def regel_terugval(r: dict) -> str:
    """Wat op de achterkant van een arrestkaart komt als je geen rechtsregel opgaf. Van EUR-Lex (Cellar) is de
    toelichting een reeks trefwoorden uit de titel ('Prejudiciële verwijzing – … – Geen'): dat is geen regel, dus niets."""
    return "" if r.get("bron") == "cellar" else (r.get("toelichting") or "")


def bron_uit(db: Session, o: Opzoeking) -> Bron | None:
    """Een uitspraak uit een opzoeking als Bron (rechtspraak), zodat er een arrestkaart van kan komen."""
    r = o.resultaat or {}
    if r.get("bron_id"):
        return db.get(Bron, r["bron_id"])
    if o.bron_id:
        return db.get(Bron, o.bron_id)
    if r.get("soort") != "uitspraak":
        return None
    stelsel = (r.get("stelsel") or "").upper()
    from ..models import Stelsel

    if db.get(Stelsel, stelsel) is None:
        stelsel = "EU" if stelsel in ("HVJ", "CJEU", "EUGH") else "NL"
    vindplaats = (r.get("vindplaats") or "").strip() or None
    if vindplaats and (b := db.scalar(select(Bron).where(Bron.vindplaats == vindplaats))):
        # een eerdere, ongeverifieerde gok van Claude ('Niet vastgesteld') wordt bijgewerkt met wat nu wél vaststaat
        if r.get("bron") in ("cellar", "rechtspraak", "eigen") and (b.opmerking or "").startswith(OPMERKING["claude"]):
            b.citeertitel = (r.get("citeer") or b.citeertitel)[:200]
            b.titel = (r.get("titel") or None) and r["titel"][:300]
            b.url = r.get("url") or b.url
            b.stelsel_code = stelsel
            b.opmerking = OPMERKING[r["bron"]] + (r.get("toelichting") or "")
        o.bron_id = b.id
        return b
    b = Bron(stelsel_code=stelsel, soort="rechtspraak", citeertitel=(r.get("citeer") or o.invoer)[:200],
             titel=(r.get("titel") or None) and r["titel"][:300], tekst=r.get("tekst") or None,
             taal={"DE": "de", "FR": "fr", "EU": "nl", "NL": "nl"}.get(stelsel, "nl"),
             vindplaats_type=_vindplaats_type(vindplaats),
             vindplaats=vindplaats and vindplaats[:200], url=(r.get("url") or None),
             opmerking=OPMERKING.get(r.get("bron"), OPMERKING["claude"]) + (r.get("toelichting") or ""))
    db.add(b)
    db.flush()
    o.bron_id = b.id
    return b


def _vindplaats_type(vindplaats: str | None) -> str | None:
    i = herkennen.herken_id(vindplaats or "")
    return i.soort.upper() if i else None


# Wat in het formulier 'kloppend maken' te corrigeren is; de rest van de opzoeking blijft zoals ze was.
VELDEN = ("citeer", "titel", "vindplaats", "url", "plaats", "toelichting")


def corrigeer(db: Session, o: Opzoeking, velden: dict[str, str], stelsel: str | None = None) -> Opzoeking:
    """Zelf verbeteren: de opzoeking wordt `bron: "eigen"`, zodat 'niet geverifieerd' verdwijnt.

    Hoort er al een Bron bij (de uitspraak is eerder bewaard), dan wordt die bijgewerkt; anders komt ze er pas bij het
    bewaren (`bron_uit`), met de gecorrigeerde gegevens."""
    r = dict(o.resultaat or {})
    for k in VELDEN:
        if k in velden:
            r[k] = (velden[k] or "").strip()
    if stelsel:
        r["stelsel"] = stelsel.strip().upper()
    r.update(bron="eigen", zekerheid="hoog")
    o.resultaat, o.status, o.fout = r, "klaar", None
    if o.bron_id and (b := db.get(Bron, o.bron_id)):
        b.citeertitel = (r.get("citeer") or b.citeertitel)[:200]
        b.titel = (r.get("titel") or None) and r["titel"][:300]
        b.vindplaats = (r.get("vindplaats") or None) and r["vindplaats"][:200]
        b.vindplaats_type = _vindplaats_type(b.vindplaats)
        b.url = r.get("url") or None
        b.opmerking = OPMERKING["eigen"] + (r.get("toelichting") or "")
    db.flush()
    return o
