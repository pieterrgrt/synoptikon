"""Alle wetten van een bron in één keer: gesetze-im-internet.de (DE) en de geldende EU-handelingen (Cellar).

Downloaden en parsen gebeurt in een paar threads tegelijk, wegschrijven in één thread (SQLite). Een tweede run slaat
over wat er al is: DE op `wet_id`, EU op `wet_id` plus versie (een nieuwe consolidatie wordt wel opgehaald). Met
`opnieuw` wordt alles opnieuw opgehaald. Een fout bij één wet stopt de rest niet.

DE: elke wet en verordening uit `gii-toc.xml`, behalve die uit het register (BGB, HGB, …: die heeft `import-alles`
al, met systematiek). Citeerafkorting = `amtabk` of `jurabk` (PatG, GG, SGB 5).

EU: elke geldende verordening, richtlijn en elk kaderbesluit uit de catalogus (`eu-catalogus`), in het Duits, als
geconsolideerde tekst waar die bestaat. Bestaat een handeling niet in het Duits, dan Engels of Frans. De drie
verdragen (VEU, VWEU, Handvest) in alle zes talen van de interface.
"""
from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import EuHandeling, EuTitel, Wettekst
from ..services import eunamen
from . import Geparseerd, cellar, eurlex, gii, register, store
from .http import client

Melder = Callable[[str], None]


def _parallel(taken: Iterable, werk: Callable, schrijf: Callable, parallel: int, melder: Melder, elke: int = 50) -> dict[str, int]:
    """`werk(taak)` in threads (downloaden + parsen), `schrijf(taak, uitkomst)` hier; uitkomst None = overgeslagen."""
    tel = dict(nieuw=0, overgeslagen=0, fout=0)
    taken = list(taken)
    begin = time.time()
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        # Een begrensde wachtrij: `parallel` downloads tegelijk, en nooit meer dan een paar documenten in het geheugen.
        rij: deque = deque()
        volgende = iter(taken)

        def vul() -> None:
            while len(rij) < parallel * 2:
                t = next(volgende, _KLAAR)
                if t is _KLAAR:
                    return
                rij.append((t, pool.submit(werk, t)))

        vul()
        i = 0
        while rij:
            taak, toekomst = rij.popleft()
            vul()
            i += 1
            try:
                uit = toekomst.result()
            except Exception as e:  # netwerk, parser: melden en door
                tel["fout"] += 1
                melder(f"FOUT {taak}: {type(e).__name__}: {e}"[:300])
                uit = False
            if uit is None:
                tel["overgeslagen"] += 1
            elif uit is not False:
                schrijf(taak, uit)
                tel["nieuw"] += 1
            if i % elke == 0:
                melder(f"{i}/{len(taken)} · {tel} · {time.time() - begin:.0f}s")
    return tel


_KLAAR = object()


# --- DE -----------------------------------------------------------------------------

def duitsland(sessie: Callable[[], Session], parallel: int = 4, limiet: int | None = None, opnieuw: bool = False,
              melder: Melder = print) -> dict[str, int]:
    register_ids = {w.id.lower() for w in register.WETTEN if w.stelsel == "DE"}
    with sessie() as s:
        al = set(s.scalars(select(Wettekst.wet_id).where(Wettekst.stelsel_code == "DE")))
    taken = [kurz for _, kurz in gii.toc() if kurz.lower() not in register_ids and (opnieuw or kurz.lower() not in al)]
    taken = taken[:limiet] if limiet else taken
    melder(f"DE: {len(taken)} wetten op te halen ({len(al)} al aanwezig)")
    c = client(timeout=120.0)
    s = sessie()

    def werk(kurz: str) -> Geparseerd | None:
        r = c.get(gii.URL.format(kurz=kurz))
        if r.status_code == 404:
            return None
        r.raise_for_status()
        g = gii.parse_zip(r.content, kurz.lower(), gii.URL.format(kurz=kurz))
        return g if g.artikelen else None

    n = 0

    def schrijf(kurz: str, g: Geparseerd) -> None:
        nonlocal n
        store.sla_op(s, "DE", g, (g.afkorting or kurz.upper())[:60], kern=False, vervang=True)
        n += 1
        if n % 25 == 0:
            s.commit()
            s.expunge_all()  # expire_on_commit staat uit: zonder dit blijven alle teksten in het geheugen

    try:
        tel = _parallel(taken, werk, schrijf, parallel, melder)
        s.commit()
    finally:
        s.close()
        c.close()
    return tel


# --- EU -----------------------------------------------------------------------------

