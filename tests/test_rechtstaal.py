"""De taal van het recht staat los van de interfacetaal (Profiel.rechtstaal).

Wie in Berlijn studeert wil de Duitse verdragstekst, 'AEUV' in plaats van 'VWEU' en Duitse kaarten, terwijl
Synoptikon zelf Nederlands blijft. Er wordt nooit vertaald: de Duitse versie wordt gekozen of bij de bron opgehaald.
"""
import pytest
from sqlalchemy import select

from synoptikon import db as database
from synoptikon import i18n
from synoptikon.config import settings
from synoptikon.models import Bron, Kaart, Leerlijst, Profiel, Wettekst, WettekstArtikel
from synoptikon.services import artikelen, correspondentie, herkennen, leren, opzoeken
from synoptikon.services.artikelen import Ref

from test_herkennen import NepNet

CELLAR_DE = '''"ecli","celex","datum","titel"
"ECLI:EU:C:2015:806","62014CJ0594",2015-12-10,"Urteil des Gerichtshofs (Sechste Kammer) vom 10. Dezember 2015.#Simona Kornhaas gegen Thomas Dithmar.#Vorabentscheidungsersuchen des Bundesgerichtshofs.#Vorlage zur Vorabentscheidung.#Rechtssache C-594/14."
'''


@pytest.fixture(autouse=True)
def schoon():
    """De rechtstaal is een ContextVar: na elke test weer leeg, anders lekt ze naar de volgende."""
    yield
    i18n.zet_rechtstaal(None)
    i18n.zet_taal("nl")


# --- de laag zelf -------------------------------------------------------------------------------------------------


def test_rechtstaal_volgt_de_interface_tenzij_ze_gezet_is():
    i18n.zet_taal("nl")
    assert i18n.rechtstaal() == "nl" and i18n.eigen_rechtstaal() == ""
    i18n.zet_rechtstaal("de")
    assert i18n.rechtstaal() == "de" and i18n.eigen_rechtstaal() == "de"
    i18n.zet_rechtstaal("klingon")  # onbekend: terug naar de interface
    assert i18n.rechtstaal() == "nl"


def test_in_taal_zet_de_interfacetaal_tijdelijk_om():
    i18n.zet_taal("nl")
    with i18n.in_taal("de"):
        assert i18n.taal() == "de"
    assert i18n.taal() == "nl"


def test_in_taal_herstelt_ook_na_een_fout():
    i18n.zet_taal("nl")
    with pytest.raises(ValueError):
        with i18n.in_taal("de"):
            raise ValueError
    assert i18n.taal() == "nl"


# --- welke taalversie van een verdrag -----------------------------------------------------------------------------


@pytest.fixture
def verdrag():
    """Hetzelfde artikel in het Nederlands en het Duits, zoals de EU-verdragen in de database staan."""
    with database.session() as s:
        for taal, titel, tekst in (("nl", "Verdrag betreffende de werking van de EU", "Beperkingen zijn verboden."),
                                   ("de", "Vertrag über die Arbeitsweise der EU", "Beschränkungen sind verboten.")):
            w = Wettekst(stelsel_code="EU", wet_id=f"test-vweu-{taal}", wet="VWEU", taal=taal, titel=titel,
                         versie="2026-01-01", kern=False, aantal=1)
            s.add(w)
            s.flush()
            s.add(WettekstArtikel(wettekst_id=w.id, nummer="49", tekst=tekst, volgorde=1))
        s.commit()
    yield
    with database.session() as s:
        for w in s.scalars(select(Wettekst).where(Wettekst.wet == "VWEU")).all():
            s.delete(w)
        s.commit()


@pytest.mark.parametrize("interface,recht,verwacht", [
    ("nl", None, "Beperkingen zijn verboden."),      # oud gedrag: de interface beslist
    ("nl", "de", "Beschränkungen sind verboten."),   # Pieters geval: Nederlandse interface, Duits recht
    ("de", None, "Beschränkungen sind verboten."),
    ("de", "nl", "Beperkingen zijn verboden."),
])
def test_verdragstekst_volgt_de_rechtstaal(verdrag, interface, recht, verwacht):
    i18n.zet_taal(interface)
    i18n.zet_rechtstaal(recht)
    with database.session() as s:
        wa = correspondentie.wettekst_artikel(s, Ref("EU", "49", "VWEU"))
    assert wa is not None and wa.tekst == verwacht


