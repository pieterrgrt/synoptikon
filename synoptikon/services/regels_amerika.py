"""Citeerregels voor de stelsels van Amerika (Canada, Québec, Latijns-Amerika).

* **CA** (federaal, common law): geen codificatie; een section van een Act, `s 91 CA 1867`, `s 265 Criminal Code`,
  `s 7 CA 1982` (de Charter is Part I van de Constitution Act, 1982). Ingevoegde sections met een punt (`83.01`),
  de Constitution Act, 1867 ook met een letter (`90S.1`).
* **QC** (Code civil du Québec): `art. 1457 C.c.Q.`, ingevoegde artikelen met een punt (`521.1`); de andere wetten
  zoals de Québecse doctrine ze citeert (`C.p.c.`, `L.p.c.`).
"""
from __future__ import annotations

from .artikelen import Regels

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
}