def consolidaties(c) -> dict[str, str]:
    """CELEX van een handeling → CELEX van haar nieuwste geconsolideerde versie."""
    # Zonder ORDER BY/OFFSET: met paginering geeft de endpoint een 500 op deze groepering; het resultaat (±11.000
    # rijen) past in één antwoord.
    rijen = cellar._query(c, """SELECT ?bc (MAX(STR(?cc)) AS ?laatste) WHERE {
  ?cons cdm:act_consolidated_based_on_resource_legal ?b ; cdm:resource_legal_id_celex ?cc .
  ?b cdm:resource_legal_id_celex ?bc .
} GROUP BY ?bc""")
    return {r["bc"]: r["laatste"] for r in rijen if r.get("bc") and r.get("laatste")}


def _download_met_terugval(celex: str, tekst_celex: str, taal: str, c, datum: str | None = None) -> tuple[Geparseerd, str] | None:
    for t in (taal, "en", "fr") if taal == "de" else (taal,):
        doc = eurlex.download(tekst_celex, t, c)
        if doc is None and tekst_celex != celex:  # geconsolideerde tekst niet in deze taal: de oorspronkelijke
            doc = eurlex.download(celex, t, c)
            if doc is not None:
                tekst_celex = celex
        if doc is not None:
            versie = (eurlex.versie_van(tekst_celex) + " (konsolidiert)") if tekst_celex.startswith("0") else (datum or eurlex.versie_van(tekst_celex))
            url = eurlex.EURLEX.format(taal=t.upper(), celex=tekst_celex.split("/")[0])
            return eurlex.parse(doc, celex, url, taal=t, versie=versie), t
    return None


def europa(sessie: Callable[[], Session], parallel: int = 4, limiet: int | None = None, opnieuw: bool = False,
           alleen_verdragen: bool = False, melder: Melder = print) -> dict[str, int]:
    c = cellar.verbinding()
    with sessie() as s:
        handelingen = list(s.scalars(select(EuHandeling)))
        catalogus = [(h.celex, h.soort, h.nummer) for h in handelingen]
        datums = {h.celex: h.datum.isoformat() for h in handelingen if h.datum}
        titels = dict(s.execute(select(EuTitel.celex, EuTitel.titel).where(EuTitel.taal == "de")).all())
        nl_titels = {h.celex: h.titel for h in handelingen}
        # Alleen de kolommen: hele Wettekst-rijen laden zou alle al geïmporteerde teksten in het geheugen zetten.
        al = {(w, t): v for w, t, v in s.execute(select(Wettekst.wet_id, Wettekst.taal, Wettekst.versie)
                                                 .where(Wettekst.stelsel_code == "EU"))}
    eunamen.laad(catalogus)
    cons = {} if alleen_verdragen else consolidaties(c)
    melder(f"EU: {len(catalogus)} handelingen in de catalogus, {len(cons)} met een geconsolideerde versie")

    # (celex, tekst-celex, taal, sleutel, kern)
    taken: list[tuple[str, str, str, str, bool]] = []
    for celex, wet in eunamen.VERDRAGEN.items():
        for taal in eunamen.TALEN:
            if opnieuw or (celex if taal == "de" else f"{celex}.{taal}", taal) not in al:
                taken.append((celex, f"{celex}/TXT", taal, wet, True))
    if not alleen_verdragen:
        kern_namen = set(eunamen.BIJNAAM.values()) | set(register_eu_namen())
        for celex, soort, nummer in sorted(catalogus):
            tekst = cons.get(celex, celex)
            versie = eurlex.versie_van(tekst)
            if not opnieuw and str(al.get((celex, "de")) or "").startswith(versie) and tekst.startswith("0"):
                continue
            if not opnieuw and (celex, "de") in al and not tekst.startswith("0"):
                continue
            wet = eunamen.sleutel(celex, soort, nummer)
            taken.append((celex, tekst, "de", wet, wet in kern_namen))
    taken = taken[:limiet] if limiet else taken
    melder(f"EU: {len(taken)} teksten op te halen")
    s = sessie()
    n = 0

    def werk(taak):
        celex, tekst, taal, _, _ = taak
        return _download_met_terugval(celex, tekst, taal, c, eunamen.VERDRAG_DATUM if celex in eunamen.VERDRAGEN else datums.get(celex))

    def schrijf(taak, uitkomst) -> None:
        nonlocal n
        celex, _, gevraagd, wet, kern = taak
        g, taal = uitkomst
        if celex in eunamen.VERDRAGEN:
            g.titel = eunamen.titel(wet, taal) or g.titel
            g.wet_id = celex if gevraagd == "de" else f"{celex}.{gevraagd}"
        else:
            g.titel = titels.get(celex) or nl_titels.get(celex) or g.titel
        store.sla_op(s, "EU", g, wet, taal=taal, kern=kern, vervang=True)
        n += 1
        if n % 20 == 0:
            s.commit()
            s.expunge_all()

    try:
        tel = _parallel(taken, werk, schrijf, parallel, melder)
        s.commit()
    finally:
        s.close()
        c.close()
    return tel


def register_eu_namen() -> list[str]:
    from ..services.artikelen import regels
    return list(regels("EU").andere)
