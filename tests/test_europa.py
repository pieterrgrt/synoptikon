"""Importers, citeerregels en seed van de Europese uitbreiding (register_europa, stelsels_europa, regels_europa)."""
from pathlib import Path

FIX = Path(__file__).parent / "fixtures"


def _herken(t: str) -> list[tuple]:
    from synoptikon.services.artikelen import herken

    return [(r.stelsel, r.nummer, r.wet) for r in herken(t)]


def test_ris_kschg():
    from synoptikon.importers import ris

    g = ris.parse((FIX / "ris_kschg.html").read_text(encoding="utf-8"), "10002462")
    assert g.versie == "BGBl. I Nr. 60/2026"
    assert g.titel.endswith("(Konsumentenschutzgesetz – KSchG)")
    per = {a.nummer: a for a in g.artikelen}
    assert {"1", "2", "3"} <= set(per)
    assert "32" not in per  # "Art. 32" (overgangsrecht van een wijzigingswet) valt buiten de §-reeks
    a3 = per["3"]
    assert a3.opschrift == "Rücktrittsrecht"
    assert a3.pad.endswith("› Abschnitt II Allgemeine Regeln")
    assert a3.tekst.startswith("(1) Hat der Verbraucher seine Vertragserklärung")
    assert "Absatz eins" not in a3.tekst  # voorleestekst weg
    assert "\n1. einerseits jemand" in per["1"].tekst


def test_ris_kopniveaus():
    from synoptikon.importers import ris

    assert ris._niveau("Zweyter Theil") == 1
    assert ris._niveau("Erste Abtheilung des Sachenrechtes.") == 2
    assert ris._niveau("Vier u. zwanzigstes Hauptstück. Von dem Kaufvertrage.") == 3
    assert ris._niveau("Zweiter Abschnitt Abstammung des Kindes") == 4
    assert ris._niveau("des") is None


def test_oostenrijkse_verwijzingen():
    assert _herken("§ 1295 ABGB") == [("AT", "1295", None)]
    assert _herken("§ 6 Abs. 1 KSchG") == [("AT", "6", "KSchG")]
    assert _herken("§ 879 Allgemeines bürgerliches Gesetzbuch") == [("AT", "879", None)]
    assert _herken("§ 929 BGB") == [("DE", "929", None)]


def test_seed_europa_vorm():
    from synoptikon.models import RECHTSFAMILIES
    from synoptikon.services.artikelen import parse_bereik
    from synoptikon.seed import stelsels_europa as s

    codes = [st[0] for st in s.STELSELS]
    assert len(codes) == len(set(codes))
    families = RECHTSFAMILIES if isinstance(RECHTSFAMILIES, (list, tuple, set)) else list(RECHTSFAMILIES)
    for code, naam, taal, toelichting, actief, familie in s.STELSELS:
        assert familie in families, (code, familie)
        assert (Path(__file__).parent.parent / "synoptikon" / "static" / "vlaggen" / f"{code.lower()}.svg").exists(), code

    def loop(stelsel, knopen):
        for k in knopen:
            assert k[2] == "" or parse_bereik(stelsel, k[2]) is not None, (stelsel, k[0], k[2])
            loop(stelsel, k[3])

    for code, boom in s.SYSTEMATIEK.items():
        assert code in codes
        loop(code, boom)


def test_vertalingen_stelsels_europa():
    import json

    from synoptikon.seed import stelsels_europa as s

    for taal in ("de", "en", "fr", "it", "es"):
        d = json.loads((Path(__file__).parent.parent / "synoptikon" / "seed" / "vertalingen" / f"{taal}.json").read_text(encoding="utf-8"))
        for code, naam, _, toelichting, *_ in s.STELSELS:
            assert naam in d and toelichting in d, (taal, code)


def test_retsinformation_aftl():
    from synoptikon.importers import retsinformation

    g = retsinformation.parse((FIX / "retsinformation_aftl.xml").read_bytes(), "lta/2016/193")
    assert g.versie == "LBK nr 193 af 2016-03-02"
    per = {a.nummer: a for a in g.artikelen}
    assert set(per) == {"1", "9 a", "36"}
    assert per["36"].pad == "III. Om ugyldige viljeserklæringer"
    assert per["36"].tekst.startswith("En aftale kan ændres eller tilsidesættes")
    assert "Stk. 2." in per["36"].tekst


def test_deense_verwijzingen():
    assert _herken("§ 36 aftl.") == [("DK", "36", "aftl.")]
    assert _herken("§ 4 a kbl.") == [("DK", "4 a", "kbl.")]
    assert _herken("§ 76, stk. 1, kbl.") == [("DK", "76", "kbl.")]


