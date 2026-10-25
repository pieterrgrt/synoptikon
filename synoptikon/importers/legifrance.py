"""FR: Légifrance via de PISTE-API (OAuth2 client credentials).

Zonder LEGIFRANCE_CLIENT_ID en LEGIFRANCE_CLIENT_SECRET gooit `haal_op`
`ImportOvergeslagen`; de CLI meldt dat en gaat door. Sandbox-eindpunten via
LEGIFRANCE_SANDBOX=1.

Werkwijze: de inhoudsopgave van een code (tableMatieres) geeft de boom van
secties met artikel-id's en -nummers; voor de gevraagde artikelnummers (of
alle, als je geduld hebt) wordt getArticle aangeroepen. De Code civil is
LEGITEXT000006070721.
"""
from __future__ import annotations

import re
from datetime import date
from html.parser import HTMLParser

from . import Artikel, Geparseerd, ImportOvergeslagen
from ..config import settings
from .http import client

OAUTH = {"prod": "https://oauth.piste.gouv.fr/api/oauth/token", "sandbox": "https://sandbox-oauth.piste.gouv.fr/api/oauth/token"}
API = {"prod": "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app", "sandbox": "https://sandbox-api.piste.gouv.fr/dila/legifrance/lf-engine-app"}
LINK = "https://www.legifrance.gouv.fr/codes/article_lc/{id}"


class _Strip(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.delen: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in ("p", "br", "div", "li"):
            self.delen.append("\n")

    def handle_endtag(self, tag):
        if tag in ("p", "div", "li"):
            self.delen.append("\n")

    def handle_data(self, data):
        self.delen.append(data)


def html_naar_tekst(html: str) -> str:
    p = _Strip()
    p.feed(html or "")
    tekst = "".join(p.delen)
    tekst = re.sub(r"[ \t]+", " ", tekst)
    tekst = re.sub(r"\n\s*\n+", "\n\n", tekst)
    return tekst.strip()


def _omgeving() -> str:
    return "sandbox" if settings.legifrance_sandbox else "prod"


def token() -> str:
    if not settings.legifrance_client_id or not settings.legifrance_client_secret:
        raise ImportOvergeslagen("Légifrance: LEGIFRANCE_CLIENT_ID/LEGIFRANCE_CLIENT_SECRET ontbreken; import overgeslagen.")
    with client() as c:
        r = c.post(
            OAUTH[_omgeving()],
            data={
                "grant_type": "client_credentials",
                "client_id": settings.legifrance_client_id,
                "client_secret": settings.legifrance_client_secret,
                "scope": "openid",
            },
        )
        r.raise_for_status()
    return r.json()["access_token"]


def _loop_secties(secties: list[dict], pad: list[str], uit: list[tuple[str, str, str]]):
    for s in secties or []:
        titel = s.get("title") or ""
        nieuw_pad = pad + [titel] if titel else pad
        for a in s.get("articles") or []:
            if a.get("etat", "VIGUEUR").startswith("VIGUEUR") or a.get("etat") is None:
                uit.append((a.get("id"), a.get("num"), " › ".join(nieuw_pad)))
        _loop_secties(s.get("sections") or [], nieuw_pad, uit)


def inhoudsopgave(textid: str, datum: str, tok: str) -> tuple[str, list[tuple[str, str, str]]]:
    with client() as c:
        r = c.post(
            f"{API[_omgeving()]}/consult/code/tableMatieres",
            json={"textId": textid, "date": datum, "sctCid": "", "nature": "CODE"},
            headers={"Authorization": f"Bearer {tok}", "Accept": "application/json"},
        )
        r.raise_for_status()
        data = r.json()
    titel = data.get("title") or textid
    uit: list[tuple[str, str, str]] = []
    _loop_secties(data.get("sections") or [], [], uit)
    return titel, uit


def artikel(artikel_id: str, tok: str) -> dict:
    with client() as c:
        r = c.post(
            f"{API[_omgeving()]}/consult/getArticle",
            json={"id": artikel_id},
            headers={"Authorization": f"Bearer {tok}", "Accept": "application/json"},
        )
        r.raise_for_status()
    return r.json().get("article") or {}


def haal_op(textid: str, nummers: list[str] | None = None, datum: str | None = None) -> Geparseerd:
    tok = token()
    datum = datum or date.today().isoformat()
    titel, lijst = inhoudsopgave(textid, datum, tok)
    gewenst = {n.strip().lower().replace("art.", "").strip() for n in (nummers or [])}
    artikelen: list[Artikel] = []
    for art_id, num, pad in lijst:
        if gewenst and (num or "").lower() not in gewenst:
            continue
        a = artikel(art_id, tok)
        tekst = html_naar_tekst(a.get("texteHtml") or a.get("texte") or "")
        if not tekst:
            continue
        artikelen.append(Artikel(nummer=num or art_id, tekst=tekst, opschrift=None, pad=pad or None))
    return Geparseerd(
        wet_id=textid,
        titel=titel,
        versie=datum,
        bron_url=f"https://www.legifrance.gouv.fr/codes/texte_lc/{textid}",
        artikelen=artikelen,
        ruw=None,
    )
