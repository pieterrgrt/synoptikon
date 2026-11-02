"""Kaarten uit notities: bestanden kiezen, voorstellen via (nep-)Claude, beoordelen, en pas daarna naar Wunderkammer."""
import json
from types import SimpleNamespace as NS

import pytest
from sqlalchemy import func, select

from synoptikon import db as database
from synoptikon.config import settings
from synoptikon.models import Kaart, Leerlijst, NotitieBestand
from synoptikon.services import claude, notities
from tests.test_leren import _wettekst

TOKEN = "n" * 32
LANG = "Inhalt der Vorlesung. " * 20

VOORSTEL = {"kaarten": [
    {"soort": "artikel", "verwijzing": "§ 929 BGB", "vraag": "", "antwoord": "wordt genegeerd", "zaak": "", "vindplaats": "", "feiten": ""},
    {"soort": "vrij", "verwijzing": "", "vraag": "Was ist das Abstraktionsprinzip?", "antwoord": "Trennung von Verpflichtung und Verfügung.",
     "zaak": "", "vindplaats": "", "feiten": ""},
    {"soort": "vrij", "verwijzing": "", "vraag": "Was ist das Trennungsprinzip?", "antwoord": "Zwei Rechtsgeschäfte.",
     "zaak": "", "vindplaats": "", "feiten": ""},
    {"soort": "arrest", "verwijzing": "", "vraag": "", "antwoord": "Sitzverlegung ist geschützt.", "zaak": "EuGH, Kornhaas",
     "vindplaats": "ECLI:EU:C:2015:806", "feiten": "Insolvenz einer Ltd."},
    {"soort": "kern", "verwijzing": "§ 2 FantasieG", "vraag": "Was regelt das Fantasiegesetz?", "antwoord": "Durch Eintragung.",
     "zaak": "", "vindplaats": "", "feiten": ""},
    {"soort": "kern", "verwijzing": "Paragraf ohne Nummer", "vraag": "Übereignung beweglicher Sachen?", "antwoord": "Einigung und Übergabe.",
     "zaak": "", "vindplaats": "", "feiten": ""},
]}


class Stroom:
    def __init__(self, bericht):
        self.bericht = bericht

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return self.bericht


class NepClient:
    """Geeft meteen het eindantwoord (zonder toolronde) en onthoudt de verzoeken."""

    def __init__(self, eind):
        self.eind, self.verzoeken = eind, []
        self.beta = NS(messages=NS(stream=self._stream))

    def _stream(self, **params):
        self.verzoeken.append(params)
        return Stroom(NS(content=[NS(type="text", text=json.dumps(self.eind))], stop_reason="end_turn",
                         usage=NS(input_tokens=1000, output_tokens=200, cache_creation_input_tokens=0, cache_read_input_tokens=0,
                                  server_tool_use=None)))


@pytest.fixture
def map_(tmp_path, monkeypatch):
    (tmp_path / "Zivilrecht 1A" / "1 Einführung").mkdir(parents=True)
    (tmp_path / "Zivilrecht 1A" / "1 Einführung" / "Vorlesung.md").write_text(LANG, encoding="utf-8")
    (tmp_path / "Zivilrecht 1A" / "Naamloos.md").write_text("", encoding="utf-8")
    (tmp_path / "Metaphysik").mkdir()
    (tmp_path / "Metaphysik" / "Kant.md").write_text(LANG, encoding="utf-8")
    (tmp_path / "Metaphysik" / "Eigen vak.md").write_text("---\nvak: Philosophie\n---\n" + LANG, encoding="utf-8")
    (tmp_path / "Zivilrecht 1A" / "Privé.md").write_text("---\nsynoptikon: nee\n---\n" + LANG, encoding="utf-8")
    monkeypatch.setattr(settings, "notities_dir", tmp_path)
    monkeypatch.setattr(settings, "notities_vakken", "Zivilrecht 1A = ZR Ia; Kapitalmarktrecht=W")
    return tmp_path


