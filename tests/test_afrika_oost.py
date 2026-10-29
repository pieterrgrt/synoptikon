"""Regio Oost-Europa, Turkije, Midden-Oosten en Afrika: mevzuat-parser, citeerregels, zoeken in Cyrillisch en Arabisch."""
from pathlib import Path

from synoptikon.importers import mevzuat
from synoptikon.services.artikelen import citeer, herken

FIX = Path(__file__).parent / "fixtures"


def test_mevzuat_parse():
    g = mevzuat.parse((FIX / "mevzuat_tbk.html").read_bytes(), "6098", titel="Türk Borçlar Kanunu")
    assert [a.nummer for a in g.artikelen] == ["1", "2", "Geçici 1"]
    a1, a2, _ = g.artikelen
    assert a1.opschrift == "1. Genel olarak"
    assert a1.pad == "BİRİNCİ KISIM · Genel Hükümler › BİRİNCİ BÖLÜM · Borç İlişkisinin Kaynakları › A. Sözleşmenin kurulması › I. İrade açıklaması"
    assert a1.tekst.endswith("açık veya örtülü olabilir.")
    assert a2.opschrift == "2. İkinci derecedeki noktalar"
    assert a2.tekst.endswith("1. Cenaze giderleri.")  # een lijstpunt na een lege regel is geen kantkop
    assert g.versie == "2022-06-11"  # laatste inwerkingtreding uit de tabel, niet de ophaaldatum


def test_citeerregels():
    def een(t):
        (r,) = herken(t)
        return r.stelsel, r.nummer, r.wet

    assert een("ст. 10 ГК РФ") == ("RU", "10", None)
    assert een("п. 1 ст. 434.1 ГК РФ") == ("RU", "434.1", None)
    assert een("ст. 3 ГПК РФ") == ("RU", "3", "ГПК РФ")
    assert een("TMK m. 706") == ("TR", "706", None)
    assert een("TBK m. 49") == ("TR", "49", "TBK")
    assert een("m. 1 Türk Borçlar Kanunu") == ("TR", "1", "TBK")
    assert citeer("TR", "49", "TBK") == "art. 49 TBK"


def test_fts_cyrillisch_en_arabisch():
    """De tokenizer van de app (unicode61, remove_diacritics 2, zie db.py) in het Cyrillisch, Arabisch en Turks.

    Vastgelegd wat hij wél en níet doet: hoofdletters vouwen werkt, stamming en ё/е niet, en Arabische vocaaltekens
    (harakat) breken een woord, zodat "العقد" een gevocaliseerd "العَقْدُ" niet vindt."""
    import sqlite3

    c = sqlite3.connect(":memory:")
    c.execute("CREATE VIRTUAL TABLE t USING fts5(tekst, tokenize=\"unicode61 remove_diacritics 2\")")
    c.executemany("INSERT INTO t VALUES (?)", [("Гражданские права возникают из договоров. Ёлка",), ("العقد شريعة المتعاقدين",),
                                                ("العَقْدُ",), ("İrade açıklaması",)])

    def n(q):
        return c.execute("SELECT count(*) FROM t WHERE t MATCH ?", (q,)).fetchone()[0]

    assert n("ДОГОВОРОВ") == 1 and n("شريعة") == 1 and n("irade") == 1
    assert n("договор") == 0 and n("договор*") == 1  # geen stamming: prefix-* nodig
    assert n("елка") == 0  # ё wordt niet tot е gevouwen
    assert n("العقد") == 1  # alleen de ongevocaliseerde tekst
    assert n("عقد") == 0  # het lidwoord ال hoort bij het token
