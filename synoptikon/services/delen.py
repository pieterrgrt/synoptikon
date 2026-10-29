"""Leerlijsten delen onder studenten: zichtbaarheid, likes, reacties en overnemen.

Een lijst is privé (standaard), te zien voor wie de link `/gedeeld/<deelcode>` heeft, of voor iedereen op /gedeeld.
Een gedeelde lijst toont alleen de kaarten die echt in de lijst staan (geen voorstellen of uitgezette kaarten).
Overnemen kopieert de lijst met haar kaarten naar je eigen leerlijsten; staat de koppeling met Wunderkammer aan, dan
herhaal je ze daar. Wijzigingen van de eigenaar komen niet vanzelf in de kopie.
"""
from __future__ import annotations

import secrets

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..models import ZICHTBAAR, Kaart, Leerlijst, LijstLike, LijstReactie, Profiel, now
from . import leren

MAX_REACTIE = 2000
_VELDEN = ("soort", "stelsel_code", "wet", "nummer", "doel_stelsel", "bron_id", "zaak", "vindplaats", "feiten", "vraag",
           "antwoord", "notitie")


def kaarten(lijst: Leerlijst) -> list[Kaart]:
    """Wat anderen van de lijst zien."""
    return [k for k in lijst.kaarten if k.actief and k.status is None]


def zet_zichtbaar(lijst: Leerlijst, zichtbaar: str) -> None:
    if zichtbaar not in ZICHTBAAR:
        raise ValueError(zichtbaar)
    lijst.zichtbaar = zichtbaar
    if zichtbaar != "prive":
        lijst.deelcode = lijst.deelcode or secrets.token_urlsafe(9)
        lijst.gedeeld_op = lijst.gedeeld_op or now()


def mag_zien(lijst: Leerlijst, profiel_id: int) -> bool:
    return lijst.profiel_id == profiel_id or lijst.zichtbaar in ("link", "iedereen")


def mag_reactie_wissen(r: LijstReactie, lijst: Leerlijst, p: Profiel) -> bool:
    return r.profiel_id == p.id or lijst.profiel_id == p.id or p.is_beheerder


def openbaar(db: Session, volgorde: str = "populair") -> list[tuple[Leerlijst, int, int]]:
    """Lijsten op /gedeeld met (lijst, likes, reacties), populairste of nieuwste eerst."""
    likes = select(LijstLike.lijst_id, func.count().label("n")).group_by(LijstLike.lijst_id).subquery()
    reacties = select(LijstReactie.lijst_id, func.count().label("n")).group_by(LijstReactie.lijst_id).subquery()
    q = (select(Leerlijst, func.coalesce(likes.c.n, 0), func.coalesce(reacties.c.n, 0))
         .outerjoin(likes, likes.c.lijst_id == Leerlijst.id).outerjoin(reacties, reacties.c.lijst_id == Leerlijst.id)
         .where(Leerlijst.zichtbaar == "iedereen")
         .options(selectinload(Leerlijst.kaarten), selectinload(Leerlijst.profiel)))
    q = q.order_by(Leerlijst.gedeeld_op.desc()) if volgorde == "nieuw" else q.order_by(func.coalesce(likes.c.n, 0).desc(), Leerlijst.gedeeld_op.desc())
    return [(l, n_l, n_r) for l, n_l, n_r in db.execute(q).all()]


def like(db: Session, lijst: Leerlijst, profiel_id: int) -> bool:
    """Aan of uit; → of het nu geliket is."""
    bestaand = db.get(LijstLike, (lijst.id, profiel_id))
    if bestaand is not None:
        db.delete(bestaand)
        return False
    db.add(LijstLike(lijst_id=lijst.id, profiel_id=profiel_id))
    return True


def reageer(db: Session, lijst: Leerlijst, profiel_id: int, tekst: str) -> LijstReactie | None:
    tekst = tekst.strip()[:MAX_REACTIE]
    if not tekst:
        return None
    r = LijstReactie(lijst_id=lijst.id, profiel_id=profiel_id, tekst=tekst)
    db.add(r)
    return r


def overnemen(db: Session, bron: Leerlijst, profiel_id: int) -> Leerlijst:
    """Kopie van de lijst en haar kaarten in de eigen leerlijsten (privé, naar Wunderkammer als de koppeling aan staat)."""
    kopie = Leerlijst(profiel_id=profiel_id, naam=bron.naam[:120], vak=bron.vak, examen=bron.examen,
                      omschrijving=bron.omschrijving, naar_wk=True, overgenomen_van=bron.id)
    db.add(kopie)
    db.flush()
    for k in kaarten(bron):
        db.add(Kaart(uid=leren.nieuwe_uid(), lijst=kopie, **{v: getattr(k, v) for v in _VELDEN}))
    db.flush()
    return kopie
