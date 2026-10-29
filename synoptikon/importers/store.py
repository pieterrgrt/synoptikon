"""Opslag van geïmporteerde wetteksten: ruw bestand op schijf, artikelen in de database.

Het ruwe bestand is alleen een bewijsstuk (wat de bron leverde); de app leest uitsluitend uit de database. Daarom mag
het verhuizen: `ruim_ruw_op` houdt per wet de laatste `SYNOPTIKON_RUW_HOUDEN` versies in data/wetteksten en zet oudere
in het archief (`SYNOPTIKON_ARCHIEF_DIR`, zelfde relatieve pad), of gooit ze weg als het archief de lokale map is.
"""
from __future__ import annotations

import hashlib
import re
import shutil
from collections.abc import Iterable
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Wettekst, WettekstArtikel, now
from . import Artikel, Geparseerd


def _veilig(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.\-]+", "_", s)[:80]


def _rijen(artikelen: Iterable[Artikel]) -> list[tuple[str, str | None, str, str | None]]:
    """(nummer, opschrift, tekst, pad) zoals ze in de database komen: ingekort, eerste van een dubbel nummer."""
    gezien: set[str] = set()
    uit = []
    for a in artikelen:
        nummer = a.nummer[:40]
        if nummer in gezien:
            continue
        gezien.add(nummer)
        uit.append((nummer, (a.opschrift or None) and a.opschrift[:300], a.tekst, (a.pad or None) and a.pad[:400]))
    return uit


def _hash(rijen: Iterable[tuple]) -> str:
    h = hashlib.sha256()
    for r in rijen:
        h.update("\x1f".join(x or "" for x in r).encode("utf-8", "surrogatepass"))
        h.update(b"\x1e")
    return h.hexdigest()


def inhoud_hash(artikelen: Iterable[Artikel]) -> str:
    """Vingerafdruk van de tekst: verandert alleen als een nummer, opschrift, pad of tekst verandert."""
    return _hash(_rijen(artikelen))


def db_hash(db: Session, wettekst_id: int) -> tuple[str, int, int]:
    """(hash, aantal, grootte) van een opgeslagen wettekst, rij voor rij uit de database (voor oude rijen zonder hash)."""
    rijen = db.execute(select(WettekstArtikel.nummer, WettekstArtikel.opschrift, WettekstArtikel.tekst, WettekstArtikel.pad)
                       .where(WettekstArtikel.wettekst_id == wettekst_id).order_by(WettekstArtikel.volgorde)).all()
    return _hash(rijen), len(rijen), sum(len(r[2] or "") for r in rijen)


def _schrijf_ruw(stelsel_code: str, g: Geparseerd) -> str:
    map_ = settings.wetteksten_dir / stelsel_code / _veilig(g.wet_id) / _veilig(g.versie)
    map_.mkdir(parents=True, exist_ok=True)
    pad = map_ / f"ruw.{g.ruw_extensie}"
    pad.write_bytes(g.ruw)
    return str(pad.relative_to(settings.wetteksten_dir))


def sla_op(db: Session, stelsel_code: str, g: Geparseerd, wet: str | None = None, taal: str | None = None, kern: bool = True,
           vervang: bool = False) -> Wettekst:
    """`wet`: citeerafkorting waaronder de artikelen gevonden worden (None = hoofdcodificatie).

    `kern=False` voor een bulkimport (alle wetten van een bron): geen ruw bestand op schijf, niet in het overzicht en de
    systematiek. `vervang`: oudere versies van dezelfde wet weg (bulk houdt één versie per wet bij)."""
    bestand = _schrijf_ruw(stelsel_code, g) if g.ruw and kern else None

    q = select(Wettekst).where(Wettekst.stelsel_code == stelsel_code, Wettekst.wet_id == g.wet_id)
    for bestaand in db.scalars(q if vervang else q.where(Wettekst.versie == g.versie)).all():
        db.delete(bestaand)
    db.flush()
    rijen = _rijen(g.artikelen)
    w = Wettekst(stelsel_code=stelsel_code, wet_id=g.wet_id, wet=wet or None, titel=g.titel[:300], versie=g.versie, bron_url=g.bron_url,
                 bestand=bestand, taal=taal, kern=kern, stijl=g.stijl, hash=_hash(rijen), gecontroleerd=now(), aantal=len(rijen),
                 grootte=sum(len(r[2]) for r in rijen))
    for i, (nummer, opschrift, tekst, pad) in enumerate(rijen):
        w.artikelen.append(WettekstArtikel(nummer=nummer, opschrift=opschrift, tekst=tekst, pad=pad, volgorde=i))
    db.add(w)
    db.flush()
    if bestand and settings.ruw_houden:
        ruim_ruw_op(stelsel_code, g.wet_id)
    return w


