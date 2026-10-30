"""Bewaren met vak in één tik: afleiden, onthouden, en het vak wisselen als correctie."""
import pytest
from sqlalchemy import select

from synoptikon import db as database
from synoptikon.models import Kaart, Leerlijst, Opzoeking, Profiel
from synoptikon.services import vakken


@pytest.mark.parametrize("stelsel,wet,nummer,vak", [
    ("DE", "BGB", "145", "ZR Ia"),
    ("DE", None, "119", "ZR Ia"),  # hoofdwet van DE is het BGB
    ("DE", "BGB", "929", "Sachenrecht"),
    ("DE", "BGB", "823", None),  # Schuldrecht BT: geen vak van dit semester
    ("DE", "AktG", "76", "UG"),
    ("EU", "AEUV", "101", "W"),
    ("EU", None, None, "W"),  # een arrest van het HvJ
    ("NL", "BW", "3:84", None),
    ("DE", "GG", "1", None),
])
def test_afleiden(stelsel, wet, nummer, vak):
    assert vakken.afleiden(stelsel, wet, nummer) == vak


def _lijsten(pid=1):
    with database.session() as s:
        return {l.vak: l for l in s.scalars(select(Leerlijst).where(Leerlijst.profiel_id == pid, Leerlijst.vak.is_not(None)))}


def test_bewaren_leidt_vak_af_en_maakt_de_lijst(client):
    r = client.post("/leren/snel", data={"stelsel": "DE", "wet": "BGB", "nummer": "145", "terug": "/artikelen/DE/145"},
                    follow_redirects=False)
    assert r.status_code == 303 and "vak=ZR%20Ia" in r.headers["location"] and "kaarten=" in r.headers["location"]
    with database.session() as s:
        k = s.scalar(select(Kaart).where(Kaart.nummer == "145"))
        assert k.lijst.vak == "ZR Ia" and k.lijst.naar_wk
        assert s.get(Profiel, 1).laatste_vak == "ZR Ia"
    html = client.get(r.headers["location"]).text
    assert "bewaard in ZR Ia" in html and 'action="/leren/vak"' in html


def test_zonder_afleiding_geldt_het_laatste_vak(client):
    vakken_pid = 1
    with database.session() as s:
        vakken.onthoud(s, vakken_pid, "UG")
    client.post("/leren/snel", data={"stelsel": "NL", "wet": "BW", "nummer": "6:162"})
    with database.session() as s:
        k = s.scalar(select(Kaart).where(Kaart.nummer == "6:162"))
        assert k.lijst.vak == "UG"


def test_vak_expliciet_gaat_voor_afleiding(client):
    client.post("/leren/snel", data={"stelsel": "DE", "wet": "BGB", "nummer": "146", "vak": "Sachenrecht"})
    with database.session() as s:
        k = s.scalar(select(Kaart).where(Kaart.nummer == "146"))
        assert k.lijst.vak == "Sachenrecht" and s.get(Profiel, 1).laatste_vak == "Sachenrecht"


def test_vak_wisselen_is_een_correctie(client):
    client.post("/leren/snel", data={"stelsel": "DE", "wet": "BGB", "nummer": "147"})
    with database.session() as s:
        kid = s.scalar(select(Kaart).where(Kaart.nummer == "147")).id
    r = client.post("/leren/vak", data={"kaarten": str(kid), "vak": "W", "terug": "/artikelen/DE/147?bewaard=1&vak=ZR%20Ia&kaarten=1"},
                    follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/artikelen/DE/147"
    with database.session() as s:
        k = s.get(Kaart, kid)
        assert k.lijst.vak == "W" and s.get(Profiel, 1).laatste_vak == "W"
        assert k.lijst_id == min(s.scalars(select(Leerlijst.id).where(Leerlijst.vak == "W", Leerlijst.profiel_id == 1, ~Leerlijst.naam.startswith("Notities"))))  # de oudste lijst van het vak
    assert client.post("/leren/vak", data={"kaarten": "999999", "vak": "W"}).status_code == 400


def test_notitielijst_is_nooit_het_doel(client):
    with database.session() as s:
        s.add(Leerlijst(profiel_id=1, naam="Notities · Wüstenland", vak="Wüstenland"))
        s.flush()
        assert vakken.lijst_voor(s, 1, "Wüstenland").naam == "Wüstenland"


def test_opzoeking_bewaren_in_afgeleid_vak(client):
    with database.session() as s:
        o = Opzoeking(profiel_id=1, invoer="hvj", resultaat=dict(soort="uitspraak", stelsel="EU", citeer="HvJ EU 10 december 2015, C-594/14",
                                                                 titel="Kornhaas", vindplaats="ECLI:EU:C:2015:806", toelichting="x", bron="cellar"))
        s.add(o)
        s.flush()
        oid = o.id
    html = client.get(f"/opzoeken/{oid}").text
    assert '<option selected>W</option>' in html
    client.post(f"/opzoeken/{oid}/bewaren", data={"vak": ""})
    with database.session() as s:
        o = s.get(Opzoeking, oid)
        assert o.kaart.lijst.vak == "W" and o.kaart.soort == "arrest"
    html = client.get(f"/opzoeken/{oid}").text
    assert "★ Bewaard · W" in html and 'action="/leren/vak"' in html
