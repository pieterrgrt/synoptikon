"""Rechten: een lezer houdt zijn eigen spullen bij (main._LEZER_POST), gedeelde inhoud blijft voor een redacteur."""
import pytest

from synoptikon import db as database
from synoptikon.auth import hash_password
from synoptikon.models import Bron, Casus, CasusPoging, Markering, Opzoeking, Profiel
from tests.test_markeringen import artikel823  # noqa: F401 (fixture)

VELDEN = ("gebruikersnaam", "naam", "rol", "actief", "wachtwoord_hash", "stelsels", "sessie_versie")
PLEK = 5


@pytest.fixture
def lezer(anoniem):
    """Profielplek 5 tijdelijk als lezer, ingelogd; daarna terug zoals ze was (andere tests rekenen daarop)."""
    with database.session() as s:
        p = s.get(Profiel, PLEK)
        oud = {v: getattr(p, v) for v in VELDEN}
        p.gebruikersnaam, p.naam, p.rol, p.actief, p.wachtwoord_hash, p.stelsels = \
            "lezer-rechten", "Lezer", "lezer", True, hash_password("lees-maar"), "NL,DE"
    anoniem.post("/login", data={"gebruikersnaam": "lezer-rechten", "wachtwoord": "lees-maar", "volgende": "/"})
    try:
        yield anoniem
    finally:
        with database.session() as s:
            p = s.get(Profiel, PLEK)
            for v in VELDEN:
                setattr(p, v, oud[v])


def test_lezer_markeert(lezer, artikel823):
    r = lezer.post("/markeringen", data=dict(quote="widerrechtlich verletzt", stelsel="DE", wet="MARKG", nummer="823"))
    assert r.status_code == 200
    mid = r.json()["id"]
    assert lezer.post(f"/markeringen/{mid}", data={"soort": "voorwaarde"}).status_code == 200
    with database.session() as s:
        assert s.get(Markering, mid).profiel_id == PLEK
    assert lezer.post(f"/markeringen/{mid}/verwijder").status_code == 200


def test_lezer_oefent_in_de_klausurtrainer(lezer):
    with database.session() as s:
        cid = s.query(Casus).filter_by(sleutel="vertippter-preis").one().id
    html = lezer.get(f"/klausur/{cid}").text
    assert "Beginnen" in html and "Casus bewerken" not in html
    r = lezer.post(f"/klausur/{cid}/start", data={"modus": "oefenen"}, follow_redirects=False)
    assert r.status_code == 303
    pad = r.headers["location"]
    assert lezer.post(f"{pad}/bewaar", data={"skizze": "A. § 433 BGB", "uitwerking": "K könnte …"}, follow_redirects=False).status_code == 303
    assert lezer.post(f"{pad}/inleveren", follow_redirects=False).status_code == 303
    pid = int(pad.rsplit("/", 1)[1])
    with database.session() as s:
        p = s.get(CasusPoging, pid)
        assert p.profiel_id == PLEK and not p.open
    # een eigen casus mag hij maken en bewerken
    r = lezer.post("/klausur/nieuw", data={"sachverhalt": "A verkauft B ein Fahrrad.", "titel": "Eigen"}, follow_redirects=False)
    assert r.status_code == 303
    eigen = r.headers["location"]
    assert lezer.post(f"{eigen}/bewerk", data={"titel": "Eigen 2", "sachverhalt": "A verkauft B ein Rad."}, follow_redirects=False).status_code == 303
    # een voorbeeldcasus is gedeelde inhoud
    assert lezer.post(f"/klausur/{cid}/bewerk", data={"titel": "Weg"}).status_code == 404
    assert lezer.post(f"/klausur/{cid}/muster").status_code == 403
    assert lezer.post(f"{pad}/verwijder", follow_redirects=False).status_code == 303
    lezer.post(f"{eigen}/verwijder")


def test_lezer_verbetert_zijn_opzoeking_maar_niet_de_bron(lezer):
    with database.session() as s:
        b = Bron(stelsel_code="NL", soort="rechtspraak", citeertitel="HR rechten-test", taal="nl", vindplaats="NJ 1999/rechten")
        s.add(b)
        s.flush()
        o = Opzoeking(profiel_id=PLEK, invoer="rechten-test", status="klaar", bron_id=b.id,
                      resultaat=dict(soort="uitspraak", stelsel="NL", citeer="HR rechten-test", vindplaats="NJ 1999/rechten", bron="claude"))
        s.add(o)
        s.flush()
        oid, bid = o.id, b.id
    assert "Kloppend maken" in lezer.get(f"/opzoeken/{oid}").text
    r = lezer.post(f"/opzoeken/{oid}/corrigeer", data=dict(citeer="Overschreven", titel="", vindplaats="NJ 1999/rechten", url="",
                                                          plaats="", toelichting="", stelsel="NL"), follow_redirects=False)
    assert r.status_code == 303
    with database.session() as s:
        assert s.get(Opzoeking, oid).resultaat["citeer"] == "Overschreven"
        assert s.get(Bron, bid).citeertitel == "HR rechten-test"
    assert lezer.post(f"/opzoeken/{oid}/verwijder", follow_redirects=False).status_code == 303


def test_lezer_wijzigt_geen_gedeelde_inhoud(lezer):
    for pad in ("/vragen/nieuw", "/bronnen/nieuw", "/begrippen/nieuw", "/invoer/notitie", "/stelsels", "/vertalingen"):
        assert lezer.post(pad, data={}).status_code == 403, pad
    html = lezer.get("/klausur").text
    assert "alleen-lezen" in html and 'href="/klausur/nieuw"' in html
