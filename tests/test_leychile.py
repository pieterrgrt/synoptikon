"""CL: Ley Chile (kleine XML-fixture, geen netwerk) en de Chileense citeerregels."""
from synoptikon.services.artikelen import herken


def _ef(soort, naam, tekst, kinderen="", titel=None, **attrs):
    extra = "".join(f' {k}="{v}"' for k, v in attrs.items())
    tp = f'<TituloParte presente="si">{titel}</TituloParte>' if titel else '<TituloParte presente="no"> </TituloParte>'
    sub = f"<EstructurasFuncionales>{kinderen}</EstructurasFuncionales>" if kinderen else ""
    return (f'<EstructuraFuncional tipoParte="{soort}" fechaVersion="{attrs.pop("fv", "2000-05-30")}"{extra}><Texto>{tekst}</Texto>'
            f"<Metadatos><NombreParte presente=\"si\">{naam}</NombreParte>{tp}</Metadatos>{sub}</EstructuraFuncional>")


def test_leychile_codigo_civil_in_dfl():
    from synoptikon.importers import leychile

    art1 = _ef("Artículo", "1 (DEL ART. 2)", "     Art. 1º. La ley es una declaración de la\nvoluntad soberana.")
    art58 = _ef("Artículo", "58 BIS", "     Art. 58 bis. Nombre es el conjunto de           L. 21.334\npalabras que sirve legalmente.\n     Segunda alinea.", fv="2024-06-14")
    cc = _ef("Doble Articulado", "", "\xa0", _ef("Título", "", "\n     TITULO PRELIMINAR\n", _ef("Enumeración", "", "§ 1.", art1, titel="§ 1. De la ley"))
             + _ef("Libro", "", "     LIBRO PRIMERO\n     DE LAS PERSONAS\n", _ef("Título", "", "x", art58, titel="Título I DEL NOMBRE")))
    xml = ('<?xml version="1.0" encoding="UTF-8"?><Norma xmlns="http://www.leychile.cl/esquemas" fechaVersion="2222-02-02">'
           "<Metadatos><TituloNorma>FIJA TEXTO REFUNDIDO</TituloNorma><NombresUsoComun><NombreUsoComun>CODIGO CIVIL</NombreUsoComun></NombresUsoComun></Metadatos>"
           "<EstructurasFuncionales>" + _ef("Artículo", "1 ", "     Artículo 1º.- Déjase sin efecto el D.F.L. Nº 1.")
           + _ef("Artículo", "2 ", "     Artículo 2º.- Fíjase el siguiente texto refundido.", cc) + "</EstructurasFuncionales>"
           '<Anexos><DataCodificada xmlns="http://valida.aem.gob.cl">JVBERi0xLjMNCiWhs8XXDQ</DataCodificada></Anexos></Norma>')
    g = leychile.parse(xml.encode(), "172986/2")
    assert (g.titel, g.versie) == ("CODIGO CIVIL", "2024-06-14")
    assert [a.nummer for a in g.artikelen] == ["1", "58 bis"]  # zonder de artikelen van het DFL zelf
    a1, a58 = g.artikelen
    assert a1.tekst == "La ley es una declaración de la voluntad soberana."
    assert a1.pad == "TITULO PRELIMINAR › § 1. De la ley"
    assert a58.pad == "LIBRO PRIMERO · DE LAS PERSONAS › Título I · DEL NOMBRE"
    assert a58.tekst == "Nombre es el conjunto de palabras que sirve legalmente.\n\nSegunda alinea."  # zonder randnoot
    assert b"JVBER" not in g.ruw
    assert len(leychile.parse(xml.encode(), "172986").artikelen) == 4


def test_verwijzingen_latijns_amerika():
    def stelsels(t):
        return {(r.stelsel, r.nummer, r.wet) for r in herken(t)}

    assert ("CL", "1545", None) in stelsels("art. 1545 CC")
    assert stelsels("art. 19 CPR") == {("CL", "19", "CPR")}
    assert {(s, w) for s, _, w in stelsels("art. 3 bis LPDC")} == {("CL", "LPDC")}
