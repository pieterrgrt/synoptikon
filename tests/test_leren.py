import re

from synoptikon import db as database
from synoptikon.config import settings
from synoptikon.models import Kaart, Leerlijst, Profiel, Wettekst, WettekstArtikel

TOKEN = "k" * 32


def _wettekst():
    with database.session() as s:
        w = s.query(Wettekst).filter_by(stelsel_code="DE", wet_id="test-bgb").first()
        if w is None:
            w = Wettekst(stelsel_code="DE", wet_id="test-bgb", titel="Bürgerliches Gesetzbuch", versie="2026-01-01")
            s.add(w)
            s.flush()
            for i, nr in enumerate(("929", "930", "931")):
                s.add(WettekstArtikel(wettekst_id=w.id, nummer=nr, opschrift=f"Opschrift {nr}", tekst=f"Tekst van § {nr}", volgorde=i))
        return w.id


def test_lezen_in_de_systematiek(client):
    _wettekst()
    r = client.get("/stelsels/DE?artikel=§ 929")
    assert r.status_code == 200
    m = re.search(r'data-k="(\d+)" open data-artikel="art-929"', r.text)
    assert m, "de knoop met het gezochte artikel staat open"
    frag = client.get(f"/stelsels/DE/lees/{m.group(1)}?fragment=1")
    assert frag.status_code == 200 and "Tekst van § 929" in frag.text and "<html" not in frag.text
    pagina = client.get(f"/stelsels/DE/lees/{m.group(1)}")
    assert "Tekst van § 929" in pagina.text and "☆" in pagina.text
    r = client.get("/artikelen/DE/929")
    assert f"/stelsels/DE/lees/{m.group(1)}#art-929" in r.text


def test_leerlijst_kaarten_en_oefenen(client):
    _wettekst()
    r = client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "Sachenrecht", "vak": "Sachenrecht",
                                          "stelsel": "DE", "nummer": "929", "wet": "", "soort": ["artikel", "kern", "plaats", "tegenhanger"],
                                          "doel": ["NL", "FR"], "notitie": "Einigung + Übergabe", "terug": "/artikelen/DE/929"},
                    follow_redirects=False)
    assert r.status_code == 303 and "bewaard=5" in r.headers["location"]
    # Nog eens: geen dubbele kaarten.
    with database.session() as s:
        lijst = s.query(Leerlijst).filter_by(naam="Sachenrecht").one()
        lid = lijst.id
    r = client.post("/leren/nieuw", data={"lijst": str(lid), "stelsel": "DE", "nummer": "929", "soort": "artikel"}, follow_redirects=False)
    assert "bewaard=0" in r.headers["location"]
    assert "★" in client.get("/artikelen/DE/929").text
    r = client.get(f"/leren/{lid}")
    # De tekst komt uit een eigen bron als die er is, anders uit de wettekst.
    assert r.status_code == 200 and "§ 929 BGB" in r.text and "Einigung + Übergabe" in r.text
    r = client.get(f"/leren/{lid}/oefenen")
    assert r.status_code == 200 and "kaarten-data" in r.text
    with database.session() as s:
        k = s.query(Kaart).filter_by(lijst_id=lid, soort="artikel").one()
        kid = k.id
    assert client.post(f"/leren/kaart/{kid}/oefen", data={"gekend": "1"}).json() == {"ok": True}
    with database.session() as s:
        assert s.get(Kaart, kid).gekend is True
    r = client.get(f"/leren/{lid}/export.md")
    assert r.status_code == 200 and "# Sachenrecht" in r.text


def test_arrest_en_vrije_kaart(client):
    r = client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "Jurisprudentie", "soort": ["arrest", "feiten"],
                                          "zaak": "HR 18 juni 1982 (Plas/Valburg)", "vindplaats": "NJ 1983/723",
                                          "feiten": "Onderhandelingen afgebroken", "antwoord": "Afbreken kan onaanvaardbaar zijn"},
                    follow_redirects=False)
    assert "bewaard=2" in r.headers["location"]
    r = client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "Leeg", "soort": "vrij"})
    assert r.status_code == 400


