"""Opzoeken (één zoekingang), bewaren met één tik, en Claude (met een nep-client) voor opzoeken en onderzoek."""
import json
from types import SimpleNamespace as NS

import pytest
from sqlalchemy import select

from synoptikon import db as database
from synoptikon.config import settings
from synoptikon.models import Antwoord, Kaart, Onderzoek, Opzoeking, Vraag, Wettekst, WettekstArtikel
from synoptikon.services import claude, onderzoek, opzoeken


@pytest.fixture(scope="module", autouse=True)
def grundgesetz():
    """Een kleine 'bulkwet' (niet uit het register), zoals de 6.000 Duitse wetten."""
    with database.session() as s:
        if s.scalar(select(Wettekst).where(Wettekst.wet == "GG")):
            return
        w = Wettekst(stelsel_code="DE", wet_id="gg", wet="GG", stijl="Art", kern=False, versie="2026-05-06",
                     titel="Grundgesetz für die Bundesrepublik Deutschland")
        s.add(w)
        s.flush()
        for i, (nr, tekst) in enumerate([("1", "(1) Die Würde des Menschen ist unantastbar."),
                                         ("2", "(1) Jeder hat das Recht auf die freie Entfaltung seiner Persönlichkeit.")]):
            s.add(WettekstArtikel(wettekst_id=w.id, nummer=nr, tekst=tekst, pad="I. Die Grundrechte", volgorde=i))
    from synoptikon.services.artikelen import laad_wetnamen

    with database.session() as s:
        laad_wetnamen(s)


def test_wet_op_naam_en_afkorting(client):
    for q in ("Grundgesetz", "GG"):
        html = client.get("/opzoeken", params={"q": q}).text
        assert "Grundgesetz für die Bundesrepublik Deutschland" in html, q


def test_artikel_meteen_met_tekst_en_bewaren(client):
    html = client.get("/opzoeken", params={"q": "Art. 2 GG"}).text
    assert "freie Entfaltung" in html and "I. Die Grundrechte" in html
    assert 'action="/leren/snel"' in html
    # in het logboek van vandaag
    with database.session() as s:
        assert s.scalar(select(Opzoeking).where(Opzoeking.invoer == "Art. 2 GG")) is not None
    r = client.post("/leren/snel", data={"stelsel": "DE", "wet": "GG", "nummer": "2", "terug": "/opzoeken?q=Art.%202%20GG"},
                    follow_redirects=False)
    assert r.status_code == 303 and "bewaard=1" in r.headers["location"]
    with database.session() as s:
        k = s.scalar(select(Kaart).where(Kaart.wet == "GG", Kaart.nummer == "2"))
        assert k is not None and k.lijst.naar_wk
    # nu met ster
    assert "★" in client.get("/opzoeken", params={"q": "Art. 2 GG"}).text


def test_lezen_bulkwet_met_ster_en_zoeken_in_wet(client):
    with database.session() as s:
        wid = s.scalar(select(Wettekst.id).where(Wettekst.wet == "GG"))
    html = client.get(f"/stelsels/DE/wet/{wid}", params={"deel": "I. Die Grundrechte"}).text
    assert "Würde des Menschen" in html and 'action="/leren/snel"' in html
    html = client.get(f"/stelsels/DE/wet/{wid}", params={"artikel": "Würde"}).text
    assert "Gevonden in deze wet" in html and "Art. 1 GG" in html


def test_wetten_overzicht_toont_belangrijke_wetten(client):
    html = client.get("/stelsels").text
    assert "Grundgesetz für die Bundesrepublik Deutschland" in html


# --- Claude, met een nep-client -------------------------------------------------------------------------------------


class NepStream:
    def __init__(self, bericht):
        self.bericht = bericht

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return self.bericht


def _bericht(content, stop="end_turn"):
    return NS(content=content, stop_reason=stop, usage=NS(input_tokens=1000, output_tokens=200, cache_creation_input_tokens=0,
                                                         cache_read_input_tokens=0, server_tool_use=NS(web_search_requests=1)))


class NepClient:
    """Eerst één toolronde (artikel_lezen), dan het eindantwoord."""

    def __init__(self, eind: dict):
        self.eind = eind
        self.verzoeken = []
        self.beta = NS(messages=NS(stream=self._stream))

    def _stream(self, **params):
        self.verzoeken.append(params)
        if len(self.verzoeken) == 1:
            return NepStream(_bericht([NS(type="tool_use", id="t1", name="artikel_lezen", input={"verwijzing": "Art. 1 GG"})], "tool_use"))
        return NepStream(_bericht([NS(type="text", text=json.dumps(self.eind))]))


