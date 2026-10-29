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


def test_japanse_verwijzingen():
    assert _refs("民法第709条") == [("JP", None, "709")]
    assert _refs("第七百九条 民法") == [("JP", None, "709")]
    assert _refs("会社法第429条") == [("JP", "会社法", "429")]
    assert _refs("民事訴訟法第248条") == [("JP", "民訴法", "248")]
    assert _refs("消費者契約法10条") == [("JP", "消契法", "10")]
    assert lees("JP", "第709条の2").nummer == "709の2"
    assert sleutel("JP", "709") < sleutel("JP", "709の2") < sleutel("JP", "710")
