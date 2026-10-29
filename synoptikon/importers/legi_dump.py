"""FR: de LEGI-dump van de DILA ophalen en bijhouden, gestreamd (geen tar.gz op schijf).

https://echanges.dila.gouv.fr/OPENDATA/LEGI/ biedt een volledige dump (`Freemium_legi_global_<datum>.tar.gz`, ±1,1 GB)
en daarna elke werkdag een of meer aanvullingen (`LEGI_<datum>-<tijd>.tar.gz`, enkele MB) met alleen de gewijzigde
bestanden, plus soms `liste_suppression_legi.dat` met verwijderde bestanden. Eén keer de volledige dump, daarna
alleen de aanvullingen: dat is wat `synoptikon bijwerken` elke nacht doet.

Twee reikwijdten:

* *register* (standaard): alleen de codes uit het register (Code civil, C. consom., C. com.);
* *alle* (`synoptikon legi --alle`): alle geldende codes (map `code_en_vigueur`, ±75 codes).

Van de artikelen worden alleen de versies bewaard die vandaag of later gelden (DATE_FIN na vandaag); een versie die al
is afgelopen, gaat niet op schijf en wordt bij een aanvulling verwijderd. Secties en structuur blijven volledig.
Markeringen in de doelmap (`.globaal-[alle-]<datum>`, `.aanvulling-[alle-]<datum-tijd>`) houden bij wat verwerkt is;
ze zijn verenigbaar met de oude `scripts/legi_ophalen.sh`.
"""
from __future__ import annotations

import re
import tarfile
from collections.abc import Callable, Iterator
from datetime import date
from pathlib import Path, PurePosixPath

from . import ImportOvergeslagen, ruimte
from .http import client

URL = "https://echanges.dila.gouv.fr/OPENDATA/LEGI/"
Melder = Callable[[str], None]
_FIN = re.compile(rb"<DATE_FIN>(\d{4}-\d{2}-\d{2})</DATE_FIN>")


class _Stroom:
    """Bestandsachtig object over een iterator van bytes, voor `tarfile.open(mode="r|gz")`."""

    def __init__(self, stukken: Iterator[bytes]) -> None:
        self.stukken = stukken
        self.buffer = b""

    def read(self, n: int = -1) -> bytes:
        while n < 0 or len(self.buffer) < n:
            stuk = next(self.stukken, None)
            if stuk is None:
                break
            self.buffer += stuk
        if n < 0:
            uit, self.buffer = self.buffer, b""
        else:
            uit, self.buffer = self.buffer[:n], self.buffer[n:]
        return uit


def register_codes() -> set[str]:
    from .register import WETTEN
    return {w.id for w in WETTEN if w.importer == "legi"}


def lijst(c) -> tuple[str | None, list[str]]:
    """(naam van de nieuwste volledige dump, aanvullingen oud → nieuw)."""
    r = c.get(URL)
    r.raise_for_status()
    globaal = sorted(set(re.findall(r"Freemium_legi_global_[0-9-]+\.tar\.gz", r.text)))
    aanvullingen = sorted(set(re.findall(r"LEGI_\d{8}-\d{6}\.tar\.gz", r.text)))
    return (globaal[-1] if globaal else None), aanvullingen


def alle(basis: Path) -> bool:
    return any(Path(basis).glob(".globaal-alle-*"))


def _globale_stempel(basis: Path, voorvoegsel: str) -> str | None:
    stempels = sorted(re.sub(r"\D", "", p.name)[:8] for p in Path(basis).glob(f".globaal-{voorvoegsel}*")
                      if voorvoegsel or not p.name.startswith(".globaal-alle-"))
    return stempels[-1] if stempels else None


def _relatief(naam: str) -> PurePosixPath | None:
    """Pad vanaf `legi/` (de aanvullingen hebben er een map met de tijdstempel voor); None bij iets verdachts."""
    p = PurePosixPath(naam)
    if p.is_absolute() or ".." in p.parts or "legi" not in p.parts:
        return None
    return PurePosixPath(*p.parts[p.parts.index("legi"):])


