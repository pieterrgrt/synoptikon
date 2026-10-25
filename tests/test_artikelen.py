from pathlib import Path

from sqlalchemy import select

from synoptikon import db as database
from synoptikon.importers import bwb, store
from synoptikon.models import Correspondentie, Systematiek
from synoptikon.seed import seed
from synoptikon.services.artikelen import Plaatser, herken, lees, parse_bereik, plaatser, sleutel
from synoptikon.services.systematiek import bouw_uit_wettekst

FIX = Path(__file__).parent / "fixtures"


def test_herkennen_van_verwijzingen():
    def een(t, stelsel=None):
        (r,) = herken(t, stelsel)
        return r.stelsel, r.nummer, r.wet, r.tot, r.detail

    assert een("3:84") == ("NL", "3:84", None, None, None)
    assert een("art. 3:44 lid 4 BW") == ("NL", "3:44", None, None, "lid 4")
    assert een("§ 812 Abs. 1 S. 1 BGB") == ("DE", "812", None, None, "Abs. 1 S. 1")
    assert een("art. 1112-1 C. civ.") == ("FR", "1112-1", None, None, None)
    assert een("art. L217-3 C. consom.") == ("FR", "L217-3", "C. consom.", None, None)
    assert een("§ 1 ProdHaftG") == ("DE", "1", "ProdHaftG", None, None)
    assert een("art. 1132–1136") == ("FR", "1132", None, "1136", None)
    assert een("7A:1655") == ("NL", "7A:1655", None, None, None)
    assert {r.stelsel for r in herken("929")} == {"DE", "FR"}  # kaal nummer: dubbelzinnig
    assert herken("culpa in contrahendo") == [] and herken("ECLI:NL:HR:2005:AT7337") == []
    assert lees("FR", "—").nummer is None
    assert lees("NL", "3:84").citeer == "art. 3:84 BW" and lees("DE", "§§ 203–213").citeer == "§§ 203–213 BGB"


def test_sleutels_en_bereiken():
    assert sleutel("NL", "6:230a") > sleutel("NL", "6:230")
    assert sleutel("DE", "312k") > sleutel("DE", "312")
    assert sleutel("FR", "1231-7") > sleutel("FR", "1231") > sleutel("FR", "1112-2")
    lo, hi = parse_bereik("FR", "art. 1101–1231-7")
    assert lo <= sleutel("FR", "1196") <= hi
    assert parse_bereik("NL", "art. 6:212") == (("6", 212, ""), ("6", 212, ""))


def test_plaatsen_in_de_systematiek():
    with database.session() as s:
        assert [k.code for k in plaatser(s, "NL").pad("3:84")] == ["BW-3", "BW-3-4", "BW-3-4-2"]
        assert plaatser(s, "DE").pad("929")[-1].code == "BGB-3-3-3-1"
        assert plaatser(s, "DE").pad("812")[-1].code == "BGB-2-8-26"
        assert plaatser(s, "FR").pad("1112-1")[-1].code == "CC-III-III-I-2-1-1"
        assert plaatser(s, "FR").pad("2276")[-1].code == "CC-III-XXI-II-3"
        # Boekknopen zonder bereik bevatten elk artikel van hun boek.
        assert [k.code for k in plaatser(s, "NL").pad("8:1")] == ["BW-8"]
        assert plaatser(s, "NL").pad("onzin") == []


def test_plaatser_leidt_bereik_af_van_kinderen():
    class K:
        def __init__(self, id, parent_id, code, bereik):
            self.id, self.parent_id, self.code, self.bereik, self.label = id, parent_id, code, bereik, code

    p = Plaatser("DE", [K(1, None, "X", None), K(2, 1, "X-1", "§§ 1–10"), K(3, 1, "X-2", "§§ 11–20")])
    assert [k.code for k in p.pad("15")] == ["X", "X-2"]
    assert p.pad("25") == []


def test_artikelpagina_toont_corresponderende_artikelen(client):
    r = client.get("/artikelen/NL/3:84")
    assert r.status_code == 200
    html = r.text
    # plaats in de eigen systematiek
    assert "Titel 4 · Verkrijging en verlies van goederen" in html and "Afdeling 2" in html
    # corresponderende artikelen, elk met hun plaats in hun eigen systematiek
    assert "§ 929 BGB" in html and "Untertitel 1 · Übertragung" in html
    assert "art. 1196 C. civ." in html and "Sous-section 2 · Effet translatif" in html
    # tekst uit de bron, concordantie
    assert "Voor overdracht van een goed" in html and "art. 639 BW (oud)" in html


