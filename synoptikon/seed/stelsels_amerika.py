"""Stelsels van Amerika: Canada (federaal), Québec en Latijns-Amerika. Bronnen: zie `importers/register_amerika.py`."""

from .systematiek_ca import CA
from .systematiek_qc import QC

# code, naam, taal, toelichting, actief, rechtsfamilie (zelfde vorm als seed/stelsels.py)
STELSELS = [
    ("CA", "Canada", "en", "Common law (Engelse receptie); federaal straf-, echtscheidings- en insolventierecht, de rest is provinciaal recht", True, "common_law"),
    ("QC", "Québec", "fr", "Code civil du Québec (1994), opvolger van de Code civil du Bas-Canada (1866): civil law binnen een common-law-federatie", True, "gemengd"),
]

SYSTEMATIEK = {
    "CA": CA,
    "QC": QC,
}
