"""Mijn stelsels per profiel, de indeling per regio en 'meer stelsels…' bij veel stelsels."""
import pytest


def test_regios_dekken_de_wereld():
    from synoptikon.seed.regios import REGIO, REGIOS, regio

    assert len([c for c in REGIO if len(c) == 2]) >= 249
    assert set(REGIO.values()) <= set(REGIOS)
    assert regio("NL") == "europa_west" and regio("QC") == "noord_amerika" and regio("SC") == "europa_west"
    assert regio("EU") == "supranationaal" and regio("JP") == "azie_oost" and regio("BR") == "latijns_amerika"
    assert regio("US-LA") == "noord_amerika" and regio("XX") == "overig"


def test_profiel_kiest_stelsels(client):
    r = client.get("/profiel")
    assert r.status_code == 200 and "data-stelselkiezer" in r.text
    r = client.post("/profiel/stelsels", data={"stelsel": ["NL", "DE"]}, follow_redirects=False)
    assert r.status_code == 303
    r = client.get("/profiel")
    assert 'value="NL" checked' in r.text and 'value="FR" checked' not in r.text
    assert client.get("/welkom").status_code == 200
    _herstel(client)


def _herstel(client):
    """Terug naar alle actieve stelsels, zodat de andere tests niets merken."""
    from synoptikon import db as database
    from synoptikon.models import Profiel

    with database.session() as s:
        s.get(Profiel, 1).stelsels = None
