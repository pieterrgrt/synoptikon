"""`synoptikon bijwerken`: alle wetteksten actueel houden, beleefd en in kleine porties.

Loopt de bronnen af en vergelijkt per wet de bron met wat er in de database staat:

* `register`: elke regel van `register.WETTEN` (ook die uit `register_<regio>.py`), via `register.haal_op`; FR-regels
  gaan mee met `fr`. Een nieuwe stand wordt een nieuwe versie (de oude blijft), en waar het register dat aangeeft
  wordt de systematiek aangevuld.
* `de`: alle wetten van gesetze-im-internet.de buiten het register. Met conditional GET: een ongewijzigde wet kost één
  304 en geen download.
* `nl`: alle geldende wetten, rijkswetten en AMvB's uit het BWB (SRU-lijst met de datum van de geldende toestand); een
  wet wordt alleen opgehaald als die datum verschilt van de opgeslagen versie.
* `fr`: eerst de dagelijkse aanvullingen van de LEGI-dump (`legi_dump`), dan de register-codes en, als de dump met
  `--alle` is opgehaald, alle andere codes.
* `eu-catalogus`: de catalogus uit Cellar (`eu.werk_catalogus_bij`), één keer per week (deel 1).
* `eu`: nieuwe handelingen en nieuwe consolidaties; ongewijzigde handelingen kosten geen verzoek.

Opgeslagen wordt alleen wat echt veranderd is: niet de versie alleen, maar de hash over de artikelen
(`store.inhoud_hash`). Gelijke hash = alleen `gecontroleerd` bijwerken. De bulk (alle wetten van een bron) wordt in
place bijgewerkt (`store.werk_bij`), artikel voor artikel.

`--deel 3/7` neemt een vast zevende van elke bron: de verdeling volgt uit een hash van de sleutel, dus elke wet komt
één keer per week aan de beurt, altijd op dezelfde dag. De ronde stopt netjes bij `--max-minuten`, bij te weinig
schijfruimte of geheugen (`ruimte.py`); wat niet aan de beurt kwam, komt de volgende week. Per bron (en stelsel) komt
één regel in de tabel `bijwerking`.
"""
from __future__ import annotations

import fcntl
import hashlib
import time
from collections.abc import Callable, Iterator
from contextlib import nullcontext
from dataclasses import dataclass, field

from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings
from ..models import Bijwerking, Wettekst, now
from . import Geparseerd, ImportOvergeslagen, http, register, ruimte, store
from .ruimte import Stop

Melder = Callable[[str], None]
BRONNEN = ("register", "fr", "de", "nl", "eu-catalogus", "eu")


@dataclass
class Taak:
    sleutel: str  # voor de verdeling over de week, bijv. "DE:bgb"
    stelsel: str
    wet_id: str
    ophalen: Callable[[], Geparseerd | tuple[Geparseerd, str] | None]  # (g, taal) als de taal pas bij het ophalen blijkt
    wet: Callable[[Geparseerd, Wettekst | None], str | None] = lambda g, b: None
    kern: bool = False
    historie: bool = False  # nieuwe stand = nieuwe rij (register) in plaats van in place (bulk)
    taal: str | None = None
    conditioneel: bool = False  # conditional GET als de wet er al is
    actueel: bool = False  # de lijst van de bron zegt al dat de opgeslagen versie de geldende is: niets ophalen
    systematiek: bool = False


@dataclass
class Telling:
    bron: str
    stelsel: str | None
    gecontroleerd: int = 0
    gewijzigd: int = 0
    nieuw: int = 0
    fouten: int = 0
    meldingen: list[str] = field(default_factory=list)

    def tekst(self) -> str:
        return f"{self.gecontroleerd} gecontroleerd, {self.gewijzigd} gewijzigd, {self.nieuw} nieuw, {self.fouten} fouten"


def _kort(e: BaseException) -> str:
    """Eerste regel van de fout (SQLAlchemy plakt de hele SQL erachter)."""
    return f"{type(e).__name__}: {str(e).splitlines()[0] if str(e) else ''}"[:240]


def deel_van(sleutel: str, n: int) -> int:
    """1…n, deterministisch (sha1, niet Pythons hash(), die per proces verschilt)."""
    return int(hashlib.sha1(sleutel.encode()).hexdigest()[:8], 16) % n + 1


