"""Citeerregels voor de stelsels van Amerika (Canada, Québec, Latijns-Amerika).

* **CA** (federaal, common law): geen codificatie; een section van een Act, `s 91 CA 1867`, `s 265 Criminal Code`,
  `s 7 CA 1982` (de Charter is Part I van de Constitution Act, 1982). Ingevoegde sections met een punt (`83.01`),
  de Constitution Act, 1867 ook met een letter (`90S.1`).
* **QC** (Code civil du Québec): `art. 1457 C.c.Q.`, ingevoegde artikelen met een punt (`521.1`); de andere wetten
  zoals de Québecse doctrine ze citeert (`C.p.c.`, `L.p.c.`).
* **CL** (Código Civil van Bello, 1855): `art. 1545 CC`, `art. 19 CPR` (Constitución Política de la República),
  `art. 3 bis LPDC` (Ley 19.496); ingevoegde artikelen met bis/ter, enkele met een streepje (`225-2`).
* **BR** (Código Civil 2002): `art. 186 CC`, `art. 5º CF` (Constituição Federal), `art. 54-A CDC`; ingevoegde
  artikelen met een hoofdletter (`1.142-A` wordt `1142-A`, zonder duizendtalpunt).
"""
from __future__ import annotations

from .artikelen import _LAT, Regels

REGELS = {
    "CA": Regels(
        None,
        ("CA 1867", "CA 1982", "Criminal Code", "Divorce Act", "BIA", "CBCA", "Interest Act"),
        stijl="s",
        nummer=r"\d+[A-Z]?(?:\.\d+)*",
        namen={"CA 1867": "Constitution Act, 1867", "CA 1982": "Constitution Act, 1982", "Criminal Code": "Criminal Code (R.S.C. 1985, c. C-46)",
               "Divorce Act": "Divorce Act (R.S.C. 1985, c. 3 (2nd Supp.))", "BIA": "Bankruptcy and Insolvency Act",
               "CBCA": "Canada Business Corporations Act", "Interest Act": "Interest Act (R.S.C. 1985, c. I-15)"},
    ),
    "QC": Regels(
        "C.c.Q.",
        ("C.p.c.", "L.p.c.", "Charte québécoise"),
        nummer=r"\d+(?:\.\d+)*",
        namen={"C.c.Q.": "Code civil du Québec", "C.p.c.": "Code de procédure civile du Québec",
               "L.p.c.": "Loi sur la protection du consommateur", "Charte québécoise": "Charte des droits et libertés de la personne"},
    ),
    "CL": Regels(
        "CC",
        ("CPR", "C. de C.", "CP", "CPC", "LPDC"),
        nummer=rf"\d+(?:-\d+)?(?:\s?(?:{_LAT}))?",
        namen={"CC": "Código Civil de Chile", "CPR": "Constitución Política de la República de Chile", "C. de C.": "Código de Comercio de Chile",
               "CP": "Código Penal de Chile", "CPC": "Código de Procedimiento Civil", "LPDC": "Ley 19.496 sobre Protección de los Derechos de los Consumidores"},
    ),
    "BR": Regels(
        "CC",
        ("CF", "CDC", "CPC", "CP", "LINDB"),
        nummer=r"\d+(?:-[A-Z]{1,2})?",
        namen={"CC": "Código Civil brasileiro (Lei 10.406/2002)", "CF": "Constituição da República Federativa do Brasil",
               "CDC": "Código de Defesa do Consumidor", "CPC": "Código de Processo Civil", "CP": "Código Penal brasileiro",
               "LINDB": "Lei de Introdução às normas do Direito Brasileiro"},
    ),
}
