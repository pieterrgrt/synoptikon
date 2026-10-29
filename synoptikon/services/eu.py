"""EU-catalogus bijwerken en bevragen; omzettingstabel laden; Unierecht bij een nationaal artikel.

`werk_catalogus_bij` haalt alles opnieuw uit Cellar en werkt de tabellen bij
op CELEX-nummer. Handelingen die niet meer gelden worden verwijderd, tenzij
er een eigen omzettingskoppeling aan hangt: die blijven staan, met hun
einddatum, zodat de koppeling niet verloren gaat. Roepnamen (seed) worden
alleen gezet als er nog geen staat.
"""
from __future__ import annotations

import re
from collections import Counter
from datetime import date

from sqlalchemy import delete, func, insert, select, text, update
from sqlalchemy.orm import Session, selectinload

from ..importers import cellar
from ..i18n import BRONTAAL, taal
from ..models import EuHandeling, EuNim, EuRepertorium, EuRepertoriumLabel, EuTitel, Omzetting, now
from .artikelen import Ref, ref_bevat


def werk_catalogus_bij(db: Session, nims: bool = True) -> dict[str, int]:
    from ..seed.omzetting import ROEPNAMEN

    with cellar.verbinding() as c:
        handelingen = cellar.handelingen(c)
        rep = cellar.repertorium(c)
        rubrieken = cellar.rubrieken(c)
        maatregelen = cellar.nims(c) if nims else []

    db.execute(delete(EuRepertorium))
    db.execute(insert(EuRepertorium), [{"code": code, "label": label, "ouder_code": ouder, "niveau": code.count(".") + 1} for code, label, ouder in rep])

    bestaand = {h.celex: h.roepnaam for h in db.execute(select(EuHandeling.celex, EuHandeling.roepnaam)).all()}
    met_koppeling = set(db.scalars(select(Omzetting.celex).distinct()).all())
    geldig = {h.celex for h in handelingen}
    nieuw, bij = [], []
    for h in handelingen:
        rij = {
            "celex": h.celex, "soort": h.soort, "variant": h.variant, "nummer": h.nummer, "titel": h.titel,
            "datum": h.datum, "in_werking": h.in_werking, "toepassing": h.toepassing, "geldig_tot": h.geldig_tot,
            "omzettingstermijn": h.omzettingstermijn, "eer": h.eer, "eli": h.eli,
            "repertorium": ",".join(rubrieken.get(h.celex, [])) or None, "bijgewerkt": now(),
        }
        if h.celex in bestaand:
            if not bestaand[h.celex] and h.celex in ROEPNAMEN:
                rij["roepnaam"] = ROEPNAMEN[h.celex]
            bij.append(rij)
        else:
            rij["roepnaam"] = ROEPNAMEN.get(h.celex)
            nieuw.append(rij)
    if nieuw:
        db.execute(insert(EuHandeling), nieuw)
    for rij in bij:
        db.execute(update(EuHandeling).where(EuHandeling.celex == rij["celex"]).values(**rij))
    weg = [c for c in bestaand if c not in geldig and c not in met_koppeling]
    for i in range(0, len(weg), 500):
        db.execute(delete(EuHandeling).where(EuHandeling.celex.in_(weg[i:i + 500])))

    if nims:
        db.execute(delete(EuNim))
        rijen = [{"celex": n.celex, "land": n.land, "nim_id": n.nim_id, "titel": n.titel, "soort_akte": n.soort_akte, "datum": n.datum, "vindplaats": n.vindplaats}
                 for n in maatregelen if n.celex in geldig]
        gezien: set[tuple[str, str]] = set()
        uniek = []
        for r in rijen:
            if (r["celex"], r["nim_id"]) not in gezien:
                gezien.add((r["celex"], r["nim_id"]))
                uniek.append(r)
        for i in range(0, len(uniek), 2000):
            db.execute(insert(EuNim), uniek[i:i + 2000])
    db.flush()
    db.execute(text("INSERT INTO eu_handeling_fts(eu_handeling_fts) VALUES('rebuild')"))
    return {"handelingen": len(handelingen), "nieuw": len(nieuw), "vervallen": len(weg), "rubrieken": len(rep),
            "nims": db.scalar(select(func.count()).select_from(EuNim)) or 0}


def werk_talen_bij(db: Session, talen: list[str] | None = None) -> dict[str, int]:
    """Officiële titels en rubrieknamen in fr, de, it, en en es uit Cellar (het Nederlands staat in de hoofdtabellen)."""
    talen = talen or list(cellar.TALEN_CELLAR)
    geldig = set(db.scalars(select(EuHandeling.celex)).all())
    uit: dict[str, int] = {}
    with cellar.verbinding() as c:
        labels = cellar.repertorium_labels(c)
        db.execute(delete(EuRepertoriumLabel))
        db.execute(insert(EuRepertoriumLabel), [{"code": code, "taal": t, "label": label} for code, t, label in labels if t in talen])
        for t in talen:
            titels = cellar.titels(c, t)
            db.execute(delete(EuTitel).where(EuTitel.taal == t))
            rijen = [{"celex": celex, "taal": t, "titel": titel} for celex, titel in titels.items() if celex in geldig]
            for i in range(0, len(rijen), 2000):
                db.execute(insert(EuTitel), rijen[i:i + 2000])
            db.commit()
            uit[t] = len(rijen)
    _LABELS.clear()
    uit["rubrieken"] = len(labels)
    return uit