def lees_deel(tekst: str | None) -> tuple[int, int] | None:
    if not tekst:
        return None
    k, _, n = tekst.partition("/")
    k, n = int(k), int(n or 7)
    if not 1 <= k <= n:
        raise ValueError(f"--deel {tekst}: verwacht k/n met 1 ≤ k ≤ n")
    return k, n


class Ronde:
    def __init__(self, fabriek: sessionmaker[Session], *, bronnen: list[str] | None = None, stelsels: list[str] | None = None,
                 deel: tuple[int, int] | None = None, droog: bool = False, max_minuten: float | None = None,
                 limiet: int | None = None, melder: Melder = print) -> None:
        self.fabriek = fabriek
        self.bronnen = [b for b in BRONNEN if not bronnen or b in bronnen]
        self.stelsels = {s.upper() for s in stelsels} if stelsels else None
        self.deel = deel
        self.droog = droog
        self.einde = time.monotonic() + max_minuten * 60 if max_minuten else None
        self.limiet = limiet
        self.meld = melder
        self.tellingen: list[Telling] = []
        self.gestopt: str | None = None

    # --- verdeling en bewaking ------------------------------------------------------------

    def wil(self, stelsel: str) -> bool:
        return self.stelsels is None or stelsel.upper() in self.stelsels

    def aan_de_beurt(self, sleutel: str) -> bool:
        return self.deel is None or deel_van(sleutel, self.deel[1]) == self.deel[0]

    def bewaak(self) -> None:
        if self.einde and time.monotonic() > self.einde:
            raise Stop("tijd op (--max-minuten)")
        ruimte.controleer()

    # --- één wet --------------------------------------------------------------------------

    def _bestaand(self, s: Session, stelsel: str, wet_id: str) -> Wettekst | None:
        return s.scalars(select(Wettekst).where(Wettekst.stelsel_code == stelsel, Wettekst.wet_id == wet_id)
                         .order_by(Wettekst.opgehaald.desc(), Wettekst.id.desc())).first()

    def verwerk(self, taak: Taak, t: Telling) -> str:
        """'nieuw' · 'gewijzigd' · 'ongewijzigd' · 'leeg' (bron gaf niets) · 'droog'."""
        with self.fabriek() as s:
            bestaand = self._bestaand(s, taak.stelsel, taak.wet_id)
            if self.droog:
                return "droog"
            cond = http.conditioneel() if taak.conditioneel and bestaand is not None else nullcontext()
            try:
                with cond as c:
                    uit = taak.ophalen()
            except http.Ongewijzigd:
                bestaand.gecontroleerd = now()
                s.commit()
                return "ongewijzigd"
            g, taal = uit if isinstance(uit, tuple) else (uit, taak.taal)
            if g is None or not g.artikelen:
                return "leeg"
            if g.wet_id != taak.wet_id:  # de importer bepaalt het id (bijv. normalisatie van een URN)
                bestaand = self._bestaand(s, taak.stelsel, g.wet_id)
            uitkomst, w = vergelijk(s, taak.stelsel, g, taak.wet(g, bestaand), bestaand, kern=taak.kern, historie=taak.historie, taal=taal)
            if taak.systematiek and uitkomst != "ongewijzigd" and w is not None:
                from ..services.systematiek import bouw_uit_wettekst
                bouw_uit_wettekst(s, w)
            s.commit()
            if c is not None:
                http.bevestig(c)
            if uitkomst != "ongewijzigd":
                self.meld(f"  {taak.stelsel} {taak.wet_id}: {uitkomst} ({g.versie}, {len(g.artikelen)} artikelen)")
            return uitkomst

    def _markeer_actueel(self, stelsel: str, wet_ids: list[str]) -> None:
        if self.droog or not wet_ids:
            return
        with self.fabriek() as s:
            for i in range(0, len(wet_ids), 500):
                s.execute(update(Wettekst).where(Wettekst.stelsel_code == stelsel, Wettekst.wet_id.in_(wet_ids[i:i + 500]))
                          .values(gecontroleerd=now()))
            s.commit()

    # --- een bron -------------------------------------------------------------------------

    def _bron(self, naam: str, taken: Iterator[Taak]) -> None:
        tellingen: dict[str | None, Telling] = {}
        begin = time.time()
        actueel: dict[str, list[str]] = {}
        n = 0
        gestopt = None

        def telling(stelsel: str | None) -> Telling:
            if stelsel not in tellingen:
                tellingen[stelsel] = Telling(naam, stelsel)
            return tellingen[stelsel]

        try:
            for taak in taken:
                if not self.wil(taak.stelsel) or not self.aan_de_beurt(taak.sleutel):
                    continue
                t = telling(taak.stelsel)
                if taak.actueel:
                    t.gecontroleerd += 1
                    actueel.setdefault(taak.stelsel, []).append(taak.wet_id)
                    continue
                if self.limiet and n >= self.limiet:
                    break
                self.bewaak()
                n += 1
                try:
                    uitkomst = self.verwerk(taak, t)
                except (Stop, KeyboardInterrupt):
                    raise
                except ImportOvergeslagen as e:
                    t.meldingen.append(f"overgeslagen: {e}"[:300])
                    continue
                except Exception as e:  # netwerk, parser: melden en door
                    t.fouten += 1
                    t.meldingen.append(f"{taak.wet_id}: {_kort(e)}"[:300])
                    self.meld(f"  FOUT {taak.stelsel} {taak.wet_id}: {_kort(e)}"[:300])
                    continue
                t.gecontroleerd += 1
                if uitkomst == "nieuw":
                    t.nieuw += 1
                elif uitkomst == "gewijzigd":
                    t.gewijzigd += 1
                if n % 50 == 0:
                    http.bewaar()
                    self.meld(f"{naam}: {n} opgehaald · {sum(x.gecontroleerd for x in tellingen.values())} gecontroleerd · {time.time() - begin:.0f}s")
        except Stop as e:
            gestopt = str(e)
        except Exception as e:  # de lijst van de bron zelf is niet op te halen
            telling(None).fouten += 1
            telling(None).meldingen.append(f"{_kort(e)}"[:300])
            self.meld(f"FOUT {naam}: {_kort(e)}"[:300])
        finally:
            http.bewaar()
            for stelsel, ids in actueel.items():
                self._markeer_actueel(stelsel, ids)
        duur = time.time() - begin
        if gestopt:
            telling(next(iter(tellingen), None)).meldingen.insert(0, f"gestopt: {gestopt}")
        for t in tellingen.values():
            self.tellingen.append(t)
            self.meld(f"{naam} {t.stelsel or ''}: {t.tekst()}" + (f" · {t.meldingen[0]}" if t.meldingen else ""))
            if not self.droog:
                with self.fabriek() as s:
                    s.add(Bijwerking(bron=naam, stelsel=t.stelsel, gecontroleerd=t.gecontroleerd, gewijzigd=t.gewijzigd, nieuw=t.nieuw,
                                     fouten=t.fouten, duur=round(duur, 1), melding="\n".join(t.meldingen[:8]) or None))
                    s.commit()
        if gestopt:
            raise Stop(gestopt)

    def draai(self) -> list[Telling]:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        with open(settings.data_dir / ".bijwerken.lock", "w") as slot:
            try:
                fcntl.flock(slot, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                self.gestopt = "er loopt al een bijwerkronde"
                self.meld(self.gestopt)
                return []
            try:
                ruimte.controleer()
                for naam in self.bronnen:
                    self.meld(f"— {naam}" + (f" (deel {self.deel[0]}/{self.deel[1]})" if self.deel else ""))
                    self._bron(naam, BRON_TAKEN[naam](self))
            except Stop as e:
                self.gestopt = str(e)
                self.meld(f"gestopt: {e}")
        return self.tellingen


def vergelijk(s: Session, stelsel: str, g: Geparseerd, wet: str | None, bestaand: Wettekst | None, *, kern: bool, historie: bool,
              taal: str | None = None) -> tuple[str, Wettekst | None]:
    """Slaat `g` alleen op als de artikelen echt verschillen van de laatst opgeslagen stand."""
    if bestaand is None:
        return "nieuw", store.sla_op(s, stelsel, g, wet, taal=taal, kern=kern, vervang=not historie)
    if bestaand.hash is None:  # rij van vóór de hash: eenmalig uit de database berekenen
        bestaand.hash, bestaand.aantal, bestaand.grootte = store.db_hash(s, bestaand.id)
    if store.inhoud_hash(g.artikelen) == bestaand.hash:
        bestaand.gecontroleerd = now()
        return "ongewijzigd", bestaand
    if historie and g.versie != bestaand.versie:
        return "gewijzigd", store.sla_op(s, stelsel, g, wet, taal=taal, kern=kern)
    return "gewijzigd", store.werk_bij(s, bestaand, g, wet)


# --- de bronnen ---------------------------------------------------------------------------

def _register(r: Ronde) -> Iterator[Taak]:
    for w in register.WETTEN:
        if w.importer == "legi":
            continue  # met de LEGI-dump, bij fr
        yield _register_taak(w)


def _register_taak(w: register.Wet) -> Taak:
    legi = str(settings.legi_dir) if w.importer == "legi" else None
    return Taak(sleutel=f"{w.stelsel}:{w.id}", stelsel=w.stelsel, wet_id=_wet_id(w), ophalen=lambda: register.haal_op(w, legi),
                wet=lambda g, b: w.wet, kern=True, historie=True, systematiek=w.systematiek)


def _wet_id(w: register.Wet) -> str:
    """Het wet_id zoals de importer het opslaat (gii verkleint, de rest neemt het id over)."""
    return w.id.lower() if w.importer == "gii" else w.id


def _de(r: Ronde) -> Iterator[Taak]:
    from . import gii

    register_ids = {w.id.lower() for w in register.WETTEN if w.stelsel == "DE"}
    if not r.wil("DE"):
        return
    c = http.client(timeout=120.0)
    try:
        for _, kurz in gii.toc(c):
            if kurz.lower() in register_ids:
                continue
            url = gii.URL.format(kurz=kurz)

            def ophalen(kurz=kurz, url=url):
                resp = c.get(url)
                if resp.status_code == 404:
                    return None
                resp.raise_for_status()
                return gii.parse_zip(resp.content, kurz.lower(), url)

            yield Taak(sleutel=f"DE:{kurz.lower()}", stelsel="DE", wet_id=kurz.lower(), ophalen=ophalen, conditioneel=True,
                       wet=lambda g, b, kurz=kurz: (g.afkorting or kurz.upper())[:60])
    finally:
        c.close()


def _nl(r: Ronde) -> Iterator[Taak]:
    from . import bwb

    if not r.wil("NL"):
        return
    register_ids = {w.id for w in register.WETTEN if w.stelsel == "NL"}
    with r.fabriek() as s:
        al = dict(s.execute(select(Wettekst.wet_id, Wettekst.versie).where(Wettekst.stelsel_code == "NL")).all())
    c = http.client(timeout=120.0)
    try:
        for regeling in bwb.geldende(c):
            if regeling.id in register_ids:
                continue

            def wet(g, b, regeling=regeling):
                if b is not None and b.wet:
                    return b.wet
                return (bwb.afkorting(regeling.id, c) or g.titel)[:60]

            yield Taak(sleutel=f"NL:{regeling.id}", stelsel="NL", wet_id=regeling.id, wet=wet,
                       ophalen=lambda regeling=regeling: bwb.haal_toestand(regeling.url, regeling.id, c),
                       actueel=al.get(regeling.id) == regeling.versie)
    finally:
        c.close()


def _fr(r: Ronde) -> Iterator[Taak]:
    from . import legi, legi_dump

    if not r.wil("FR"):
        return
    basis = settings.legi_dir
    if not r.droog:
        try:
            r.meld(legi_dump.werk_bij(basis, melder=r.meld))
        except ImportOvergeslagen as e:  # nog geen dump: geen fout, FR blijft zoals het is
            r.meld(f"fr: {e}")
            return
    for w in register.WETTEN:
        if w.importer == "legi":
            yield _register_taak(w)
    if not legi_dump.alle(basis):
        return
    register_ids = {w.id for w in register.WETTEN if w.stelsel == "FR"}
    for code, titel in legi.codes(basis):
        if code in register_ids:
            continue
        yield Taak(sleutel=f"FR:{code}", stelsel="FR", wet_id=code, ophalen=lambda code=code, titel=titel: legi.parse_map(basis, code, titel=titel),
                   wet=lambda g, b, titel=titel: legi.afkorting(titel)[:60])


def _eu_catalogus(r: Ronde) -> Iterator[Taak]:
    """Eén taak; de catalogus is geen wettekst, dus hier rechtstreeks en alleen op deel 1."""
    if not r.wil("EU") or (r.deel and r.deel[0] != 1):
        return iter(())
    t = Telling("eu-catalogus", "EU")
    if r.droog:
        t.gecontroleerd = 1
    else:
        from ..services import eu
        begin = time.time()
        r.bewaak()
        try:
            with r.fabriek() as s:
                uit = eu.werk_catalogus_bij(s, nims=True)
                s.commit()
            t.gecontroleerd, t.nieuw = uit["handelingen"], uit["nieuw"]
            t.meldingen.append(f"{uit['vervallen']} vervallen, {uit['rubrieken']} rubrieken, {uit['nims']} uitvoeringsmaatregelen")
        except Stop:
            raise
        except Exception as e:
            t.fouten = 1
            t.meldingen.append(f"{_kort(e)}"[:300])
        with r.fabriek() as s:
            s.add(Bijwerking(bron="eu-catalogus", stelsel="EU", gecontroleerd=t.gecontroleerd, nieuw=t.nieuw, fouten=t.fouten,
                             duur=round(time.time() - begin, 1), melding="\n".join(t.meldingen) or None))
            s.commit()
    r.tellingen.append(t)
    r.meld(f"eu-catalogus: {t.tekst()}" + (f" · {t.meldingen[0]}" if t.meldingen else ""))
    return iter(())


def _eu(r: Ronde) -> Iterator[Taak]:
    from ..models import EuHandeling, EuTitel
    from ..services import eunamen
    from . import bulk, cellar, eurlex

    if not r.wil("EU"):
        return
    with r.fabriek() as s:
        handelingen = list(s.execute(select(EuHandeling.celex, EuHandeling.soort, EuHandeling.nummer, EuHandeling.datum, EuHandeling.titel)))
        titels = dict(s.execute(select(EuTitel.celex, EuTitel.titel).where(EuTitel.taal == "de")).all())
        al = {(w, t): v for w, t, v in s.execute(select(Wettekst.wet_id, Wettekst.taal, Wettekst.versie).where(Wettekst.stelsel_code == "EU"))}
    eunamen.laad([(h.celex, h.soort, h.nummer) for h in handelingen])
    c = cellar.verbinding()
    try:
        cons = bulk.consolidaties(c)
        for celex, wet in eunamen.VERDRAGEN.items():
            for taal in eunamen.TALEN:
                wid = celex if taal == "de" else f"{celex}.{taal}"
                if (wid, taal) in al:
                    continue  # de verdragen veranderen niet

                def verdrag(celex=celex, wet=wet, taal=taal, wid=wid):
                    uit = bulk._download_met_terugval(celex, f"{celex}/TXT", taal, c, eunamen.VERDRAG_DATUM)
                    if uit is None:
                        return None
                    g, t = uit
                    g.titel, g.wet_id = eunamen.titel(wet, t) or g.titel, wid
                    return g, t

                yield Taak(sleutel=f"EU:{wid}", stelsel="EU", wet_id=wid, ophalen=verdrag, wet=lambda g, b, wet=wet: wet, kern=True, taal=taal)
        kern_namen = set(eunamen.BIJNAAM.values()) | set(bulk.register_eu_namen())
        for h in sorted(handelingen):
            tekst = cons.get(h.celex, h.celex)
            opgeslagen = al.get((h.celex, "de")) or al.get((h.celex, "en")) or al.get((h.celex, "fr"))
            actueel = opgeslagen is not None and (str(opgeslagen).startswith(eurlex.versie_van(tekst)) or not tekst.startswith("0"))
            wet = eunamen.sleutel(h.celex, h.soort, h.nummer)

            def handeling(h=h, tekst=tekst):
                uit = bulk._download_met_terugval(h.celex, tekst, "de", c, h.datum.isoformat() if h.datum else None)
                if uit is not None:
                    uit[0].titel = titels.get(h.celex) or h.titel or uit[0].titel
                return uit

            yield Taak(sleutel=f"EU:{h.celex}", stelsel="EU", wet_id=h.celex, ophalen=handeling, wet=lambda g, b, wet=wet: wet,
                       kern=wet in kern_namen, taal="de", actueel=actueel)
    finally:
        c.close()


BRON_TAKEN: dict[str, Callable[[Ronde], Iterator[Taak]]] = {
    "register": _register, "fr": _fr, "de": _de, "nl": _nl, "eu-catalogus": _eu_catalogus, "eu": _eu,
}
