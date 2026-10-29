"""Registerregels voor Amerika. Bronnen per stelsel en waarom:

* CA: Justice Laws Website (laws-lois.justice.gc.ca), geconsolideerde XML onder de Open Government Licence – Canada;
  de Constitution Acts alleen als HTML op dezelfde site. Engelse tekst (de Franse is gelijkwaardig maar staat apart).
* QC: Données Québec, dataset "Lois et règlements codifiés du Québec" (XML-zip van het ministerie van Justitie, CC
  BY-NC-ND 4.0), geconsolideerd; LégisQuébec zelf weigert geautomatiseerde verzoeken.
* CL: Ley Chile van de Biblioteca del Congreso Nacional (XML per idNorma, open data), geconsolideerd. Het Código
  Civil is artikel 2 van DFL 1 (2000).
* BR: Normas.leg.br (Congresso Nacional, open API, CC BY 4.0), de "Compilação Monovigente" van de Câmara dos
  Deputados, geconsolideerd. Planalto verbreekt de verbinding van buiten Brazilië.
"""
from __future__ import annotations

from .register import Wet

WETTEN: list[Wet] = [
    # CA: de federale kern
    *[Wet("CA", afk, "justicelaws", i, t, systematiek=True) for afk, i, t in [
        ("CA 1867", "Const/1867", "Constitution Act, 1867"),
        ("CA 1982", "Const/1982", "Constitution Act, 1982"),
        ("Criminal Code", "C-46", "Criminal Code"),
        ("Divorce Act", "D-3.4", "Divorce Act"),
        ("BIA", "B-3", "Bankruptcy and Insolvency Act"),
        ("CBCA", "C-44", "Canada Business Corporations Act"),
        ("Interest Act", "I-15", "Interest Act"),
    ]],
    # QC: de Code civil en de wetten eromheen
    Wet("QC", None, "quebec", "CCQ-1991", "Code civil du Québec"),
    *[Wet("QC", afk, "quebec", i, t, systematiek=True) for afk, i, t in [
        ("C.p.c.", "C-25.01", "Code de procédure civile"),
        ("L.p.c.", "P-40.1", "Loi sur la protection du consommateur"),
        ("Charte québécoise", "C-12", "Charte des droits et libertés de la personne"),
    ]],
    # CL: Bello's Código Civil en de kern eromheen
    Wet("CL", None, "leychile", "172986/2", "Código Civil"),
    *[Wet("CL", afk, "leychile", i, t, systematiek=True) for afk, i, t in [
        ("CPR", "242302", "Constitución Política de la República"),
        ("C. de C.", "1974", "Código de Comercio"),
        ("CPC", "22740", "Código de Procedimiento Civil"),
        ("LPDC", "61438", "Ley 19.496 sobre Protección de los Derechos de los Consumidores"),
        ("CP", "1984", "Código Penal"),
    ]],
    # BR: het Código Civil van 2002 en de kern eromheen (id = LexML-URN)
    Wet("BR", None, "normasleg", "urn:lex:br:federal:lei:2002-01-10;10406", "Código Civil"),
    *[Wet("BR", afk, "normasleg", i, t, systematiek=True) for afk, i, t in [
        ("CF", "urn:lex:br:federal:constituicao:1988-10-05;1988", "Constituição da República Federativa do Brasil"),
        ("CDC", "urn:lex:br:federal:lei:1990-09-11;8078", "Código de Defesa do Consumidor"),
        ("CPC", "urn:lex:br:federal:lei:2015-03-16;13105", "Código de Processo Civil"),
        ("LINDB", "urn:lex:br:federal:decreto.lei:1942-09-04;4657", "Lei de Introdução às normas do Direito Brasileiro"),
        ("CP", "urn:lex:br:federal:decreto.lei:1940-12-07;2848", "Código Penal"),
    ]],
]