def _pak_uit(c, url: str, basis: Path, past: Callable[[str], bool], melder: Melder) -> tuple[int, set[str]]:
    """Streamt één tar.gz en schrijft wat `past`; geeft (aantal bestanden, aangeraakte LEGITEXT-codes)."""
    vandaag = date.today().isoformat().encode()
    n, codes = 0, set()
    with c.stream("GET", url, timeout=600.0) as r:
        r.raise_for_status()
        with tarfile.open(fileobj=_Stroom(r.iter_bytes(1 << 16)), mode="r|gz") as tar:
            for i, lid in enumerate(tar):
                if i % 5000 == 0:
                    ruimte.controleer_schijf()
                if not lid.isfile():
                    continue
                rel = _relatief(lid.name)
                if rel is None:
                    continue
                if rel.name == "liste_suppression_legi.dat":
                    for regel in tar.extractfile(lid).read().decode("utf-8", "replace").splitlines():
                        weg = _relatief(regel.strip())
                        if weg is not None and past(str(weg)):
                            for doel in (basis / weg, (basis / weg).with_suffix(".xml")):
                                if doel.is_file():
                                    doel.unlink()
                    continue
                pad = str(rel)
                if not past(pad):
                    continue
                data = tar.extractfile(lid).read()
                doel = basis / rel
                if "/article/" in pad:
                    m = _FIN.search(data)
                    if m and m.group(1) <= vandaag:  # afgelopen versie: niet bewaren, en een oude kopie weg
                        if doel.is_file():
                            doel.unlink()
                        continue
                doel.parent.mkdir(parents=True, exist_ok=True)
                doel.write_bytes(data)
                n += 1
                code = next((x for x in rel.parts if x.startswith("LEGITEXT")), None)
                if code:
                    codes.add(code)
    return n, codes


def _filter(met_alles: bool, codes: set[str]) -> Callable[[str], bool]:
    if met_alles:
        return lambda pad: "/code_en_vigueur/" in pad
    return lambda pad: any(code in pad for code in codes)


def haal_globaal(basis: Path, met_alles: bool = False, codes: set[str] | None = None, melder: Melder = print) -> str:
    """De volledige dump (eenmalig, ±1,1 GB over het netwerk, een half uur tot een uur), daarna de aanvullingen."""
    basis = Path(basis)
    basis.mkdir(parents=True, exist_ok=True)
    voorvoegsel = "alle-" if met_alles else ""
    with client(timeout=600.0) as c:
        globaal, _ = lijst(c)
        if globaal is None:
            raise ImportOvergeslagen("geen volledige LEGI-dump gevonden op " + URL)
        stempel = re.sub(r"\D", "", globaal)[:8]
        marker = basis / f".globaal-{voorvoegsel}{stempel}"
        if not marker.exists():
            melder(f"LEGI: volledige dump {globaal} ({'alle codes' if met_alles else 'registercodes'}) …")
            n, _ = _pak_uit(c, URL + globaal, basis, _filter(met_alles, codes or register_codes()), melder)
            marker.touch()
            melder(f"LEGI: {n} bestanden uit de volledige dump")
    return werk_bij(basis, melder=melder, codes=codes)


def werk_bij(basis: Path, melder: Melder = print, codes: set[str] | None = None) -> str:
    """Alle aanvullingen na de volledige dump die nog niet verwerkt zijn, oudste eerst. Geeft een korte melding."""
    basis = Path(basis)
    met_alles = alle(basis)
    voorvoegsel = "alle-" if met_alles else ""
    stempel = _globale_stempel(basis, voorvoegsel)
    if stempel is None:
        raise ImportOvergeslagen(f"geen LEGI-dump in {basis}; eerst `synoptikon legi` (of `--alle`)")
    past = _filter(met_alles, codes or register_codes())
    bestanden, codes_geraakt, verwerkt = 0, set(), 0
    with client(timeout=600.0) as c:
        _, aanvullingen = lijst(c)
        for naam in aanvullingen:
            moment = naam[5:20]  # 20261028-212713
            if moment[:8] <= stempel:
                continue
            if (basis / f".aanvulling-{voorvoegsel}{moment}").exists() or (not met_alles and (basis / f".aanvulling-{moment[:8]}").exists()):
                continue
            n, geraakt = _pak_uit(c, URL + naam, basis, past, melder)
            (basis / f".aanvulling-{voorvoegsel}{moment}").touch()
            bestanden += n
            codes_geraakt |= geraakt
            verwerkt += 1
    return f"LEGI: {verwerkt} aanvullingen, {bestanden} bestanden, {len(codes_geraakt)} codes geraakt"