def test_finlex_ksl():
    from synoptikon.importers import finlex

    g = finlex.parse((FIX / "finlex_ksl.xml").read_bytes(), "1978/38")
    assert g.titel == "Kuluttajansuojalaki"
    assert g.versie == "ajantasa 2026-09-04 (835/2026)"  # de jongste van de twee Finse standen, niet de Zweedse
    per = {a.nummer: a for a in g.artikelen}
    assert {"1:1", "1:6", "2:2", "5:1", "5 a:1"} <= set(per)  # nummering per hoofdstuk
    assert per["5:1"].pad == "5 luku Tavarankauppa › Yleiset säännökset tavarankaupasta"
    assert per["2:2"].opschrift == "Markkinoinnin hyvän tavan vastaisuus"
    assert "\n1) se loukkaa ihmisarvoa" in per["2:2"].tekst
    assert per["1:6"].tekst == "6 § on kumottu L:lla 5.1.1994/16."
    assert b"swe@" not in g.ruw[:2000]


def test_finse_verwijzingen():
    assert _herken("OikTL 36 §") == [("FI", "36", "OikTL")]
    assert _herken("RL 21:1") == [("FI", "21:1", "RL")]
    assert _herken("KSL 7 a:14 a") == [("FI", "7 a:14 a", "KSL")]


def test_lovdata_tvl():
    from synoptikon.importers import lovdata

    g = lovdata.parse((FIX / "lovdata_tvl.xml").read_bytes(), "2005-06-17-90")
    assert g.versie == "endret ved lov/2026-06-19-45 fra 2026-07-01"
    per = {a.nummer: a for a in g.artikelen}
    assert set(per) == {"1-1", "1-3", "4-1"}
    assert per["1-1"].opschrift == "Lovens formål"
    assert per["1-1"].pad.endswith("› Kapittel 1. Lovens formål og anvendelse")
    assert "\n- partene få argumentere for sin sak og føre bevis," in per["1-1"].tekst
    assert "Endret ved lov" not in per["1-3"].tekst
    assert lovdata._bestand("1918-05-31-4") == "nl/nl-19180531-004.xml"


def test_noorse_verwijzingen():
    assert _herken("avtl. § 36") == [("NO", "36", "avtl.")]
    assert _herken("tvl. § 1-1") == [("NO", "1-1", "tvl.")]


def test_riksdagen_kkl():
    from synoptikon.importers import riksdagen

    g = riksdagen.parse((FIX / "riksdagen_kkl.json").read_bytes(), "sfs-2022-260")
    assert g.titel == "Konsumentköplag (2022:260)"
    assert g.versie == "t.o.m. SFS 2023:732"
    per = {a.nummer: a for a in g.artikelen}
    assert set(per) == {"1:1", "1:2", "1:3", "5:1"}  # nummering per hoofdstuk; overgangsbepalingen vallen weg
    assert per["1:1"].opschrift == "Lagens innehåll"  # kop boven één paragraaf (in de fixture ook bij 1:3)
    assert per["1:3"].pad == "1 kap. Grundläggande bestämmelser"
    assert "\n\ndigitalt innehåll: data som" in per["1:2"].tekst
    assert "<" not in per["1:2"].tekst


def test_zweedse_verwijzingen():
    assert _herken("36 § AvtL") == [("SE", "36", "AvtL")]
    assert _herken("BrB 3:1") == [("SE", "3:1", "BrB")]


def test_poolse_verwijzingen():
    assert _herken("art. 415 KC") == [("PL", "415", None)]
    assert _herken("art. 22¹ KC") == [("PL", "22¹", None)]
    assert _herken("art. 299 KSH") == [("PL", "299", "KSH")]


def test_pgdl_cc():
    from synoptikon.importers import pgdl

    g = pgdl.parse((FIX / "pgdl_cc.html").read_bytes(), "775")
    assert g.versie == "Lei n.º 29/2026, de 23/06"
    per = {a.nummer: a for a in g.artikelen}
    assert set(per) == {"1", "2", "3", "85"}
    assert per["1"].opschrift == "Fontes imediatas"
    assert per["85"].opschrift == "Domicílio legal dos menores e dos maiores acompanhados"  # opschrift zonder haakjes
    assert per["1"].pad == "Livro I · Parte geral › Título I · Das leis, sua interpretação e aplicação › Capítulo I · Fontes do direito"
    assert per["1"].tekst.startswith("1. São fontes imediatas do direito")
    assert "\n2. Consideram-se leis" in per["1"].tekst


def test_portugese_verwijzingen():
    assert ("PT", "405", None) in _herken("art. 405.º CC")
    assert _herken("art. 13.º CRP") == [("PT", "13", "CRP")]
