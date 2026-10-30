"""Markeren: quote + context terugvinden, tekst kleuren, en gemarkeerde stukken als materiaal voor kaarten."""
import pytest
from sqlalchemy import select

from synoptikon import db as database
from synoptikon.models import Bron, Kaart, Leerlijst, Markering, Opzoeking, Wettekst, WettekstArtikel
from synoptikon.services import leren, markeringen
from synoptikon.services.artikelen import Ref, laad_wetnamen

TEKST = ("Wer vorsätzlich oder fahrlässig das Leben, den Körper oder das Eigentum eines anderen widerrechtlich verletzt, "
         "ist dem anderen zum Ersatz des daraus entstehenden Schadens verpflichtet. Die gleiche Verpflichtung trifft denjenigen.")


def _m(quote, voor="", na="", soort="kern", id=1, **kw):
    return Markering(id=id, profiel_id=1, quote=quote, voor=voor, na=na, soort=soort, **kw)


def test_vind_kiest_de_plek_met_de_beste_omgeving():
    t = "Der Käufer zahlt. Der Verkäufer liefert. Der Käufer zahlt nochmals."
    eerste = markeringen.vind(t, _m("Der Käufer zahlt", na=". Der Verkäufer"))
    tweede = markeringen.vind(t, _m("Der Käufer zahlt", voor="liefert. ", na=" nochmals"))
    assert t[eerste[0]:eerste[1]] == "Der Käufer zahlt" and eerste[0] == 0
    assert tweede[0] == t.rindex("Der Käufer")
    assert markeringen.vind(t, _m("Der Käufer zahlt  ")) is not None  # witruimte telt niet
    assert markeringen.vind(t, _m("kommt nicht vor")) is None


def test_witruimte_en_regeleinden_tellen_niet():
    assert markeringen.vind("a b\nc d", _m("b c")) == (2, 5)


def test_markeer_html_over_tags_heen_en_met_entiteiten():
    html = "<p>Recht &amp; Gesetz: <em>vorsätzlich</em> oder fahrlässig.</p>"
    uit = str(markeringen.markeer_html(html, [_m("Gesetz: vorsätzlich oder", soort="voorwaarde", id=7, notitie='zie "x"')]))
    assert uit.count("<mark") == 3 and 'data-id="7"' in uit and "m-voorwaarde" in uit
    assert "Recht &amp; <mark" in uit and "</em>" in uit and "&quot;" in uit
    assert "<p>" in uit and uit.endswith("</p>")
    # niets te kleuren of niet te vinden: ongewijzigd
    assert str(markeringen.markeer_html(html, [_m("bestaat niet")])) == html
    assert markeringen.verweesd(html, [_m("bestaat niet", id=3), _m("fahrlässig", id=4)]) == {3}


def test_overlap_eerste_wint():
    uit = str(markeringen.markeer_html("<p>abcdefgh</p>", [_m("abcd", id=1), _m("cdef", id=2, soort="let_op")]))
    assert 'data-id="1"' in uit and 'data-id="2"' not in uit


def test_markeer_md_vet_kern_en_voorwaarde_niet_let_op():
    uit = markeringen.markeer_md("Wer schuldhaft handelt, haftet. Ausnahme: Notwehr.",
                                 [_m("schuldhaft handelt", id=1), _m("Notwehr", id=2, soort="let_op"), _m("haftet", id=3, soort="voorwaarde")])
    assert uit == "Wer **schuldhaft handelt**, **haftet**. Ausnahme: Notwehr."


# --- via de routes -----------------------------------------------------------------------------------------------------


@pytest.fixture
def artikel823():
    with database.session() as s:
        w = s.scalar(select(Wettekst).where(Wettekst.wet_id == "test-markeren"))
        if w is None:
            w = Wettekst(stelsel_code="DE", wet_id="test-markeren", wet="MARKG", stijl="§", kern=False, versie="2026-01-01", titel="Marker-Gesetz")
            s.add(w)
            s.flush()
            s.add(WettekstArtikel(wettekst_id=w.id, nummer="823", opschrift="Schadensersatzpflicht", tekst=TEKST, volgorde=0))
    with database.session() as s:
        laad_wetnamen(s)


def test_markeren_bewaart_toont_en_verwijdert(client, artikel823):
    r = client.get("/artikelen/DE/823?wet=MARKG")
    assert r.status_code == 200 and "data-markeerbaar" in r.text and 'data-nummer="823"' in r.text and "markeren.js" in r.text
    r = client.post("/markeringen", data=dict(quote="widerrechtlich verletzt", voor="eines anderen ", na=", ist dem", soort="kern", vak="ZR Ia",
                                            notitie="Rechtsgutverletzung", stelsel="DE", wet="MARKG", nummer="823"))
    assert r.status_code == 200
    mid = r.json()["id"]
    html = client.get("/artikelen/DE/823?wet=MARKG").text
    assert f'<mark class="markering m-kern" data-id="{mid}"' in html and 'title="Rechtsgutverletzung"' in html
    assert "1 markering" in html
    # een quote die er niet staat wordt wel bewaard maar kleurt niets en staat als verweesd in de lijst
    client.post("/markeringen", data=dict(quote="staat er niet in", stelsel="DE", wet="MARKG", nummer="823"))
    assert "niet meer in de tekst te vinden" in client.get("/artikelen/DE/823?wet=MARKG").text
    assert client.post("/markeringen", data=dict(quote="  ", stelsel="DE", nummer="823")).status_code == 422
    assert client.post("/markeringen", data=dict(quote="zonder doel")).status_code == 422
    r = client.post(f"/markeringen/{mid}/verwijder", data={"terug": "/artikelen/DE/823?wet=MARKG"}, follow_redirects=False)
    assert r.status_code == 303
    assert f'data-id="{mid}"' not in client.get("/artikelen/DE/823?wet=MARKG").text


