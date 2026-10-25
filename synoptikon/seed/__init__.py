"""Voorbeeldinhoud: stelsels, systematiek, twee uitgewerkte vragen, begrippen, concordanties.

De wetteksten zijn de geldende officiële teksten zoals gepubliceerd op
wetten.overheid.nl, gesetze-im-internet.de, legifrance.gouv.fr en EUR-Lex;
versiedatum en link staan bij elke bron. Rechtspraak is beperkt tot de
kernoverweging; dat staat in `opmerking`. Vertalingen zijn eigen werk-
vertalingen (herkomst "eigen") en als zodanig gemarkeerd.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import (
    Antwoord,
    AntwoordBron,
    Begrip,
    BegripRelatie,
    Bron,
    Concordantie,
    Correspondentie,
    CorrespondentieArtikel,
    Stelsel,
    Systematiek,
    Vertaling,
    Vraag,
    VraagBegrip,
)
from . import data_eigendom, data_precontractueel
from .correspondenties import CORRESPONDENTIES
from .stelsels import CONCORDANTIES, STELSELS, SYSTEMATIEK
from .systematiek_fr import HERNOEMD


def _stelsels(db: Session) -> None:
    for i, (code, naam, taal, toelichting, actief) in enumerate(STELSELS):
        if db.get(Stelsel, code) is None:
            db.add(Stelsel(code=code, naam=naam, taal=taal, volgorde=(i + 1) * 10, actief=actief, toelichting=toelichting))
    db.flush()


def _systematiek(db: Session) -> dict[str, Systematiek]:
    """Legt de systematiekbomen aan of werkt ze bij.

    Knopen worden op code herkend; label, bereik, ouder en volgorde volgen de
    seed, zodat een bestaande database bij een nieuwe `synoptikon seed` de
    volledige boom krijgt. Zelf toegevoegde knopen (andere codes) blijven
    staan, net als de bronnen die aan een knoop hangen.
    """
    index: dict[str, Systematiek] = {k.code: k for k in db.scalars(select(Systematiek)).all()}
    for oud, nieuw in HERNOEMD.items():
        if oud in index and nieuw not in index:
            index[nieuw] = index.pop(oud)
            index[nieuw].code = nieuw

    def voeg_toe(code: str, knopen: list, parent: Systematiek | None):
        for i, (kcode, label, bereik, kinderen) in enumerate(knopen):
            knoop = index.get(kcode)
            if knoop is None:
                knoop = Systematiek(stelsel_code=code, code=kcode)
                db.add(knoop)
                index[kcode] = knoop
            knoop.parent, knoop.label, knoop.bereik, knoop.volgorde = parent, label, bereik or None, (i + 1) * 10
            voeg_toe(code, kinderen, knoop)

    for code, knopen in SYSTEMATIEK.items():
        voeg_toe(code, knopen, None)
    db.flush()
    return index


def _concordanties(db: Session) -> None:
    bestaand = {(c.stelsel_code, c.wet, c.oud) for c in db.scalars(select(Concordantie)).all()}
    for code, wet, oud, nieuw, datum, grond, toelichting in CONCORDANTIES:
        if (code, wet, oud) in bestaand:
            continue
        db.add(Concordantie(stelsel_code=code, wet=wet, oud=oud, nieuw=nieuw, datum=date.fromisoformat(datum) if datum else None, grond=grond, toelichting=toelichting))
    db.flush()


def _correspondenties(db: Session) -> None:
    """Thema's met corresponderende artikelen; aanvullend, nooit overschrijvend.

    Bestaande thema's (zelfde titel) krijgen alleen artikelen erbij die er nog
    niet in staan, zodat eigen aanpassingen blijven staan.
    """
    from ..services.artikelen import lees

    bestaand = {c.titel: c for c in db.scalars(select(Correspondentie)).all()}
    for spec in CORRESPONDENTIES:
        c = bestaand.get(spec["titel"])
        if c is None:
            c = Correspondentie(titel=spec["titel"], rechtsgebied=spec.get("rechtsgebied"), toelichting=spec.get("toelichting"))
            db.add(c)
        aanwezig = {(a.stelsel_code, a.wet, a.nummer, a.tot) for a in c.artikelen}
        for i, lid in enumerate(spec["artikelen"]):
            stelsel, verwijzing, rol, opmerking = (*lid, None, None)[:4]
            ref = lees(stelsel, verwijzing)
            if ref is None:
                raise ValueError(f"Onleesbare verwijzing in correspondentie {spec['titel']!r}: {stelsel} {verwijzing}")
            if (ref.stelsel, ref.wet, ref.nummer, ref.tot) in aanwezig:
                continue
            c.artikelen.append(
                CorrespondentieArtikel(
                    stelsel_code=stelsel, wet=ref.wet, nummer=ref.nummer, tot=ref.tot, detail=ref.detail, rol=rol, opmerking=opmerking, volgorde=(i + 1) * 10
                )
            )
    db.flush()


def _bron(db: Session, systematiek: dict[str, Systematiek], spec: dict) -> Bron:
    bestaand = db.scalar(select(Bron).where(Bron.stelsel_code == spec["stelsel"], Bron.citeertitel == spec["citeertitel"]))
    if bestaand:
        return bestaand
    b = Bron(
        stelsel_code=spec["stelsel"],
        soort=spec["soort"],
        citeertitel=spec["citeertitel"],
        titel=spec.get("titel"),
        tekst=spec.get("tekst"),
        taal=spec["taal"],
        vindplaats_type=spec.get("vindplaats_type"),
        vindplaats=spec.get("vindplaats"),
        url=spec.get("url"),
        geldig_van=date.fromisoformat(spec["geldig_van"]) if spec.get("geldig_van") else None,
        geldig_tot=date.fromisoformat(spec["geldig_tot"]) if spec.get("geldig_tot") else None,
        opmerking=spec.get("opmerking"),
        systematiek=systematiek.get(spec["systematiek"]) if spec.get("systematiek") else None,
    )
    for taal, tekst in (spec.get("vertalingen") or {}).items():
        b.vertalingen.append(Vertaling(taal=taal, tekst=tekst, herkomst="eigen"))
    db.add(b)
    db.flush()
    return b


def _begrip(db: Session, spec: dict) -> Begrip:
    bestaand = db.scalar(select(Begrip).where(Begrip.stelsel_code == spec["stelsel"], Begrip.term == spec["term"]))
    if bestaand:
        return bestaand
    g = Begrip(stelsel_code=spec["stelsel"], term=spec["term"], taal=spec["taal"], definitie=spec.get("definitie"), vindplaats=spec.get("vindplaats"))
    db.add(g)
    db.flush()
    return g


def _vraag(db: Session, systematiek: dict[str, Systematiek], spec: dict, overschrijf: bool) -> Vraag | None:
    bestaand = db.scalar(select(Vraag).where(Vraag.slug == spec["slug"]))
    if bestaand:
        if not overschrijf:
            return None
        db.delete(bestaand)
        db.flush()
    v = Vraag(slug=spec["slug"], titel=spec["titel"], omschrijving=spec.get("omschrijving"), rechtsgebied=spec.get("rechtsgebied"), tags=spec.get("tags"))
    db.add(v)
    for code, a_spec in spec["antwoorden"].items():
        a = Antwoord(stelsel_code=code, kern=a_spec.get("kern"), analyse=a_spec.get("analyse"))
        v.antwoorden.append(a)
        for i, b_spec in enumerate(a_spec.get("bronnen", [])):
            b = _bron(db, systematiek, b_spec)
            a.bronnen.append(AntwoordBron(bron=b, volgorde=i * 10, rol=b_spec.get("rol"), notitie=b_spec.get("notitie")))
    begrippen: dict[str, Begrip] = {}
    for g_spec in spec.get("begrippen", []):
        g = _begrip(db, g_spec)
        begrippen[g_spec["sleutel"]] = g
        if not any(vb.begrip_id == g.id for vb in v.begrippen):
            v.begrippen.append(VraagBegrip(begrip=g))
    for van, naar, typ, toelichting in spec.get("relaties", []):
        a_, b_ = begrippen[van], begrippen[naar]
        bestaande = db.scalar(
            select(BegripRelatie).where(
                ((BegripRelatie.van_id == a_.id) & (BegripRelatie.naar_id == b_.id)) | ((BegripRelatie.van_id == b_.id) & (BegripRelatie.naar_id == a_.id))
            )
        )
        if bestaande is None:
            db.add(BegripRelatie(van=a_, naar=b_, type=typ, toelichting=toelichting))
    db.flush()
    return v


def seed(db: Session, overschrijf: bool = False) -> int:
    _stelsels(db)
    systematiek = _systematiek(db)
    _concordanties(db)
    _correspondenties(db)
    n = 0
    for spec in (data_eigendom.VRAAG, data_precontractueel.VRAAG):
        if _vraag(db, systematiek, spec, overschrijf) is not None:
            n += 1
    return n