def test_afkorting_volgt_de_rechtstaal():
    i18n.zet_taal("nl")
    assert artikelen.wet_kort("EU", "VWEU") == "VWEU"
    i18n.zet_rechtstaal("de")
    assert artikelen.wet_kort("EU", "VWEU") == "AEUV"
    assert artikelen.wet_kort("EU", "Insolventieverordening") == "EuInsVO"
    assert artikelen.wet_kort("DE", "GmbHG") == "GmbHG"  # nationale wetten blijven zoals ze heten


# --- de kaart -----------------------------------------------------------------------------------------------------


def test_kaartzijden_staan_in_de_rechtstaal(verdrag):
    """De vaste zin op de voorkant hoort bij de wettekst, niet bij de interface."""
    with database.session() as s:
        lijst = Leerlijst(naam="Test rechtstaal", profiel_id=1, vak="GÖ")
        s.add(lijst)
        s.flush()
        k = Kaart(uid="test-rechtstaal-kaart", lijst_id=lijst.id, soort="artikel", stelsel_code="EU",
                  wet="VWEU", nummer="49")
        s.add(k)
        s.flush()

        i18n.zet_taal("nl")
        nl = leren.Bouwer(s).zijden(k)
        i18n.zet_rechtstaal("de")
        de = leren.Bouwer(s).zijden(k)

        s.delete(k)
        s.delete(lijst)
        s.commit()

    assert "Wat staat erin?" in nl.voor and "VWEU" in nl.voor
    assert "Beperkingen zijn verboden." in nl.achter
    assert "Wat staat erin?" not in de.voor and "AEUV" in de.voor
    assert "Beschränkungen sind verboten." in de.achter
    # en de interface is daarna weer Nederlands
    assert i18n.taal() == "nl"


# --- bij de bron ophalen ------------------------------------------------------------------------------------------


def test_eurlex_wordt_in_de_rechtstaal_opgehaald(monkeypatch):
    nep = NepNet(cellar_csv=CELLAR_DE)
    monkeypatch.setattr(herkennen, "verbinding", lambda: nep)
    r = herkennen.zoek(herkennen.herken_id("ECLI:EU:C:2015:806"), taal="de")
    assert r is not None
    assert r["citeer"].startswith("EuGH 10. Dezember 2015")       # niet 'HvJ EU 10 december 2015'
    assert r["titel"] == "Simona Kornhaas gegen Thomas Dithmar"
    assert "/legal-content/DE/TXT/" in r["url"]
    gevraagd = "".join(str(v) for _s, _u, v in nep.verzoeken)
    assert "language/DEU" in gevraagd and "language/NLD" not in gevraagd


def test_zonder_taal_volgt_het_ophalen_de_rechtstaal_van_het_verzoek(monkeypatch):
    nep = NepNet(cellar_csv=CELLAR_DE)
    monkeypatch.setattr(herkennen, "verbinding", lambda: nep)
    i18n.zet_taal("nl")
    i18n.zet_rechtstaal("de")
    r = herkennen.zoek(herkennen.herken_id("ECLI:EU:C:2015:806"))
    assert r and "language/DEU" in "".join(str(v) for _s, _u, v in nep.verzoeken)


@pytest.mark.parametrize("datum,taal,verwacht", [
    ("nl", "nl", "10 december 2015"),
    ("de", "de", "10. Dezember 2015"),
    ("es", "es", "10 de diciembre de 2015"),
])
def test_datum_in_een_citaat(datum, taal, verwacht):
    from datetime import date

    assert herkennen._datum(date(2015, 12, 10), taal) == verwacht


# --- wat er al stond ----------------------------------------------------------------------------------------------


