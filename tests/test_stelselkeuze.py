"""Mijn stelsels per profiel, de indeling per regio en 'meer stelsels…' bij veel stelsels."""
import pytest


def test_regios_dekken_de_wereld():
    from synoptikon.seed.regios import REGIO, REGIOS, regio

    assert len([c for c in REGIO if len(c) == 2]) >= 249
    assert set(REGIO.values()) <= set(REGIOS)
    assert regio("NL") == "europa_west" and regio("QC") == "noord_amerika" and regio("SC") == "europa_west"
    assert regio("EU") == "supranationaal" and regio("JP") == "azie_oost" and regio("BR") == "latijns_amerika"
    assert regio("US-LA") == "noord_amerika" and regio("XX") == "overig"


def test_profiel_kiest_stelsels(client):
    r = client.get("/profiel")
    assert r.status_code == 200 and "data-stelselkiezer" in r.text
    r = client.post("/profiel/stelsels", data={"stelsel": ["NL", "DE"]}, follow_redirects=False)
    assert r.status_code == 303
    r = client.get("/profiel")
    assert 'value="NL" checked' in r.text and 'value="FR" checked' not in r.text
    assert client.get("/welkom").status_code == 200
    _herstel(client)


def _herstel(client):
    """Terug naar alle actieve stelsels, zodat de andere tests niets merken."""
    from synoptikon import db as database
    from synoptikon.models import Profiel

    with database.session() as s:
        s.get(Profiel, 1).stelsels = None


# --- ±60 stelsels: de pagina's blijven klein -------------------------------------------------------------------------

PAGINAS = ["/opzoeken?q=koop", "/vragen/nieuw", "/stelsels", "/stelsels/NL", "/artikelen", "/begrippen", "/begrippen/lijst",
           "/eu/omzetting", "/bronnen", "/bronnen/nieuw", "/invoer"]
MIJN = ["NL", "DE", "FR", "EU"]


def _vraag_slug():
    from sqlalchemy import select

    from synoptikon import db as database
    from synoptikon.models import Vraag

    with database.session() as s:
        return s.scalars(select(Vraag.slug)).first()


def _groottes(client, paginas):
    uit = {}
    for pad in paginas:
        r = client.get(pad)
        assert r.status_code == 200, pad
        uit[pad] = len(r.content)
    return uit


@pytest.fixture
def zestig_stelsels():
    """Vult de database aan tot 60 actieve stelsels (codes uit seed/regios.py, verspreid over de wereld) en zet de
    keuze van het beheerdersprofiel op vier stelsels; ruimt daarna alles op."""
    from sqlalchemy import delete, select

    from synoptikon import db as database
    from synoptikon.models import Profiel, Stelsel
    from synoptikon.seed.regios import REGIO

    extra: list[str] = []

    class Vuller(list):
        def vul(self):
            with database.session() as s:
                bestaand = set(s.scalars(select(Stelsel.code)).all())
                actief = len(s.scalars(select(Stelsel.code).where(Stelsel.actief == True)).all())  # noqa: E712
                extra[:] = [c for c in sorted(REGIO) if len(c) == 2 and c not in bestaand][::3][: max(0, 60 - actief)]
                for i, c in enumerate(extra):
                    s.add(Stelsel(code=c, naam=f"Stelsel {c}", taal="en", volgorde=1000 + i, actief=True, familie="common_law"))
            self[:] = extra
            return extra

    yield Vuller()
    with database.session() as s:
        s.execute(delete(Stelsel).where(Stelsel.code.in_(extra)))
        s.get(Profiel, 1).stelsels = None


