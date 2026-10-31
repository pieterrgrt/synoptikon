"""Het bibliotheekoverzicht op de hoofdpagina: de cijfers, de boekenkast en de wereldkaart."""
import pytest
from sqlalchemy import select

from synoptikon import db as database
from synoptikon.models import Stelsel, Wettekst, WettekstArtikel
from synoptikon.services import bibliotheek


@pytest.fixture
def kast():
    """Een kleine kast: een Duitse wet, een Franse, en de EU met een taalvariant erbij."""
    gemaakt = []
    with database.session() as s:
        for wet_id, stelsel, wet, titel, aantal in (
                ("test-bib-de", "DE", "TESTG", "Testgesetz", 40),
                ("test-bib-fr", "FR", None, "Code de test", 10),
                ("test-bib-eu", "EU", "TESTVO", "Test-Verordnung", 7),
                ("test-bib-eu.nl", "EU", "TESTVO", "Testverordening", 7),   # taalvariant: telt niet mee
        ):
            w = Wettekst(stelsel_code=stelsel, wet_id=wet_id, wet=wet, titel=titel, versie="2026-01-01", kern=False)
            s.add(w)
            s.flush()
            gemaakt.append(w.id)
            for i in range(aantal):
                s.add(WettekstArtikel(wettekst_id=w.id, nummer=str(i + 1), tekst=f"Tekst {i + 1}", volgorde=i))
        s.commit()
    bibliotheek._cache.clear()
    yield
    with database.session() as s:
        for i in gemaakt:
            if (w := s.get(Wettekst, i)) is not None:
                s.delete(w)
        s.commit()
    bibliotheek._cache.clear()


def test_taalvarianten_tellen_niet_dubbel(kast):
    """De EU-verdragen staan er in zes talen; die mogen niet zesmaal in de kast staan."""
    with database.session() as s:
        o = bibliotheek.overzicht(s, vernieuw=True)
    eu = next(l for l in o.landen if l.code == "EU")
    assert eu.wetten == 1 and eu.artikelen == 7


def test_overzicht_telt_wetten_artikelen_en_stelsels(kast):
    with database.session() as s:
        o = bibliotheek.overzicht(s, vernieuw=True)
        stelsels = s.scalar(select(__import__("sqlalchemy").func.count()).select_from(Stelsel))
    assert o.wetten >= 3 and o.artikelen >= 57
    assert o.stelsels_totaal == stelsels
    assert 0 < o.stelsels <= o.stelsels_totaal
    assert not o.leeg


def test_elke_rug_verwijst_naar_een_wettekst(kast):
    with database.session() as s:
        o = bibliotheek.overzicht(s, vernieuw=True)
        for sch in o.schappen:
            for r in sch.ruggen:
                assert s.get(Wettekst, r.wettekst_id) is not None
                assert r.url == f"/wetteksten/{r.wettekst_id}"
                assert r.artikelen > 0 and r.naam


def test_schappen_staan_in_de_orde_van_de_taxonomie(kast):
    from synoptikon.models import RECHTSFAMILIES

    with database.session() as s:
        o = bibliotheek.overzicht(s, vernieuw=True)
    orde = list(RECHTSFAMILIES)
    gezien = [sch.sleutel for sch in o.schappen]
    assert gezien == sorted(gezien, key=orde.index)
    assert all(sch.ruggen for sch in o.schappen), "een leeg schap hoort niet in de kast"


def test_een_schap_meldt_hoeveel_wetten_er_niet_op_passen(kast, monkeypatch):
    monkeypatch.setattr(bibliotheek, "RUGGEN", 1)
    with database.session() as s:
        o = bibliotheek.overzicht(s, vernieuw=True)
    for sch in o.schappen:
        assert len(sch.ruggen) == 1
        assert sch.rest == sch.wetten - 1


def test_lege_stelsels_staan_wel_op_de_kaart(kast):
    """Een stelsel zonder tekst is een omtrek zonder vulling, niet een gat in de kaart."""
    with database.session() as s:
        o = bibliotheek.overzicht(s, vernieuw=True)
    leeg = [l for l in o.landen if l.leeg]
    assert leeg and all(l.tint == 0.0 for l in leeg)
    assert all(l.tint > 0 for l in o.landen if not l.leeg)


