"""Wachtlijst: aanmelden zonder account, weghalen, en het bericht bij de opening."""
from sqlalchemy import select

from synoptikon import cli
from synoptikon.db import session
from synoptikon.models import Wachtlijst


def _adressen():
    with session() as s:
        return {r.email: r.taal for r in s.scalars(select(Wachtlijst))}


def test_anoniem_naar_wachtlijst(anoniem, client):
    r = anoniem.get("/", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/wachtlijst"
    html = anoniem.get("/wachtlijst").text
    assert 'name="email"' in html and "art. 3:84 lid 1 BW" in html and 'href="/login"' in html
    assert client.get("/", follow_redirects=False).status_code == 200  # ingelogd blijft / de app


def test_aanmelden_en_weghalen(anoniem):
    anoniem.post("/taal", data={"taal": "de", "terug": "/wachtlijst"})
    r = anoniem.post("/wachtlijst", data={"email": " Iemand@Example.org ", "actie": "op"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/wachtlijst?stand=op"
    assert "Warteliste" in anoniem.get(r.headers["location"]).text
    anoniem.post("/wachtlijst", data={"email": "iemand@example.org", "actie": "op"})  # dubbel: geen fout
    assert _adressen().get("iemand@example.org") == "de"
    assert anoniem.post("/wachtlijst", data={"email": "geen-adres"}).status_code == 400
    anoniem.post("/wachtlijst", data={"email": "bot@example.org", "website": "x"})  # verborgen veld ingevuld
    assert "bot@example.org" not in _adressen()
    r = anoniem.post("/wachtlijst", data={"email": "iemand@example.org", "actie": "af"}, follow_redirects=False)
    assert r.headers["location"] == "/wachtlijst?stand=af" and "iemand@example.org" not in _adressen()


def test_bericht_bij_opening(anoniem, tmp_path, monkeypatch):
    from synoptikon.config import settings

    for adres, taal in [("a@example.org", "nl"), ("b@example.org", "de")]:
        anoniem.post("/taal", data={"taal": taal, "terug": "/wachtlijst"})
        anoniem.post("/wachtlijst", data={"email": adres})
    (tmp_path / "opening.txt").write_text("Synoptikon is open\n\nZie https://example.org\n", encoding="utf-8")
    (tmp_path / "opening.de.txt").write_text("Synoptikon ist offen\n\nSiehe https://example.org\n", encoding="utf-8")

    verstuurd = []

    class NepSMTP:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def starttls(self): pass
        def login(self, *a): pass
        def send_message(self, m): verstuurd.append((m["To"], m["Subject"], m.get_content()))

    monkeypatch.setattr("smtplib.SMTP", NepSMTP)
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.org")
    monkeypatch.setattr(settings, "smtp_van", "synoptikon@example.org")
    assert cli.main(["wachtlijst", "--tekst", str(tmp_path / "opening.txt")]) == 0  # proef
    assert not verstuurd and {"a@example.org", "b@example.org"} <= set(_adressen())
    assert cli.main(["wachtlijst", "--tekst", str(tmp_path / "opening.txt"), "--doen"]) == 0
    assert ("b@example.org", "Synoptikon ist offen", "Siehe https://example.org\n") in verstuurd
    assert ("a@example.org", "Synoptikon is open", "Zie https://example.org\n") in verstuurd
    assert _adressen() == {}
