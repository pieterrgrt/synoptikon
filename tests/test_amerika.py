"""Stelsels van Amerika: importers (met kleine fixtures, geen netwerk), citeerregels en stelsellijst."""
from pathlib import Path

from synoptikon.services.artikelen import herken, sleutel

FIX = Path(__file__).parent / "fixtures"


def test_justicelaws_sections_en_onderdelen():
    from synoptikon.importers import justicelaws

    g = justicelaws.parse((FIX / "justicelaws_interest.xml").read_bytes(), "I-15")
    assert (g.titel, g.versie) == ("Interest Act", "2008-06-18")
    assert [a.nummer for a in g.artikelen][:3] == ["1", "2", "3"]
    a = next(a for a in g.artikelen if a.nummer == "10")
    assert a.opschrift == "When no further interest payable"
    assert a.pad == "Interest on Moneys Secured by Mortgage on Real Property or Hypothec on Immovables"
    assert a.tekst.startswith("(1) Whenever any principal money")
    assert "\n\n    (a) to any mortgage on real property" in a.tekst


def test_justicelaws_constitution_acts():
    from synoptikon.importers import justicelaws

    html = (FIX / "justicelaws_const.html").read_text(encoding="utf-8")
    g = justicelaws.parse_const(html, "1867")
    assert g.versie == "2026-10-15" and g.titel == "Constitution Act, 1867"
    assert [(a.nummer, a.opschrift, a.pad) for a in g.artikelen][:2] == [("1", "Short title", "I. Preliminary"), ("2", None, "I. Preliminary")]
    assert g.artikelen[0].tekst == "This Act may be cited as the Constitution Act, 1867."  # zonder eindnoot
    g = justicelaws.parse_const(html, "1982")
    a = g.artikelen[1]
    assert (a.nummer, a.opschrift) == ("2", "Fundamental freedoms")
    assert a.pad == "PART I · Canadian Charter of Rights and Freedoms › Fundamental Freedoms"
    assert "\n\n(a) freedom of conscience and religion;" in a.tekst


def test_quebec_groepen_en_versie():
    from synoptikon.importers import quebec

    g = quebec.parse((FIX / "quebec_charte.xml").read_bytes(), "C-12")
    assert g.titel == "Charte des droits et libertés de la personne" and g.versie == "2026-10-01"
    a1, a2 = g.artikelen
    assert (a1.nummer, a2.nummer) == ("1", "2")
    assert a1.pad == "PARTIE I · LES DROITS ET LIBERTÉS DE LA PERSONNE › CHAPITRE I · LIBERTÉS ET DROITS FONDAMENTAUX"
    assert a1.tekst.endswith("\n\nIl possède également la personnalité juridique.")
    status = '"CCQ-1991", "À jour au 15 octobre 2026", "J", "20261015"\n"C-12", "À jour au 1er octobre 2026", "J", "20261001"\n'
    assert quebec.versie_uit_status(status, "CCQ-1991") == "2026-10-15"
    assert quebec.versie_uit_status(status, "P-40.1") is None


def test_verwijzingen_canada_en_quebec():
    def een(t):
        (r,) = herken(t)
        return r.stelsel, r.nummer, r.wet

    assert een("s 91 CA 1867") == ("CA", "91", "CA 1867")
    assert een("s 2 Constitution Act, 1867") == ("CA", "2", "CA 1867")
    assert een("s. 83.01 Criminal Code") == ("CA", "83.01", "Criminal Code")
    assert een("art. 1457 C.c.Q.") == ("QC", "1457", None)
    assert een("art. 1457 Code civil du Québec") == ("QC", "1457", None)
    assert een("art. 8 L.p.c.") == ("QC", "8", "L.p.c.")
    assert sleutel("QC", "521.1") > sleutel("QC", "521") and sleutel("CA", "90S.1") > sleutel("CA", "90")


def test_stelsels_amerika():
    from synoptikon.importers.register import WETTEN  # het register eerst: dat laadt register_amerika
    from synoptikon.models import RECHTSFAMILIES
    from synoptikon.seed.stelsels_amerika import STELSELS, SYSTEMATIEK

    codes = {s[0] for s in STELSELS}
    assert {s[5] for s in STELSELS} <= set(RECHTSFAMILIES)
    assert set(SYSTEMATIEK) <= codes and {"CA", "QC"} <= {w.stelsel for w in WETTEN}
    for code in codes:
        assert (Path(__file__).parent.parent / "synoptikon" / "static" / "vlaggen" / f"{code.lower()}.svg").exists()
