"""Clozekaarten: elke gemarkeerde voorwaarde (Tatbestandsmerkmal) een gat in de tekst, ook als typkaart in Wunderkammer."""
import pytest
from sqlalchemy import select

from synoptikon import db as database
from synoptikon.config import settings
from synoptikon.models import Kaart, Leerlijst, Markering, Profiel, Wettekst, WettekstArtikel
from synoptikon.services import leren
from synoptikon.services.artikelen import Ref, laad_wetnamen

LANG = ("(1) Zur Übertragung des Eigentums an einer beweglichen Sache ist erforderlich, dass der Eigentümer die Sache "
        "dem Erwerber übergibt und beide darüber einig sind, dass das Eigentum übergehen soll. " + "Füllt den Text auf. " * 20 +
        "\n(2) Ist der Erwerber im Besitz der Sache, so genügt die Einigung über den Übergang des Eigentums.")
REF = Ref("DE", "929", "CLOZEG")


@pytest.fixture
def artikel929():
    with database.session() as s:
        w = s.scalar(select(Wettekst).where(Wettekst.wet_id == "test-cloze"))
        if w is None:
            w = Wettekst(stelsel_code="DE", wet_id="test-cloze", wet="CLOZEG", stijl="§", kern=False, versie="2026-01-01", titel="Cloze-Gesetz")
            s.add(w)
            s.flush()
            s.add(WettekstArtikel(wettekst_id=w.id, nummer="929", opschrift="Einigung und Übergabe", tekst=LANG, volgorde=0))
    with database.session() as s:
        laad_wetnamen(s)


def _voorwaarde(s, quote, vak="ZR Ia"):
    m = Markering(profiel_id=1, stelsel_code="DE", wet="CLOZEG", nummer="929", quote=quote, vak=vak, soort="voorwaarde")
    s.add(m)
    s.flush()
    return m


def test_een_cloze_per_voorwaarde_in_tekstvolgorde_en_niet_dubbel(artikel929):
    with database.session() as s:
        _voorwaarde(s, "dem Erwerber übergibt")
        _voorwaarde(s, "beweglichen Sache")
        _voorwaarde(s, "Sache", vak="GÖ")  # ander vak: telt niet
        lijst = Leerlijst(profiel_id=1, naam="Cloze-lijst", vak="ZR Ia")
        s.add(lijst)
        s.flush()
        ks = leren.maak_kaarten(s, lijst, ["cloze"], ref=REF)
        assert [k.antwoord for k in ks] == ["beweglichen Sache", "dem Erwerber übergibt"]
        assert leren.maak_kaarten(s, lijst, ["cloze"], ref=REF) == []
        b = leren.Bouwer(s)
        z = b.zijden(ks[0])
        assert "[…]" in z.voor and "beweglichen Sache" not in z.voor and "**beweglichen Sache**" in z.achter
        assert "(2)" not in z.voor  # alleen het lid waar het gat in staat
        assert b.cloze(ks[0]).count("{{c1::beweglichen Sache}}") == 1
        assert b.cloze(ks[0]).startswith("(1) Zur Übertragung")


def test_nieuwe_voorwaarde_geeft_meteen_een_cloze_waar_het_artikel_al_kaarten_heeft(client, artikel929):
    with database.session() as s:
        lijst = Leerlijst(profiel_id=1, naam="Cloze-auto", vak="Sachenrecht")
        andere = Leerlijst(profiel_id=1, naam="Cloze-anders", vak="Sachenrecht")
        s.add_all([lijst, andere])
        s.flush()
        leren.maak_kaarten(s, lijst, ["artikel"], ref=REF)
        lid, aid = lijst.id, andere.id
    r = client.post("/markeringen", data=dict(quote="Einigung über den Übergang", soort="voorwaarde", vak="Sachenrecht",
                                            stelsel="DE", wet="CLOZEG", nummer="929"))
    assert r.status_code == 200 and r.json()["kaarten"] == 1
    with database.session() as s:
        assert [k.antwoord for k in s.scalars(select(Kaart).where(Kaart.lijst_id == lid, Kaart.soort == "cloze"))] == ["Einigung über den Übergang"]
        assert not list(s.scalars(select(Kaart).where(Kaart.lijst_id == aid)))  # daar stond het artikel niet in


def test_cloze_gaat_mee_naar_wunderkammer(client, artikel929, monkeypatch):
    monkeypatch.setattr(settings, "wk_token", "k" * 32)
    with database.session() as s:
        s.get(Profiel, 1).wunderkammer = True
        lijst = Leerlijst(profiel_id=1, naam="Cloze-wk", vak="ZR Ia", naar_wk=True)
        s.add(lijst)
        s.flush()
        _voorwaarde(s, "beide darüber einig sind")
        leren.maak_kaarten(s, lijst, ["cloze"], ref=REF)
    data = client.get("/api/wk/kaarten", headers={"Authorization": "Bearer " + "k" * 32}).json()
    mine = [k for k in data["kaarten"] if k["soort"] == "cloze" and "{{c1::beide darüber einig sind}}" in (k["cloze"] or "")]
    assert mine and "{{c1::beide darüber einig sind}}" in mine[0]["cloze"]
    assert all(k["cloze"] is None for k in data["kaarten"] if k["soort"] != "cloze")


def test_verdwenen_voorwaarde_breekt_de_kaart_niet(artikel929):
    with database.session() as s:
        lijst = Leerlijst(profiel_id=1, naam="Cloze-weg", vak="ZR Ia")
        s.add(lijst)
        s.flush()
        k = Kaart(uid=leren.nieuwe_uid(), lijst=lijst, soort="cloze", antwoord="staat er niet", stelsel_code="DE", wet="CLOZEG", nummer="929")
        s.add(k)
        s.flush()
        b = leren.Bouwer(s)
        assert "staat er niet" in b.zijden(k).achter and b.cloze(k) is None
