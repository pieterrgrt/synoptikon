"""Bewaren met vak: kiezen bij de eerste ☆, de keuze vasthouden, afleiden, en het vak wisselen als correctie."""
from datetime import timedelta

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
    ("DE", "AktG", "76", None),  # vennootschapsrecht: geen vak van dit semester (EuGesR is EU-recht)
    ("DE", "BGB", "327a", "Digi"),
    ("DE", "GWB", "1", "KartR"),
    ("DE", "WpHG", "33", "KapMR"),
    ("DE", "UrhG", "44b", "Digi"),
    ("EU", "AEUV", "101", "KartR"),
    ("EU", "AEUV", "49", None),
    ("EU", None, None, None),  # een arrest van het HvJ: geen vak uit het onderwerp
    ("NL", "BW", "3:84", None),
    ("DE", "GG", "1", None),
])
def test_afleiden(stelsel, wet, nummer, vak):
    assert vakken.afleiden(stelsel, wet, nummer) == vak


def _keuze(vak=None, uren_geleden=0.0, pid=1):
    """Zet de lopende keuze: geen (None), of een vak dat zoveel uur geleden het laatst gebruikt is."""
    from synoptikon.models import now

    with database.session() as s:
        p = s.get(Profiel, pid)
        p.laatste_vak = vak or p.laatste_vak
        p.vak_sinds = None if vak is None else now() - timedelta(hours=uren_geleden)
        s.commit()


def _lijsten(pid=1):
    with database.session() as s:
        return {l.vak: l for l in s.scalars(select(Leerlijst).where(Leerlijst.profiel_id == pid, Leerlijst.vak.is_not(None)))}


