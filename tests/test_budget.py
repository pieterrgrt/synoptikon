"""Budget voor Claude: per profiel geboekt, een grens per profiel naast het totaal, en het overzicht voor de beheerder."""
from __future__ import annotations

import pytest

from synoptikon import db as database
from synoptikon.config import settings
from synoptikon.models import Casus, LlmGebruik, Profiel
from synoptikon.services import claude, klausur
from tests.test_klausur import nep  # noqa: F401  (fixture)

PID = 3  # een lezer zonder eigen grens


@pytest.fixture
def schoon():
    yield
    with database.session() as s:
        s.query(LlmGebruik).filter(LlmGebruik.profiel_id == PID).delete()
        s.get(Profiel, PID).llm_grens_usd = None


def test_grens_per_profiel(nep, schoon, monkeypatch):  # noqa: F811
    nep({"musterloesung": "Gutachten."})
    monkeypatch.setattr(settings, "llm_profiel_usd", 0.5)
    with database.session() as s:
        assert claude.grens(s.get(Profiel, PID)) == 0.5 and claude.grens(s.get(Profiel, 1)) is None  # beheerder: alleen het totaal
        claude.controleer_budget(s, PID)
        s.add(LlmGebruik(profiel_id=PID, doel="muster", model="x", usd=0.6))
        s.flush()
        assert claude.per_profiel(s)[PID] == pytest.approx(0.6)
        with pytest.raises(claude.ClaudeFout, match="maandgrens"):
            claude.controleer_budget(s, PID)
        claude.controleer_budget(s, 1)  # een ander profiel merkt er niets van
        s.get(Profiel, PID).llm_grens_usd = 2.0
        claude.controleer_budget(s, PID)


def test_musterloesung_van_voorbeeldcasus_op_wie_erom_vraagt(nep, schoon):  # noqa: F811
    nep({"musterloesung": "Gutachten."})
    with database.session() as s:
        c = Casus(profiel_id=None, titel="Voorbeeld budget", sachverhalt="Ein Fall.", herkomst="voorbeeld")
        s.add(c)
        s.flush()
        klausur.muster(s, c, "nl", PID)
        assert c.muster_status == "klaar"
        assert s.query(LlmGebruik).filter_by(doel="muster", profiel_id=PID).count() == 1
        s.delete(c)


def test_overzicht_en_grens_instellen(client, schoon):
    with database.session() as s:
        s.add(LlmGebruik(profiel_id=PID, doel="opzoeken", model="x", usd=1.25))
    r = client.get("/beheer/profielen")
    assert r.status_code == 200 and "$1.25 van $5.00" in r.text and "geen eigen grens" in r.text  # beheerder
    with database.session() as s:
        p = s.get(Profiel, PID)
        velden = {"gebruikersnaam": p.gebruikersnaam, "naam": p.naam, "rol": p.rol, "taal": p.taal, "llm_grens": "2,50"}
    r = client.post(f"/beheer/profielen/{PID}", data=velden, follow_redirects=False)
    assert "fout" not in r.headers["location"]
    assert "$1.25 van $2.50" in client.get("/beheer/profielen").text
    client.post(f"/beheer/profielen/{PID}", data={**velden, "llm_grens": "veel"})  # ongeldig: de oude grens blijft
    with database.session() as s:
        assert s.get(Profiel, PID).llm_grens_usd == 2.5