def test_markering_op_een_bron_en_niet_van_een_ander(client):
    with database.session() as s:
        b = Bron(stelsel_code="NL", soort="rechtspraak", citeertitel="HR Test/Mark", taal="nl", tekst="De rechter oordeelt dat de partij moet betalen.")
        s.add(b)
        s.flush()
        bid = b.id
        s.add(Markering(profiel_id=2, bron_id=bid, quote="partij moet betalen"))
    r = client.post("/markeringen", data=dict(quote="moet betalen", voor="partij ", na=".", bron_id=bid, soort="voorwaarde"))
    mid = r.json()["id"]
    html = client.get(f"/bronnen/{bid}").text
    assert html.count("data-id=") == 1 and "m-voorwaarde" in html and f'data-bron="{bid}"' in html  # die van profiel 2 niet
    with database.session() as s:
        andere = s.scalar(select(Markering.id).where(Markering.profiel_id == 2, Markering.bron_id == bid))
    assert client.post(f"/markeringen/{andere}/verwijder").status_code == 404
    assert client.post(f"/markeringen/{mid}", data={"soort": "let_op", "notitie": "pas op"}).json()["id"] == mid
    with database.session() as s:
        m = s.get(Markering, mid)
        assert (m.soort, m.notitie) == ("let_op", "pas op")


# --- materiaal voor kaarten --------------------------------------------------------------------------------------------


def test_arrestkaart_krijgt_de_gemarkeerde_rechtsregel():
    with database.session() as s:
        b = Bron(stelsel_code="NL", soort="rechtspraak", citeertitel="HR Mark/Kaart", taal="nl", vindplaats="NJ 2026/1",
                 tekst="Overwegingen. Wie onderhandelingen afbreekt handelt onrechtmatig indien dit in strijd is met de goede trouw. Meer tekst.")
        s.add(b)
        s.flush()
        s.add_all([Markering(profiel_id=1, bron_id=b.id, soort="kern", vak="ZR Ia", quote="handelt onrechtmatig indien dit in strijd is met de goede trouw"),
                   Markering(profiel_id=1, bron_id=b.id, soort="kern", vak="GÖ", quote="Meer tekst"),
                   Markering(profiel_id=1, bron_id=b.id, soort="let_op", quote="Overwegingen")])
        zr = Leerlijst(profiel_id=1, naam="ZR Ia markeer", vak="ZR Ia")
        go = Leerlijst(profiel_id=1, naam="GÖ markeer", vak="GÖ")
        s.add_all([zr, go])
        s.flush()
        k1 = leren.maak_kaarten(s, zr, ["arrest"], bron=b)[0]
        k2 = leren.maak_kaarten(s, go, ["arrest"], bron=b)[0]
        eigen = leren.maak_kaarten(s, Leerlijst(profiel_id=1, naam="eigen regel", vak="ZR Ia"), ["arrest"], bron=b, antwoord="Mijn regel.")[0]
        # per vak een andere regel; een zelf geschreven regel gaat voor
        assert k1.antwoord == "handelt onrechtmatig indien dit in strijd is met de goede trouw"
        assert k2.antwoord == "Meer tekst" and eigen.antwoord == "Mijn regel."
        assert leren.Bouwer(s).zijden(k1).achter.startswith("handelt onrechtmatig")


def test_artikelkaart_toont_kern_vet_en_let_op(artikel823):
    with database.session() as s:
        s.add_all([Markering(profiel_id=1, stelsel_code="DE", wet="MARKG", nummer="823", quote="widerrechtlich verletzt", vak="ZR Ia", soort="kern"),
                   Markering(profiel_id=1, stelsel_code="DE", wet="MARKG", nummer="823", quote="Die gleiche Verpflichtung", vak="ZR Ia", soort="let_op", notitie="auch Dritte"),
                   Markering(profiel_id=1, stelsel_code="DE", wet="MARKG", nummer="823", quote="Schadens", vak="GÖ", soort="kern")])
        lijst = Leerlijst(profiel_id=1, naam="Mark-artikel", vak="ZR Ia")
        s.add(lijst)
        s.flush()
        k = leren.maak_kaarten(s, lijst, ["artikel"], ref=Ref("DE", "823", "MARKG"))[0]
        achter = leren.Bouwer(s).zijden(k).achter
        assert "**widerrechtlich verletzt**" in achter and "**Schadens**" not in achter  # het andere vak telt niet
        assert achter.rstrip().endswith("*Let op:* auch Dritte")


def test_opzoeking_vult_rechtsregel_uit_markering_voor(client):
    with database.session() as s:
        b = Bron(stelsel_code="EU", soort="rechtspraak", citeertitel="HvJ Mark/Voorbeeld", taal="nl", vindplaats="ECLI:EU:C:2026:1",
                 tekst="Het Hof oordeelt dat de vestigingsvrijheid niet wordt beperkt.")
        s.add(b)
        s.flush()
        s.add(Markering(profiel_id=1, bron_id=b.id, soort="kern", quote="vestigingsvrijheid niet wordt beperkt"))
        o = Opzoeking(profiel_id=1, invoer="mark voorbeeld", bron_id=b.id, resultaat=dict(
            soort="uitspraak", stelsel="EU", citeer="HvJ Mark/Voorbeeld", vindplaats="ECLI:EU:C:2026:1", toelichting="trefwoorden", bron="cellar"))
        s.add(o)
        s.flush()
        oid = o.id
    html = client.get(f"/opzoeken/{oid}").text
    assert ">vestigingsvrijheid niet wordt beperkt</textarea>" in html
