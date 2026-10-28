def test_profielen(client, anoniem):
    assert client.get("/profiel").status_code == 200
    r = client.get("/beheer/profielen"); assert r.status_code == 200 and "profiel2" in r.text
    # profiel 2 aanzetten als lezer met wachtwoord
    r = client.post("/beheer/profielen/2", data={"gebruikersnaam": "lezer", "naam": "Lezer", "rol": "lezer", "taal": "fr", "actief": "1", "wachtwoord": "lang-genoeg-1"}, follow_redirects=False)
    assert "fout" not in r.headers["location"], r.headers["location"]
    r = anoniem.post("/login", data={"gebruikersnaam": "Lezer", "wachtwoord": "lang-genoeg-1"}, follow_redirects=False)
    assert r.status_code == 303
    assert anoniem.get("/bronnen").status_code == 200
    assert anoniem.post("/stelsels/NL/actief", data={"actief": "0"}).status_code == 403
    assert anoniem.get("/beheer/profielen").status_code == 403
    assert 'lang="fr"' in anoniem.get("/").text
    # zichzelf niet uitzetten
    r = client.post("/beheer/profielen/1", data={"gebruikersnaam": "beheerder", "naam": "B", "rol": "lezer", "taal": "nl", "actief": "1"}, follow_redirects=False)
    assert "fout" in r.headers["location"]
    # uitzetten logt uit
    client.post("/beheer/profielen/2", data={"gebruikersnaam": "lezer", "naam": "Lezer", "rol": "lezer", "taal": "fr"})
    assert anoniem.get("/bronnen", follow_redirects=False).status_code == 303