@pytest.fixture
def nep(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-test")
    client = NepClient(VOORSTEL)
    monkeypatch.setattr(claude, "client_factory", lambda key: client)
    return client


def test_vakken_en_bestanden(map_):
    assert notities.vakken() == {"Zivilrecht 1A": "ZR Ia", "Kapitalmarktrecht": "W"}
    gekozen = {b.pad: b.vak for b in notities.bestanden()}
    # leeg, zonder vak en met 'synoptikon: nee' vallen weg; frontmatter `vak:` gaat voor de map
    assert gekozen == {"Zivilrecht 1A/1 Einführung/Vorlesung.md": "ZR Ia", "Metaphysik/Eigen vak.md": "Philosophie"}


def test_voorstellen_beoordelen_en_wunderkammer(map_, nep, client, monkeypatch):
    _wettekst()
    client.post("/profiel/wunderkammer", data={"aan": "1"})
    monkeypatch.setattr(settings, "wk_token", TOKEN)
    with database.session() as s:
        u = notities.verwerk(s, profiel_id=1)
    assert (u.notities, u.fouten) == (2, 0)
    assert len(nep.verzoeken) == 2
    with database.session() as s:
        lijst = s.query(Leerlijst).filter_by(profiel_id=1, naam="Notities · ZR Ia").one()
        lid, kaarten = lijst.id, list(lijst.kaarten)
        assert lijst.vak == "ZR Ia" and lijst.naar_wk
        # twee vrije kaarten in één lijst (dat ging vroeger mis), de onbekende norm wordt een vrije kaart
        # een onbekende wet (§ 2 FantasieG) wordt geen § 2 BGB, maar ook een vrije kaart
        assert sorted(k.soort for k in kaarten) == ["arrest", "artikel", "vrij", "vrij", "vrij", "vrij"]
        assert all(k.status == "voorstel" and not k.actief and k.herkomst.endswith("Vorlesung.md") for k in kaarten)
        art = next(k for k in kaarten if k.soort == "artikel")
        assert (art.stelsel_code, art.nummer, art.antwoord) == ("DE", "929", None)
        over = {art.id, next(k.id for k in kaarten if k.soort == "arrest")}
    hdr = {"Authorization": f"Bearer {TOKEN}"}
    assert not [k for k in client.get("/api/wk/kaarten", headers=hdr).json()["kaarten"] if k["lijst"] == lid]

    html = client.get(f"/leren/{lid}").text
    assert 'id="voorstellen"' in html and "Was ist das Abstraktionsprinzip?" in html
    assert "voorstellen uit je notities" in client.get("/leren").text
    r = client.post(f"/leren/{lid}/voorstellen", data={"kaart": [str(i) for i in over]}, follow_redirects=False)
    assert r.status_code == 303 and "overgenomen=2&afgewezen=4" in r.headers["location"]
    naar_wk = [k for k in client.get("/api/wk/kaarten", headers=hdr).json()["kaarten"] if k["lijst"] == lid]
    assert sorted(k["soort"] for k in naar_wk) == ["arrest", "artikel"]

    # Ongewijzigd: geen nieuwe aanroep. Gewijzigd: wel, met wat er al is (ook afgewezen) in de opdracht.
    with database.session() as s:
        assert notities.verwerk(s, profiel_id=1).ongewijzigd == 2
    assert len(nep.verzoeken) == 2
    (map_ / "Zivilrecht 1A" / "1 Einführung" / "Vorlesung.md").write_text(LANG + "\nNeu: § 930 BGB.", encoding="utf-8")
    with database.session() as s:
        u = notities.verwerk(s, profiel_id=1)
    assert u.notities == 1 and u.voorstellen == 0  # alles bestond al
    opdracht = nep.verzoeken[-1]["messages"][0]["content"]
    assert "(afgewezen)" in opdracht and "§ 929 BGB" in opdracht and "Neu: § 930 BGB." in opdracht


def test_fout_wordt_later_opnieuw_geprobeerd(map_, nep, monkeypatch):
    monkeypatch.setattr(settings, "notities_vakken", "Kapitalmarktrecht=W")
    (map_ / "Kapitalmarktrecht").mkdir()
    (map_ / "Kapitalmarktrecht" / "Sitzung.md").write_text(LANG, encoding="utf-8")

    echt = notities.verwerk_notitie

    def eerst_kapot(*a, **k):
        if not eerst_kapot.gedaan:
            eerst_kapot.gedaan = True
            raise claude.ClaudeFout("Claude weigerde deze opdracht.")
        return echt(*a, **k)

    eerst_kapot.gedaan = False
    monkeypatch.setattr(notities, "verwerk_notitie", eerst_kapot)
    with database.session() as s:
        assert notities.verwerk(s, profiel_id=1).fouten == 1
    with database.session() as s:
        assert s.query(NotitieBestand).filter_by(pad="Kapitalmarktrecht/Sitzung.md").one().fout
        u = notities.verwerk(s, profiel_id=1)
    assert u.notities == 1 and u.fouten == 0
    with database.session() as s:
        assert s.query(NotitieBestand).filter_by(pad="Kapitalmarktrecht/Sitzung.md").one().fout is None


def test_droog_en_maximum(map_, nep):
    with database.session() as s:
        u = notities.verwerk(s, profiel_id=2, maximum=1, droog=True)
    assert (u.notities, u.over, len(nep.verzoeken)) == (1, 1, 0)
    with database.session() as s:
        assert s.query(Kaart).join(Leerlijst).filter(Leerlijst.profiel_id == 2).count() == 0


def test_voorstellen_per_notitie_en_per_kaart(map_, nep, client):
    _wettekst()
    with database.session() as s:
        notities.verwerk(s, profiel_id=1)
        # Alleen voorstellen uit notities (met herkomst); andere tests laten ook losse voorstellen achter.
        lijst = next(l for l in s.query(Leerlijst).filter_by(profiel_id=1)
                     if any(k.status == "voorstel" and k.herkomst for k in l.kaarten))
        ids = [k.id for k in lijst.kaarten if k.status == "voorstel" and k.herkomst]
        lid = lijst.id
    html = client.get(f"/leren/voorstellen?lijst={lid}").text
    assert "voorstellen.js" in html and f'data-kaart="{ids[0]}"' in html
    assert "/leren/voorstellen" in client.get("/leren").text
    r = client.post(f"/leren/kaart/{ids[0]}/beoordeel", data={"besluit": "over"}, headers={"X-Requested-With": "fetch"})
    assert r.json() == {"ok": True, "status": "over"}
    client.post(f"/leren/kaart/{ids[0]}/beoordeel", data={"besluit": "terug"}, headers={"X-Requested-With": "fetch"})
    r = client.post("/leren/voorstellen", data={"kaart": [str(i) for i in ids], "besluit": "af", "terug": f"/leren/voorstellen?lijst={lid}"},
                    follow_redirects=False)
    assert r.status_code == 303 and f"afgewezen={len(ids)}" in r.headers["location"]
    with database.session() as s:
        assert all(s.get(Kaart, i).status == "afgewezen" for i in ids)


def test_herindelen_na_ander_vak(map_, nep, monkeypatch):
    """Kapitalmarktrecht en Kartellrecht stonden samen onder W; nu elk een eigen vak (02-11-2026). De voorstellen verhuizen
    mee, de notitie hoeft niet opnieuw naar Claude als alleen `vak:` veranderde."""
    monkeypatch.setattr(settings, "notities_vakken", "Kapitalmarktrecht=W")
    (map_ / "Kapitalmarktrecht").mkdir()
    (map_ / "Kapitalmarktrecht" / "Sitzung.md").write_text(LANG, encoding="utf-8")
    (map_ / "Kartellrecht").mkdir()
    (map_ / "Kartellrecht" / "1.pdf.md").write_text("---\nvak: W\nbron: Kartellrecht/1.pdf\n---\n" + LANG, encoding="utf-8")
    with database.session() as s:
        notities.verwerk(s, profiel_id=2)
        assert s.scalar(select(func.count()).select_from(Kaart).join(Leerlijst).where(Leerlijst.naam == "Notities · W", Leerlijst.profiel_id == 2)) > 0
        # de nep-Claude geeft voor de tweede notitie dezelfde kaarten (die bestaan al): geef er één de Kartellrecht-herkomst
        s.scalars(select(Kaart).join(Leerlijst).where(Leerlijst.naam == "Notities · W", Leerlijst.profiel_id == 2)).first().herkomst = "Kartellrecht/1.pdf.md"
        s.commit()
    vragen = len(nep.verzoeken)

    monkeypatch.setattr(settings, "notities_vakken", "Kapitalmarktrecht=KapMR")
    (map_ / "Kartellrecht" / "1.pdf.md").write_text("---\nvak: KartR\nbron: Kartellrecht/1.pdf\n---\n" + LANG, encoding="utf-8")
    with database.session() as s:
        u = notities.verwerk(s, profiel_id=2)
        lijsten = {l.naam: {k.herkomst for k in l.kaarten} for l in s.scalars(select(Leerlijst).where(Leerlijst.profiel_id == 2))}
        vakken_ = {n.pad: n.vak for n in s.scalars(select(NotitieBestand).where(NotitieBestand.profiel_id == 2))}
    assert u.notities == 0 and len(nep.verzoeken) == vragen  # geen nieuwe Claude-ronde
    assert "Notities · W" not in lijsten
    assert lijsten["Notities · KapMR"] == {"Kapitalmarktrecht/Sitzung.md"} and lijsten["Notities · KartR"] == {"Kartellrecht/1.pdf.md"}
    assert vakken_["Kapitalmarktrecht/Sitzung.md"] == "KapMR" and vakken_["Kartellrecht/1.pdf.md"] == "KartR"


def test_hernoemde_map_is_geen_nieuwe_notitie(map_, nep):
    """'1. Sitzung' → '1 Finanzmärkte': zelfde bestand, andere map. Geen nieuwe Claude-ronde, herkomst gaat mee."""
    oud = map_ / "Zivilrecht 1A" / "1 Einführung"
    with database.session() as s:
        notities.verwerk(s, profiel_id=3)
    vragen = len(nep.verzoeken)
    oud.rename(map_ / "Zivilrecht 1A" / "1 Einführung und Grundlagen")
    with database.session() as s:
        u = notities.verwerk(s, profiel_id=3)
        herkomst = set(s.scalars(select(Kaart.herkomst).join(Leerlijst).where(Leerlijst.profiel_id == 3)))
        paden = set(s.scalars(select(NotitieBestand.pad).where(NotitieBestand.profiel_id == 3)))
    assert u.notities == 0 and len(nep.verzoeken) == vragen
    assert "Zivilrecht 1A/1 Einführung und Grundlagen/Vorlesung.md" in herkomst & paden
    assert not any(p.startswith("Zivilrecht 1A/1 Einführung/") for p in herkomst | paden)
