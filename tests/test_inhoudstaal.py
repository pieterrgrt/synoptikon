"""De taal van eigen inhoud (Profiel.inhoudstaal): wat een redacteur in het Duits schrijft, is geen 'vertaling'.

Een Duitse lezer ziet de tekst zoals hij geschreven is; een Nederlandse lezer de vertaling als die er is, anders het
Duits. Wie in het Nederlands schrijft, merkt niets: dat blijft de standaard.
"""
from sqlalchemy import select

from synoptikon import db as database
from synoptikon import i18n
from synoptikon.models import InhoudTaal, Profiel, Vraag
from synoptikon.services import vertalen

TITEL = "Wann geht das Eigentum an einer beweglichen Sache über?"


def _profiel(client, inhoudstaal):
    return client.post("/profiel/gegevens", data={"naam": "Beheerder", "taal": "nl", "inhoudstaal": inhoudstaal},
                       follow_redirects=False)


def test_duits_geschreven_inhoud_krijgt_de_taal_van_de_schrijver(client):
    assert _profiel(client, "de").status_code == 303
    r = client.post("/vragen/nieuw", data={"titel": TITEL, "tags": "Sachenrecht, Übereignung"}, follow_redirects=False)
    assert r.status_code == 303
    _profiel(client, "nl")
    with database.session() as s:
        assert s.get(Profiel, 1).inhoudstaal is None  # Nederlands wordt niet opgeslagen: dat is de standaard
        v = s.scalar(select(Vraag).where(Vraag.titel == TITEL))
        slug = v.slug
        talen = {r.hash: r.taal for r in s.scalars(select(InhoudTaal))}
        assert talen[i18n.sleutel(TITEL)] == "de"
        assert talen[i18n.sleutel("Übereignung")] == "de"  # tags apart, zoals vt ze toont
        vertalen.zet(s, "nl", TITEL, "Wanneer gaat de eigendom van een roerende zaak over?")
        vertalen.zet(s, "de", TITEL, "Dit mag nooit verschijnen")  # een 'vertaling' in de eigen taal telt niet

    i18n.geheugen.ongeldig()
    # Nederlandse lezer: de vertaling.
    assert "Wanneer gaat de eigendom" in client.get(f"/vragen/{slug}").text
    # Duitse lezer: zoals geschreven.
    client.post("/taal", data={"taal": "de", "terug": "/"})
    html = client.get(f"/vragen/{slug}").text
    assert TITEL in html and "Dit mag nooit" not in html
    # Franse lezer zonder vertaling: het Duits.
    client.post("/taal", data={"taal": "fr", "terug": "/"})
    assert TITEL in client.get(f"/vragen/{slug}").text
    client.post("/taal", data={"taal": "nl", "terug": "/"})


def test_nederlandse_redacteur_legt_niets_vast(client):
    _profiel(client, "nl")
    titel = "Wanneer is een overeenkomst nietig wegens strijd met de goede zeden?"
    client.post("/vragen/nieuw", data={"titel": titel}, follow_redirects=False)
    with database.session() as s:
        assert s.get(InhoudTaal, i18n.sleutel(titel)) is None


def test_vt_zonder_andere_talen_raakt_niets():
    i18n.zet_taal("nl")
    assert i18n.vt("Een tekst") == "Een tekst" and not i18n.is_vertaald("Een tekst")