def test_eerste_ster_vraagt_het_vak_met_het_afgeleide_vak_aangevinkt(client):
    _keuze(None)
    r = client.post("/leren/snel", data={"stelsel": "DE", "wet": "BGB", "nummer": "145", "terug": "/artikelen/DE/145"},
                    follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith("/leren/snel?")
    with database.session() as s:
        assert s.scalar(select(Kaart).where(Kaart.nummer == "145")) is None, "nog niets bewaard"
    html = client.get(r.headers["location"]).text
    assert 'value="ZR Ia" checked' in html and 'name="project"' in html and "§ 145" in html
    r = client.post("/leren/snel", data={"stelsel": "DE", "wet": "BGB", "nummer": "145", "vak": "ZR Ia", "terug": "/artikelen/DE/145"},
                    follow_redirects=False)
    assert r.status_code == 303 and "vak=ZR%20Ia" in r.headers["location"] and "kaarten=" in r.headers["location"]
    with database.session() as s:
        k = s.scalar(select(Kaart).where(Kaart.nummer == "145"))
        assert k.lijst.vak == "ZR Ia" and k.lijst.naar_wk
        assert s.get(Profiel, 1).laatste_vak == "ZR Ia"
    html = client.get(r.headers["location"]).text
    assert "bewaard in ZR Ia" in html and 'action="/leren/vak"' in html


def test_de_keuze_geldt_daarna_zonder_te_vragen_ook_tegen_de_afleiding_in(client):
    _keuze("KartR")
    r = client.post("/leren/snel", data={"stelsel": "DE", "wet": "BGB", "nummer": "930"}, follow_redirects=False)
    assert "vak=KartR" in r.headers["location"], "§ 930 zou Sachenrecht zijn, maar je koos KartR"
    with database.session() as s:
        assert s.scalar(select(Kaart).where(Kaart.nummer == "930").order_by(Kaart.id.desc())).lijst.vak == "KartR"


def test_na_een_pauze_wordt_weer_gevraagd(client):
    _keuze("KartR", uren_geleden=3)
    r = client.post("/leren/snel", data={"stelsel": "DE", "wet": "BGB", "nummer": "931"}, follow_redirects=False)
    assert r.headers["location"].startswith("/leren/snel?")
    assert 'value="Sachenrecht" checked' in client.get(r.headers["location"]).text, "voorgesteld: wat uit het artikel volgt"


def test_een_project_met_eigen_naam(client):
    _keuze(None)
    client.post("/leren/snel", data={"stelsel": "DE", "wet": "BGB", "nummer": "932", "vak": "ZR Ia", "project": "Seminar Haftung"})
    with database.session() as s:
        assert s.scalar(select(Kaart).where(Kaart.nummer == "932").order_by(Kaart.id.desc())).lijst.vak == "Seminar Haftung"
        assert vakken.actief(s, 1) == "Seminar Haftung"
    html = client.get("/leren/snel?stelsel=DE&wet=BGB&nummer=933").text
    assert 'value="Seminar Haftung"' in html, "eigen projecten staan daarna in de keuze"


def test_uitspraak_vraagt_ook_het_vak(client):
    from synoptikon.models import Bron

    _keuze(None)
    with database.session() as s:
        b = Bron(stelsel_code="EU", soort="rechtspraak", citeertitel="HvJ test-vak-kiezen", taal="nl")
        s.add(b)
        s.commit()
        bid = b.id
    r = client.post("/leren/snel", data={"bron": str(bid)}, follow_redirects=False)
    assert r.headers["location"].startswith("/leren/snel?") and "HvJ test-vak-kiezen" in client.get(r.headers["location"]).text
    client.post("/leren/snel", data={"bron": str(bid), "vak": "EuGesR"})
    with database.session() as s:
        assert s.scalar(select(Kaart).where(Kaart.bron_id == bid)).lijst.vak == "EuGesR"
    assert 'title="Bewaren in EuGesR"' in client.get(f"/bronnen/{bid}").text, "de ster zegt waar hij heen bewaart"


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
    r = client.post("/leren/vak", data={"kaarten": str(kid), "vak": "KartR", "terug": "/artikelen/DE/147?bewaard=1&vak=ZR%20Ia&kaarten=1"},
                    follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/artikelen/DE/147"
    with database.session() as s:
        k = s.get(Kaart, kid)
        assert k.lijst.vak == "KartR" and s.get(Profiel, 1).laatste_vak == "KartR"
        assert k.lijst_id == min(s.scalars(select(Leerlijst.id).where(Leerlijst.vak == "KartR", Leerlijst.profiel_id == 1, ~Leerlijst.naam.startswith("Notities"))))  # de oudste lijst van het vak
    assert client.post("/leren/vak", data={"kaarten": "999999", "vak": "KartR"}).status_code == 400


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
        vakken.onthoud(s, 1, "EuGesR")  # een HvJ-arrest geeft zelf geen vak: het laatst gebruikte geldt
        s.flush()
        oid = o.id
    html = client.get(f"/opzoeken/{oid}").text
    assert '<option selected>EuGesR</option>' in html
    client.post(f"/opzoeken/{oid}/bewaren", data={"vak": "", "regel": "Vestigingsvrijheid staat er niet aan in de weg."})
    with database.session() as s:
        o = s.get(Opzoeking, oid)
        assert o.kaart.lijst.vak == "EuGesR" and o.kaart.soort == "arrest"
    html = client.get(f"/opzoeken/{oid}").text
    assert "★ Bewaard · EuGesR" in html and 'action="/leren/vak"' in html


def test_laatste_vak_niet_over_de_grens_eu_nationaal():
    """Na het venster is het laatste vak alleen nog een voorstel, en dan geldt de grens tussen EU en nationaal."""
    _keuze("KartR", uren_geleden=3)
    with database.session() as s:
        assert vakken.kies(s, 1, "", "DE", "BGB", "433") == "KartR"  # kartelrecht is ook nationaal: geen grens
        assert vakken.kies(s, 1, "", "EU", "Verordening 1/2003", "4") == "KartR"
    _keuze("Sachenrecht", uren_geleden=3)
    with database.session() as s:
        assert vakken.kies(s, 1, "", "EU", "AEUV", "102") == "KartR"  # afgeleid
        assert vakken.kies(s, 1, "", "EU", "VO", "12") is None
        assert vakken.kies(s, 1, "", "NL", "BW", "3:84") == "Sachenrecht"  # vergelijken mag


def test_lopende_keuze_kent_geen_grens():
    _keuze("Sachenrecht")
    with database.session() as s:
        assert vakken.kies(s, 1, "", "EU", "AEUV", "102") == "Sachenrecht"
