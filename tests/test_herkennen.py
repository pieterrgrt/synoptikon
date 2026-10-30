"""ECLI/CELEX herkennen en ophalen vóór Claude, en 'kloppend maken'. Het netwerk is overal vervangen door een nep-client."""
from types import SimpleNamespace as NS

import httpx
import pytest
from sqlalchemy import select

from synoptikon import db as database
from synoptikon.config import settings
from synoptikon.models import Bron, Kaart, Opzoeking
from synoptikon.services import claude, herkennen, opzoeken

CELLAR_CSV = '''"ecli","celex","datum","titel"
"ECLI:EU:C:2015:806","62014CJ0594",2015-12-10,"Arrest van het Hof (Zesde kamer) van 10 december 2015.#Simona Kornhaas tegen Thomas Dithmar.#Verzoek van het Bundesgerichtshof om een prejudiciële beslissing.#Prejudiciële verwijzing – Insolventieprocedures – Artikel 4, lid 1.#Zaak C-594/14."
"ECLI:EU:C:2015:806","62014CJ0594",2015-12-10,
'''

RECHTSPRAAK_XML = '''<?xml version="1.0" encoding="utf-8"?>
<open-rechtspraak><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:psi="http://psi.rechtspraak.nl/"><rdf:Description>
 <dcterms:identifier>ECLI:NL:HR:2015:1</dcterms:identifier>
 <dcterms:creator>Hoge Raad</dcterms:creator><dcterms:date>2015-01-06</dcterms:date>
 <psi:zaaknummer>14/02483</psi:zaaknummer></rdf:Description></rdf:RDF>
 <inhoudsindicatie xmlns="http://www.rechtspraak.nl/schema/rechtspraak-1.0"><para>HR: art. 80a RO.</para></inhoudsindicatie>
</open-rechtspraak>'''


class NepNet:
    """Antwoordt als de Cellar (post) en rechtspraak.nl (get); houdt bij wat er gevraagd is."""

    def __init__(self, cellar_csv=CELLAR_CSV, rs_status=200, rs_xml=RECHTSPRAAK_XML, fout=None):
        self.cellar_csv, self.rs_status, self.rs_xml, self.fout = cellar_csv, rs_status, rs_xml, fout
        self.verzoeken = []

    def _antwoord(self, status, text):
        return NS(status_code=status, text=text, content=text.encode(), raise_for_status=lambda: None)

    def post(self, url, data=None, headers=None):
        self.verzoeken.append(("post", url, data))
        if self.fout:
            raise self.fout
        return self._antwoord(200, self.cellar_csv)

    def get(self, url, params=None):
        self.verzoeken.append(("get", url, params))
        if self.fout:
            raise self.fout
        return self._antwoord(self.rs_status, self.rs_xml)

    def close(self):
        pass


@pytest.fixture
def net(monkeypatch):
    def zet(**kw):
        nep = NepNet(**kw)
        monkeypatch.setattr(herkennen, "verbinding", lambda: nep)
        return nep

    return zet


@pytest.mark.parametrize("invoer,soort,waarde", [
    ("ECLI:EU:C:2015:806", "ecli", "ECLI:EU:C:2015:806"),
    ("ecli:nl:hr:2015:1", "ecli", "ECLI:NL:HR:2015:1"),
    ("62014CJ0594", "celex", "62014CJ0594"),
    ("CELEX: 62014cj0594", "celex", "62014CJ0594"),
    ("https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX%3A62014CJ0594", "celex", "62014CJ0594"),
    ("https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=ecli:ECLI:EU:C:2015:806", "ecli", "ECLI:EU:C:2015:806"),
])
def test_herken_id(invoer, soort, waarde):
    i = herkennen.herken_id(invoer)
    assert i and (i.soort, i.waarde) == (soort, waarde)


@pytest.mark.parametrize("invoer", ["§ 823 BGB", "Baris/Riezenkamp", "art. 6:162 BW", "BGHZ 63, 369", "", "arrest 32016R0679 uit het college"])
def test_geen_id(invoer):
    assert herkennen.herken_id(invoer) is None


def test_eu_ecli_via_cellar(net):
    nep = net()
    r = herkennen.zoek(herkennen.herken_id("ECLI:EU:C:2015:806"))
    assert r["stelsel"] == "EU" and r["bron"] == "cellar" and r["zekerheid"] == "hoog"
    assert r["citeer"] == "HvJ EU 10 december 2015, C-594/14 (Simona Kornhaas tegen Thomas Dithmar)"
    assert r["vindplaats"] == "ECLI:EU:C:2015:806" and r["celex"] == "62014CJ0594"
    assert r["url"].endswith("uri=ecli:ECLI:EU:C:2015:806") and r["plaats"].startswith("Arrest van het Hof")
    assert "Insolventieprocedures" in r["toelichting"]
    assert nep.verzoeken[0][0] == "post" and "ECLI:EU:C:2015:806" in nep.verzoeken[0][2]["query"]


def test_eu_celex_rechtspraak_geeft_ook_ecli(net):
    net()
    r = herkennen.zoek(herkennen.herken_id("62014CJ0594"))
    assert r["vindplaats"] == "ECLI:EU:C:2015:806"


