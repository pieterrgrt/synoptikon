"""Leessets (`/leren/sets`): artikelen, uitspraken en notities die je samen leest, op volgorde, met een reden."""
import re

import pytest

from synoptikon import db as database
from synoptikon.models import Bron, Kaart, Leerlijst, Leesset, Wettekst, WettekstArtikel
from synoptikon.services import leessets
from synoptikon.services.artikelen import Ref


@pytest.fixture
def materiaal():
    """Een stukje BGB met tekst en een uitspraak; na afloop alles weg wat de test maakte."""
    weg: dict[str, list[int]] = {"wettekst": [], "bron": []}
    with database.session() as f:
        w = Wettekst(stelsel_code="DE", wet_id="test-leesset-bgb", titel="BGB", versie="2026-01-01", kern=False)
        f.add(w)
        f.flush()
        weg["wettekst"].append(w.id)
        for nr in ("929", "932", "986"):
            f.add(WettekstArtikel(wettekst_id=w.id, nummer=nr, opschrift=f"Opschrift {nr}", tekst=f"Tekst van {nr}", volgorde=0))
        b = Bron(stelsel_code="DE", soort="rechtspraak", citeertitel="BGHZ 10, 81", vindplaats="NJW 1953, 1099", taal="de",
                 tekst="Gutgläubiger Erwerb …")
        f.add(b)
        f.flush()
        weg["bron"].append(b.id)
        f.commit()
    yield weg
    with database.session() as f:
        for s in f.query(Leesset).all():
            f.delete(s)
        for l in f.query(Leerlijst).filter(Leerlijst.naam.in_(["Test leesset", "Gutgläubiger Erwerb"])).all():
            f.delete(l)
        for k in f.query(Kaart).filter(Kaart.bron_id.in_(weg["bron"])).all():
            f.delete(k)
        for i in weg["bron"]:
            if (o := f.get(Bron, i)) is not None:
                f.delete(o)
        for i in weg["wettekst"]:
            if (o := f.get(Wettekst, i)) is not None:
                f.delete(o)
        f.commit()


def test_volgorde_reden_en_geen_dubbele(materiaal):
    with database.session() as db:
        s = leessets.maak(db, 1, "Test leesset", "Sachenrecht")
        a = leessets.voeg_toe(db, s, ref=Ref("DE", "929", None))
        b = leessets.voeg_toe(db, s, ref=Ref("DE", "932", None), reden="Gutgläubig: vergelijk met 929")
        n = leessets.voeg_toe(db, s, notitie="Eerst Trennungsprinzip herhalen")
        assert leessets.voeg_toe(db, s, ref=Ref("DE", "929", None), reden="Grundtatbestand") is None, "staat er al in"
        assert a.reden == "Grundtatbestand", "een lege reden wordt wel aangevuld"
        assert [o.positie for o in s.onderdelen] == [0, 1, 2]
        assert [o.soort for o in s.onderdelen] == ["artikel", "artikel", "notitie"]

        assert leessets.verplaats(s, n.id, -1)
        assert [o.id for o in sorted(s.onderdelen, key=lambda o: o.positie)] == [a.id, n.id, b.id]
        assert not leessets.verplaats(s, a.id, -1), "de eerste kan niet hoger"

        assert leessets.verwijder(db, s, n.id)
        assert [o.positie for o in sorted(s.onderdelen, key=lambda o: o.positie)] == [0, 1]
        db.commit()


def test_lezen_zet_de_wettekst_erbij(materiaal):
    with database.session() as db:
        s = leessets.maak(db, 1, "Test leesset")
        leessets.voeg_toe(db, s, ref=Ref("DE", "929", None))
        leessets.voeg_toe(db, s, bron=db.get(Bron, materiaal["bron"][0]))
        g = leessets.lezen(db, s)
        assert g[0].tekst == "Tekst van 929" and g[0].opschrift == "Opschrift 929" and g[0].url == "/artikelen/DE/929"
        assert g[1].titel == "BGHZ 10, 81" and g[1].opschrift == "NJW 1953, 1099" and g[1].url.startswith("/bronnen/")
        db.commit()


def test_invoer_wordt_herkend():
    r = leessets.lees_invoer("§ 929 BGB")
    assert r is not None and (r.stelsel, r.nummer) == ("DE", "929")
    assert leessets.lees_invoer("geen artikel") is None


