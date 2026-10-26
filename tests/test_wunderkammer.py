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
