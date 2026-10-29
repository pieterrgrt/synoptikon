"""`synoptikon bijwerken`, de beleefde HTTP-client en het logboek op /wetteksten. Geen netwerk."""
import httpx
import pytest
from sqlalchemy import delete, select

from synoptikon import db as database
from synoptikon.importers import Artikel, Geparseerd, bijwerken, bwb, http, legi, ruimte, store
from synoptikon.models import Bijwerking, Wettekst


def _g(wet_id="TEST-1", versie="2026-01-01", tekst="Oude tekst."):
    return Geparseerd(wet_id=wet_id, titel="Testwet", versie=versie, bron_url=None,
                      artikelen=[Artikel("1", tekst, "Eerste"), Artikel("2", "Tweede artikel.")])


@pytest.fixture
def schoon():
    yield
    with database.session() as s:
        s.execute(delete(Wettekst).where(Wettekst.wet_id.like("TEST-%")))
        s.execute(delete(Bijwerking))
        s.commit()


def test_deel_is_vast_en_dekt_alles():
    sleutels = [f"DE:wet{i}" for i in range(700)]
    delen = [bijwerken.deel_van(k, 7) for k in sleutels]
    assert delen == [bijwerken.deel_van(k, 7) for k in sleutels]
    assert set(delen) == set(range(1, 8))
    assert all(60 < delen.count(d) < 140 for d in range(1, 8))  # ongeveer gelijk verdeeld
    assert bijwerken.lees_deel("3/7") == (3, 7)
    assert bijwerken.lees_deel(None) is None
    with pytest.raises(ValueError):
        bijwerken.lees_deel("8/7")


def test_vergelijk_slaat_alleen_echte_wijzigingen_op(schoon):
    with database.session() as s:
        uit, w = bijwerken.vergelijk(s, "DE", _g(), None, None, kern=False, historie=False)
        s.commit()
        assert uit == "nieuw" and w.hash and w.aantal == 2
        eerste = w.id
        # Zelfde artikelen, andere versie: niets opslaan, alleen gecontroleerd.
        uit, w = bijwerken.vergelijk(s, "DE", _g(versie="2026-02-01"), None, w, kern=False, historie=False)
        assert uit == "ongewijzigd" and w.versie == "2026-01-01" and w.gecontroleerd
        # Bulk: in place.
        uit, w = bijwerken.vergelijk(s, "DE", _g(versie="2026-03-01", tekst="Nieuwe tekst."), None, w, kern=False, historie=False)
        s.commit()
        assert uit == "gewijzigd" and w.id == eerste and w.versie == "2026-03-01"
        # Register: een nieuwe stand wordt een nieuwe rij, de oude blijft.
        uit, w2 = bijwerken.vergelijk(s, "DE", _g(versie="2026-04-01", tekst="Nog nieuwer."), None, w, kern=False, historie=True)
        s.commit()
        assert uit == "gewijzigd" and w2.id != eerste
        assert len(s.scalars(select(Wettekst).where(Wettekst.wet_id == "TEST-1")).all()) == 2


def test_ronde_met_deel_limiet_en_logboek(schoon, monkeypatch):
    gehaald = []

    def bron(r):
        for i in range(30):
            wid = f"TEST-{i}"
            yield bijwerken.Taak(sleutel=f"DE:{wid}", stelsel="DE", wet_id=wid,
                                 ophalen=lambda wid=wid: (gehaald.append(wid), _g(wet_id=wid))[1])

    monkeypatch.setitem(bijwerken.BRON_TAKEN, "de", bron)
    monkeypatch.setattr(ruimte, "controleer", lambda: None)
    r = bijwerken.Ronde(database.session_factory(), bronnen=["de"], deel=(2, 3), melder=lambda t: None)
    t = r.draai()[0]
    verwacht = [f"TEST-{i}" for i in range(30) if bijwerken.deel_van(f"DE:TEST-{i}", 3) == 2]
    assert gehaald == verwacht and t.nieuw == len(verwacht) and t.fouten == 0
    # Tweede keer: niets veranderd.
    t = bijwerken.Ronde(database.session_factory(), bronnen=["de"], deel=(2, 3), melder=lambda t: None).draai()[0]
    assert t.nieuw == t.gewijzigd == 0 and t.gecontroleerd == len(verwacht)
    # Droog: niets ophalen.
    gehaald.clear()
    bijwerken.Ronde(database.session_factory(), bronnen=["de"], droog=True, melder=lambda t: None).draai()
    assert gehaald == []
    with database.session() as s:
        log = s.scalars(select(Bijwerking).order_by(Bijwerking.id)).all()
    assert [(b.bron, b.stelsel, b.nieuw) for b in log] == [("de", "DE", len(verwacht)), ("de", "DE", 0)]


