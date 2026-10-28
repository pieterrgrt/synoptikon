import json


def test_login_vereist(anoniem):
    r = anoniem.get("/vragen/eigendomsoverdracht-roerende-zaken", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith("/login")
    r = anoniem.post("/login", data={"gebruikersnaam": "beheerder", "wachtwoord": "fout", "volgende": "/"})
    assert r.status_code == 401
    r = anoniem.post("/login", data={"gebruikersnaam": "beheerder", "wachtwoord": "geheim", "volgende": "/bronnen"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/bronnen"
    assert "synoptikon_sessie" in r.cookies


def test_open_redirect_geblokkeerd(anoniem):
    r = anoniem.post("/login", data={"gebruikersnaam": "beheerder", "wachtwoord": "geheim", "volgende": "//kwaad.example"}, follow_redirects=False)
    assert r.headers["location"] == "/"


def test_pictogrammen_zonder_login(anoniem):
    # Een startpagina of dashboard haalt het pictogram op zonder sessie.
    for pad, soort in [
        ("/favicon.ico", "image/"),
        ("/apple-touch-icon.png", "image/png"),
        ("/apple-touch-icon-precomposed.png", "image/png"),
        ("/static/favicon.svg", "image/svg+xml"),
        ("/static/manifest.json", "application/json"),
    ]:
        r = anoniem.get(pad, follow_redirects=False)
        assert r.status_code == 200 and r.headers["content-type"].startswith(soort), pad
    assert "prefers-color-scheme: dark" in anoniem.get("/static/favicon.svg").text
    for icoon in anoniem.get("/static/manifest.json").json()["icons"]:
        assert anoniem.get(icoon["src"]).status_code == 200
    html = anoniem.get("/").text  # belandt op de loginpagina
    assert 'href="/favicon.ico"' in html and 'rel="apple-touch-icon"' in html


def test_synopse_toont_drie_lagen(client):
    r = client.get("/vragen/eigendomsoverdracht-roerende-zaken?vertaling=nl")
    assert r.status_code == 200
    html = r.text
    assert "§ 929 BGB" in html and "art. 1196 C. civ." in html and "art. 3:84 BW" in html
    assert 'class="origineel"' in html and 'class="vertaling"' in html and 'class="annotatie"' in html
    assert "Abstraktionsprinzip" in html
    # concordantie 1138 → 1196 verschijnt automatisch
    assert "art. 1138" in html


def test_zoeken_zonder_accenten(client):
    r = client.get("/zoeken", params={"q": "delivrance"})
    assert "<mark>délivrance</mark>" in r.text
    r = client.get("/zoeken", params={"q": "Ubergabe"})
    assert "Übergabe" in r.text
    r = client.get("/zoeken", params={"q": "ECLI:NL:HR:2005"})
    assert "CBB/JPO" in r.text


def test_export_markdown(client):
    r = client.get("/vragen/precontractuele-aansprakelijkheid/export.md")
    assert r.status_code == 200
    assert r.text.startswith("# Wanneer leidt het afbreken")
    assert "## Duitsland" in r.text and "§ 311 BGB" in r.text and "### Analyse" in r.text


def test_export_begrippenparen(client):
    r = client.get("/begrippen/export.json")
    doc = json.loads(r.text)
    assert doc["format"] == "synoptikon-begrippenparen" and doc["version"] == 1
    assert len(doc["pairs"]) >= 20
    faux = [p for p in doc["pairs"] if p["relation"] == "faux_ami"]
    assert any({p["front"]["term"], p["back"]["term"]} == {"levering", "délivrance"} for p in faux)
    p = doc["pairs"][0]
    assert set(p) >= {"id", "front", "back", "relation", "relation_label", "note", "questions", "tags"}


def test_begrippenkaart_json(client):
    data = client.get("/begrippen/kaart.json").json()
    assert {k["stelsel"] for k in data["knopen"]} == {"NL", "DE", "FR", "EU", "BE", "IT", "ES", "CH", "EN", "US", "AU"}
    assert {k["type"] for k in data["kanten"]} == {"equivalent", "deels", "faux_ami", "geen"}
    assert all(k["familie"] for k in data["knopen"])
    # De twee clusters (vragen) blijven gescheiden; ieder begrip hangt aan een vraag.
    assert {v for k in data["knopen"] for v in k["vragen"]} == {"eigendomsoverdracht-roerende-zaken", "precontractuele-aansprakelijkheid"}
    assert all(k["vragen"] for k in data["knopen"])
    r = client.get("/begrippen", params={"vraag": "precontractuele-aansprakelijkheid"})
    assert r.status_code == 200 and "Walford" in r.text and "Kausalitätsprinzip" not in r.text


def test_systematiek_markeert_bronnen(client):
    r = client.get("/stelsels/DE", params={"vraag": "eigendomsoverdracht-roerende-zaken"})
    assert "bevat-markering" in r.text and "Untertitel 1 · Übertragung" in r.text
    assert "§ 812 BGB" in r.text  # staat in Schuldrecht, niet in Sachenrecht: structuurverschil zichtbaar


def test_volledige_invoerstroom(client):
    r = client.post("/vragen/nieuw", data={"titel": "Testvraag verjaring", "rechtsgebied": "Goederenrecht"}, follow_redirects=False)
    slug = r.headers["location"].rsplit("/", 1)[-1]
    assert slug == "testvraag-verjaring"
    r = client.post("/invoer/bron", data={"vraag_slug": slug, "stelsel_code": "DE", "soort": "wet", "citeertitel": "§ 937 BGB", "tekst": "Wer eine bewegliche Sache zehn Jahre im Eigenbesitz hat, erwirbt das Eigentum.", "rol": "hoofdregel"}, follow_redirects=False)
    assert r.status_code == 303
    client.post("/invoer/notitie", data={"vraag_slug": slug, "tekst": "Snelle notitie"})
    client.post("/invoer/begrip", data={"vraag_slug": slug, "stelsel_code": "DE", "term": "Ersitzung", "definitie": "Erwerb durch Eigenbesitz"})
    client.post(f"/vragen/{slug}/antwoord/DE", data={"kern": "Kern", "analyse": "## Analyse\n\n*tekst*"})
    html = client.get(f"/vragen/{slug}").text
    for s in ("§ 937 BGB", "Snelle notitie", "Ersitzung", "<em>tekst</em>", "Kern"):
        assert s in html
    # zoekindex is via triggers bijgewerkt
    assert "Ersitzung" in client.get("/zoeken", params={"q": "Eigenbesitz"}).text
    client.post(f"/vragen/{slug}/verwijderen")
    assert client.get(f"/vragen/{slug}").status_code == 404
    # bron en begrip blijven bestaan
    assert "§ 937 BGB" in client.get("/bronnen").text


def test_print_en_pdf(client):
    assert client.get("/vragen/eigendomsoverdracht-roerende-zaken/print").status_code == 200
    r = client.get("/vragen/eigendomsoverdracht-roerende-zaken/export.pdf")
    assert r.status_code in (200, 501)
    if r.status_code == 200:
        assert r.content[:5] == b"%PDF-"