def met_titels(db: Session, handelingen: list[EuHandeling]) -> list[EuHandeling]:
    """Zet op elke handeling de officiële titel in de taal van het verzoek (voor `toon_titel` en `citeer`)."""
    t = taal()
    if t == BRONTAAL or not handelingen:
        return handelingen
    titels = dict(db.execute(select(EuTitel.celex, EuTitel.titel).where(EuTitel.taal == t, EuTitel.celex.in_([h.celex for h in handelingen]))).all())
    for h in handelingen:
        if h.celex in titels:
            h._titel_vertaald = titels[h.celex]
    return handelingen


_LABELS: dict[tuple[str, str], str] = {}


def rubrieklabel(code: str, t: str) -> str | None:
    if t == BRONTAAL:
        return None
    if not _LABELS:
        from ..db import session_factory

        with session_factory()() as s:
            _LABELS.update({(r.code, r.taal): r.label for r in s.scalars(select(EuRepertoriumLabel))})
            _LABELS.setdefault(("", ""), "")  # niet opnieuw laden als de tabel leeg is
    return _LABELS.get((code, t))


def laad_omzettingen(db: Session) -> int:
    """Zet de omzettingstabel uit de seed in de database; eigen (nieuwere) regels blijven staan.

    Een seedregel is dezelfde als (celex, stelsel, wet, nummer, eu_artikel, wet_titel) overeenkomen.
    Ontbreekt de handeling nog (catalogus niet geladen), dan komt er een voorlopige rij met
    alleen de roepnaam; `synoptikon eu-catalogus` vult die aan.
    """
    from ..seed.omzetting import OMZETTINGEN, ROEPNAMEN

    bekend = {(o.celex, o.stelsel_code, o.wet, o.nummer, o.eu_artikel, o.wet_titel) for o in db.scalars(select(Omzetting)).all()}
    handelingen = set(db.scalars(select(EuHandeling.celex)).all())
    n = 0
    for i, o in enumerate(OMZETTINGEN):
        if o.celex not in handelingen:
            m = re.fullmatch(r"3(\d{4})([RL])(\d{4})", o.celex)
            soort = "verordening" if m and m.group(2) == "R" else "richtlijn"
            db.add(EuHandeling(celex=o.celex, soort=soort, nummer=f"{m.group(1)}/{int(m.group(3))}" if m else None,
                               titel=ROEPNAMEN.get(o.celex, o.celex), roepnaam=ROEPNAMEN.get(o.celex)))
            db.flush()
            handelingen.add(o.celex)
        sleutel_ = (o.celex, o.stelsel, o.wet, o.van, o.eu_artikel, o.wet_titel)
        if sleutel_ in bekend:
            continue
        db.add(Omzetting(celex=o.celex, eu_artikel=o.eu_artikel, stelsel_code=o.stelsel, wet=o.wet, wet_titel=o.wet_titel, nummer=o.van, tot=o.tot,
                         soort=o.soort, opmerking=o.opmerking, geverifieerd=False, volgorde=(i + 1) * 10))
        bekend.add(sleutel_)
        n += 1
    db.flush()
    return n


# --- bevragen --------------------------------------------------------------------------


def zoek(db: Session, q: str = "", soort: str = "", variant: str = "", rubriek: str = "", omgezet: bool = False,
         pagina: int = 1, per_pagina: int = 50, tel: bool = True) -> tuple[list[EuHandeling], int]:
    """Handelingen op CELEX, nummer of woorden in titel en roepnaam; `tel=False` slaat het (dure) totaal over (dan 0)."""
    from .zoeken import fts_query

    stmt = select(EuHandeling)
    if q.strip():
        celex = re.sub(r"\s+", "", q.strip()).upper()
        if re.fullmatch(r"3\d{4}[A-Z]\d{4}", celex):
            stmt = stmt.where(EuHandeling.celex == celex)
        elif re.fullmatch(r"\d{2,4}/\d{1,4}", q.strip()):
            stmt = stmt.where(EuHandeling.nummer == q.strip())
        else:
            m = fts_query(q)
            # Nederlandse titel en roepnaam, of de titel in de taal van het verzoek.
            stmt = stmt.where(text(
                "eu_handeling.rowid IN (SELECT rowid FROM eu_handeling_fts WHERE eu_handeling_fts MATCH :m) "
                "OR eu_handeling.celex IN (SELECT t.celex FROM eu_titel t JOIN eu_titel_fts f ON f.rowid = t.rowid "
                "WHERE eu_titel_fts MATCH :m AND t.taal = :taal)").bindparams(m=m, taal=taal()))
    if soort:
        stmt = stmt.where(EuHandeling.soort == soort)
    if variant:
        stmt = stmt.where(EuHandeling.variant == variant)
    if rubriek:
        stmt = stmt.where((EuHandeling.repertorium == rubriek) | EuHandeling.repertorium.like(f"{rubriek}%") | EuHandeling.repertorium.like(f"%,{rubriek}%"))
    if omgezet:
        stmt = stmt.where(EuHandeling.celex.in_(select(Omzetting.celex)))
    totaal = (db.scalar(select(func.count()).select_from(stmt.subquery())) or 0) if tel else 0
    # Basishandelingen met roepnaam eerst, dan nieuwste eerst.
    stmt = stmt.order_by(EuHandeling.roepnaam.is_(None), EuHandeling.variant != "basis", EuHandeling.datum.desc().nulls_last())
    return met_titels(db, list(db.scalars(stmt.offset((pagina - 1) * per_pagina).limit(per_pagina)).all())), totaal


