"""Geschiedenis van gedeelde inhoud: wie wijzigde wat, wanneer, en wat stond er eerst.

Vragen, analyses, notities, begrippen, bronnen, thema's en omzettingen zijn van iedereen; zonder dit overschreef een
tweede redacteur een analyse onzichtbaar. Een `after_flush`-luisteraar op elke Session schrijft per gevolgde rij een
`Wijziging`, maar alleen als er een auteur is gezet (`zet_auteur`): de middleware doet dat per verzoek, het onderzoek
door Claude in zijn eigen draad. Imports en seed vanaf de opdrachtregel komen er dus niet in.

Bij een eerste wijziging van iets wat al bestond voor deze geschiedenis bewaart `oud` de vorige waarden: zo is ook
die oorspronkelijke toestand terug te zetten.
"""
from __future__ import annotations

import difflib
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy import Date, DateTime, event, inspect, select
from sqlalchemy.orm import Session

from ..models import (
    Antwoord,
    AntwoordBron,
    Begrip,
    Bron,
    Correspondentie,
    Notitie,
    Omzetting,
    Profiel,
    Vraag,
    Wijziging,
)

# soort → (model, velden die de inhoud vormen: die worden vergeleken, getoond en teruggezet)
SOORTEN: dict[str, tuple[type, tuple[str, ...]]] = {
    "vraag": (Vraag, ("titel", "omschrijving", "rechtsgebied", "tags")),
    "antwoord": (Antwoord, ("kern", "analyse")),
    "antwoord_bron": (AntwoordBron, ("rol", "notitie", "volgorde")),
    "notitie": (Notitie, ("stelsel_code", "tekst")),
    "begrip": (Begrip, ("term", "taal", "definitie", "vindplaats")),
    "bron": (Bron, ("soort", "citeertitel", "titel", "tekst", "taal", "vindplaats_type", "vindplaats", "url",
                    "geldig_van", "geldig_tot", "opmerking")),
    "thema": (Correspondentie, ("titel", "rechtsgebied", "toelichting")),
    "omzetting": (Omzetting, ("eu_artikel", "stelsel_code", "wet", "wet_titel", "nummer", "tot", "soort", "opmerking",
                              "geverifieerd")),
}
_SOORT_VAN = {model: soort for soort, (model, _v) in SOORTEN.items()}


@dataclass(frozen=True)
class Auteur:
    profiel_id: int | None
    naam: str | None
    door: str | None = None  # "claude"


_auteur: ContextVar[Auteur | None] = ContextVar("wijziging_auteur", default=None)


def zet_auteur(profiel: Profiel | None, door: str | None = None):
    return _auteur.set(Auteur(getattr(profiel, "id", None), getattr(profiel, "naam", None), door))


def zet_auteur_id(db: Session, profiel_id: int | None, door: str | None = None):
    """Geeft het token voor `herstel_auteur`."""
    return zet_auteur(db.get(Profiel, profiel_id) if profiel_id else None, door)


def herstel_auteur(token) -> None:
    _auteur.reset(token)


def huidige_auteur() -> Auteur | None:
    return _auteur.get()


def _json(v):
    return v.isoformat() if isinstance(v, (date, datetime)) else v


def _alles(obj) -> dict:
    return {a.key: _json(getattr(obj, a.key)) for a in inspect(obj).mapper.column_attrs}


@event.listens_for(Session, "after_flush")
def _na_flush(session: Session, _ctx) -> None:
    auteur = _auteur.get()
    if auteur is None:
        return
    rijen = []
    for actie, objecten in (("nieuw", session.new), ("gewijzigd", session.dirty), ("verwijderd", session.deleted)):
        for obj in objecten:
            soort = _SOORT_VAN.get(type(obj))
            if soort is None:
                continue
            velden = SOORTEN[soort][1]
            oud = nieuw = None
            if actie == "nieuw":
                nieuw = _alles(obj)
                if not any(nieuw.get(v) not in (None, "") for v in velden):
                    continue  # lege rij (bijv. een leeg antwoord per stelsel): niets om bij te houden
            elif actie == "gewijzigd":
                staat = inspect(obj)
                oud = {}
                for v in velden:
                    h = staat.attrs[v].history
                    if h.has_changes() and h.deleted:
                        oud[v] = _json(h.deleted[0])
                if not oud or all(_json(getattr(obj, v)) == w for v, w in oud.items()):
                    continue
                nieuw = _alles(obj)
            else:
                oud = _alles(obj)
            rijen.append(dict(soort=soort, rij_id=obj.id, actie=actie, profiel_id=auteur.profiel_id,
                              naam=auteur.naam, door=auteur.door, oud=oud, nieuw=nieuw))
    if rijen:
        session.connection().execute(Wijziging.__table__.insert(), rijen)