def test_celex_van_wetgeving_wordt_niet_opgehaald(net):
    nep = net()
    assert herkennen.zoek(herkennen.herken_id("32016R0679")) is None and nep.verzoeken == []


def test_nl_ecli_via_rechtspraak(net):
    nep = net()
    r = herkennen.zoek(herkennen.herken_id("ECLI:NL:HR:2015:1"))
    assert r["citeer"] == "HR 6 januari 2015, 14/02483, ECLI:NL:HR:2015:1" and r["bron"] == "rechtspraak"
    assert r["plaats"] == "Hoge Raad, 6 januari 2015, 14/02483" and r["toelichting"] == "HR: art. 80a RO."
    assert nep.verzoeken[0][2] == {"id": "ECLI:NL:HR:2015:1"}


def test_niets_gevonden_of_netwerkfout_is_none(net):
    net(cellar_csv='"ecli","celex","datum","titel"\n')
    assert herkennen.zoek(herkennen.herken_id("ECLI:EU:C:2099:1")) is None
    net(rs_status=404)
    assert herkennen.zoek(herkennen.herken_id("ECLI:NL:HR:2015:1")) is None
    net(fout=httpx.ConnectError("geen netwerk"))
    assert herkennen.zoek(herkennen.herken_id("ECLI:NL:HR:2015:1")) is None
    assert herkennen.zoek(herkennen.herken_id("ECLI:DE:BGH:2020:1")) is None  # niet ondersteund: aan Claude


# --- in Opzoeken -----------------------------------------------------------------------------------------------------


def test_opzoeken_ecli_gaat_niet_naar_claude(net, monkeypatch):
    net()
    monkeypatch.setattr(claude, "loop", lambda *a, **k: pytest.fail("Claude hoort hier niet gebeld te worden"))
    with database.session() as s:
        o = opzoeken.met_claude(s, 1, "ECLI:EU:C:2015:806", achtergrond=False)
        assert o.status == "klaar" and o.resultaat["bron"] == "cellar"
        oid = o.id
    # bewaren maakt een Bron met de echte vindplaats
    with database.session() as s:
        b = opzoeken.bron_uit(s, s.get(Opzoeking, oid))
        assert b.vindplaats == "ECLI:EU:C:2015:806" and b.vindplaats_type == "ECLI" and "Cellar" in b.opmerking
        assert "niet geverifieerd" not in b.opmerking


def test_opzoeken_valt_terug_op_claude_als_bron_niets_geeft(net, monkeypatch):
    net(cellar_csv='"ecli","celex","datum","titel"\n')
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-test")
    gezien = []

    def nep_loop(db, soort, systeem, vraag, schema, **kw):
        gezien.append(vraag)
        return dict(soort="uitspraak", stelsel="EU", citeer="HvJ ?", titel="?", vindplaats="", url="", plaats="", tekst="",
                    tekst_herkomst="geen", toelichting="", artikelverwijzing="", zekerheid="laag"), 0.0

    monkeypatch.setattr(claude, "loop", nep_loop)
    with database.session() as s:
        o = opzoeken.met_claude(s, 1, "ECLI:EU:C:2099:1", achtergrond=False)
        assert gezien and o.resultaat["bron"] == "claude"


def test_knop_ophalen_ook_zonder_claude(client, net, monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "")
    html = client.get("/opzoeken", params={"q": "ECLI:EU:C:2015:806"}).text
    assert "Ophalen bij EUR-Lex" in html
    net()
    gestart = []
    monkeypatch.setattr(opzoeken, "_vul", lambda oid, db=None: gestart.append(oid))  # de achtergrondthread doet hier niets
    r = client.post("/opzoeken/claude", data={"q": "ECLI:EU:C:2015:806"}, follow_redirects=False)
    assert r.status_code == 303
    import time

    time.sleep(0.2)
    assert len(gestart) == 1
    assert client.post("/opzoeken/claude", data={"q": "iets anders"}, follow_redirects=False).status_code == 503


# --- kloppend maken --------------------------------------------------------------------------------------------------


def _claude_opzoeking(**extra):
    r = dict(soort="uitspraak", stelsel="NL", citeer="HR 1982 Plas/Valburg?", titel="Plas/Valburg", vindplaats="", url="",
             plaats="HR", tekst="", tekst_herkomst="geen", toelichting="Iets.", zekerheid="laag", bron="claude", **extra)
    with database.session() as s:
        o = Opzoeking(profiel_id=1, invoer="plas valburg", resultaat=r)
        s.add(o)
        s.flush()
        return o.id