@pytest.fixture
def nep_claude(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-test")

    def maak(eind):
        nep = NepClient(eind)
        monkeypatch.setattr(claude, "client_factory", lambda key: nep)
        return nep

    return maak


def test_opzoeken_met_claude_uitspraak_als_arrestkaart(client, nep_claude):
    nep = nep_claude(dict(soort="uitspraak", stelsel="DE", citeer="BVerfGE 65, 1 (Volkszählung)", titel="Volkszählungsurteil",
                          vindplaats="BVerfGE 65, 1", url="https://www.bundesverfassungsgericht.de", plaats="BVerfG, 15.12.1983",
                          tekst="", tekst_herkomst="geen", toelichting="Recht op informationele zelfbeschikking.",
                          artikelverwijzing="", zekerheid="hoog"))
    with database.session() as s:
        o = opzoeken.met_claude(s, 1, "Volkszählungsurteil", achtergrond=False)
        oid = o.id
    # de toolronde kreeg de lokale wettekst terug
    resultaat = json.loads(nep.verzoeken[1]["messages"][2]["content"][0]["content"])
    assert "Würde des Menschen" in resultaat["artikelen"][0]["tekst"]
    with database.session() as s:
        o = s.get(Opzoeking, oid)
        assert o.status == "klaar" and o.resultaat["bron"] == "claude"
    assert "Volkszählungsurteil" in client.get(f"/opzoeken/{oid}").text
    r = client.post(f"/opzoeken/{oid}/bewaren", data={"lijst": ""}, follow_redirects=False)
    assert r.status_code == 303
    with database.session() as s:
        o = s.get(Opzoeking, oid)
        k = s.get(Kaart, o.kaart_id)
        assert k.soort == "arrest" and k.bron.vindplaats == "BVerfGE 65, 1" and k.bron.soort == "rechtspraak"


def test_opzoeken_met_claude_artikel_krijgt_lokale_tekst(nep_claude):
    nep_claude(dict(soort="artikel", stelsel="DE", citeer="Art. 1 GG", titel="Menschenwürde", vindplaats="", url="",
                    plaats="GG", tekst="(verzonnen)", tekst_herkomst="lokaal", toelichting="", artikelverwijzing="Art. 1 GG",
                    zekerheid="hoog"))
    with database.session() as s:
        o = opzoeken.met_claude(s, 1, "menschenwürde grundgesetz", achtergrond=False)
        assert "Würde des Menschen" in o.resultaat["tekst"] and o.resultaat["nummer"] == "1" and o.resultaat["wet"] == "GG"


def test_budget_op(nep_claude, monkeypatch):
    nep_claude({})
    monkeypatch.setattr(settings, "llm_budget_usd", 0.0)
    with database.session() as s:
        o = opzoeken.met_claude(s, 1, "iets", achtergrond=False)
        assert o.status == "fout" and "budget" in o.fout


def test_onderzoek_vult_synopse_aan(client, nep_claude):
    nep_claude(dict(synthese="DE en NL komen functioneel op hetzelfde uit.", stelsels=[
        dict(code="DE", kern="Menselijke waardigheid is onaantastbaar.", analyse="Art. 1 GG.", bronnen=[
            dict(soort="wet", citeer="Art. 1 GG", titel="", vindplaats="", url="", tekst="", rol="hoofdregel", notitie="kern"),
            dict(soort="rechtspraak", citeer="BVerfG, Lüth", titel="Lüth", vindplaats="BVerfGE 7, 198", url="", tekst="",
                 rol="rechtspraak", notitie="")]),
        dict(code="XX", kern="genegeerd", analyse="", bronnen=[])]))
    with database.session() as s:
        v = Vraag(titel="Menselijke waardigheid", slug="waardigheid-test")
        v.antwoorden.append(Antwoord(stelsel_code="DE"))
        v.antwoorden.append(Antwoord(stelsel_code="NL", analyse="Mijn eigen analyse."))
        s.add(v)
        s.flush()
        onderzoek.start(s, v, ["DE", "NL"], achtergrond=False)
    with database.session() as s:
        v = s.scalar(select(Vraag).where(Vraag.slug == "waardigheid-test"))
        de, nl = v.antwoord_voor("DE"), v.antwoord_voor("NL")
        assert de.kern.startswith("Menselijke") and de.analyse.startswith(onderzoek.MARKERING)
        cites = {ab.bron.citeertitel for ab in de.bronnen}
        assert "Art. 1 GG" in cites and "BVerfG, Lüth" in cites
        wet = next(ab.bron for ab in de.bronnen if ab.bron.soort == "wet")
        assert wet.wettekst_artikel_id and "Würde" in wet.tekst
        assert nl.analyse == "Mijn eigen analyse."
        ok = s.scalar(select(Onderzoek).where(Onderzoek.vraag_id == v.id))
        assert ok.status == "klaar" and ok.usd > 0
    html = client.get("/vragen/waardigheid-test").text
    assert "functioneel op hetzelfde uit" in html
