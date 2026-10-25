from pathlib import Path

import pytest

from synoptikon.importers import ImportOvergeslagen, bwb, eurlex, gii, legifrance

FIX = Path(__file__).parent / "fixtures"


def test_bwb_parse():
    g = bwb.parse((FIX / "bwb_boek3.xml").read_bytes(), "BWBR0005291")
    assert g.titel == "Burgerlijk Wetboek Boek 3"
    assert g.versie == "2024-01-01"
    nummers = [a.nummer for a in g.artikelen]
    assert nummers == ["3:84", "3:85", "3:90"]
    a84 = g.artikelen[0]
    assert a84.tekst.startswith("1. Voor overdracht van een goed")
    assert "2. Bij de titel" in a84.tekst
    assert a84.pad == "Boek 3 Vermogensrecht in het algemeen › Titel 4 Verkrijging en verlies van goederen › Afdeling 2 Overdracht"
    assert g.artikelen[1].tekst == "Enkele alinea."


def test_gii_parse():
    g = gii.parse((FIX / "gii_bgb.xml").read_bytes(), "bgb")
    assert g.titel == "Bürgerliches Gesetzbuch"
    assert g.versie.startswith("2024-09-15")
    assert [a.nummer for a in g.artikelen] == ["929", "930"]
    a = g.artikelen[0]
    assert a.opschrift == "Einigung und Übergabe"
    assert a.pad == "Buch 3 Sachenrecht › Abschnitt 3 Eigentum"
    assert a.tekst.startswith("Zur Übertragung des Eigentums") and "\n\n" in a.tekst


def test_gii_parse_zip(tmp_path):
    import zipfile

    z = tmp_path / "xml.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(FIX / "gii_bgb.xml", "BJNR001950896.xml")
    g = gii.parse_zip(z.read_bytes(), "bgb")
    assert len(g.artikelen) == 2


def test_eurlex_parse():
    g = eurlex.parse((FIX / "eurlex_romeII.html").read_text(encoding="utf-8"), "32007R0864")
    assert "ROME II" in g.titel
    arts = {a.nummer: a for a in g.artikelen}
    assert set(arts) == {"12", "13", "14"}
    assert arts["12"].opschrift == "Culpa in contrahendo"
    assert arts["12"].tekst.startswith("1. The law applicable")
    assert "paragraph 1" in arts["12"].tekst
    assert arts["12"].pad == "CHAPTER III › UNJUST ENRICHMENT, NEGOTIORUM GESTIO AND CULPA IN CONTRAHENDO"
    assert arts["14"].opschrift == "Freedom of choice"  # oude opmaak zonder eli-subdivision


def test_legifrance_slaat_over_zonder_sleutel(monkeypatch):
    monkeypatch.setattr(legifrance.settings, "legifrance_client_id", None)
    with pytest.raises(ImportOvergeslagen):
        legifrance.haal_op("LEGITEXT000006070721", ["1196"])


def test_legifrance_html_naar_tekst():
    t = legifrance.html_naar_tekst("<p>Dans les contrats&nbsp;…</p><p>Ce transfert peut être différé.</p>")
    assert t == "Dans les contrats\xa0…\n\nCe transfert peut être différé."


def test_store_en_zoekindex():
    from synoptikon import db as database
    from synoptikon.importers import store
    from synoptikon.services.zoeken import zoek

    g = gii.parse((FIX / "gii_bgb.xml").read_bytes(), "bgb")
    with database.session() as s:
        w = store.sla_op(s, "DE", g)
        assert w.bestand and (database.settings.wetteksten_dir / w.bestand).exists()
        assert len(w.artikelen) == 2
        res = zoek(s, "Besitzkonstitut")
        assert any(t.titel.endswith("930") for t in res.wetteksten)
        # opnieuw opslaan van dezelfde versie vervangt in plaats van dupliceert
        store.sla_op(s, "DE", g)
        from sqlalchemy import select

        from synoptikon.models import Wettekst

        assert len(s.scalars(select(Wettekst).where(Wettekst.wet_id == "bgb")).all()) == 1
