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
    # kop en titel van een hoofdstuk vormen samen één niveau
    assert arts["12"].pad == "CHAPTER III UNJUST ENRICHMENT, NEGOTIORUM GESTIO AND CULPA IN CONTRAHENDO"
    assert arts["14"].pad == "CHAPTER IV FREEDOM OF CHOICE"
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
        assert any("930" in t.titel for t in res.wetteksten)
        # opnieuw opslaan van dezelfde versie vervangt in plaats van dupliceert
        store.sla_op(s, "DE", g)
        from sqlalchemy import select

        from synoptikon.models import Wettekst

        assert len(s.scalars(select(Wettekst).where(Wettekst.wet_id == "bgb")).all()) == 1


def test_bwb_parse_huidig_formaat():
    """Zoals wetten.overheid.nl het nu levert: inwerkingtreding op de wortel, meta-data in de elementen, boek 7a."""
    xml = b"""<?xml version="1.0" encoding="UTF-8"?><toestand bwb-id="BWBR0006000" inwerkingtreding="2025-07-01">
<wetgeving><citeertitel status="officieel">Burgerlijk Wetboek Boek 7A<meta-data><jcis/>196925728</meta-data></citeertitel>
<wet-besluit><wettekst><boek><kop><label>Boek</label><nr>7a</nr><titel>Bijzondere overeenkomsten; vervolg</titel></kop>
<titeldeel><kop><label>titel</label><nr>Negende</nr><titel>Van maatschap</titel></kop>
<artikel status="goed"><kop><label>Artikel</label><nr>1655</nr></kop><al>Maatschap is eene overeenkomst.</al>
<meta-data><jcis><jci verwijzing="jci1.3:c:BWBR0006000"/></jcis>2025-07-01</meta-data></artikel>
</titeldeel></boek></wettekst></wet-besluit></wetgeving></toestand>"""
    g = bwb.parse(xml, "BWBR0006000")
    assert g.titel == "Burgerlijk Wetboek Boek 7A" and g.versie == "2025-07-01"
    (a,) = g.artikelen
    assert a.nummer == "7A:1655" and a.tekst == "Maatschap is eene overeenkomst."
    assert a.pad == "Boek 7a Bijzondere overeenkomsten; vervolg › titel Negende Van maatschap"


def test_gii_pad_uit_documentvolgorde():
    """Zoals gesetze-im-internet.de het nu levert: paragrafen zonder eigen gliederungseinheit."""
    xml = b"""<?xml version="1.0" encoding="UTF-8"?><dokumente builddate="20260926">
<norm><metadaten><jurabk>BGB</jurabk><langue>B\xc3\xbcrgerliches Gesetzbuch</langue></metadaten></norm>
<norm><metadaten><gliederungseinheit><gliederungskennzahl>030</gliederungskennzahl><gliederungsbez>Buch 3</gliederungsbez><gliederungstitel>Sachenrecht</gliederungstitel></gliederungseinheit></metadaten></norm>
<norm><metadaten><gliederungseinheit><gliederungskennzahl>030030</gliederungskennzahl><gliederungsbez>Abschnitt 3</gliederungsbez><gliederungstitel>Eigentum</gliederungstitel></gliederungseinheit></metadaten></norm>
<norm><metadaten><enbez>\xc2\xa7 929</enbez><titel>Einigung und \xc3\x9cbergabe</titel></metadaten><textdaten><text><Content><P>Tekst.</P></Content></text></textdaten></norm>
</dokumente>"""
    g = gii.parse(xml, "bgb")
    assert g.titel == "Bürgerliches Gesetzbuch"
    (a,) = g.artikelen
    assert a.nummer == "929" and a.pad == "Buch 3 Sachenrecht › Abschnitt 3 Eigentum"


def test_normattiva_bijlagen():
    from synoptikon.importers import normattiva

    g = normattiva.parse((FIX / "normattiva_cc.xml").read_bytes(), "urn:nir:stato:regio.decreto:1942-03-16;262")
    assert g.versie == "2026-08-12"
    per = {a.nummer: a for a in g.artikelen}
    assert set(per) == {"1", "5", "42-bis", "1337"}
    assert per["1337"].opschrift == "Trattative e responsabilita' precontrattuale"
    assert per["1337"].tekst.startswith("Le parti, nello svolgimento")
    # opschrift met wijzigingshaken, voetnootnummers en het blok AGGIORNAMENTO verdwijnen
    assert per["42-bis"].opschrift == "Trasformazione, fusione e scissione"
    assert "((" not in per["42-bis"].tekst
    assert "AGGIORNAMENTO" not in per["5"].tekst and "(3a)" not in per["5"].tekst


