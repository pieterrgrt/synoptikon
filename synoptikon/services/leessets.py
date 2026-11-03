"""Leessets: artikelen, uitspraken en eigen notities die je samen leest voor één onderwerp.

Een leesset is persoonlijk (per profiel) en geordend: de volgorde en de reden per onderdeel ('waarom staat dit erbij')
zijn de kern. Dat is iets anders dan een thema uit de correspondentietabel (`services/correspondentie.py`): dat is een
vergelijkingsas tussen stelsels, gedeeld door iedereen. Een thema op /bewaard kan wel het begin van een leesset zijn.

Een leesset wordt met één tik kaarten in de leerlijst van zijn vak (`naar_kaarten`): een artikelkaart per artikel (per
lid, zoals bij ☆ Bewaren), een arrestkaart per uitspraak. Eigen notities worden geen kaart; die zijn om te lezen.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..i18n import _
from ..models import Bron, Leerlijst, Leesset, LeessetOnderdeel
from . import leren, vakken
from .artikelen import Ref, herken
from .correspondentie import wettekst_artikel


def van(db: Session, profiel_id: int) -> list[Leesset]:
    return list(db.scalars(select(Leesset).where(Leesset.profiel_id == profiel_id)
                           .options(selectinload(Leesset.onderdelen)).order_by(Leesset.vak, Leesset.naam)).all())


def maak(db: Session, profiel_id: int, naam: str, vak: str | None = None, omschrijving: str | None = None) -> Leesset:
    s = Leesset(profiel_id=profiel_id, naam=(naam or "").strip()[:120] or _("Nieuwe leesset"),
                vak=(vak or "").strip()[:60] or None, omschrijving=(omschrijving or "").strip() or None)
    db.add(s)
    db.flush()
    return s


def _volgende_positie(db: Session, s: Leesset) -> int:
    hoogste = db.scalar(select(func.max(LeessetOnderdeel.positie)).where(LeessetOnderdeel.leesset_id == s.id))
    return (hoogste if hoogste is not None else -1) + 1


def _zelfde(o: LeessetOnderdeel, ref: Ref | None, bron_id: int | None) -> bool:
    if ref is not None:
        return (o.stelsel_code, o.wet, o.nummer) == (ref.stelsel, ref.wet, ref.nummer)
    return bron_id is not None and o.bron_id == bron_id


def voeg_toe(db: Session, s: Leesset, ref: Ref | None = None, bron: Bron | None = None, notitie: str | None = None,
             reden: str | None = None) -> LeessetOnderdeel | None:
    """Achteraan erbij. Een artikel of uitspraak die er al in staat komt er niet nog eens bij (None); een nieuwe reden
    vult dan wel een lege reden aan."""
    notitie = (notitie or "").strip() or None
    reden = (reden or "").strip() or None
    if ref is None and bron is None and notitie is None:
        return None
    if ref is not None and not ref.nummer:
        return None
    bron_id = bron.id if bron is not None else None
    if ref is not None or bron_id is not None:
        for o in s.onderdelen:
            if _zelfde(o, ref, bron_id):
                if reden and not o.reden:
                    o.reden = reden
                return None
    o = LeessetOnderdeel(leesset_id=s.id, positie=_volgende_positie(db, s), notitie=notitie if ref is None and bron is None else None,
                         reden=reden, bron=bron)
    if ref is not None:
        o.stelsel_code, o.wet, o.nummer = ref.stelsel, ref.wet, ref.nummer
    db.add(o)
    db.flush()
    db.refresh(s, ["onderdelen"])
    return o


def lees_invoer(invoer: str, stelsel: str | None = None) -> Ref | None:
    """'§ 929 BGB', 'art. 3:84 BW', '1240 C. civ.' → het eerste artikel dat de herkenner erin ziet."""
    refs = [r for r in herken(invoer or "", stelsel or None) if r.nummer]
    return refs[0] if refs else None


def verplaats(s: Leesset, onderdeel_id: int, stap: int) -> bool:
    """Eén plek omhoog (stap -1) of omlaag (+1). Nummert daarna opnieuw, zodat de posities aaneengesloten blijven."""
    rij = sorted(s.onderdelen, key=lambda o: (o.positie, o.id))
    i = next((i for i, o in enumerate(rij) if o.id == onderdeel_id), None)
    j = None if i is None else i + stap
    if i is None or j < 0 or j >= len(rij):
        return False
    rij[i], rij[j] = rij[j], rij[i]
    for n, o in enumerate(rij):
        o.positie = n
    return True


def verwijder(db: Session, s: Leesset, onderdeel_id: int) -> bool:
    o = next((o for o in s.onderdelen if o.id == onderdeel_id), None)
    if o is None:
        return False
    s.onderdelen.remove(o)
    db.delete(o)
    for n, x in enumerate(sorted(s.onderdelen, key=lambda o: (o.positie, o.id))):
        x.positie = n
    return True


@dataclass
class Gelezen:
    """Een onderdeel zoals het op de leespagina staat: titel, link en de tekst zelf."""

    onderdeel: LeessetOnderdeel
    titel: str
    url: str | None = None
    opschrift: str | None = None
    tekst: str | None = None
    stelsel: str | None = None


def lezen(db: Session, s: Leesset) -> list[Gelezen]:
    uit = []
    for o in sorted(s.onderdelen, key=lambda o: (o.positie, o.id)):
        if o.nummer:
            ref = Ref(o.stelsel_code, o.nummer, o.wet)
            wa = wettekst_artikel(db, ref)
            uit.append(Gelezen(o, ref.citeer, ref.url, wa.opschrift if wa else None, wa.tekst if wa else None, o.stelsel_code))
        elif o.bron is not None:
            b = o.bron
            uit.append(Gelezen(o, b.citeertitel, f"/bronnen/{b.id}", b.vindplaats if b.vindplaats != b.citeertitel else None,
                               b.tekst, b.stelsel_code))
        else:
            uit.append(Gelezen(o, _("Notitie"), tekst=o.notitie))
    return uit


def naar_kaarten(db: Session, s: Leesset) -> tuple[Leerlijst, int]:
    """Alle artikelen en uitspraken als kaarten in de leerlijst van het vak (of een eigen lijst als de set geen vak heeft).
    Wat er al in staat komt er niet nog eens bij (maak_kaarten). Geeft de lijst en het aantal nieuwe kaarten."""
    if s.vak:
        lijst = vakken.lijst_voor(db, s.profiel_id, s.vak)
        vakken.onthoud(db, s.profiel_id, s.vak)
    else:
        lijst = db.scalar(select(Leerlijst).where(Leerlijst.profiel_id == s.profiel_id, Leerlijst.naam == s.naam,
                                                  Leerlijst.vak.is_(None)).order_by(Leerlijst.id))
        if lijst is None:
            lijst = Leerlijst(profiel_id=s.profiel_id, naam=s.naam, omschrijving=s.omschrijving, naar_wk=True)
            db.add(lijst)
            db.flush()
    nieuw = 0
    for o in sorted(s.onderdelen, key=lambda o: (o.positie, o.id)):
        if o.nummer:
            nieuw += len(leren.maak_kaarten(db, lijst, ["artikel"], ref=Ref(o.stelsel_code, o.nummer, o.wet), per_lid=True))
        elif o.bron is not None:
            nieuw += len(leren.maak_kaarten(db, lijst, ["arrest"], bron=o.bron))
    return lijst, nieuw
