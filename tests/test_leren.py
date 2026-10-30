import re

from synoptikon import db as database
from synoptikon.config import settings
from synoptikon.models import Kaart, Leerlijst, Profiel, Wettekst, WettekstArtikel

TOKEN = "k" * 32


def _wettekst():
    with database.session() as s:
        w = s.query(Wettekst).filter_by(stelsel_code="DE", wet_id="test-bgb").first()
        if w is None:
            w = Wettekst(stelsel_code="DE", wet_id="test-bgb", titel="Bürgerliches Gesetzbuch", versie="2026-01-01")
            s.add(w)
            s.flush()
            for i, nr in enumerate(("929", "930", "931")):
                s.add(WettekstArtikel(wettekst_id=w.id, nummer=nr, opschrift=f"Opschrift {nr}", tekst=f"Tekst van § {nr}", volgorde=i))
        return w.id


def test_lezen_in_de_systematiek(client):
    _wettekst()
    r = client.get("/stelsels/DE?artikel=§ 929")
    assert r.status_code == 200
    m = re.search(r'data-k="(\d+)" open data-artikel="art-929"', r.text)
    assert m, "de knoop met het gezochte artikel staat open"
    frag = client.get(f"/stelsels/DE/lees/{m.group(1)}?fragment=1")
    assert frag.status_code == 200 and "Tekst van § 929" in frag.text and "<html" not in frag.text
    pagina = client.get(f"/stelsels/DE/lees/{m.group(1)}")
    assert "Tekst van § 929" in pagina.text and "☆" in pagina.text
    r = client.get("/artikelen/DE/929")
    assert f"/stelsels/DE/lees/{m.group(1)}#art-929" in r.text


def test_leerlijst_kaarten_en_oefenen(client):
    _wettekst()
    r = client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "Sachenrecht", "vak": "Sachenrecht",
                                          "stelsel": "DE", "nummer": "929", "wet": "", "soort": ["artikel", "kern", "plaats", "tegenhanger"],
                                          "doel": ["NL", "FR"], "notitie": "Einigung + Übergabe", "terug": "/artikelen/DE/929"},
                    follow_redirects=False)
    assert r.status_code == 303 and "bewaard=5" in r.headers["location"]
    # Nog eens: geen dubbele kaarten.
    with database.session() as s:
        lijst = s.query(Leerlijst).filter_by(naam="Sachenrecht").one()
        lid = lijst.id
    r = client.post("/leren/nieuw", data={"lijst": str(lid), "stelsel": "DE", "nummer": "929", "soort": "artikel"}, follow_redirects=False)
    assert "bewaard=0" in r.headers["location"]
    assert "★" in client.get("/artikelen/DE/929").text
    r = client.get(f"/leren/{lid}")
    # De tekst komt uit een eigen bron als die er is, anders uit de wettekst.
    assert r.status_code == 200 and "§ 929 BGB" in r.text and "Einigung + Übergabe" in r.text
    r = client.get(f"/leren/{lid}/oefenen")
    assert r.status_code == 200 and "kaarten-data" in r.text
    with database.session() as s:
        k = s.query(Kaart).filter_by(lijst_id=lid, soort="artikel").one()
        kid = k.id
    assert client.post(f"/leren/kaart/{kid}/oefen", data={"gekend": "1"}).json() == {"ok": True}
    with database.session() as s:
        assert s.get(Kaart, kid).gekend is True
    r = client.get(f"/leren/{lid}/export.md")
    assert r.status_code == 200 and "# Sachenrecht" in r.text


def test_arrest_en_vrije_kaart(client):
    r = client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "Jurisprudentie", "soort": ["arrest", "feiten"],
                                          "zaak": "HR 18 juni 1982 (Plas/Valburg)", "vindplaats": "NJ 1983/723",
                                          "feiten": "Onderhandelingen afgebroken", "antwoord": "Afbreken kan onaanvaardbaar zijn"},
                    follow_redirects=False)
    assert "bewaard=2" in r.headers["location"]
    r = client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "Leeg", "soort": "vrij"})
    assert r.status_code == 400


def _lijst_id(naam: str) -> int:
    with database.session() as s:
        return s.query(Leerlijst).filter_by(naam=naam).one().id


