from synoptikon.config import settings

TOKEN = "t" * 32


def test_uit_zonder_token(anoniem):
    settings.wk_token = None
    assert anoniem.get("/api/wk/themen").status_code == 404


def test_token_verplicht(anoniem):
    settings.wk_token = TOKEN
    assert anoniem.get("/api/wk/themen").status_code == 401
    assert anoniem.get("/api/wk/themen", headers={"Authorization": "Bearer fout"}).status_code == 401


def test_themen_en_artikelen(anoniem):
    settings.wk_token = TOKEN
    h = {"Authorization": f"Bearer {TOKEN}"}
    r = anoniem.get("/api/wk/themen", headers=h)
    assert r.status_code == 200
    data = r.json()
    assert data["format"] == "synoptikon-wunderkammer" and data["version"] == 1
    assert data["correspondenties"] and all("artikelen" in c for c in data["correspondenties"])
    leden = [a for c in data["correspondenties"] for a in c["artikelen"]]
    assert any(a["stelsel"] == "DE" and a["nummer"] == "929" for a in leden)
    assert isinstance(data["begrippen"], list)
    r = anoniem.post("/api/wk/artikelen", headers=h, json={"refs": [{"stelsel": "DE", "wet": None, "nummer": "929"},
                                                                     {"stelsel": "XX", "nummer": "1"}]})
    assert r.status_code == 200
    assert isinstance(r.json()["artikelen"], list)
    assert anoniem.post("/api/wk/artikelen", headers=h, json={"refs": "x"}).status_code == 422
    settings.wk_token = None


def test_alleen_het_profiel_van_wunderkammer_ziet_de_koppeling(anoniem, client, monkeypatch):
    """Wunderkammer haalt één profiel op; een medestudent ziet niets van de koppeling, ook als hij hem eerder aanzette."""
    from synoptikon import db as database
    from synoptikon.auth import hash_password
    from synoptikon.models import Profiel

    monkeypatch.setattr(settings, "wk_token", "t" * 30)
    with database.session() as s:
        if s.query(Profiel).filter_by(gebruikersnaam="wk-ander").first() is None:
            s.add(Profiel(gebruikersnaam="wk-ander", naam="Ander", wachtwoord_hash=hash_password("geheimgeheim"), actief=True,
                          wunderkammer=True))
    anoniem.post("/login", data={"gebruikersnaam": "wk-ander", "wachtwoord": "geheimgeheim", "volgende": "/"})
    anoniem.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "Ander WK", "stelsel": "DE", "nummer": "931",
                                       "soort": ["artikel", "cloze"]})
    assert "Ander WK" in anoniem.get("/leren").text
    for url in ("/profiel", "/leren", "/leren/nieuw?stelsel=DE&nummer=931"):
        r = anoniem.get(url, follow_redirects=False)
        assert r.status_code == 200 and "Wunderkammer" not in r.text, url
    assert anoniem.post("/profiel/wunderkammer", data={"aan": "1"}, follow_redirects=False).status_code == 404
    # Het eigen profiel (1, of SYNOPTIKON_WK_PROFIEL) wel.
    assert "Koppeling met Wunderkammer" in client.get("/profiel").text
    monkeypatch.setattr(settings, "wk_profiel", "wk-ander")
    assert "Koppeling met Wunderkammer" not in client.get("/profiel").text
    assert "Koppeling met Wunderkammer" in anoniem.get("/profiel").text