def test_normattiva_body_en_latijnse_nummers():
    from synoptikon.importers import normattiva

    g = normattiva.parse((FIX / "normattiva_consumo.xml").read_bytes(), "c. cons.", deel=None)
    assert [a.nummer for a in g.artikelen] == ["33", "135-vicies-ter"]
    a33 = g.artikelen[0]
    assert a33.opschrift == "Clausole vessatorie nel contratto tra professionista e consumatore"
    assert a33.pad == "Parte III IL RAPPORTO DI CONSUMO Titolo I DEI CONTRATTI DEL CONSUMATORE IN GENERALE"
    assert a33.tekst.startswith("1. Nel contratto concluso")
    assert g.artikelen[1].pad == "Parte IV Capo I-bis Dei contratti di fornitura di contenuto digitale"


def test_boe_pad_uit_koppen():
    from synoptikon.importers import boe

    g = boe.parse((FIX / "boe_cc.xml").read_bytes(), "BOE-A-1889-4763", titel="Código Civil")
    [a] = g.artikelen
    assert a.nummer == "1902"
    assert a.pad.startswith("LIBRO CUARTO De las obligaciones y contratos › TÍTULO XVI")
    assert a.tekst.startswith("El que por acción u omisión causa daño a otro")


def test_boe_artikelkop_varianten():
    from synoptikon.importers.boe import _ART

    assert _ART.match("Artículo 94 bis.").group(1, 2) == ("94", "bis")
    assert _ART.match("Artículo 1º.").group(1) == "1"
    assert _ART.match("Art. 50.").group(1) == "50"
    assert _ART.match("Artículo 10 octies.").group(1, 2) == ("10", "octies")


def test_fedlex_randtitels_en_voetnoten():
    from synoptikon.importers import fedlex

    g = fedlex.parse((FIX / "fedlex_zgb.xml").read_bytes(), "eli/cc/24/233_245_233")
    assert g.titel == "Schweizerisches Zivilgesetzbuch"
    a641, a641a = g.artikelen
    assert (a641.nummer, a641a.nummer) == ("641", "641a")
    assert a641.opschrift == "Inhalt des Eigentums › Im Allgemeinen"
    assert a641.pad == "Vierter Teil Das Sachenrecht › Erste Abteilung Das Eigentum › Achtzehnter Titel Allgemeine Bestimmungen"
    assert a641a.tekst == "1 Tiere sind keine Sachen.\n\n2 Soweit für Tiere keine besonderen Regelungen bestehen, gelten für sie die auf Sachen anwendbaren Vorschriften."
    assert "Eingefügt" not in a641a.tekst


def test_clml_sections():
    from synoptikon.importers import legislation_uk

    g = legislation_uk.parse((FIX / "clml_sga.xml").read_bytes(), "ukpga/1979/54")
    assert g.titel == "Sale of Goods Act 1979"
    per = {a.nummer: a for a in g.artikelen}
    assert per["17"].opschrift == "Property passes when intended to pass"
    assert per["17"].tekst.startswith("(1) Where there is a contract for the sale of specific or ascertained goods")
    assert per["21"].pad == "Part III Effects of the Contract › Transfer of title"
    assert "20A" in per


def test_etaamb_koppen_en_opschriften():
    from synoptikon.importers import etaamb

    g = etaamb.parse((FIX / "etaamb_boek5.html").read_text(encoding="utf-8"), "wet-van-28-april-2022_n2022032058")
    assert g.versie == "bekendmaking 2022-07-01"
    per = {a.nummer: a for a in g.artikelen}
    assert per["5.1"].opschrift == "Verbintenis"
    assert per["5.1"].tekst.startswith("Een verbintenis is een rechtsband")
    assert per["5.69"].opschrift == "Beginsel van de overeenkomst-wet"
    assert per["5.69"].pad.endswith("Afdeling 4 Gevolgen van het contract tussen partijen › Onderafdeling 1 Bindende kracht")


def test_legi_geldende_versie_en_pad():
    from datetime import date

    from synoptikon.importers import legi

    g = legi.parse_map(FIX / "legi", "LEGITEXT000006070721")
    [a] = g.artikelen
    assert a.nummer == "1240"
    assert a.tekst.startswith("Tout fait quelconque de l'homme")
    assert a.pad == "Livre III : Des différentes manières dont on acquiert la propriété › Titre III : Des sources d'obligations"
    # Op een peildatum vóór 2016 geldt de oude tekst onder de oude titre
    oud = legi.parse_map(FIX / "legi", "LEGITEXT000006070721", peildatum=date(2010, 1, 1))
    assert oud.artikelen == []  # de oude titre verwijst in deze fixture niet naar artikelen