def test_api_kaarten_en_stand(anoniem, client):
    _wettekst()
    client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "API", "stelsel": "DE", "nummer": "930", "soort": "artikel"})
    settings.wk_token = TOKEN
    h = {"Authorization": f"Bearer {TOKEN}"}
    try:
        assert anoniem.get("/api/wk/kaarten").status_code == 401
        # De koppeling staat per profiel aan of uit (op /profiel); uit: 403, en de pagina's noemen Wunderkammer niet.
        client.post("/profiel/wunderkammer", data={})
        assert anoniem.get("/api/wk/kaarten", headers=h).status_code == 403
        assert "naar_wk" not in client.get("/leren").text and "Herhalen in Wunderkammer" not in client.get(
            f"/leren/{_lijst_id('API')}").text
        assert 'name="aan" value="1"' in client.get("/profiel").text
        client.post("/profiel/wunderkammer", data={"aan": "1"})
        data = anoniem.get("/api/wk/kaarten", headers=h).json()
        assert data["version"] == 2 and data["kaarten"]
        k = next(k for k in data["kaarten"] if k["refs"] and k["refs"][0]["nummer"] == "930")
        # De achterkant krijgt de wettekst; welke BGB-versie dat is (deze of de fixture uit test_importers) hangt van de volgorde af.
        assert "§ 930 BGB" in k["achter"] and ("Opschrift 930" in k["achter"] or "Besitzkonstitut" in k["achter"])
        assert k["url"].startswith("/artikelen/DE/")
        r = anoniem.post("/api/wk/kaarten/stand", headers=h, json={"stand": [
            {"uid": k["uid"], "due": "2026-11-02T08:00:00+00:00", "stability": 4.2, "reps": 3, "lapses": 1, "last_rating": 3},
            {"uid": "bestaat-niet"}]})
        assert r.json() == {"bijgewerkt": 1}
        with database.session() as s:
            kaart = s.query(Kaart).filter_by(uid=k["uid"]).one()
            assert kaart.stand.herhalingen == 3 and kaart.stand.missers == 1
            assert s.get(Profiel, 1).wk_gezien is not None
        assert "Laatst opgehaald" in client.get("/profiel").text and "Herhalen in Wunderkammer" in client.get(
            f"/leren/{_lijst_id('API')}").text
        # Uit: de stand van dit profiel wordt genegeerd.
        client.post("/profiel/wunderkammer", data={})
        r = anoniem.post("/api/wk/kaarten/stand", headers=h, json={"stand": [{"uid": k["uid"], "reps": 9}]})
        assert r.json() == {"bijgewerkt": 0}
        client.post("/profiel/wunderkammer", data={"aan": "1"})
    finally:
        settings.wk_token = None


def test_lijsten_zijn_persoonlijk(client, anoniem):
    from synoptikon.auth import hash_password

    with database.session() as s:
        p = s.get(Profiel, 3)
        p.gebruikersnaam, p.naam, p.rol, p.actief, p.wachtwoord_hash = "lezer3", "Lezer", "lezer", True, hash_password("lezerwachtwoord")
        lid = s.query(Leerlijst).filter_by(naam="Sachenrecht").one().id
    anoniem.post("/login", data={"gebruikersnaam": "lezer3", "wachtwoord": "lezerwachtwoord", "volgende": "/"})
    assert anoniem.get(f"/leren/{lid}").status_code == 404
    # Een lezer mag wel zijn eigen lijsten bijhouden.
    r = anoniem.post("/leren", data={"naam": "Eigen lijst"}, follow_redirects=False)
    assert r.status_code == 303
    with database.session() as s:
        assert s.query(Leerlijst).filter_by(naam="Eigen lijst").one().profiel_id == 3