def test_artikel_opzoeken(client):
    r = client.get("/artikelen", params={"q": "art. 3:84 BW"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/artikelen/NL/3:84"
    r = client.get("/artikelen", params={"q": "929"})
    assert "/artikelen/DE/929" in r.text and "/artikelen/FR/929" in r.text
    assert "Artikel:" in client.get("/zoeken", params={"q": "§ 823"}).text
    assert "art. 6:162 BW" in client.get("/artikelen/DE/823").text
    # niet-hoofdwet
    assert "art. 6:185 BW" in client.get("/artikelen/DE/1", params={"wet": "ProdHaftG"}).text


def test_correspondentietabel_en_knoop(client):
    html = client.get("/artikelen").text
    assert "Correspondentietabel" in html and "Onrechtmatige daad: algemene grondslag" in html
    with database.session() as s:
        kid = s.scalar(select(Systematiek.id).where(Systematiek.code == "BW-3-4-2"))
    html = client.get(f"/stelsels/NL/knoop/{kid}").text
    # Afdeling 2 valt in DE uiteen over Sachenrecht én Schuldrecht.
    assert "Buch 3 · Sachenrecht" in html and "Buch 2 · Recht der Schuldverhältnisse" in html
    html = client.get("/stelsels/NL", params={"artikel": "3:84"}).text
    assert "bevat-markering" in html and f"/stelsels/NL/knoop/{kid}" in html


def test_thema_aanmaken_en_bewerken(client):
    r = client.post("/artikelen/thema", data={"titel": "Testthema", "rechtsgebied": "Test", "stelsel_code": "NL", "verwijzing": "6:162"}, follow_redirects=False)
    url = r.headers["location"]
    cid = int(url.rsplit("/", 1)[-1])
    client.post(f"/artikelen/thema/{cid}/artikel", data={"stelsel_code": "DE", "verwijzing": "§ 826", "rol": "deels"})
    client.post("/artikelen/koppel", data={"thema_id": cid, "stelsel_code": "FR", "verwijzing": "art. 1240", "terug": "/artikelen/FR/1240"})
    html = client.get(url).text
    assert "art. 6:162 BW" in html and "§ 826 BGB" in html and "art. 1240 C. civ." in html
    assert "Testthema" in client.get("/artikelen/DE/826").text
    assert client.post(f"/artikelen/thema/{cid}/artikel", data={"stelsel_code": "NL", "verwijzing": "geen nummer"}).status_code == 400
    client.post(f"/artikelen/thema/{cid}/verwijderen")
    assert client.get(url).status_code == 404


def test_seed_is_herhaalbaar_en_hernoemt():
    with database.session() as s:
        n = len(s.scalars(select(Correspondentie)).all())
        # Simuleer een oude database: de sectie met de oude code.
        k = s.scalar(select(Systematiek).where(Systematiek.code == "CC-III-XXI-II-3"))
        k.code = "CC-III-XXI-III-3"
    with database.session() as s:
        seed(s)
        assert len(s.scalars(select(Correspondentie)).all()) == n
        k = s.scalar(select(Systematiek).where(Systematiek.code == "CC-III-XXI-II-3"))
        assert k is not None and k.parent.code == "CC-III-XXI-II" and k.bronnen
        assert s.scalar(select(Systematiek).where(Systematiek.code == "CC-III-XXI-III-3")) is None


def test_systematiek_uit_wettekst():
    g = bwb.parse((FIX / "bwb_boek3.xml").read_bytes(), "BWBR0005291")
    g.artikelen[0].pad = g.artikelen[0].pad.replace("Afdeling 2 Overdracht", "Afdeling 2 Overdracht › Paragraaf 1 Proef")
    with database.session() as s:
        voor = {k.id: (k.bereik, k.volgorde) for k in s.scalars(select(Systematiek).where(Systematiek.stelsel_code == "NL"))}
        w = store.sla_op(s, "NL", g)
        r = bouw_uit_wettekst(s, w)
        assert r.nieuw == 1  # alleen de paragraaf; Boek 3, Titel 4 en Afdeling 2 bestonden al
        k = s.scalar(select(Systematiek).where(Systematiek.code == "BW-3-4-2-1"))
        assert k.label == "Paragraaf 1 · Proef" and k.bereik == "art. 3:84"
        assert s.scalar(select(Systematiek).where(Systematiek.code == "BW-3-4-2")).bereik == "art. 3:84–3:90"
        assert plaatser(s, "NL").pad("3:84")[-1].code == "BW-3-4-2-1"
        # Opruimen voor de andere tests.
        s.delete(k)
        s.delete(w)
        for knoop in s.scalars(select(Systematiek).where(Systematiek.id.in_(voor))):
            knoop.bereik, knoop.volgorde = voor[knoop.id]