@pytest.fixture
def bronnen():
    with database.session() as s:
        ids = []
        for stelsel, vindplaats, titel, taal, opmerking in (
                ("EU", "ECLI:EU:C:2015:806", "Niet vastgesteld", "nl", opzoeken.OPMERKING["claude"]),
                ("EU", "ECLI:EU:C:2007:623", "Commissie/Duitsland", "nl", opzoeken.OPMERKING["eigen"]),
                ("NL", "ECLI:NL:HR:2015:1", "HR 6 januari 2015", "nl", opzoeken.OPMERKING["rechtspraak"]),
        ):
            b = Bron(stelsel_code=stelsel, soort="rechtspraak", citeertitel=vindplaats, titel=titel, taal=taal,
                     vindplaats=vindplaats, opmerking=opmerking)
            s.add(b)
            s.flush()
            ids.append(b.id)
        s.commit()
    yield ids
    with database.session() as s:
        for i in ids:
            if (b := s.get(Bron, i)) is not None:
                s.delete(b)
        s.commit()


def test_hertaal_haalt_oude_uitspraken_opnieuw_op_en_laat_eigen_werk_staan(bronnen, monkeypatch):
    nep = NepNet(cellar_csv=CELLAR_DE)
    monkeypatch.setattr(herkennen, "verbinding", lambda: nep)
    with database.session() as s:
        proef = herkennen.hertaal(s, "de")
        assert proef.omgezet >= 1
        assert s.get(Bron, bronnen[0]).titel == "Niet vastgesteld"  # een proef schrijft niets

    with database.session() as s:
        herkennen.hertaal(s, "de", doen=True)

    with database.session() as s:
        om, eigen, nederlands = (s.get(Bron, i) for i in bronnen)
        assert om.titel == "Simona Kornhaas gegen Thomas Dithmar" and om.taal == "de"
        assert om.citeertitel.startswith("EuGH") and "Cellar" in (om.opmerking or "")
        assert eigen.titel == "Commissie/Duitsland"          # zelf nagekeken blijft staan
        assert nederlands.titel == "HR 6 januari 2015"       # een NL-uitspraak citeer je niet in het Duits


# --- de levering aan Wunderkammer --------------------------------------------------------------------------------


def test_wunderkammer_krijgt_de_kaarten_in_de_rechtstaal(anoniem, verdrag):
    with database.session() as s:
        p = s.get(Profiel, 1)
        p.wunderkammer, p.taal, p.rechtstaal = True, "nl", "de"
        lijst = Leerlijst(naam="Levering rechtstaal", profiel_id=p.id, vak="GÖ", naar_wk=True)
        s.add(lijst)
        s.flush()
        s.add(Kaart(uid="test-rechtstaal-levering", lijst_id=lijst.id, soort="artikel", stelsel_code="EU",
                    wet="VWEU", nummer="49"))
        lid, naam = lijst.id, p.gebruikersnaam
        s.commit()

    settings.wk_token = "k" * 32
    r = anoniem.get(f"/api/wk/kaarten?profiel={naam}", headers={"Authorization": f"Bearer {'k' * 32}"})
    assert r.status_code == 200, r.text
    tekst = r.text
    assert "AEUV" in tekst and "Beschränkungen sind verboten." in tekst
    assert "Wat staat erin?" not in tekst

    with database.session() as s:
        for k in s.scalars(select(Kaart).where(Kaart.lijst_id == lid)).all():
            s.delete(k)
        s.delete(s.get(Leerlijst, lid))
        s.get(Profiel, 1).rechtstaal = None
        s.commit()




def test_een_bron_in_de_verkeerde_taal_verliest_van_de_wettekst(verdrag):
    """Art. 49 AEUV stond als Nederlandse wetsbron bewaard en versloeg daarmee de Duitse wettekst."""
    from synoptikon.services.correspondentie import Context

    with database.session() as s:
        b = Bron(stelsel_code="EU", soort="wet", citeertitel="VWEU 49 (bewaard)", titel="VWEU", taal="nl",
                 vindplaats="VWEU 49", tekst="In het kader van de volgende bepalingen …")
        s.add(b)
        s.flush()

        i18n.zet_taal("nl")
        heen = Context(s).tekst(Ref("EU", "49", "VWEU"))
        i18n.zet_rechtstaal("de")
        terug = Context(s).tekst(Ref("EU", "49", "VWEU"))

        s.delete(b)
        s.commit()

    assert heen is not None and heen.tekst.startswith("In het kader")        # zonder rechtstaal wint de bron
    assert terug is not None and terug.tekst == "Beschränkungen sind verboten."
