"""`/bewaard`: de wetsartikelen en uitspraken die jij zelf bewaarde, per vak."""
import pytest
from sqlalchemy import select

from synoptikon import db as database
from synoptikon.models import Bron, Kaart, Leerlijst, Markering, Wettekst, WettekstArtikel
from synoptikon.services import bewaard


@pytest.fixture
def materiaal():
    """Twee vakken met kaarten, een zelf bewaarde wetsbron zonder vak, en een markering."""
    weg = {"kaart": [], "lijst": [], "bron": [], "mark": [], "wettekst": []}
    with database.session() as f:
        w = Wettekst(stelsel_code="DE", wet_id="test-bewaard-bgb", titel="BGB", versie="2026-01-01", kern=False)
        f.add(w)
        f.flush()
        weg["wettekst"].append(w.id)
        for nr in ("90", "929", "823"):
            f.add(WettekstArtikel(wettekst_id=w.id, nummer=nr, opschrift=f"Opschrift {nr}", tekst=f"Text {nr}", volgorde=0))

        for naam, vak, nummers in (("ZR", "ZR Ia", ["929", "90"]), ("SR", "Sachenrecht", ["929"])):
            l = Leerlijst(naam=f"Test {naam}", profiel_id=1, vak=vak)
            f.add(l)
            f.flush()
            weg["lijst"].append(l.id)
            for i, nr in enumerate(nummers):
                k = Kaart(uid=f"test-bewaard-{naam}-{nr}", lijst_id=l.id, soort="artikel", stelsel_code="DE", nummer=nr)
                f.add(k)
                f.flush()
                weg["kaart"].append(k.id)

        # een uitspraak met een kaart in ZR Ia
        b = Bron(stelsel_code="DE", soort="rechtspraak", citeertitel="BGHZ 63, 369", vindplaats="BGHZ 63, 369", taal="de")
        f.add(b)
        f.flush()
        weg["bron"].append(b.id)
        k = Kaart(uid="test-bewaard-arrest", lijst_id=weg["lijst"][0], soort="arrest", bron_id=b.id)
        f.add(k)
        f.flush()
        weg["kaart"].append(k.id)

        # een zelf bewaarde wetsbron die aan geen enkel vak hangt
        wb = Bron(stelsel_code="DE", soort="wet", citeertitel="§ 823 BGB", titel="Schadensersatzpflicht",
                  tekst="Wer vorsätzlich …", taal="de")
        f.add(wb)
        f.flush()
        weg["bron"].append(wb.id)

        m = Markering(profiel_id=1, stelsel_code="DE", nummer="929", quote="Übergabe", vak="ZR Ia", soort="kern")
        f.add(m)
        f.flush()
        weg["mark"].append(m.id)
        f.commit()
    yield
    with database.session() as f:
        for soort, model in (("kaart", Kaart), ("mark", Markering), ("lijst", Leerlijst), ("bron", Bron),
                             ("wettekst", Wettekst)):
            for i in weg[soort]:
                if (o := f.get(model, i)) is not None:
                    f.delete(o)
        f.commit()


def test_groepen_per_vak(materiaal):
    with database.session() as s:
        ov = bewaard.overzicht(s, 1)
    vakken = [g.vak for g in ov.groepen]
    assert "ZR Ia" in vakken and "Sachenrecht" in vakken
    assert vakken[-1] == bewaard.ZONDER_VAK, "wat geen vak heeft staat onderaan"


def test_hetzelfde_artikel_in_twee_vakken_is_een_regel_per_vak(materiaal):
    """§ 929 zit in ZR Ia en in Sachenrecht; het is één artikel, dat in beide groepen staat."""
    with database.session() as s:
        ov = bewaard.overzicht(s, 1)
    per_vak = {g.vak: [a.nummer for a in g.artikelen] for g in ov.groepen}
    assert "929" in per_vak["ZR Ia"] and "929" in per_vak["Sachenrecht"]
    assert per_vak["ZR Ia"].count("929") == 1
    assert per_vak["Sachenrecht"] == ["929"]
    # drie kaarten naar twee artikelen: § 929 is één artikel, geen twee regels in dezelfde groep
    nummers = [a.nummer for g in ov.groepen for a in g.artikelen if a.nummer in ("90", "929")]
    assert sorted(nummers) == ["90", "929", "929"], "eenmaal per vak, niet eenmaal per kaart"