def test_stand_uit_wunderkammer_bij_artikel_en_lijst(anoniem, client, monkeypatch):
    """Eén plek om te herhalen: met de koppeling aan toont Synoptikon de stand en verwijst het naar Wunderkammer."""
    from synoptikon.services import wk

    _wettekst()
    client.post("/leren/nieuw", data={"lijst": "nieuw", "nieuwe_lijst": "Stand", "stelsel": "DE", "nummer": "931", "soort": "artikel"})
    lid = _lijst_id("Stand")
    monkeypatch.setattr(settings, "wk_token", TOKEN)
    gemeld = []
    monkeypatch.setattr(wk, "meld", lambda: gemeld.append(1))
    client.post("/profiel/wunderkammer", data={"aan": "1"})
    h = {"Authorization": f"Bearer {TOKEN}"}
    k = next(k for k in anoniem.get("/api/wk/kaarten", headers=h).json()["kaarten"] if k["lijst"] == lid)
    assert k["lees_url"] == "/lezen/DE/931" and isinstance(k["tegenhangers"], list)
    gemeld.clear()
    anoniem.post("/api/wk/kaarten/stand", headers=h, json={"stand": [
        {"uid": k["uid"], "due": "2026-11-02T08:00:00+00:00", "stability": 2.0, "reps": 5, "lapses": 3, "last_rating": 1}]})
    assert not gemeld, "de stand uit Wunderkammer seint niet terug"
    html = client.get("/artikelen/DE/931").text
    assert "wk-fase fase-vastzit" in html and "★" in html
    html = client.get(f"/leren/{lid}").text
    assert f"/review?synoptikon={lid}" in html and f"/leren/{lid}/oefenen" not in html
    assert "Zit vast in Wunderkammer" in client.get("/leren").text
    assert "fase-vastzit" in client.get(f"/leren/{lid}?fase=vastzit").text
    # Een nieuwe kaart seint Wunderkammer (na de commit).
    client.post("/leren/snel", data={"stelsel": "DE", "nummer": "929", "lijst": str(lid)})
    assert gemeld
    r = client.get("/lezen/DE/931", follow_redirects=False)
    assert r.status_code == 303 and "931" in r.headers["location"]
    # Uit: weer het eigen oefenen.
    client.post("/profiel/wunderkammer", data={})
    html = client.get(f"/leren/{lid}").text
    assert f"/leren/{lid}/oefenen" in html and "review?synoptikon" not in html


def test_sein_naar_wunderkammer(monkeypatch):
    import httpx

    from synoptikon.services import wk

    monkeypatch.setattr(settings, "wk_token", TOKEN)
    gezien = {}

    def post(url, headers, json, timeout):
        gezien.update(url=url, auth=headers["Authorization"])
        return httpx.Response(202)

    monkeypatch.setattr(httpx, "post", post)
    assert wk.stuur() and gezien == {"url": settings.wk_url + "/api/synoptikon/push", "auth": f"Bearer {TOKEN}"}

    def stuk(*a, **kw):
        raise httpx.ConnectError("weg")

    monkeypatch.setattr(httpx, "post", stuk)
    assert wk.stuur() is False  # de cron haalt het later op


# --- arrestkaarten: de rechtsregel is het antwoord, de rest is samenhang ------------------------------------------------


def _arrest(**kw):
    from synoptikon.models import Bron
    from synoptikon.services import leren

    with database.session() as s:
        bron = Bron(stelsel_code="NL", soort="rechtspraak", citeertitel="HR 18 juni 1982 (Plas/Valburg)", taal="nl",
                    vindplaats="NJ 1982/659", tekst=kw.pop("tekst", None))
        k = Kaart(soort="arrest", bron=bron, **kw)
        return leren.Bouwer(s).zijden(k)


def test_arrestkaart_rechtsregel_eerst_dan_samenhang():
    z = _arrest(antwoord="Afbreken van onderhandelingen kan onaanvaardbaar zijn.", feiten="Plas brak de onderhandelingen af.",
                tekst="De kern. " * 200)
    assert "Welke rechtsregel volgt uit dit arrest?" in z.voor and "Plas/Valburg" in z.voor
    assert z.achter.startswith("Afbreken van onderhandelingen")
    assert z.achter.index("Samenhang") < z.achter.index("Feiten") < z.achter.index("> De kern.")
    assert len(z.achter) < 1000, "de kerntekst komt ingekort onder de regel, niet in zijn geheel"


def test_arrestkaart_zonder_regel_valt_terug_op_de_kern():
    z = _arrest(tekst="Eén zin kern.")
    assert z.achter == "> Eén zin kern."
    assert "(schrijf bij deze kaart de rechtsregel)" in _arrest().achter


def test_inkorten_op_zinseinde():
    from synoptikon.services.leren import _inkorten

    t = ("Een zin die lang genoeg is om mee te tellen. " * 30).strip()
    kort = _inkorten(t, 200)
    assert kort.endswith("tellen. …") and len(kort) <= 205
    assert _inkorten("kort", 200) == "kort"


