"""Talen: interface volledig vertaald, taalkeuze, vertaalgeheugen voor eigen inhoud."""
import re

import pytest

from synoptikon import i18n
from synoptikon.i18n_teksten import alle, ontbrekend


@pytest.mark.parametrize("taal", ["fr", "de", "it", "en", "es"])
def test_catalogus_volledig(taal):
    assert ontbrekend(taal) == []
    cat = i18n.catalogus(taal)
    for nl in alle():
        # dezelfde {plaatshouders}, anders gaat format() mis
        assert set(re.findall(r"\{\w+\}", nl)) == set(re.findall(r"\{\w+\}", cat[nl])), nl


def test_accept_language():
    assert i18n.kies_taal("de-CH,de;q=0.9,en;q=0.8") == "de"
    assert i18n.kies_taal("pt-BR,pt;q=0.9,es;q=0.5") == "es"
    assert i18n.kies_taal("") == "nl"


def test_pagina_s_in_alle_talen(client):
    for taal, woord in [("fr", "Questions"), ("de", "Fragen"), ("it", "Domande"), ("en", "Questions"), ("es", "Preguntas")]:
        client.post("/taal", data={"taal": taal, "terug": "/"})
        html = client.get("/").text
        assert f'lang="{taal}"' in html and woord in html
        for pad in ["/stelsels", "/begrippen", "/artikelen", "/eu", "/bronnen", "/zoeken?q=levering", "/vertalingen", "/profiel"]:
            assert client.get(pad).status_code == 200, (taal, pad)
    client.post("/taal", data={"taal": "nl", "terug": "/"})


def test_inhoud_vertalen(client):
    from synoptikon import db as database
    from synoptikon.models import Vraag
    from synoptikon.services import vertalen

    with database.session() as s:
        v = s.query(Vraag).first()
        titel = v.titel
        vertalen.zet(s, "fr", titel, "Comment la propriété se transfère-t-elle ?", "claude")
        slug = v.slug
    client.post("/taal", data={"taal": "fr", "terug": "/"})
    assert "Comment la propriété se transfère-t-elle ?" in client.get(f"/vragen/{slug}").text
    # origineel tonen
    client.post("/taal/inhoud", data={"origineel": "1", "terug": "/"})
    assert titel in client.get(f"/vragen/{slug}").text
    client.post("/taal/inhoud", data={"origineel": "0", "terug": "/"})
    client.post("/taal", data={"taal": "nl", "terug": "/"})
    assert titel in client.get(f"/vragen/{slug}").text


def test_wet_lezen(client):
    from synoptikon import db as database
    from synoptikon.models import Wettekst, WettekstArtikel

    with database.session() as s:
        w = Wettekst(stelsel_code="FR", wet_id="LEGITEXT000006070721", titel="Code civil", versie="2026-01-01")
        s.add(w)
        s.flush()
        for i, (nr, pad) in enumerate([("1240", "Livre III › Titre III › Chapitre Ier"), ("1241", "Livre III › Titre III › Chapitre Ier"),
                                       ("1242", "Livre III › Titre III › Chapitre II")]):
            s.add(WettekstArtikel(wettekst_id=w.id, nummer=nr, tekst=f"Tekst {nr}", pad=pad, volgorde=i))
        wid = w.id
    r = client.get("/stelsels")
    assert f"/stelsels/FR/wet/{wid}" in r.text
    # Een wet openen gaat naar haar plek in de systematiek.
    r = client.get(f"/stelsels/FR?wet={wid}", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith("/stelsels/FR#knoop-")
    r = client.get(f"/stelsels/FR/wet/{wid}")
    assert r.status_code == 200 and "Livre III" in r.text
    r = client.get(f"/stelsels/FR/wet/{wid}?deel=Livre III › Titre III › Chapitre Ier")
    assert "Tekst 1240" in r.text and "Tekst 1241" in r.text and "Tekst 1242" not in r.text
    assert 'rel="next"' in r.text
    r = client.get(f"/stelsels/FR/wet/{wid}?artikel=1242", follow_redirects=False)
    assert r.status_code == 303 and "Chapitre%20II" in r.headers["location"]
    r = client.get("/artikelen/FR/1241")
    assert "in de wettekst lezen" in r.text and "1240" in r.text and "1242" in r.text