def test_herkomst_vertelt_waarom_het_artikel_er_staat(materiaal):
    with database.session() as s:
        ov = bewaard.overzicht(s, 1)
    zr = next(g for g in ov.groepen if g.vak == "ZR Ia")
    a929 = next(a for a in zr.artikelen if a.nummer == "929")
    assert a929.kaarten == 2 and a929.markeringen == 1   # een kaart in elk vak, plus de markering
    assert any("kaart" in h for h in a929.herkomst) and any("markering" in h for h in a929.herkomst)

    geen_vak = next(g for g in ov.groepen if g.vak == bewaard.ZONDER_VAK)
    a823 = next(a for a in geen_vak.artikelen if a.nummer == "823")
    assert a823.bron_id and "zelf bewaard" in a823.herkomst and a823.kaarten == 0


def test_artikelen_staan_op_nummer_en_niet_alfabetisch(materiaal):
    """§ 929 hoort na § 90, niet ervoor."""
    with database.session() as s:
        ov = bewaard.overzicht(s, 1)
    zr = next(g for g in ov.groepen if g.vak == "ZR Ia")
    assert [a.nummer for a in zr.artikelen] == ["90", "929"]


def test_de_wettekst_wordt_erbij_gezocht(materiaal):
    with database.session() as s:
        ov = bewaard.overzicht(s, 1)
    zr = next(g for g in ov.groepen if g.vak == "ZR Ia")
    a = next(a for a in zr.artikelen if a.nummer == "929")
    assert a.heeft_tekst and a.opschrift == "Opschrift 929"
    assert a.citeer.startswith("§ 929") and a.url == "/artikelen/DE/929"


def test_uitspraken_staan_bij_hun_vak(materiaal):
    with database.session() as s:
        ov = bewaard.overzicht(s, 1)
    zr = next(g for g in ov.groepen if g.vak == "ZR Ia")
    assert [u.citeertitel for u in zr.uitspraken] == ["BGHZ 63, 369"]
    assert ov.uitspraken == 1
    sr = next(g for g in ov.groepen if g.vak == "Sachenrecht")
    assert sr.uitspraken == []


def test_filter_op_een_vak(materiaal):
    with database.session() as s:
        ov = bewaard.overzicht(s, 1, vak="Sachenrecht")
    assert [g.vak for g in ov.groepen] == ["Sachenrecht"]


def test_materiaal_van_een_ander_profiel_blijft_buiten(materiaal):
    """Kaarten en markeringen zijn van een profiel; bewaarde wetsbronnen zijn gedeeld en blijven dus zichtbaar."""
    with database.session() as s:
        ov = bewaard.overzicht(s, 999)
    assert all(g.vak == bewaard.ZONDER_VAK for g in ov.groepen)
    assert not any(a.kaarten or a.markeringen for g in ov.groepen for a in g.artikelen)
    assert ov.uitspraken == 0


def test_de_pagina_toont_de_vakken_en_de_artikelen(client, materiaal):
    h = client.get("/bewaard").text
    assert "ZR Ia" in h and "Sachenrecht" in h
    assert "§ 929" in h and "§ 90" in h and "Opschrift 929" in h
    assert 'href="/artikelen/DE/929"' in h
    assert "BGHZ 63, 369" in h
    assert 'class="vaktabs"' in h


def test_de_pagina_kan_op_een_vak_filteren(client, materiaal):
    h = client.get("/bewaard?vak=Sachenrecht").text
    assert "Sachenrecht" in h and "§ 929" in h
    assert "§ 90" not in h, "§ 90 zit alleen in ZR Ia"
    assert "ZR Ia" in h, "de tab van het andere vak blijft staan, anders kun je niet terug"


def test_bewaard_staat_in_de_navigatie(client):
    assert 'href="/bewaard"' in client.get("/").text