# --- lezen en terugzetten --------------------------------------------------------------------------------------------


def _teruggezet(nieuw: Wijziging, weg: Wijziging) -> bool:
    """Is `nieuw` het terugzetten van de verwijderde rij `weg` (en niet een andere rij met hetzelfde id)?"""
    a, b = nieuw.nieuw or {}, weg.oud or {}
    return all(a.get(k) == v for k, v in b.items() if k != "gewijzigd")


def _snijd(ws: list[Wijziging], bestaat: bool) -> list[Wijziging]:
    """SQLite geeft het id van een verwijderde rij opnieuw uit. Nieuwste eerst; alles van vóór een verwijdering hoort bij
    een eerdere rij, tenzij die rij daarna is teruggezet."""
    uit: list[Wijziging] = []
    for w in ws:
        if w.actie == "verwijderd" and (uit or bestaat):
            if not (uit and uit[-1].actie == "nieuw" and _teruggezet(uit[-1], w)):
                break
        uit.append(w)
    return uit


def _per_rij(db: Session, soort: str, ids: list[int]) -> dict[int, list[Wijziging]]:
    uit: dict[int, list[Wijziging]] = {}
    if ids:
        for w in db.scalars(select(Wijziging).where(Wijziging.soort == soort, Wijziging.rij_id.in_(ids))
                            .order_by(Wijziging.id.desc())):
            uit.setdefault(w.rij_id, []).append(w)
    return uit


def geschiedenis(db: Session, soort: str, rij_id: int, bestaat: bool = True) -> list[Wijziging]:
    """Nieuwste eerst."""
    return _snijd(_per_rij(db, soort, [rij_id]).get(rij_id, []), bestaat)


def laatste(db: Session, soort: str, ids: list[int]) -> dict[int, Wijziging]:
    """Per bestaande rij de laatste wijziging."""
    return {i: g[0] for i, ws in _per_rij(db, soort, ids).items() if (g := _snijd(ws, True))}


def eerste(db: Session, soort: str, ids: list[int]) -> dict[int, Wijziging]:
    """Per bestaande rij de eerste wijziging (bij een notitie: wie haar schreef)."""
    return {i: g[-1] for i, ws in _per_rij(db, soort, ids).items() if (g := _snijd(ws, True))}


def stand(w: Wijziging, ervoor: bool = False) -> dict | None:
    """De volledige toestand na deze wijziging, of (ervoor) de toestand ervoor."""
    if ervoor:
        if w.actie == "nieuw":
            return None
        if w.actie == "verwijderd":
            return dict(w.oud or {})
        return {**(w.nieuw or {}), **(w.oud or {})}
    return None if w.actie == "verwijderd" else dict(w.nieuw or {})


@dataclass
class Verschil:
    veld: str
    oud: str
    nieuw: str
    regels: list[tuple[str, str]] | None  # bij lange tekst: (teken, regel) met teken in " -+@"


def verschillen(w: Wijziging) -> list[Verschil]:
    velden = SOORTEN[w.soort][1]
    voor, na = stand(w, ervoor=True) or {}, stand(w) or {}
    uit = []
    for v in velden:
        a, b = voor.get(v), na.get(v)
        if a == b or (w.actie == "nieuw" and b in (None, "")) or (w.actie == "verwijderd" and a in (None, "")):
            continue
        a, b = "" if a is None else str(a), "" if b is None else str(b)
        regels = None
        if a and b and ("\n" in a or "\n" in b or len(a) + len(b) > 300):
            regels = [(r[0], r[1:]) for r in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=1)][2:]
        uit.append(Verschil(v, a, b, regels))
    return uit


class TerugzettenMislukt(Exception):
    pass