def test_naar_kaarten_in_het_vak_en_niet_dubbel(materiaal):
    with database.session() as db:
        s = leessets.maak(db, 1, "Test leesset", "Sachenrecht")
        leessets.voeg_toe(db, s, ref=Ref("DE", "929", None))
        leessets.voeg_toe(db, s, bron=db.get(Bron, materiaal["bron"][0]))
        leessets.voeg_toe(db, s, notitie="alleen om te lezen")
        lijst, nieuw = leessets.naar_kaarten(db, s)
        assert lijst.vak == "Sachenrecht"
        soorten = {k.soort for k in lijst.kaarten if k.nummer == "929" or k.bron_id == materiaal["bron"][0]}
        assert {"artikel", "arrest"} <= soorten and nieuw >= 2
        _l, nog_eens = leessets.naar_kaarten(db, s)
        assert nog_eens == 0, "wat er al in staat komt er niet nog eens bij"
        for k in list(lijst.kaarten):
            if k.nummer == "929" or k.bron_id == materiaal["bron"][0]:
                db.delete(k)
        db.commit()


def test_pagina_s(client, materiaal):
    r = client.post("/leren/sets", data={"naam": "Gutgläubiger Erwerb", "vak": "", "artikel": ["DE||929", "DE||932"]},
                    follow_redirects=False)
    assert r.status_code == 303
    pad = r.headers["location"]
    sid = int(pad.rsplit("/", 1)[1])
    h = client.get(pad).text
    assert "Gutgläubiger Erwerb" in h and "Tekst van 929" in h and "Tekst van 932" in h
    assert h.index("Tekst van 929") < h.index("Tekst van 932")

    client.post(f"{pad}/onderdeel", data={"invoer": "§ 986 BGB", "reden": "Besitzrecht als Einwand"})
    h = client.get(pad).text
    assert "Tekst van 986" in h and "Besitzrecht als Einwand" in h

    client.post(f"{pad}/onderdeel", data={"invoer": "onzin"})
    with database.session() as db:
        s = db.get(Leesset, sid)
        ids = [o.id for o in s.onderdelen]
        assert len(ids) == 3
    client.post(f"{pad}/onderdeel/{ids[2]}", data={"actie": "omhoog"})
    h = client.get(pad).text
    assert h.index("Tekst van 986") < h.index("Tekst van 932")

    assert "/leren/sets" in client.get("/leren").text
    assert "Gutgläubiger Erwerb" in client.get("/leren/sets").text

    r = client.post(f"{pad}/kaarten", follow_redirects=False)
    assert r.status_code == 303 and re.match(r"/leren/\d+\?uit_set=3$", r.headers["location"])
    assert "Uit de leesset: 3 nieuwe kaarten." in client.get(r.headers["location"]).text

    client.post(f"{pad}/verwijder")
    assert client.get(pad).status_code == 404


def test_vanaf_een_artikel_of_uitspraak(client, materiaal):
    h = client.get("/leren/sets/kies?stelsel=DE&nummer=929&terug=/artikelen/DE/929").text
    assert "§ 929" in h and 'name="leesset"' in h
    r = client.post("/leren/sets/toevoegen", data={"leesset": "", "naam": "Test leesset", "stelsel": "DE", "nummer": "929",
                                                  "reden": "Kern", "terug": "/artikelen/DE/929"}, follow_redirects=False)
    assert r.headers["location"] == "/artikelen/DE/929"
    with database.session() as db:
        s = db.query(Leesset).filter_by(naam="Test leesset").one()
        sid = s.id
    client.post("/leren/sets/toevoegen", data={"leesset": str(sid), "bron": str(materiaal["bron"][0])})
    with database.session() as db:
        s = db.get(Leesset, sid)
        assert [o.soort for o in s.onderdelen] == ["artikel", "uitspraak"] and s.onderdelen[0].reden == "Kern"
    r = client.post("/leren/sets/toevoegen", data={"leesset": str(sid), "stelsel": "DE", "nummer": "932", "terug": "/\\evil.example"},
                    follow_redirects=False)
    assert r.headers["location"] == f"/leren/sets/{sid}", "geen redirect naar een andere site"


def test_alleen_uitspraken_als_bron(client, materiaal):
    with database.session() as db:
        wb = Bron(stelsel_code="DE", soort="wet", citeertitel="§ 1 Test", taal="de")
        db.add(wb)
        db.commit()
        materiaal["bron"].append(wb.id)
    assert client.get(f"/leren/sets/kies?bron={wb.id}").status_code == 400


def test_een_ander_profiel_ziet_je_leesset_niet(client, materiaal):
    from synoptikon.models import Profiel

    with database.session() as db:
        p = Profiel(gebruikersnaam="test-leesset-ander", naam="Ander")
        db.add(p)
        db.flush()
        s = leessets.maak(db, p.id, "Test leesset")
        db.commit()
        sid, pid = s.id, p.id
    assert client.get(f"/leren/sets/{sid}").status_code == 404
    assert client.post(f"/leren/sets/{sid}/kaarten").status_code == 404
    r = client.post("/leren/sets/toevoegen", data={"leesset": str(sid), "stelsel": "DE", "nummer": "929"})
    assert r.status_code == 404
    with database.session() as db:
        db.delete(db.get(Profiel, pid))
        db.commit()