def werk_bij(db: Session, w: Wettekst, g: Geparseerd, wet: str | None = None) -> Wettekst:
    """Een bestaande wettekst in place naar de nieuwe stand brengen: alleen gewijzigde artikelen worden geschreven.

    Zo houden ongewijzigde artikelen hun id (koppelingen vanuit bronnen blijven staan) en raakt de zoekindex alleen
    wat echt veranderde. Voor de bulk (één versie per wet) en voor een nieuwe stand onder hetzelfde versielabel."""
    rijen = _rijen(g.artikelen)
    oud = {a.nummer: a for a in db.scalars(select(WettekstArtikel).where(WettekstArtikel.wettekst_id == w.id))}
    nieuw = {r[0] for r in rijen}
    for nummer, a in oud.items():
        if nummer not in nieuw:
            db.delete(a)
    db.flush()
    for i, (nummer, opschrift, tekst, pad) in enumerate(rijen):
        a = oud.get(nummer)
        if a is None:
            db.add(WettekstArtikel(wettekst_id=w.id, nummer=nummer, opschrift=opschrift, tekst=tekst, pad=pad, volgorde=i))
        elif (a.opschrift, a.tekst, a.pad, a.volgorde) != (opschrift, tekst, pad, i):
            a.opschrift, a.tekst, a.pad, a.volgorde = opschrift, tekst, pad, i
    if g.ruw and w.kern:
        w.bestand = _schrijf_ruw(w.stelsel_code, g)
    w.versie, w.titel, w.bron_url = g.versie, g.titel[:300], g.bron_url
    if wet is not None:
        w.wet = wet or None
    w.stijl = g.stijl
    w.hash, w.aantal, w.grootte = _hash(rijen), len(rijen), sum(len(r[2]) for r in rijen)
    w.opgehaald = w.gecontroleerd = now()
    db.flush()
    return w


def ruim_ruw_op(stelsel_code: str, wet_id: str, houden: int | None = None) -> int:
    """Oudere versiemappen van één wet uit data/wetteksten: naar het archief, of weg. Geeft het aantal verplaatste mappen."""
    houden = settings.ruw_houden if houden is None else houden
    if houden <= 0:
        return 0
    map_ = settings.wetteksten_dir / stelsel_code / _veilig(wet_id)
    if not map_.is_dir():
        return 0
    versies = sorted((p for p in map_.iterdir() if p.is_dir()), key=lambda p: p.stat().st_mtime, reverse=True)
    archief = settings.archief_dir
    apart = archief.resolve() != settings.wetteksten_dir.resolve()
    n = 0
    for oud in versies[houden:]:
        if apart:
            doel = archief / oud.relative_to(settings.wetteksten_dir)
            doel.parent.mkdir(parents=True, exist_ok=True)
            if doel.exists():
                shutil.rmtree(doel)
            shutil.move(str(oud), str(doel))
        else:
            shutil.rmtree(oud)
        n += 1
    return n


def ruw_grootte(stelsel_code: str) -> int:
    """Bytes aan ruwe bestanden van een stelsel, lokaal plus archief."""
    totaal = 0
    for basis in {settings.wetteksten_dir.resolve(), settings.archief_dir.resolve()}:
        p = Path(basis) / stelsel_code
        if p.is_dir():
            totaal += sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
    return totaal