def terugzetten(db: Session, w: Wijziging, ervoor: bool = False) -> None:
    """Zet de inhoudsvelden van de rij terug op de stand van `w` (of ervoor). Bestaat de rij niet meer, dan komt ze terug
    met haar oude id. Het terugzetten zelf komt als gewone wijziging in de geschiedenis."""
    model, velden = SOORTEN[w.soort]
    doel = stand(w, ervoor)
    if doel is None:
        raise TerugzettenMislukt("geen stand")
    obj = db.get(model, w.rij_id)
    kolommen = {c.key: c for c in inspect(model).mapper.column_attrs}

    def waarde(k):
        v = doel.get(k)
        soort = kolommen[k].columns[0].type
        if isinstance(v, str) and isinstance(soort, DateTime):
            return datetime.fromisoformat(v)
        if isinstance(v, str) and isinstance(soort, Date):
            return date.fromisoformat(v)
        return v

    if obj is None:
        obj = model(**{k: waarde(k) for k in kolommen if k in doel})
        db.add(obj)
    else:
        for v in velden:
            if v in doel:
                setattr(obj, v, waarde(v))
    try:
        db.flush()
    except Exception as e:  # bijv. de vraag bij deze notitie is zelf verwijderd
        db.rollback()
        raise TerugzettenMislukt(str(e)) from e


def label_en_link(db: Session, ws: list[Wijziging]) -> dict[int, tuple[str, str | None]]:
    """Per wijziging een leesbare naam van wat gewijzigd is en een link ernaartoe (als het nog bestaat)."""
    vraag_ids = set()
    ab_ids = set()
    for w in ws:
        d = w.nieuw or w.oud or {}
        if w.soort in ("antwoord", "notitie"):
            vraag_ids.add(d.get("vraag_id"))
        elif w.soort == "antwoord_bron":
            ab_ids.add(d.get("antwoord_id"))
    antw = {a.id: a for a in db.scalars(select(Antwoord).where(Antwoord.id.in_(ab_ids)))} if ab_ids else {}
    vraag_ids |= {a.vraag_id for a in antw.values()}
    vragen = {v.id: v for v in db.scalars(select(Vraag).where(Vraag.id.in_(vraag_ids)))} if vraag_ids else {}
    bron_ids = {(w.nieuw or w.oud or {}).get("bron_id") for w in ws if w.soort == "antwoord_bron"}
    bronnen = {b.id: b for b in db.scalars(select(Bron).where(Bron.id.in_(bron_ids)))} if bron_ids else {}
    uit = {}
    for w in ws:
        d = w.nieuw or w.oud or {}
        label, link = "", None
        if w.soort == "vraag":
            label, link = d.get("titel") or "", f"/vragen/{d.get('slug')}"
        elif w.soort in ("antwoord", "notitie"):
            v = vragen.get(d.get("vraag_id"))
            code = d.get("stelsel_code") or ""
            label = f"{v.titel if v else '?'}{' · ' + code if code else ''}"
            if w.soort == "notitie":
                label += f" · {(d.get('tekst') or '')[:60]}"
            link = f"/vragen/{v.slug}#{code or 'notities'}" if v else None
        elif w.soort == "antwoord_bron":
            a = antw.get(d.get("antwoord_id"))
            v = vragen.get(a.vraag_id) if a else None
            b = bronnen.get(d.get("bron_id"))
            label = f"{v.titel if v else '?'} · {a.stelsel_code if a else ''} · {b.citeertitel if b else '?'}"
            link = f"/vragen/{v.slug}#{a.stelsel_code}" if v and a else None
        elif w.soort == "begrip":
            label, link = f"{d.get('stelsel_code')} · {d.get('term')}", f"/begrippen/{w.rij_id}"
        elif w.soort == "bron":
            label, link = d.get("citeertitel") or "", f"/bronnen/{w.rij_id}"
        elif w.soort == "thema":
            label, link = d.get("titel") or "", f"/artikelen/thema/{w.rij_id}"
        elif w.soort == "omzetting":
            label = f"{d.get('celex')} {d.get('eu_artikel') or ''} → {d.get('stelsel_code')} {d.get('wet') or ''} {d.get('nummer') or ''}"
            link = f"/eu/{d.get('celex')}"
        uit[w.id] = (" ".join(label.split()), link)
    return uit
