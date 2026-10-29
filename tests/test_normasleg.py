"""BR: Normas.leg.br (kleine HTML-fixture, geen netwerk) en de Braziliaanse citeerregels."""


def test_normasleg_koppen_artikelen_en_noten():
    from synoptikon.importers import normasleg

    html = """<html><head><xml><o:LastSaved>2024-12-24T10:00:00Z</o:LastSaved></xml></head><body>
<p class="Header"><img src="data:image/png;base64,iVBORw0KGgo" /></p><p>CÂMARA DOS DEPUTADOS</p>
<h3>LEI Nº 10.406, DE 10 DE JANEIRO DE 2002</h3><p>Institui o Código Civil.</p>
<p>PARTE GERAL</p><p>LIVRO I</p><p>DAS PESSOAS</p><p>TÍTULO I</p><p>DAS PESSOAS NATURAIS</p>
<p>Art. 1º Toda pessoa é capaz de direitos e deveres na ordem civil.</p>
<p>Art. 4º-A A pessoa com deficiência. (Artigo acrescido pela Lei nº 13.146, de 6/7/2015)</p>
<p>Parágrafo único. Segunda&nbsp;alínea.</p>
<p>CAPÍTULO II</p><p>DOS DIREITOS DA PERSONALIDADE</p>
<p>Art. 1.022. (Revogado pela Lei nº 9.999, de 2020)</p>
<p>Brasília, 10 de janeiro de 2002; 181º da Independência.</p><p>Art. 9º Niet meer.</p></body></html>"""
    g = normasleg.parse(html.encode(), "urn:lex:br:federal:lei:2002-01-10;10406")
    assert (g.titel, g.versie) == ("LEI Nº 10.406, DE 10 DE JANEIRO DE 2002", "2024-12-24")
    assert [a.nummer for a in g.artikelen] == ["1", "4-A", "1022"]
    a1, a4a, a1022 = g.artikelen
    assert a1.pad == "PARTE GERAL › LIVRO I · DAS PESSOAS › TÍTULO I · DAS PESSOAS NATURAIS"
    assert a4a.tekst == "A pessoa com deficiência.\n\nParágrafo único. Segunda alínea."
    assert a1022.tekst == "(revogado)" and a1022.pad.endswith("CAPÍTULO II · DOS DIREITOS DA PERSONALIDADE")
    assert b"iVBOR" not in g.ruw
    assert normasleg.tekst_url({"encoding": [{"version": "Original", "contentUrl": "x"},
                                             {"version": "Current", "contentUrl": "https://normas.leg.br/api/binario/ab/texto"}]}) \
        == "https://normas.leg.br/api/public/binario/ab/texto"


def test_braziliaanse_verwijzingen():
    from synoptikon.services.artikelen import herken

    assert ("BR", "186", None) in {(r.stelsel, r.nummer, r.wet) for r in herken("art. 186 CC")}
    assert [(r.stelsel, r.nummer, r.wet) for r in herken("art. 54-A CDC")] == [("BR", "54-A", "CDC")]
    assert [(r.stelsel, r.wet) for r in herken("art. 7 LINDB")] == [("BR", "LINDB")]