def test_cellar_nummer_uit_titel():
    from synoptikon.importers.cellar import _nummer, _rep_code

    ai = ("Verordening (EU) 2024/1689 van het Europees Parlement en de Raad van 13 juni 2024 tot vaststelling van geharmoniseerde regels "
          "betreffende artificiële intelligentie en tot wijziging van de Verordeningen (EG) nr. 300/2008, (EU) nr. 167/2013")
    assert _nummer("32024R1689", ai) == "2024/1689"
    assert _nummer("32008R0593", "Verordening (EG) nr. 593/2008 van het Europees Parlement") == "593/2008"
    assert _nummer("31993L0013", "Richtlijn 93/13/EEG van de Raad") == "93/13"
    assert _rep_code("http://publications.europa.eu/resource/authority/dir-eu-legal-act/13301420") == "13.30.14.20"


def test_eurlex_drie_vormen():
    """Geconsolideerd (title-article-norm + div.norm), Publicatieblad met klassen, en oude HTML zonder klassen."""
    cons = eurlex.parse((FIX / "eu" / "01993L0013-20220528.xhtml").read_text(encoding="utf-8"), "31993L0013")
    a = {x.nummer: x for x in cons.artikelen}
    assert cons.titel.startswith("RICHTLINIE 93/13/EWG")
    assert a["1"].tekst.startswith("(1) Zweck dieser Richtlinie") and "(2) Vertragsklauseln" in a["1"].tekst
    assert "a) mißbräuchliche Klauseln" in a["2"].tekst
    assert "Anhang" in a
    charta = eurlex.parse((FIX / "eu" / "12016P.xhtml").read_text(encoding="utf-8"), "12016P")
    c = {x.nummer: x for x in charta.artikelen}
    assert list(c)[0] == "Präambel" and len([n for n in c if n.isdigit()]) == 54
    assert c["1"].opschrift == "Würde des Menschen" and c["1"].pad.startswith("TITEL I")
    oud = eurlex.parse((FIX / "eu" / "31985L0374.html").read_text(encoding="utf-8", errors="replace"), "31985L0374")
    o = {x.nummer: x for x in oud.artikelen}
    assert o["1"].tekst.startswith("Der Hersteller eines Produkts haftet") and "22" in o


def test_gii_nummers_en_afkorting():
    g = gii.parse((FIX / "gii_bgb.xml").read_bytes(), "bgb")
    assert g.afkorting == "BGB"


def test_lawspot_parse():
    """GR: geneste hoofdstukken als pad, kop "Άρθρο 914 - Αστικός Κώδικας - Έννοια" → nummer en opschrift."""
    from synoptikon.importers import lawspot

    html = """<h1 class="post__title fs-mb-2xl">Αστικός Κώδικας</h1><span>Τελευταία Τροποποίηση:</span><span>17.02.2023</span>
<div class="chapter root"><h3 class="chapter__title fs-mb-lg">ΒΙΒΛΙΟ ΔΕΥΤΕΡΟ ΕΝΟΧΙΚΟ ΔΙΚΑΙΟ</h3>
<div class="chapter"><h3 class="chapter__title fs-mb-lg">ΚΕΦΑΛΑΙΟ ΤΡΙΑΚΟΣΤΟ ΕΝΑΤΟ ΑΔΙΚΟΠΡΑΞΙΕΣ</h3>
<article class="legislation__article bg-greyLight" id="arthro-914"><h4><a href="/x/" class="inner">Άρθρο 914 - Αστικός Κώδικας - Έννοια</a>
<a class="article__toggle expand"><img src="x.svg"></a></h4><div class="body collapsed" hidden><p>Όποιος ζημιώσει άλλον παράνομα και υπαίτια
έχει υποχρέωση να τον αποζημιώσει.</p><p>Δεύτερη παράγραφος.</p></div></article></div></div>"""
    g = lawspot.parse(html, "astikos-kodikas")
    assert g.titel == "Αστικός Κώδικας" and g.versie == "2023-02-17"
    a = g.artikelen[0]
    assert (a.nummer, a.opschrift) == ("914", "Έννοια")
    assert a.pad == "ΒΙΒΛΙΟ ΔΕΥΤΕΡΟ ΕΝΟΧΙΚΟ ΔΙΚΑΙΟ › ΚΕΦΑΛΑΙΟ ΤΡΙΑΚΟΣΤΟ ΕΝΑΤΟ ΑΔΙΚΟΠΡΑΞΙΕΣ"
    assert a.tekst == "Όποιος ζημιώσει άλλον παράνομα και υπαίτια έχει υποχρέωση να τον αποζημιώσει.\n\nΔεύτερη παράγραφος."


def test_griekse_verwijzingen():
    from synoptikon.services.artikelen import herken

    assert [(r.stelsel, r.nummer, r.wet) for r in herken("άρθρο 914 ΑΚ")] == [("GR", "914", None)]
    assert [(r.stelsel, r.nummer, r.wet) for r in herken("Art. 1033 AK")] == [("GR", "1033", None)]
    assert [(r.stelsel, r.nummer, r.wet) for r in herken("άρθρο 5 Συντ.")] == [("GR", "5", "Συντ.")]