def test_opzoeking_toont_voorbeeld_en_bewaart_eigen_regel(client):
    from synoptikon.models import Opzoeking

    with database.session() as s:
        o = Opzoeking(profiel_id=1, invoer="plas", resultaat=dict(soort="uitspraak", stelsel="NL", citeer="HR 18 juni 1982 (Plas/Valburg)",
                                                                  titel="Plas/Valburg", vindplaats="NJ 1982/659", toelichting="Korte toelichting.", bron="eigen"))
        s.add(o)
        s.flush()
        oid = o.id
    html = client.get(f"/opzoeken/{oid}").text
    assert "Zo komt de kaart eruit" in html and "Korte toelichting." in html and 'name="regel"' in html
    client.post(f"/opzoeken/{oid}/bewaren", data={"regel": "Mijn eigen rechtsregel."})
    with database.session() as s:
        k = s.get(Opzoeking, oid).kaart
        assert k.antwoord == "Mijn eigen rechtsregel."
    assert "Zo komt de kaart eruit" not in client.get(f"/opzoeken/{oid}").text


# --- lange artikelen: één kaart per lid ----------------------------------------------------------------------------------

LANG = ("(1) " + "Wer vorsätzlich oder fahrlässig das Leben, den Körper oder das Eigentum eines anderen widerrechtlich verletzt. " * 2 +
        "\n(2) " + "Die gleiche Verpflichtung trifft denjenigen, welcher gegen ein den Schutz eines anderen bezweckendes Gesetz verstößt. " * 2 +
        "\n(3) " + "Ist nach dem Inhalt des Gesetzes ein Verstoß auch ohne Verschulden möglich, so tritt die Ersatzpflicht nur bei Verschulden ein. " * 2)


def test_leden_splitsen():
    from synoptikon.services.leren import leden

    assert [n for n, _t in leden(LANG)] == ["1", "2", "3"]
    assert leden(LANG)[1][1].startswith("(2) Die gleiche")
    assert [n for n, _t in leden("1. Eerste lid.\n2. Tweede lid.")] == ["1", "2"]
    # genummerde onderdelen binnen een lid zijn geen leden
    assert [n for n, _t in leden("(1) Voorwaarden:\n1. a\n2. b\n(2) Gevolg.")] == ["1", "2"]
    assert leden("Eén alinea zonder leden.") == [] and leden("(2) begint niet bij 1\n(3) maar bij 2") == []


def test_lang_artikel_wordt_een_kaart_per_lid(client):
    from synoptikon.models import Kaart as K
    from synoptikon.services import leren

    with database.session() as s:
        w = Wettekst(stelsel_code="DE", wet_id="test-lid", wet="LIDG", stijl="§", kern=False, versie="2026-01-01", titel="Lid-Gesetz")
        s.add(w)
        s.flush()
        s.add(WettekstArtikel(wettekst_id=w.id, nummer="1", opschrift="Haftung", tekst=LANG, volgorde=0))
        s.add(WettekstArtikel(wettekst_id=w.id, nummer="2", opschrift="Kort", tekst="(1) Kort.\n(2) Ook kort.", volgorde=1))
    from synoptikon.services.artikelen import laad_wetnamen, Ref

    with database.session() as s:
        laad_wetnamen(s)
        lijst = Leerlijst(profiel_id=1, naam="Lid-test")
        s.add(lijst)
        s.flush()
        kaarten = leren.maak_kaarten(s, lijst, ["artikel"], ref=Ref("DE", "1", "LIDG"), per_lid=True)
        assert [k.lid for k in kaarten] == ["1", "2", "3"]
        z = leren.Bouwer(s).zijden(kaarten[1])
        assert "lid 2" in z.voor and "Die gleiche Verpflichtung" in z.achter and "vorsätzlich" not in z.achter
        # nog eens bewaren voegt niets toe; een kort artikel blijft één kaart
        assert leren.maak_kaarten(s, lijst, ["artikel"], ref=Ref("DE", "1", "LIDG"), per_lid=True) == []
        kort = leren.maak_kaarten(s, lijst, ["artikel"], ref=Ref("DE", "2", "LIDG"), per_lid=True)
        assert len(kort) == 1 and kort[0].lid is None
        # staat het hele artikel er al, dan niet alsnog splitsen
        hele = Leerlijst(profiel_id=1, naam="Lid-test hele")
        s.add(hele)
        s.flush()
        assert len(leren.maak_kaarten(s, hele, ["artikel"], ref=Ref("DE", "1", "LIDG"))) == 1
        assert leren.maak_kaarten(s, hele, ["artikel"], ref=Ref("DE", "1", "LIDG"), per_lid=True) == []
