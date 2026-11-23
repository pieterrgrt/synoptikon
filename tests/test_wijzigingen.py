"""Geschiedenis van gedeelde inhoud: wie wijzigde wat, en terugzetten (services/wijzigingen.py)."""
import pytest
from fastapi.testclient import TestClient

from synoptikon import db as database
from synoptikon.auth import hash_password
from synoptikon.models import Notitie, Profiel, Vraag, Wijziging
from synoptikon.services import wijzigingen

VELDEN = ("gebruikersnaam", "naam", "rol", "actief", "wachtwoord_hash", "stelsels", "sessie_versie")


@pytest.fixture
def tweede():
    """Profielplek 4 tijdelijk als tweede redacteur 'Marijn', ingelogd; daarna terug zoals ze was."""
    from synoptikon.main import app

    with database.session() as s:
        p = s.get(Profiel, 4)
        oud = {v: getattr(p, v) for v in VELDEN}
        p.gebruikersnaam, p.naam, p.rol, p.actief, p.wachtwoord_hash, p.stelsels = \
            "marijn-test", "Marijn", "redacteur", True, hash_password("ook-geheim"), "NL,DE"
    with TestClient(app) as c:
        c.post("/login", data={"gebruikersnaam": "marijn-test", "wachtwoord": "ook-geheim", "volgende": "/"})
        try:
            yield c
        finally:
            with database.session() as s:
                p = s.get(Profiel, 4)
                for v in VELDEN:
                    setattr(p, v, oud[v])


@pytest.fixture
def vraag(client):
    r = client.post("/vragen/nieuw", data={"titel": "Geschiedenistest", "omschrijving": ""}, follow_redirects=False)
    slug = r.headers["location"].rsplit("/", 1)[-1]
    yield slug
    client.post(f"/vragen/{slug}/verwijderen")


def _antwoord_id(slug):
    with database.session() as s:
        return s.query(Vraag).filter_by(slug=slug).one().antwoord_voor("DE").id


def test_tweede_redacteur_overschrijft_en_het_is_terug_te_zetten(client, tweede, vraag):
    client.post(f"/vragen/{vraag}/antwoord/DE", data={"kern": "Kern van mij", "analyse": "Regel een\nRegel twee"})
    tweede.post(f"/vragen/{vraag}/antwoord/DE", data={"kern": "Kern van Marijn", "analyse": "Regel een\nAnders"})
    aid = _antwoord_id(vraag)
    with database.session() as s:
        ws = wijzigingen.geschiedenis(s, "antwoord", aid)[::-1]
        assert [(w.naam, w.actie) for w in ws][-2:] == [("Beheerder", "gewijzigd"), ("Marijn", "gewijzigd")]
        assert ws[-1].oud == {"kern": "Kern van mij", "analyse": "Regel een\nRegel twee"}
        mijn = ws[-2].id
    # zichtbaar in de synopse en bij het bewerken
    assert "Marijn" in client.get(f"/vragen/{vraag}").text
    assert "Laatst gewijzigd door Marijn" in client.get(f"/vragen/{vraag}/antwoord/DE").text
    html = client.get(f"/geschiedenis/antwoord/{aid}").text
    assert "Marijn" in html and "Beheerder" in html and "Regel twee" in html
    # mijn versie terugzetten
    r = client.post(f"/geschiedenis/antwoord/{aid}/terugzetten", data={"wijziging": mijn}, follow_redirects=False)
    assert r.status_code == 303
    with database.session() as s:
        a = s.query(Vraag).filter_by(slug=vraag).one().antwoord_voor("DE")
        assert (a.kern, a.analyse) == ("Kern van mij", "Regel een\nRegel twee")
        assert len(wijzigingen.geschiedenis(s, "antwoord", aid)) == len(ws) + 1
    html = client.get("/wijzigingen").text
    assert "Geschiedenistest · DE" in html and "Marijn" in html


def test_niets_veranderd_geeft_geen_wijziging(client, vraag):
    client.post(f"/vragen/{vraag}/antwoord/DE", data={"kern": "Zelfde", "analyse": ""})
    aid = _antwoord_id(vraag)
    with database.session() as s:
        n = len(wijzigingen.geschiedenis(s, "antwoord", aid))
    client.post(f"/vragen/{vraag}/antwoord/DE", data={"kern": "Zelfde", "analyse": ""})
    client.get(f"/vragen/{vraag}/antwoord/NL")  # maakt een leeg antwoord aan: niets om bij te houden
    with database.session() as s:
        assert len(wijzigingen.geschiedenis(s, "antwoord", aid)) == n
        nl = s.query(Vraag).filter_by(slug=vraag).one().antwoord_voor("NL").id
        assert wijzigingen.geschiedenis(s, "antwoord", nl) == []


def test_verwijderde_notitie_terughalen_met_schrijver(client, tweede, vraag):
    tweede.post(f"/vragen/{vraag}/notitie", data={"tekst": "Notitie van Marijn"})
    with database.session() as s:
        nid = s.query(Notitie).filter_by(tekst="Notitie van Marijn").one().id
    assert "Marijn" in client.get(f"/vragen/{vraag}").text
    client.post(f"/vragen/{vraag}/notitie/{nid}/verwijderen")
    with database.session() as s:
        assert s.get(Notitie, nid) is None
        w = wijzigingen.geschiedenis(s, "notitie", nid, bestaat=False)[0]
        assert (w.actie, w.naam) == ("verwijderd", "Beheerder")
    client.post(f"/geschiedenis/notitie/{nid}/terugzetten", data={"wijziging": w.id, "ervoor": "1"})
    with database.session() as s:
        assert s.get(Notitie, nid).tekst == "Notitie van Marijn"


def test_lezer_ziet_geschiedenis_maar_zet_niets_terug(client, vraag, anoniem):
    from tests.test_rechten import PLEK, VELDEN as RV

    client.post(f"/vragen/{vraag}/antwoord/DE", data={"kern": "Iets", "analyse": ""})
    aid = _antwoord_id(vraag)
    with database.session() as s:
        wid = wijzigingen.geschiedenis(s, "antwoord", aid)[0].id
        p = s.get(Profiel, PLEK)
        oud = {v: getattr(p, v) for v in RV}
        p.gebruikersnaam, p.rol, p.actief, p.wachtwoord_hash, p.stelsels = "lezer-gesch", "lezer", True, hash_password("x-y-z"), "NL,DE"
    try:
        anoniem.post("/login", data={"gebruikersnaam": "lezer-gesch", "wachtwoord": "x-y-z", "volgende": "/"})
        html = anoniem.get(f"/geschiedenis/antwoord/{aid}").text
        assert "Iets" in html and "terugzetten" not in html
        assert anoniem.post(f"/geschiedenis/antwoord/{aid}/terugzetten", data={"wijziging": wid}).status_code == 403
    finally:
        with database.session() as s:
            p = s.get(Profiel, PLEK)
            for v in RV:
                setattr(p, v, oud[v])


def test_zonder_auteur_geen_geschiedenis():
    """Imports en seed vanaf de opdrachtregel komen niet in de geschiedenis."""
    with database.session() as s:
        voor = s.query(Wijziging).count()
        v = Vraag(slug="zonder-auteur", titel="Zonder auteur")
        s.add(v)
    with database.session() as s:
        assert s.query(Wijziging).count() == voor
        s.delete(s.query(Vraag).filter_by(slug="zonder-auteur").one())