def test_ronde_stopt_netjes_en_telt_fouten(schoon, monkeypatch):
    def bron(r):
        yield bijwerken.Taak(sleutel="x", stelsel="DE", wet_id="TEST-fout", ophalen=lambda: 1 / 0)
        yield bijwerken.Taak(sleutel="y", stelsel="DE", wet_id="TEST-goed", ophalen=lambda: _g(wet_id="TEST-goed"))

    monkeypatch.setitem(bijwerken.BRON_TAKEN, "de", bron)
    monkeypatch.setattr(ruimte, "controleer", lambda: None)
    t = bijwerken.Ronde(database.session_factory(), bronnen=["de"], melder=lambda t: None).draai()[0]
    assert (t.fouten, t.nieuw) == (1, 1) and "ZeroDivisionError" in t.meldingen[0]

    def vol():
        raise ruimte.Stop("te weinig schijfruimte")

    monkeypatch.setattr(ruimte, "controleer", vol)
    r = bijwerken.Ronde(database.session_factory(), bronnen=["de"], melder=lambda t: None)
    assert r.draai() == [] and "schijfruimte" in r.gestopt


def test_http_conditioneel_en_retry(monkeypatch, tmp_path):
    monkeypatch.setenv("SYNOPTIKON_HTTP_TUSSENTIJD", "0")
    monkeypatch.setattr(http.time, "sleep", lambda s: None)
    monkeypatch.setattr(http, "_cache", {})
    verzoeken = []

    def antwoord(req):
        verzoeken.append(req)
        if len(verzoeken) == 1:
            return httpx.Response(503, headers={"Retry-After": "1"})
        if req.headers.get("If-None-Match") == '"v1"':
            return httpx.Response(304)
        return httpx.Response(200, headers={"ETag": '"v1"'}, content=b"tekst")

    c = http.client(transport=httpx.MockTransport(antwoord))
    with http.conditioneel() as cond:
        assert c.get("https://voorbeeld.test/wet").content == b"tekst"
    assert len(verzoeken) == 2  # 503, dan opnieuw
    with http.conditioneel():
        assert c.get("https://voorbeeld.test/wet").status_code == 200
    assert "If-None-Match" not in verzoeken[-1].headers  # niet bevestigd = niet onthouden
    http.bevestig(cond)
    with http.conditioneel(), pytest.raises(http.Ongewijzigd):
        c.get("https://voorbeeld.test/wet")
    assert c.get("https://voorbeeld.test/wet").status_code == 200  # buiten conditioneel(): gewoon ophalen


SRU = b"""<?xml version="1.0"?>
<sru:searchRetrieveResponse xmlns:sru="http://docs.oasis-open.org/ns/search-ws/sruResponse"
  xmlns:dcterms="http://purl.org/dc/terms/" xmlns:overheidbwb="http://standaarden.overheid.nl/bwb/terms/">
 <sru:records><sru:record><sru:recordData><gzd><originalData><overheidbwb:meta>
  <dcterms:identifier>BWBR0005537</dcterms:identifier><dcterms:title>Algemene wet bestuursrecht</dcterms:title>
  <dcterms:type>wet</dcterms:type></overheidbwb:meta></originalData><enrichedData>
  <overheidbwb:geldigheidsperiode_startdatum>2026-07-01</overheidbwb:geldigheidsperiode_startdatum>
  <overheidbwb:locatie_toestand>https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/x.xml</overheidbwb:locatie_toestand>
 </enrichedData></gzd></sru:recordData></sru:record></sru:records>
 <sru:nextRecordPosition>501</sru:nextRecordPosition>
</sru:searchRetrieveResponse>"""


def test_bwb_sru_lijst():
    regelingen, volgende = bwb.parse_sru(SRU)
    assert volgende == 501
    assert regelingen == [bwb.Regeling("BWBR0005537", "Algemene wet bestuursrecht", "wet", "2026-07-01",
                                       "https://repository.officiele-overheidspublicaties.nl/bwb/BWBR0005537/x.xml")]


def test_legi_afkorting():
    assert legi.afkorting("Code du travail") == "C. trav."
    assert legi.afkorting("Code minier ") == "Code minier"


def test_store_hash_volgt_inhoud():
    a = store.inhoud_hash(_g().artikelen)
    assert a == store.inhoud_hash(_g(versie="anders").artikelen)
    assert a != store.inhoud_hash(_g(tekst="Anders.").artikelen)


def test_wetteksten_toont_bijhouden(client, schoon):
    with database.session() as s:
        bijwerken.vergelijk(s, "DE", _g(), None, None, kern=False, historie=False)
        s.add(Bijwerking(bron="de", stelsel="DE", gecontroleerd=5, gewijzigd=1, fouten=2, melding="wetX: HTTPError: 500"))
        s.commit()
    r = client.get("/wetteksten")
    assert r.status_code == 200
    assert 'id="bijhouden"' in r.text and "wetX: HTTPError: 500" in r.text