def _lijst_id(naam: str) -> int:
    with database.session() as s:
        return s.query(Leerlijst).filter_by(naam=naam).one().id


def test_api_kaarten_en_stand(anoniem, client):
    _wettekst()
    client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "API", "stelsel": "DE", "nummer": "930", "soort": "artikel"})
    settings.wk_token = TOKEN
    h = {"Authorization": f"Bearer {TOKEN}"}
    try:
        assert anoniem.get("/api/wk/kaarten").status_code == 401
        # De koppeling staat per profiel aan of uit (op /profiel); uit: 403, en de pagina's noemen Wunderkammer niet.
        client.post("/profiel/wunderkammer", data={})
        assert anoniem.get("/api/wk/kaarten", headers=h).status_code == 403
        assert "naar_wk" not in client.get("/leren").text and "Herhalen in Wunderkammer" not in client.get(
            f"/leren/{_lijst_id('API')}").text
        assert 'name="aan" value="1"' in client.get("/profiel").text
        client.post("/profiel/wunderkammer", data={"aan": "1"})
        data = anoniem.get("/api/wk/kaarten", headers=h).json()
        assert data["version"] == 2 and data["kaarten"]
        k = next(k for k in data["kaarten"] if k["refs"] and k["refs"][0]["nummer"] == "930")
        # De achterkant krijgt de wettekst; welke BGB-versie dat is (deze of de fixture uit test_importers) hangt van de volgorde af.
        assert "§ 930 BGB" in k["achter"] and ("Opschrift 930" in k["achter"] or "Besitzkonstitut" in k["achter"])
        assert k["url"].startswith("/artikelen/DE/")
        r = anoniem.post("/api/wk/kaarten/stand", headers=h, json={"stand": [
            {"uid": k["uid"], "due": "2026-11-02T08:00:00+00:00", "stability": 4.2, "reps": 3, "lapses": 1, "last_rating": 3},
            {"uid": "bestaat-niet"}]})
        assert r.json() == {"bijgewerkt": 1}
        with database.session() as s:
            kaart = s.query(Kaart).filter_by(uid=k["uid"]).one()
            assert kaart.stand.herhalingen == 3 and kaart.stand.missers == 1
            assert s.get(Profiel, 1).wk_gezien is not None
        assert "Laatst opgehaald" in client.get("/profiel").text and "Herhalen in Wunderkammer" in client.get(
            f"/leren/{_lijst_id('API')}").text
        # Uit: de stand van dit profiel wordt genegeerd.
        client.post("/profiel/wunderkammer", data={})
        r = anoniem.post("/api/wk/kaarten/stand", headers=h, json={"stand": [{"uid": k["uid"], "reps": 9}]})
        assert r.json() == {"bijgewerkt": 0}
        client.post("/profiel/wunderkammer", data={"aan": "1"})
    finally:
        settings.wk_token = None


def test_lijsten_zijn_persoonlijk(client, anoniem):
    from synoptikon.auth import hash_password

    with database.session() as s:
        p = s.get(Profiel, 3)
        p.gebruikersnaam, p.naam, p.rol, p.actief, p.wachtwoord_hash = "lezer3", "Lezer", "lezer", True, hash_password("lezerwachtwoord")
        lid = s.query(Leerlijst).filter_by(naam="Sachenrecht").one().id
    anoniem.post("/login", data={"gebruikersnaam": "lezer3", "wachtwoord": "lezerwachtwoord", "volgende": "/"})
    assert anoniem.get(f"/leren/{lid}").status_code == 404
    # Een lezer mag wel zijn eigen lijsten bijhouden.
    r = anoniem.post("/leren", data={"naam": "Eigen lijst"}, follow_redirects=False)
    assert r.status_code == 303
    with database.session() as s:
        assert s.query(Leerlijst).filter_by(naam="Eigen lijst").one().profiel_id == 3