@pytest.mark.parametrize("artikelen,grootste,ondergrens,bovengrens", [
    (0, 100, 1.6, 1.6),        # niets: de smalste rug
    (100, 100, 5.0, 5.0),      # de grootste wet: de breedste
    (25, 100, 2.0, 4.0),       # een kwart van de artikelen is de helft van de breedte (wortel)
])
def test_rugbreedte_loopt_op_de_wortel(artikelen, grootste, ondergrens, bovengrens):
    b = bibliotheek.rugbreedte(artikelen, grootste)
    assert ondergrens <= b <= bovengrens


def test_rugbreedte_houdt_de_staart_leesbaar():
    """Code de commerce is 2.400x zo groot als een wet van 3 artikelen; lineair zou die een haarlijn zijn."""
    groot = bibliotheek.rugbreedte(7254, 7254)
    klein = bibliotheek.rugbreedte(3, 7254)
    assert groot == 5.0 and klein >= 1.6 and klein / groot > 0.3


def test_tint_blijft_tussen_nul_en_een():
    assert bibliotheek.tint(0, 100) == 0.0
    assert bibliotheek.tint(100, 100) == 1.0
    assert bibliotheek.tint(500, 100) == 1.0   # nooit boven 1, ook niet bij een rare verhouding


def test_een_klein_stelsel_blijft_zichtbaar_naast_een_groot():
    """Engeland & Wales (595 art.) naast Duitsland (107.000) mag niet op leeg gaan lijken."""
    klein = bibliotheek.tint(595, 106986)
    assert klein >= bibliotheek.TINT_ONDER
    assert bibliotheek.tint(0, 106986) == 0.0, "leeg blijft echt leeg, anders is het onderscheid weg"
    assert klein < bibliotheek.tint(32564, 106986) or klein == bibliotheek.TINT_ONDER


# --- de kaart -----------------------------------------------------------------------------------------------------


def test_de_wereldkaart_is_gebouwd_en_dekt_elk_stelsel():
    """`scripts/bouw_wereldkaart.py` schrijft static/kaart/wereld.json; elk stelsel hoort een vorm te hebben."""
    k = bibliotheek.kaart()
    assert k["landen"], "wereld.json ontbreekt of is leeg"
    assert round(k["breedte"] / k["hoogte"], 2) == 2.05, "Equal Earth heeft een vaste verhouding"
    with database.session() as s:
        codes = [c for (c,) in s.execute(select(Stelsel.code)).all()]
    zonder = [c for c in codes if not k["landen"].get(c)]
    assert zonder == [], f"stelsels zonder vorm op de kaart: {zonder}"


def test_de_kaart_heeft_losse_vormen_voor_quebec_engeland_en_de_eu():
    """CA en QC zijn twee stelsels op één landmassa, EN zit in het VK, en de EU is de lidstaten samen."""
    landen = bibliotheek.kaart()["landen"]
    assert landen["QC"] != landen["CA"]
    assert landen["EN"] and landen["EN"] != landen.get("GB")
    assert landen["EU"].count("M") > 20, "de EU is opgebouwd uit de lidstaten"


def test_de_kaartpaden_blijven_binnen_het_kader():
    import re

    k = bibliotheek.kaart()
    for code, pad in k["landen"].items():
        xy = [(float(x), float(y)) for x, y in re.findall(r"[ML](-?[\d.]+) (-?[\d.]+)", pad)]
        assert xy, code
        assert all(-0.01 <= x <= k["breedte"] + 0.01 for x, _ in xy), code
        assert all(-0.01 <= y <= k["hoogte"] + 0.01 for _, y in xy), code


# --- de pagina ----------------------------------------------------------------------------------------------------


def test_de_hoofdpagina_toont_de_kast_en_de_kaart(client, kast):
    bibliotheek._cache.clear()
    h = client.get("/").text
    assert 'class="bibliotheek"' in h and 'class="kast"' in h
    assert "Testgesetz" in h or "TESTG" in h
    assert 'class="wereld"' in h and 'viewBox="0 0 5.413 2.636"' in h
    assert 'href="/stelsels/DE"' in h
    assert 'class="vraaglijst"' in h or "Nog geen vragen" in h, "de vragenlijst blijft de hoofdpagina"
