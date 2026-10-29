"""Leerlijsten delen: aanmelden met een code, zichtbaarheid, liken, reageren en overnemen."""
import pytest

from synoptikon import db as database
from synoptikon.config import settings
from synoptikon.models import Kaart, Leerlijst, LijstReactie, Profiel

CODE = "hu-zr-2026"


@pytest.fixture
def student(anoniem, monkeypatch):
    """Een medestudent die zich met de uitnodigingscode aanmeldt."""
    monkeypatch.setattr(settings, "aanmeldcode", CODE)
    with database.session() as s:
        if s.query(Profiel).filter_by(gebruikersnaam="anna").first() is None:
            r = anoniem.post("/aanmelden", data={"code": CODE, "gebruikersnaam": "Anna", "naam": "Anna", "wachtwoord": "geheimgeheim",
                                                 "nogmaals": "geheimgeheim"}, follow_redirects=False)
            assert r.status_code == 303 and r.headers["location"] == "/gedeeld"
        else:
            anoniem.post("/login", data={"gebruikersnaam": "anna", "wachtwoord": "geheimgeheim", "volgende": "/"})
    return anoniem


def _lijst(client) -> tuple[int, str]:
    # Zonder _wettekst(): die moet in test_leren de nieuwste BGB-tekst blijven.
    client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "Gedeeld ZR", "vak": "ZR Ia", "stelsel": "DE", "nummer": "931",
                                      "soort": ["artikel", "kern"]})
    with database.session() as s:
        l = s.query(Leerlijst).filter_by(naam="Gedeeld ZR").one()
        # een voorstel uit een notitie gaat niet mee
        s.add(Kaart(uid="voorstel-gedeeld", lijst=l, soort="vrij", vraag="Voorstel?", antwoord="Nee", status="voorstel", actief=False))
        return l.id, l.naam


def test_aanmelden(anoniem, monkeypatch):
    assert anoniem.get("/aanmelden").status_code == 404  # zonder code staat het uit
    monkeypatch.setattr(settings, "aanmeldcode", CODE)
    assert "uitnodigingscode" in anoniem.get("/login").text
    velden = {"gebruikersnaam": "bert", "naam": "Bert", "wachtwoord": "geheimgeheim", "nogmaals": "geheimgeheim"}
    r = anoniem.post("/aanmelden", data={**velden, "code": "fout"})
    assert r.status_code == 400 and "uitnodigingscode klopt niet" in r.text
    r = anoniem.post("/aanmelden", data={**velden, "code": CODE, "gebruikersnaam": "beheerder"})
    assert r.status_code == 400 and "al in gebruik" in r.text
    r = anoniem.post("/aanmelden", data={**velden, "code": CODE, "nogmaals": "anders12345"})
    assert r.status_code == 400
    r = anoniem.post("/aanmelden", data={**velden, "code": CODE}, follow_redirects=False)
    assert r.status_code == 303
    assert anoniem.get("/gedeeld").status_code == 200
    with database.session() as s:
        p = s.query(Profiel).filter_by(gebruikersnaam="bert").one()
        assert p.rol == "lezer" and p.actief and p.id > 5 and p.zelf_aangemeld


def test_aanmelden_zonder_domeincookie(anoniem, monkeypatch):
    """Een vrij gekozen gebruikersnaam mag geen Wunderkammer-account openen, en andersom."""
    from synoptikon import sso

    geheim = "x" * 40
    monkeypatch.setattr(settings, "sso_geheim", geheim)
    monkeypatch.setattr(settings, "aanmeldcode", CODE)
    velden = {"code": CODE, "gebruikersnaam": "gast9", "naam": "Gast", "wachtwoord": "geheimgeheim", "nogmaals": "geheimgeheim"}
    r = anoniem.post("/aanmelden", data=velden, follow_redirects=False)
    assert r.status_code == 303 and sso.COOKIE not in r.cookies
    anoniem.cookies.clear()
    r = anoniem.post("/login", data={"gebruikersnaam": "gast9", "wachtwoord": "geheimgeheim", "volgende": "/"},
                     follow_redirects=False)
    assert r.status_code == 303 and sso.COOKIE not in r.cookies
    anoniem.cookies.clear()
    anoniem.cookies.set(sso.COOKIE, sso.maak("gast9", geheim))
    assert anoniem.get("/", follow_redirects=False).status_code == 303


def test_delen_liken_reageren_overnemen(client, student):
    lid, naam = _lijst(client)
    with database.session() as s:
        assert s.get(Leerlijst, lid).deelcode is None
    # Privé: een ander ziet niets.
    client.post(f"/leren/{lid}/delen", data={"zichtbaar": "link"})
    with database.session() as s:
        code = s.get(Leerlijst, lid).deelcode
    assert code and naam not in student.get("/gedeeld").text  # met link: niet in het overzicht, wel te openen
    assert student.get(f"/gedeeld/{code}").status_code == 200
    client.post(f"/leren/{lid}/delen", data={"zichtbaar": "prive"})
    assert student.get(f"/gedeeld/{code}").status_code == 404
    client.post(f"/leren/{lid}/delen", data={"zichtbaar": "iedereen"})
    assert naam in student.get("/gedeeld").text

    html = student.get(f"/gedeeld/{code}").text
    assert "§ 931 BGB" in html and "Voorstel?" not in html and "Overnemen" in html
    student.post(f"/gedeeld/{code}/like")
    assert "♥ 1" in student.get(f"/gedeeld/{code}").text
    student.post(f"/gedeeld/{code}/like")  # nog eens: weer uit
    assert "♥ 0" in student.get(f"/gedeeld/{code}").text
    student.post(f"/gedeeld/{code}/like")
    student.post(f"/gedeeld/{code}/reactie", data={"tekst": "Handig voor de **Klausur**!"})
    assert "<strong>Klausur</strong>" in client.get(f"/gedeeld/{code}").text
    with database.session() as s:
        rid = s.query(LijstReactie).filter_by(lijst_id=lid).one().id

    # Overnemen: een eigen kopie met alleen de echte kaarten.
    r = student.post(f"/gedeeld/{code}/overnemen", follow_redirects=False)
    assert r.status_code == 303
    kopie_id = int(r.headers["location"].split("/")[2].split("?")[0])
    with database.session() as s:
        kopie = s.get(Leerlijst, kopie_id)
        anna = s.query(Profiel).filter_by(gebruikersnaam="anna").one()
        assert kopie.profiel_id == anna.id and kopie.overgenomen_van == lid and kopie.zichtbaar == "prive"
        assert sorted(k.soort for k in kopie.kaarten) == ["artikel", "kern"]
        assert {k.uid for k in kopie.kaarten}.isdisjoint({k.uid for k in s.get(Leerlijst, lid).kaarten})
    assert "jouw kopie" in student.get(f"/gedeeld/{code}").text
    # De student kan andermans lijst niet instellen, wel zijn eigen kopie delen.
    assert student.post(f"/leren/{lid}/delen", data={"zichtbaar": "prive"}).status_code == 404
    assert student.post(f"/leren/{kopie_id}/delen", data={"zichtbaar": "link"}, follow_redirects=False).status_code == 303

    # Reactie wissen: de schrijver of de eigenaar van de lijst.
    assert client.post(f"/gedeeld/{code}/reactie/{rid}/verwijder", follow_redirects=False).status_code == 303
    with database.session() as s:
        assert s.get(LijstReactie, rid) is None
