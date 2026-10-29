"""Azië en Oceanië: parsers (kleine fixtures, geen netwerk) en Oost-Aziatische citeerwijze."""
from pathlib import Path

from synoptikon.services.artikelen import herken, lees, sleutel

FIX = Path(__file__).parent / "fixtures"


def _refs(t: str) -> list[tuple]:
    return [(r.stelsel, r.wet, r.nummer) for r in herken(t)]


def test_egov_parse():
    """JP: 編/章/節 als pad, ArticleCaption als opschrift, Num="6_2" → 6の2, zinnen zonder spatie, versie uit revision_info."""
    from synoptikon.importers import egov

    g = egov.parse((FIX / "egov_shohisha.xml").read_bytes(), "412AC0000000061")
    assert (g.titel, g.versie) == ("消費者契約法", "2026-06-24")
    nrs = [a.nummer for a in g.artikelen]
    assert nrs[:3] == ["1", "2", "3"] and "6の2" in nrs
    a = g.artikelen[0]
    assert (a.opschrift, a.pad) == ("目的", "第一章 総則")
    vier = next(a for a in g.artikelen if a.nummer == "4")
    assert vier.pad == "第二章 消費者契約 › 第一節 消費者契約の申込み又はその承諾の意思表示の取消し"
    assert "\n    一 重要事項について事実と異なることを告げること。" in vier.tekst
    assert "。 " not in vier.tekst


def test_lawmoj_parse():
    """TW: 章/節 als pad uit de char-N-koppen, 7-1 voor 第七條之一, leden en onderdelen, versie uit 修正日期 (民國)."""
    from synoptikon.importers import lawmoj

    g = lawmoj.parse((FIX / "lawmoj_consumentenbescherming.html").read_bytes(), "J0170001")
    assert (g.titel, g.versie) == ("消費者保護法", "2015-06-17")
    assert [a.nummer for a in g.artikelen] == ["1", "2", "7", "7-1", "8"]
    assert g.artikelen[0].pad == "第一章 總則"
    assert g.artikelen[3].pad == "第二章 消費者權益 › 第一節 健康與安全保障"
    assert g.artikelen[0].tekst.count("\n\n") == 1
    assert "\n    一、消費者：" in g.artikelen[1].tekst


def test_taiwanese_verwijzingen():
    assert _refs("消費者保護法第7條之1") == [("TW", "消保法", "7-1")]
    assert _refs("公司法第8條") == [("TW", "公司法", "8")]
    assert _refs("涉外民事法律適用法第20條") == [("TW", "涉民法", "20")]
    assert _refs("民法第一百八十四條第一項") == [("JP", None, "184"), ("TW", None, "184")]  # zelfde naam: beide
    assert sleutel("TW", "7") < sleutel("TW", "7-1") < sleutel("TW", "7-2") < sleutel("TW", "10")


def test_japanse_verwijzingen():
    assert _refs("会社法第429条の2")[0][2] == "429の2"
    assert _refs("第七百九条 民法") == [("JP", None, "709"), ("TW", None, "709")]  # 民法 ook in TW
    assert _refs("会社法第429条") == [("JP", "会社法", "429")]
    assert ("JP", "民訴法", "248") in _refs("民事訴訟法第248条")
    assert _refs("消費者契約法10条") == [("JP", "消契法", "10")]
    assert lees("JP", "第709条の2").nummer == "709の2"
    assert sleutel("JP", "709") < sleutel("JP", "709の2") < sleutel("JP", "710")


def test_hkel_parse():
    """HK: Part › crossHeading als pad, heading als opschrift, definities met de Chinese term, (a) ingesprongen."""
    from synoptikon.importers import hkel

    g = hkel.parse((FIX / "hkel_cap26.xml").read_bytes(), "cap26")
    assert (g.titel, g.versie, g.stijl) == ("Sale of Goods Ordinance", "2018-09-20", None)
    assert [a.nummer for a in g.artikelen][:3] == ["1", "2", "3"]
    s14 = next(a for a in g.artikelen if a.nummer == "14")
    assert (s14.opschrift, s14.pad) == ("Implied undertaking as to title etc.", "Part I Formation of the Contract › Conditions and warranties")
    assert s14.tekst.startswith("(1) In every contract of sale") and "\n    (a) an implied condition" in s14.tekst
    assert "\n    buyer (買方) means a person" in g.artikelen[1].tekst
    assert "Amended" not in "".join(a.tekst for a in g.artikelen)  # sourceNotes weg


def test_hkel_basic_law():
    from synoptikon.importers import hkel

    g = hkel.parse((FIX / "hkel_basic_law.xml").read_bytes(), "A101")
    assert g.titel.startswith("The Basic Law of the Hong Kong") and "Adopted" not in g.titel
    assert (g.versie, g.stijl) == ("1997-07-01", "Art")
    assert [(a.nummer, a.pad) for a in g.artikelen] == [
        ("1", "Chapter I General Principles"), ("43", "Chapter IV Political Structure › Section 1 The Chief Executive")]
    assert g.artikelen[1].tekst.count("\n\n") == 1


def test_hongkongse_verwijzingen():
    assert _refs("s 14 Cap 26") == [("HK", "Cap. 26", "14")]
    assert _refs("section 3 Misrepresentation Ordinance") == [("HK", "Cap. 284", "3")]
    assert _refs("Article 8 Basic Law") == [("HK", "BL", "8")]
    assert _refs("s 14 SGA 1979") == [("EN", "SGA 1979", "14")]