def test_zestig_stelsels_paginas_blijven_klein(client, zestig_stelsels):
    from synoptikon import db as database
    from synoptikon.models import Profiel

    paginas = PAGINAS + [f"/vragen/{_vraag_slug()}"]
    with database.session() as s:
        s.get(Profiel, 1).stelsels = ",".join(MIJN)
    klein = _groottes(client, paginas)
    extra = zestig_stelsels.vul()
    groot = _groottes(client, paginas)
    for pad in paginas:
        # Elk ander stelsel kost hoogstens een regel in 'meer stelsels…' (vlag, code, misschien de naam); /stelsels
        # heeft daarnaast per stelsel een rij in de (ingeklapte) beheertabel, met de familiekeuze.
        per_stelsel = 2000 if pad == "/stelsels" else 700
        assert groot[pad] - klein[pad] < per_stelsel * len(extra), (pad, klein[pad], groot[pad])
    # Kiezers: mijn stelsels voorop, de andere per regio eronder.
    r = client.get("/opzoeken")
    eigen = r.text.split('<optgroup label="Mijn stelsels">')[1].split("</optgroup>")[0]
    assert 'value="NL"' in eigen and f'value="{extra[0]}"' not in eigen and f'value="{extra[0]}"' in r.text
    assert "meer stelsels…" in client.get(f"/vragen/{_vraag_slug()}").text
    # Opzoeken: standaard in mijn stelsels, met één tik in alle andere.
    r = client.get("/opzoeken?q=koop")
    assert "zoek-bereik" in r.text and "alle=1" in r.text
    assert client.get("/opzoeken?q=koop&alle=1").status_code == 200
    # /stelsels: alleen kaarten voor mijn stelsels, de rest per regio met tellingen.
    r = client.get("/stelsels")
    assert r.text.count('class="stelsel-kaart"') == len(MIJN)
    assert "kiezer-regio" in r.text and "geen open bron" in r.text
    # /profiel: alle 60 in de kiezer, ingedeeld per regio.
    r = client.get("/profiel")
    assert r.text.count('name="stelsel"') >= 60 and r.text.count('class="kiezer-regio"') >= 5


def test_ook_zet_een_kolom_erbij(client, zestig_stelsels):
    from synoptikon import db as database
    from synoptikon.models import Profiel

    with database.session() as s:
        s.get(Profiel, 1).stelsels = ",".join(MIJN)
    zestig_stelsels.vul()
    slug = _vraag_slug()
    zonder = client.get(f"/vragen/{slug}").text
    code = zestig_stelsels[0]
    met = client.get(f"/vragen/{slug}?ook={code}").text
    assert f'data-kolom="{code}"' not in zonder and f'data-kolom="{code}"' in met


def test_welkom_bij_eerste_keer(client):
    """Zonder keuze stuurt de eerste pagina naar /welkom, met een voorstel naar de taal van het profiel."""
    from synoptikon import db as database
    from synoptikon.models import Profiel
    from synoptikon.services import stelselkeuze

    with database.session() as s:
        assert "FR" in stelselkeuze.voorstel(s, "fr") and "EU" in stelselkeuze.voorstel(s, "fr")
        s.get(Profiel, 1).stelsels = None
    r = client.get("/vragen/nieuw", headers={"accept": "text/html"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith("/welkom")
    r = client.post("/profiel/stelsels", data={"stelsel": ["FR", "BE"], "volgende": "/vragen/nieuw"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/vragen/nieuw"
    assert client.get("/vragen/nieuw", headers={"accept": "text/html"}, follow_redirects=False).status_code == 200
    _herstel(client)


def test_migratie_neemt_actieve_stelsels(tmp_path):
    """Een bestaande database zonder de kolom: actieve profielen krijgen de actieve stelsels van nu."""
    import sqlite3

    from sqlalchemy import create_engine

    from synoptikon.db import _migreer

    pad = tmp_path / "oud.db"
    c = sqlite3.connect(pad)
    c.executescript("""CREATE TABLE stelsel (code TEXT, actief INT, volgorde INT);
        INSERT INTO stelsel VALUES ('NL', 1, 10), ('DE', 1, 20), ('XY', 0, 30);
        CREATE TABLE profiel (id INT, actief INT, laatst_ingelogd TEXT);
        INSERT INTO profiel VALUES (1, 1, NULL), (2, 0, NULL);
        CREATE TABLE leerlijst (profiel_id INT, naar_wk INT);""")
    c.close()
    with create_engine(f"sqlite:///{pad}").begin() as conn:
        _migreer(conn)
    assert dict(sqlite3.connect(pad).execute("SELECT id, stelsels FROM profiel").fetchall()) == {1: "NL,DE", 2: None}
