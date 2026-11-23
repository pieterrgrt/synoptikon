def test_profielen(client, anoniem):
    assert client.get("/profiel").status_code == 200
    r = client.get("/beheer/profielen"); assert r.status_code == 200 and "profiel2" in r.text
    # profiel 2 aanzetten als lezer met wachtwoord
    r = client.post("/beheer/profielen/2", data={"gebruikersnaam": "lezer", "naam": "Lezer", "rol": "lezer", "taal": "fr", "actief": "1", "wachtwoord": "lang-genoeg-1"}, follow_redirects=False)
    assert "fout" not in r.headers["location"], r.headers["location"]
    r = anoniem.post("/login", data={"gebruikersnaam": "Lezer", "wachtwoord": "lang-genoeg-1"}, follow_redirects=False)
    assert r.status_code == 303
    assert anoniem.get("/bronnen").status_code == 200
    assert anoniem.post("/stelsels/NL/actief", data={"actief": "0"}).status_code == 403
    assert anoniem.get("/beheer/profielen").status_code == 403
    assert 'lang="fr"' in anoniem.get("/").text
    # zichzelf niet uitzetten
    r = client.post("/beheer/profielen/1", data={"gebruikersnaam": "beheerder", "naam": "B", "rol": "lezer", "taal": "nl", "actief": "1"}, follow_redirects=False)
    assert "fout" in r.headers["location"]
    # uitzetten logt uit
    client.post("/beheer/profielen/2", data={"gebruikersnaam": "lezer", "naam": "Lezer", "rol": "lezer", "taal": "fr"})
    assert anoniem.get("/bronnen", follow_redirects=False).status_code == 303


def _zet_aan(client, pid: int, naam: str) -> None:
    r = client.post(f"/beheer/profielen/{pid}", data={"gebruikersnaam": naam, "naam": naam, "rol": "lezer", "taal": "nl",
                                                      "actief": "1", "wachtwoord": "lang-genoeg-1"}, follow_redirects=False)
    assert "fout" not in r.headers["location"], r.headers["location"]


def _lijsten(pid: int) -> int:
    from synoptikon.db import session
    from synoptikon.models import Leerlijst

    with session() as s:
        return s.query(Leerlijst).filter_by(profiel_id=pid).count()


def test_wachtwoord_vergeten_op_login(anoniem):
    assert "Alleen de beheerder kan een nieuw wachtwoord zetten." in anoniem.get("/login").text


def test_beheerder_verwijdert_profiel(client, anoniem):
    from synoptikon.db import session
    from synoptikon.models import Leerlijst, Profiel

    _zet_aan(client, 4, "weg")
    assert anoniem.post("/login", data={"gebruikersnaam": "weg", "wachtwoord": "lang-genoeg-1"}, follow_redirects=False).status_code == 303
    with session() as s:
        s.add(Leerlijst(profiel_id=4, naam="Weg"))
    assert _lijsten(4) == 1
    # zichzelf niet
    r = client.post("/beheer/profielen/1/verwijderen", follow_redirects=False)
    assert "fout" in r.headers["location"]
    r = client.post("/beheer/profielen/4/verwijderen", follow_redirects=False)
    assert r.headers["location"].endswith("klaar=verwijderd")
    assert _lijsten(4) == 0
    with session() as s:
        p = s.get(Profiel, 4)
        assert p.gebruikersnaam == "profiel4" and not p.actief and p.wachtwoord_hash is None
    # de oude cookie geldt niet meer, ook niet als de plek weer aangaat
    _zet_aan(client, 4, "nieuw")
    assert anoniem.get("/bronnen", follow_redirects=False).status_code == 303
    client.post("/beheer/profielen/4/verwijderen")


def test_zelf_verwijderen(client, anoniem):
    from synoptikon.db import session
    from synoptikon.models import Leerlijst, Profiel

    _zet_aan(client, 5, "zelf")
    anoniem.post("/login", data={"gebruikersnaam": "zelf", "wachtwoord": "lang-genoeg-1"})
    with session() as s:
        s.add(Leerlijst(profiel_id=5, naam="Mijn lijst"))
    assert "/profiel/verwijderen" in anoniem.get("/profiel").text
    assert anoniem.post("/profiel/verwijderen", data={"wachtwoord": "fout-fout-fout"}).status_code == 400
    assert _lijsten(5) == 1
    r = anoniem.post("/profiel/verwijderen", data={"wachtwoord": "lang-genoeg-1"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/login"
    assert _lijsten(5) == 0
    with session() as s:
        assert s.get(Profiel, 5).gebruikersnaam == "profiel5"
    # de beheerder kan dat niet zelf
    assert "/profiel/verwijderen" not in client.get("/profiel").text
    assert client.post("/profiel/verwijderen", data={"wachtwoord": "geheim"}).status_code == 400