_TELLINGEN: dict[tuple, Counter] = {}


def repertorium_boom(db: Session) -> tuple[list[EuRepertorium], dict[str, list[EuRepertorium]], Counter]:
    """Hoofdstukken, kinderen per code en aantal geldende handelingen per code (inclusief onderliggende rubrieken).

    De tellingen lopen over alle handelingen; ze worden per proces bewaard tot de catalogus verandert.
    """
    alle = list(db.scalars(select(EuRepertorium).order_by(EuRepertorium.code)).all())
    kinderen: dict[str, list[EuRepertorium]] = {}
    for r in alle:
        kinderen.setdefault(r.ouder_code or "", []).append(r)
    stand = tuple(db.execute(select(func.count(), func.max(EuHandeling.bijgewerkt)).select_from(EuHandeling)).one())
    if stand not in _TELLINGEN:
        tellingen: Counter = Counter()
        for (rep,) in db.execute(select(EuHandeling.repertorium).where(EuHandeling.repertorium.is_not(None))).all():
            voorvoegsels = set()
            for code in rep.split(","):
                delen = code.split(".")
                voorvoegsels.update(".".join(delen[:i]) for i in range(1, len(delen) + 1))
            tellingen.update(voorvoegsels)
        _TELLINGEN.clear()
        _TELLINGEN[stand] = tellingen
    return kinderen.get("", []), kinderen, _TELLINGEN[stand]


def rubriek_pad(db: Session, code: str) -> list[EuRepertorium]:
    delen = code.split(".")
    codes = [".".join(delen[:i]) for i in range(1, len(delen) + 1)]
    per_code = {r.code: r for r in db.scalars(select(EuRepertorium).where(EuRepertorium.code.in_(codes))).all()}
    return [per_code[c] for c in codes if c in per_code]


def handeling(db: Session, celex: str) -> EuHandeling | None:
    h = db.scalar(select(EuHandeling).where(EuHandeling.celex == celex).options(selectinload(EuHandeling.nims), selectinload(EuHandeling.omzettingen)))
    return met_titels(db, [h])[0] if h else None


def nims_per_stelsel(h: EuHandeling) -> dict[str, list[EuNim]]:
    uit: dict[str, list[EuNim]] = {}
    for n in h.nims:
        code = cellar.LANDEN.get(n.land)
        if code:
            uit.setdefault(code, []).append(n)
    for lijst in uit.values():
        lijst.sort(key=lambda n: (n.datum or date.min), reverse=True)
    return uit


def omzettingen_voor_artikel(db: Session, ref: Ref) -> list[Omzetting]:
    """Koppelingen die dit nationale artikel (ook via een bereik) dekken."""
    if ref.nummer is None:
        return []
    kandidaten = db.scalars(
        select(Omzetting).where(Omzetting.stelsel_code == ref.stelsel, Omzetting.nummer.is_not(None)).options(selectinload(Omzetting.handeling))
    ).all()
    uit = [o for o in kandidaten if ref_bevat(o.ref, ref.stelsel, ref.nummer, ref.wet)]
    met_titels(db, [o.handeling for o in uit])
    return uit


def omzettingsmatrix(db: Session) -> tuple[list[EuHandeling], dict[str, dict[str, list[Omzetting]]]]:
    """Handelingen met een koppeling, en per handeling per stelsel de koppelingen."""
    rijen = db.scalars(select(Omzetting).options(selectinload(Omzetting.handeling)).order_by(Omzetting.volgorde)).all()
    per: dict[str, dict[str, list[Omzetting]]] = {}
    handelingen: dict[str, EuHandeling] = {}
    for o in rijen:
        per.setdefault(o.celex, {}).setdefault(o.stelsel_code, []).append(o)
        handelingen[o.celex] = o.handeling
    volgorde = sorted(handelingen.values(), key=lambda h: (h.soort != "richtlijn", h.datum or date.min))
    return met_titels(db, volgorde), per
