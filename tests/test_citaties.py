"""Verwijzingen in lopende tekst: ketens, leden, bereiken, de wet erachter, en wat er géén verwijzing is."""
import pytest

from synoptikon.services import citaties


def _cit(tekst, stelsel=None):
    return [[e.ref.citeer if e.ref else None for e in v.elementen] for v in citaties.vind(tekst, stelsel)]


@pytest.mark.parametrize("tekst, verwacht", [
    ("K könnte gegen V einen Anspruch aus § 433 I 1 BGB haben.", [["§ 433 Abs. 1 S. 1 BGB"]]),
    ("Anspruch aus §§ 280 I, III, 281 BGB.", [["§ 280 Abs. 1 BGB", "§ 281 BGB"]]),
    ("§§ 280 Abs. 1, 3, 281 BGB", [["§ 280 Abs. 1 BGB", "§ 281 BGB"]]),
    ("c.i.c., §§ 280 I, 311 II, 241 II BGB", [["§ 280 Abs. 1 BGB", "§ 311 Abs. 2 BGB", "§ 241 Abs. 2 BGB"]]),
    ("§ 280 I i.V.m. § 241 II BGB", [["§ 280 Abs. 1 BGB", "§ 241 Abs. 2 BGB"]]),
    ("§ 812 I 1 Alt. 1 BGB", [["§ 812 Abs. 1 S. 1 Alt. 1 BGB"]]),
    ("gemäß §§ 929 bis 931 BGB", [["§§ 929–931 BGB"]]),
    ("§ 437 Nr. 2 BGB", [["§ 437 Nr. 2 BGB"]]),
    ("§§ 106, 107, 108 I BGB", [["§ 106 BGB", "§ 107 BGB", "§ 108 Abs. 1 BGB"]]),
    ("Zie art. 6:162 lid 2 BW.", [["art. 6:162 lid 2 BW"]]),
    ("artikel 6:74 jo. 6:81 BW", [["art. 6:74 BW", "art. 6:81 BW"]]),
    ("artt. 3:296 en 3:297 BW", [["art. 3:296 BW", "art. 3:297 BW"]]),
    ("art. 7:17 lid 2 en 5 BW", [["art. 7:17 lid 2 BW"]]),
    ("l'article 1240 du Code civil", [["art. 1240 C. civ."]]),
    ("articles 1112 à 1112-2 C. civ.", [["art. 1112–1112-2 C. civ."]]),
    ("art. L. 217-3 C. consom.", [["art. L217-3 C. consom."]]),
])
def test_ketens(tekst, verwacht):
    assert _cit(tekst) == verwacht


def test_leden_apart():
    v = citaties.vind("§§ 280 Abs. 1, 3, 281 BGB")[0]
    assert [d.lid for d in v.elementen[0].details] == ["1", "3"] and v.elementen[1].details == []
    v = citaties.vind("§ 199 Abs. 1 Nr. 2, Abs. 3 S. 1 Nr. 1 BGB")[0]
    assert [(d.lid, d.zin, d.nr) for d in v.elementen[0].details] == [("1", None, "2"), ("3", "1", "1")]
    v = citaties.vind("art. 7:17 lid 2 en 5 BW")[0]
    assert [d.lid for d in v.elementen[0].details] == ["2", "5"]
    v = citaties.vind("§§ 987 ff. BGB")[0]
    assert v.elementen[0].ff and v.elementen[0].ref.nummer == "987"


def test_wet_overnemen_en_standaard():
    eerste, tweede = citaties.vind("Anspruch aus § 812 I 1 Alt. 1 BGB und § 985.")
    assert not eerste.aangenomen and tweede.aangenomen and tweede.refs[0].citeer == "§ 985 BGB"
    assert not tweede.ruw.endswith(".")
    # zonder wet en zonder vorige verwijzing: het standaardstelsel
    assert _cit("Voraussetzung ist § 119 II.", "DE") == [["§ 119 Abs. 2 BGB"]]
    # een nieuwe alinea neemt de wet van de vorige niet over
    los = citaties.vind("Zie art. 6:162 BW.\n\nDaarna art. 5.", None)
    assert los[1].refs == []


def test_geen_verwijzing_liever_dan_een_foute():
    # een afkorting die geen bekende wet is, wordt niet stil het BGB
    v = citaties.vind("nach § 2 FantasieG")[0]
    assert v.refs == [] and v.onbekend == "FantasieG"
    # "Art und Weise" is geen artikel; een gewoon woord na de § is geen wet
    assert _cit("Die Art und Weise der Lieferung") == []
    v = citaties.vind("wie § 119 II greift. Die Art der Sache", "DE")[0]
    assert v.ruw == "§ 119 II" and v.wet_tekst is None
    # de punt van een zin hoort niet bij "BGB", wel bij "C. civ."
    assert citaties.vind("nach § 823 Abs. 1 BGB.")[0].ruw == "§ 823 Abs. 1 BGB"
    assert citaties.vind("art. 1240 C. civ. dispose")[0].ruw == "art. 1240 C. civ."


def test_koppel_md():
    uit = citaties.koppel_md("Anspruch aus §§ 280 I, III, 281 BGB und § 985 BGB.")
    assert "[280 I, III](/artikelen/DE/280?lid=Abs.%201)" in uit and "[281](/artikelen/DE/281)" in uit
    assert "[§ 985 BGB](/artikelen/DE/985)." in uit
    # alleen wat bestaat wordt een link
    assert citaties.koppel_md("§ 985 BGB", bestaat=lambda r: False) == "§ 985 BGB"
    # een bestaande link blijft zoals hij is
    al = "[§ 985 BGB](/artikelen/DE/985)"
    assert citaties.koppel_md(al) == al
