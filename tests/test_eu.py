"""Unierecht: catalogus, werking per soort, omzetting en de koppeling met nationale artikelen."""
from datetime import date

from synoptikon import db as database
from synoptikon.models import EuHandeling, EuNim, Omzetting
from synoptikon.services.artikelen import Ref, lees, sleutel
from synoptikon.services.eu import omzettingen_voor_artikel
from synoptikon.services.eu_logica import status


def test_seed_legt_omzettingen_en_roepnamen_vast():
    with database.session() as s:
        h = s.get(EuHandeling, "32019L0771")
        assert h.roepnaam == "Richtlijn verkoop van goederen"
        nl = [o for o in h.omzettingen if o.stelsel_code == "NL"]
        assert {(o.nummer, o.tot) for o in nl} >= {("7:5", "7:25"), ("7:18a", None)}
        assert all(not o.geverifieerd for o in h.omzettingen)


def test_artikel_vindt_zijn_richtlijn_via_bereik():
    with database.session() as s:
        celexen = {o.celex for o in omzettingen_voor_artikel(s, Ref("NL", "7:18a"))}
        assert "32019L0771" in celexen
        assert {o.celex for o in omzettingen_voor_artikel(s, Ref("DE", "307"))} == {"31993L0013"}
        assert omzettingen_voor_artikel(s, Ref("DE", "929")) == []


def test_werking_richtlijn_en_status():
    h = EuHandeling(celex="32019L0771", soort="richtlijn", variant="basis", titel="x", omzettingstermijn=date(2021, 7, 1))
    st = status(h, {"NL": 1}, {"NL": 2}, vandaag=date(2026, 1, 1))
    assert st.termijn_verstreken is True
    assert any("Faccini Dori" in (r.bron or "") for r in st.werking)
    assert st.harmonisatie[0] == "maximum"
    assert st.per_stelsel["NL"].startswith("1 omzettingsmaatregel gemeld")
    assert "verstreken" in st.per_stelsel["FR"]
    assert "Brexit" in st.per_stelsel["EN"]  # termijn na 31-12-2020 en geen Britse maatregel
    assert "geen lidstaat" in st.per_stelsel["CH"]


def test_werking_verordening_kent_geen_omzetting():
    h = EuHandeling(celex="32016R0679", soort="verordening", variant="basis", titel="x", in_werking=date(2016, 5, 24))
    st = status(h, {"DE": 3}, {}, vandaag=date(2026, 1, 1))
    assert st.termijn_verstreken is None
    assert any("Variola" in (r.bron or "") for r in st.werking)
    assert st.per_stelsel["DE"] == "rechtstreeks toepasselijk; 3 uitvoeringsmaatregelen gemeld"
    assert "assimilated law" in st.per_stelsel["EN"]


def test_italiaanse_rangtelwoorden():
    assert lees("IT", "art. 135-vicies-ter c. cons.").nummer == "135-vicies-ter"
    volgorde = sorted(["135-vicies-ter", "135-vicies", "135-bis", "135-duodevicies", "135"], key=lambda n: sleutel("IT", n))
    assert volgorde == ["135", "135-bis", "135-duodevicies", "135-vicies", "135-vicies-ter"]


def test_eu_paginas(client):
    with database.session() as s:
        s.add(EuNim(celex="32019L0771", land="NLD", nim_id="72019L0771NLD_1", titel="Implementatiewet Richtlijn verkoop van goederen", soort_akte="Wet"))
    r = client.get("/eu/32019L0771")
    assert r.status_code == 200
    assert "Richtlijn verkoop van goederen" in r.text and "Faccini Dori" in r.text
    assert "art. 7:18a BW" in r.text and "Implementatiewet Richtlijn verkoop van goederen" in r.text
    assert "niet geverifieerd" in r.text
    r = client.get("/eu?q=verkoop")
    assert r.status_code == 200 and "/eu/32019L0771" in r.text
    r = client.get("/eu/omzetting")
    assert r.status_code == 200 and "Uitvoeringswet Algemene verordening gegevensbescherming" in r.text
    assert client.get("/eu/32099R9999").status_code == 404


def test_artikelpagina_toont_europese_herkomst(client):
    r = client.get("/artikelen/NL/7:18a")
    assert r.status_code == 200
    assert "Europese herkomst" in r.text and "/eu/32019L0771" in r.text


def test_koppeling_toevoegen_en_verifieren(client):
    r = client.post("/eu/32019L0771/omzetting", data={"stelsel_code": "DE", "verwijzing": "§ 477 BGB", "eu_artikel": "11", "soort": "omzetting"},
                    follow_redirects=False)
    assert r.status_code == 303
    with database.session() as s:
        o = s.query(Omzetting).filter_by(celex="32019L0771", stelsel_code="DE", nummer="477").one()
        assert o.geverifieerd and o.eu_artikel == "11"
        oid = o.id
    client.post(f"/eu/32019L0771/omzetting/{oid}/geverifieerd")
    with database.session() as s:
        assert s.get(Omzetting, oid).geverifieerd is False
    assert client.post("/eu/32019L0771/omzetting", data={"stelsel_code": "DE", "verwijzing": "", "wet_titel": ""}).status_code == 400
