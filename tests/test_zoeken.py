"""Full-text in de wetteksten: exacte afkortingen, relevantie, voorkeur en de beperking tot stelsels."""
import pytest
from sqlalchemy import select

from synoptikon import db as database
from synoptikon.models import Wettekst, WettekstArtikel
from synoptikon.services import opzoeken, wetboek, zoeken

# Verzonnen wetten (geen kern), met woorden die nergens anders voorkomen.
_WETTEN = [
    ("DE", "ztg", "ZTG", "Zoektestgesetz", [
        ("1", None, "Die Würde ist unantastbar."),
        ("2", None, "Zoekproefwoord in Deutschland."),
        ("3", "Zoekkopwoord", "Was hier geregelt ist."),
        ("4", None, "Ein langer Satz, in dem das Zoekkopwoord nur nebenbei und ganz am Rande vorkommt, mitten im Text."),
        ("7", None, "Nach Art. 1 ZTG gilt Folgendes."),
    ]),
    ("EU", "39999R0001", "Verordening 9999/1", "Zoektestverordening", [
        ("1", None, "Art der Genehmigung: ZTGED 1."),
    ]),
    ("NL", "ztw", "ZTW", "Zoektestwet", [("1", None, "Zoekproefwoord in Nederland.")]),
    ("FR", "ztc", "ZTC", "Code de recherche", [("1", None, "Zoekproefwoord en France.")]),
]


@pytest.fixture(scope="module", autouse=True)
def wetten():
    with database.session() as s:
        if s.scalar(select(Wettekst).where(Wettekst.wet == "ZTG")):
            return
        for stelsel, wid, afk, titel, artikelen in _WETTEN:
            w = Wettekst(stelsel_code=stelsel, wet_id=wid, wet=afk, kern=False, versie="2026-10-01", titel=titel)
            s.add(w)
            s.flush()
            for i, (nr, kop, tekst) in enumerate(artikelen):
                s.add(WettekstArtikel(wettekst_id=w.id, nummer=nr, opschrift=kop, tekst=tekst, volgorde=i))


def _gevonden(q, **kw):
    with database.session() as s:
        return [(wa.wettekst.stelsel_code, wa.wettekst.wet, wa.nummer) for wa, _f in zoeken.wetsartikelen(s, q, **kw)]


def test_fts_query_afkortingen_en_getallen_precies():
    assert zoeken.fts_query("Art. 1 GG") == '"Art." "1" "GG"'
    assert zoeken.fts_query("lever") == '"lever"*'
    assert zoeken.fts_query("Art. 1 GG", nabij=True) == 'NEAR("Art." "1" "GG", 6)'
    assert zoeken.fts_query("§") == ""


def test_afkorting_is_geen_prefix():
    """"Art. 1 ZTG" vindt het artikel dat ernaar verwijst, niet "Art der Genehmigung: ZTGED 1"."""
    assert _gevonden("Art. 1 ZTG") == [("DE", "ZTG", "7")]


def test_opschrift_telt_zwaarder():
    assert [nr for _s, _w, nr in _gevonden("Zoekkopwoord")] == ["3", "4"]


def test_beperkt_tot_stelsels():
    assert {s for s, _w, _n in _gevonden("Zoekproefwoord")} == {"DE", "NL", "FR"}
    assert _gevonden("Zoekproefwoord", stelsels=["NL"]) == [("NL", "ZTW", "1")]
    assert {s for s, _w, _n in _gevonden("Zoekproefwoord", stelsels=["DE", "FR"])} == {"DE", "FR"}
    assert _gevonden("Zoekproefwoord", stelsel="FR") == [("FR", "ZTC", "1")]


def test_stelsels_van_de_gebruiker_eerst():
    assert _gevonden("Zoekproefwoord", voorkeur=["FR"])[0][0] == "FR"
    assert _gevonden("Zoekproefwoord", voorkeur=["NL"])[0][0] == "NL"


def test_wetten_en_opzoeken_beperkt_tot_stelsels():
    with database.session() as s:
        ws, _n = wetboek.zoek_wetten(s, "", "Zoektest", stelsels=["NL"])
        assert [w.wet for w in ws] == ["ZTW"]
        ws, _n = wetboek.zoek_wetten(s, "", "Zoektest", stelsels=["DE", "NL"])
        assert {w.wet for w in ws} == {"ZTG", "ZTW"}
        assert opzoeken.wetten(s, "Zoektestgesetz", stelsels=["NL"]) == []
        assert [g.wettekst.wet for g in opzoeken.wetten(s, "Zoektestgesetz", stelsels=["DE"])] == ["ZTG"]
        assert [g.wettekst.wet for g in opzoeken.wetten(s, "Zoektestgesetz")] == ["ZTG"]
        u = opzoeken.lokaal(s, "Zoektestwet", stelsels=["DE"])
        assert not u.wetten
        res = zoeken.zoek(s, "Zoekproefwoord", stelsels=["NL"])
        assert {t.stelsel for t in res.wetteksten} == {"NL"}
        assert zoeken.zoek(s, "Zoekproefwoord", voorkeur=["FR"]).wetteksten[0].stelsel == "FR"