def test_kloppend_maken_wordt_eigen_bron(client):
    oid = _claude_opzoeking()
    html = client.get(f"/opzoeken/{oid}").text
    assert "Kloppend maken" in html and "niet zeker" in html
    assert 'name="citeer"' in client.get(f"/opzoeken/{oid}/corrigeer").text
    r = client.post(f"/opzoeken/{oid}/corrigeer", data=dict(
        citeer="HR 18 juni 1982, NJ 1982/659 (Plas/Valburg)", titel="Plas/Valburg", vindplaats="ECLI:NL:HR:1982:AG4521",
        url="https://uitspraken.rechtspraak.nl/details?id=ECLI:NL:HR:1982:AG4521", plaats="HR, 18-06-1982",
        toelichting="Eigen toelichting.", stelsel="nl"), follow_redirects=False)
    assert r.status_code == 303
    with database.session() as s:
        o = s.get(Opzoeking, oid)
        assert o.resultaat["bron"] == "eigen" and o.resultaat["zekerheid"] == "hoog" and o.resultaat["stelsel"] == "NL"
        b = opzoeken.bron_uit(s, o)
        assert b.citeertitel.startswith("HR 18 juni 1982") and b.vindplaats_type == "ECLI"
        assert b.opmerking.startswith("Zelf nagekeken") and "Claude" not in b.opmerking
    html = client.get(f"/opzoeken/{oid}").text
    assert "zelf nagekeken" in html and "niet zeker" not in html


def test_kloppend_maken_werkt_bestaande_bron_bij(client):
    oid = _claude_opzoeking()
    with database.session() as s:
        o = s.get(Opzoeking, oid)
        o.resultaat = {**o.resultaat, "vindplaats": "NJ 1982/659"}
        bid = opzoeken.bron_uit(s, o).id
    client.post(f"/opzoeken/{oid}/corrigeer", data=dict(citeer="HR 18 juni 1982 (Plas/Valburg)", titel="Plas/Valburg",
                                                        vindplaats="NJ 1982/659", url="", plaats="", toelichting="", stelsel="NL"))
    with database.session() as s:
        b = s.get(Bron, bid)
        assert b.citeertitel == "HR 18 juni 1982 (Plas/Valburg)" and b.opmerking.startswith("Zelf nagekeken")
        assert s.scalar(select(Bron).where(Bron.vindplaats == "NJ 1982/659", Bron.id != bid)) is None


def test_kloppend_maken_ophalen_uit_link_vult_formulier(client, net):
    oid = _claude_opzoeking()
    net()
    r = client.post(f"/opzoeken/{oid}/corrigeer", data=dict(
        citeer="", titel="", vindplaats="", url="https://eur-lex.europa.eu/legal-content/NL/TXT/?uri=CELEX%3A62014CJ0594",
        plaats="", toelichting="", stelsel="EU", ophalen="1"))
    assert r.status_code == 200 and "C-594/14" in r.text and "Opgehaald" in r.text
    with database.session() as s:  # nog niets opgeslagen
        assert s.get(Opzoeking, oid).resultaat["bron"] == "claude"


def test_kloppend_maken_niet_van_een_ander(client):
    with database.session() as s:
        o = Opzoeking(profiel_id=2, invoer="x", resultaat={"bron": "claude"})
        s.add(o)
        s.flush()
        oid = o.id
    assert client.get(f"/opzoeken/{oid}/corrigeer").status_code == 404


def test_ophalen_herstelt_een_oude_gok_van_claude_en_vraagt_een_regel(client, net, monkeypatch):
    """Na een eerdere 'Niet vastgesteld' van Claude: het ophalen werkt de Bron bij, en de trefwoorden van EUR-Lex worden
    geen rechtsregel. Zonder regel komt er geen kaart, je gaat terug naar het formulier."""
    net()
    monkeypatch.setattr(claude, "loop", lambda *a, **k: pytest.fail("Claude hoort hier niet gebeld te worden"))
    with database.session() as s:
        s.add(Bron(stelsel_code="EU", soort="rechtspraak", citeertitel="ECLI:EU:C:2015:806", titel="Niet vastgesteld", taal="nl",
                   vindplaats="ECLI:EU:C:2015:806", opmerking=opzoeken.OPMERKING["claude"] + "Ik heb niet kunnen vaststellen…"))
        s.flush()
        oid = opzoeken.met_claude(s, 1, "ECLI:EU:C:2015:806", achtergrond=False).id
        assert opzoeken.regel_terugval(s.get(Opzoeking, oid).resultaat) == ""
    assert "nodig, want de bron geeft alleen trefwoorden" in client.get(f"/opzoeken/{oid}").text
    r = client.post(f"/opzoeken/{oid}/bewaren", data={"vak": "GÖ"}, follow_redirects=False)
    assert r.status_code == 303 and f"o={oid}" in r.headers["location"]
    with database.session() as s:
        b = s.scalar(select(Bron).where(Bron.vindplaats == "ECLI:EU:C:2015:806"))
        assert "Kornhaas" in b.citeertitel and b.titel != "Niet vastgesteld" and "Cellar" in b.opmerking
        assert s.scalar(select(Kaart).where(Kaart.bron_id == b.id)) is None
    client.post(f"/opzoeken/{oid}/bewaren", data={"vak": "GÖ", "regel": "Die Norm ist insolvenzrechtlich zu qualifizieren."})
    with database.session() as s:
        k = s.scalar(select(Kaart).where(Kaart.bron_id == b.id))
        assert k.antwoord.startswith("Die Norm ist insolvenzrechtlich") and k.lijst.vak == "GÖ"
