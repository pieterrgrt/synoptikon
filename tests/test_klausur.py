"""Klausurtrainer: volgorde van Anspruchsgrundlagen, pogingen bewaren en inleveren, beoordeling via (nep-)Claude,
kaartvoorstel en het overzicht van wat steeds misgaat."""
from datetime import timedelta

import pytest

from synoptikon import db as database
from synoptikon.config import settings
from synoptikon.models import Casus, CasusPoging, CasusProbleem, Kaart, LlmGebruik, Wettekst, WettekstArtikel, now
from synoptikon.services import citaties, claude, klausur
from tests.test_notities import NepClient

BGB = {"119": "(1) Wer bei der Abgabe einer Willenserklärung über deren Inhalt im Irrtum war …\n\n(2) Als Irrtum über den Inhalt …",
       "122": "(1) Ist eine Willenserklärung nach § 118 nichtig …\n\n(2) Die Schadensersatzpflicht tritt nicht ein …",
       "433": "(1) Durch den Kaufvertrag wird der Verkäufer …\n\n(2) Der Käufer ist verpflichtet …",
       "985": "Der Eigentümer kann von dem Besitzer die Herausgabe der Sache verlangen.",
       "812": "(1) Wer durch die Leistung eines anderen …", "823": "(1) Wer vorsätzlich oder fahrlässig …"}

BEOORDELING = {
    "punkte": 25, "gesamturteil": "De Anfechtung is gezien, § 122 niet.", "staerken": ["Aufbau klopt"], "schwaechen": ["§ 122 BGB ontbreekt"],
    "aufbau": {"urteil": "richtig", "kommentar": "Vertrag vóór de rest."},
    "stil": {"urteil": "gemischt", "kommentar": "Vaak Urteilsstil.", "beispiele": [{"zitat": "V hat angefochten, weil …", "problem": "Urteilsstil",
                                                                                       "besser": "V könnte angefochten haben."}]},
    "schwerpunkte": {"urteil": "teilweise", "kommentar": "Te lang over het Angebot."},
    "pruefungspunkte": [
        {"titel": "Anspruch aus § 433 Abs. 1 S. 1 BGB", "normen": ["§ 433 Abs. 1 S. 1 BGB"], "erwartet": "Kaufvertrag", "status": "gezien",
         "anspruchsgrundlage": "richtig", "obersatz": "gut", "definition": "entfaellt", "subsumtion": "gut", "ergebnis": "gut", "kommentar": "",
         "probleem": False, "leervraag": "", "leerantwoord": ""},
        {"titel": "Anfechtungsgrund", "normen": ["§ 119 Abs. 1 BGB"], "erwartet": "Erklärungsirrtum", "status": "deels",
         "anspruchsgrundlage": "entfaellt", "obersatz": "gut", "definition": "fehlt", "subsumtion": "mangelhaft", "ergebnis": "gut",
         "kommentar": "De definitie van het Erklärungsirrtum ontbreekt.", "probleem": True,
         "leervraag": "Was ist ein Erklärungsirrtum?", "leerantwoord": "Der Erklärende wollte eine Erklärung dieses Inhalts nicht abgeben."},
    ],
    "fehlende_probleme": [{"titel": "Ersatz des Vertrauensschadens", "normen": ["§ 122 Abs. 1 BGB"], "erklaerung": "Niet behandeld.",
                           "leervraag": "", "leerantwoord": ""}],
    "skizze": [{"niveau": 1, "titel": "A. Anspruch aus § 433 Abs. 1 S. 1 BGB", "groep": "vertrag", "normen": ["§ 433 Abs. 1 S. 1 BGB"],
                "inhoud": "Kaufvertrag", "probleem": False}],
}


@pytest.fixture
def bgb():
    with database.session() as s:
        w = s.query(Wettekst).filter_by(stelsel_code="DE", wet_id="test-bgb-klausur").first()
        if w is None:
            w = Wettekst(stelsel_code="DE", wet_id="test-bgb-klausur", titel="Bürgerliches Gesetzbuch", versie="2026-01-01")
            s.add(w)
            s.flush()
            for i, (nr, tekst) in enumerate(BGB.items()):
                s.add(WettekstArtikel(wettekst_id=w.id, nummer=nr, opschrift=f"Opschrift {nr}", tekst=tekst, volgorde=i))


@pytest.fixture
def nep(monkeypatch):
    monkeypatch.setattr(settings, "anthropic_api_key", "sk-test")
    monkeypatch.setattr(klausur, "ACHTERGROND", False)

    def zet(eind):
        client = NepClient(eind)
        monkeypatch.setattr(claude, "client_factory", lambda key: client)
        return client
    return zet


def test_anspruchsgroep():
    def groep(t):
        return klausur.anspruchsgroep(citaties.vind(t, "DE")[0])
    assert groep("§ 433 I 1 BGB") == "vertrag"
    assert groep("§§ 280 I, III, 281 BGB") == "vertrag"
    assert groep("§§ 280 I, 311 II, 241 II BGB") == "vertragsaehnlich"
    assert groep("§§ 683 S. 1, 670 BGB") == "vertragsaehnlich"
    assert groep("§§ 990 I, 989 BGB") == "dinglich"
    assert groep("§ 7 I StVG") == "delikt"
    assert groep("§ 812 I 1 Alt. 1 BGB") == "bereicherung"
    assert groep("§ 119 II BGB") is None


def test_volgorde():
    goed = "A. K gegen V aus § 433 I 1 BGB\n  1. Anfechtung, § 119 II\nB. K gegen V aus § 985 BGB\nC. K gegen V aus § 812 I 1 Alt. 1 BGB"
    assert klausur.volgorde(goed) == []
    fout = "A. K gegen V aus § 812 I 1 Alt. 1 BGB\nB. K gegen V aus § 985 BGB"
    o = klausur.volgorde(fout)
    assert len(o) == 1 and o[0].regel == 2 and o[0].groep == "dinglich" and o[0].na_groep == "bereicherung"
    assert "§ 985 BGB" in o[0].tekst
    # per paar partijen begint de volgorde opnieuw
    assert klausur.volgorde("A. K gegen V aus § 823 I BGB\nB. V gegen K aus § 433 II BGB") == []


def test_stijl_en_note():
    t = klausur.stijl_telling("K könnte einen Anspruch haben. Fraglich ist, ob … Folglich ja, weil V geliefert hat.")
    assert t["gutachten"] == 3 and t["urteil"] == 1
    assert klausur.note(18) == "sehr gut" and klausur.note(9) == "befriedigend" and klausur.note(4) == "ausreichend" and klausur.note(0) == "ungenügend"


def test_voorbeeldcasussen_geladen():
    with database.session() as s:
        cs = s.query(Casus).filter(Casus.herkomst == "seed").all()
        assert len(cs) == 3 and all(c.profiel_id is None and not c.geverifieerd and c.skizze and c.normen for c in cs)
        # de skizze van elke voorbeeldcasus staat zelf in de juiste volgorde
        for c in cs:
            koppen = "\n".join(p["titel"] for p in c.skizze if p["niveau"] == 1)
            assert klausur.volgorde(koppen) == [], c.titel
            groepen = [klausur.GROEPEN.index(p["groep"]) for p in c.skizze if p["niveau"] == 1]
            assert all(g in range(5) for g in groepen)


def test_genoemde_normen(bgb):
    with database.session() as s:
        ns = klausur.genoemde_normen(s, "Anspruch aus § 433 I 1 BGB; Anfechtung nach § 119 I; § 9999 BGB; § 2 FantasieG.")
    per = {n.tekst: n for n in ns}
    assert per["§ 433 BGB"].gevonden and per["§ 433 BGB"].url == "/artikelen/DE/433?lid=Abs.%201" or per["§ 433 BGB"].url.startswith("/artikelen/DE/433")
    assert per["§ 119 BGB"].gevonden and per["§ 119 BGB"].aangenomen
    assert not per["§ 9999 BGB"].gevonden and per["§ 9999 BGB"].url is None
    assert per["§ 2 FantasieG"].onbekend == "FantasieG"


def test_poging_bewaren_en_tijd(bgb):
    with database.session() as s:
        c = klausur.maak(s, 1, "", "V verkauft K ein Rad. K verlangt Lieferung nach § 433 I 1 BGB.", niveau="klausur2")
        assert c.titel.startswith("V verkauft K ein Rad") and c.normen == ["§ 433 Abs. 1 S. 1 BGB"]
        p = klausur.start(s, 1, c, "klausur")
        assert p.limiet == 120 and klausur.rest_seconden(p) > 7000
        r = klausur.bewaar(p, "A. § 433", "K könnte …", 0)
        assert r == 1
        with pytest.raises(klausur.Conflict):
            klausur.bewaar(p, "oud", "oud", 0)  # een ander apparaat met de oude revisie
        assert p.skizze == "A. § 433"
        # de tijd is om: de poging geldt als ingeleverd op het einde van de tijd
        p.begonnen = now() - timedelta(minutes=130)
        assert klausur.sluit_als_tijd_om(p) and not p.open and p.status == "ingeleverd"
        with pytest.raises(ValueError):
            klausur.bewaar(p, "te laat", "", None)
        vrij = klausur.start(s, 1, c, "oefenen")
        assert vrij.limiet is None and klausur.rest_seconden(vrij) is None


def test_beoordelen_problemen_en_kaartvoorstel(bgb, nep):
    client = nep(BEOORDELING)
    with database.session() as s:
        c = klausur.maak(s, 1, "Tippfehler", "V vertippt sich …", vak="ZR Ia")
        p = klausur.start(s, 1, c)
        klausur.bewaar(p, "A. K gegen V aus § 433 I 1 BGB", "K könnte einen Anspruch aus § 433 I 1 BGB haben.")
        pid, cid = p.id, c.id
    with database.session() as s:
        voor = s.query(LlmGebruik).filter_by(doel="klausur").count()
        klausur.beoordeel(s, s.get(CasusPoging, pid), "nl")
        assert s.query(LlmGebruik).filter_by(doel="klausur").count() == voor + 1  # geboekt voor het budget
    verzoek = client.verzoeken[-1]
    assert "web_search" not in str(verzoek["tools"]) and verzoek["output_config"]["format"]["schema"] == klausur.BEOORDELING
    assert "<uitwerking_van_de_student>" in verzoek["messages"][0]["content"] and "Nederlands" in verzoek["system"]
    with database.session() as s:
        p = s.get(CasusPoging, pid)
        assert p.status == "beoordeeld" and not p.open and p.beoordeling["punkte"] == 18  # 25 afgekapt op de schaal
        assert "skizze" not in p.beoordeling and p.casus.skizze[0]["titel"].startswith("A. Anspruch")  # eigen skizze van Claude bewaard
        ps = {x.titel: x for x in p.problemen}
        assert len(ps) == 3 and ps["Anfechtungsgrund"].status == "deels" and ps["Anfechtungsgrund"].nummer == "119"
        gemist = ps["Ersatz des Vertrauensschadens"]
        assert gemist.status == "gemist" and (gemist.stelsel_code, gemist.nummer, gemist.detail) == ("DE", "122", "Abs. 1")
        # kaartvoorstel: met leervraag een vrije kaart, zonder een artikelkaart; beide als voorstel in de lijst van het vak
        k1 = klausur.kaartvoorstel(s, ps["Anfechtungsgrund"])
        k2 = klausur.kaartvoorstel(s, gemist)
        assert (k1.soort, k1.status, k1.actief) == ("vrij", "voorstel", False) and k1.lijst.vak == "ZR Ia" and "§ 119 Abs. 1 BGB" in k1.antwoord
        assert (k2.soort, k2.nummer, k2.status) == ("artikel", "122", "voorstel") and k2.herkomst == "Klausur/Tippfehler"
        assert klausur.kaartvoorstel(s, gemist).id == k2.id  # nog eens tikken maakt geen tweede kaart
    # een tweede casus waarin § 122 weer ontbreekt: 'steeds gemist'
    with database.session() as s:
        c2 = klausur.maak(s, 1, "Tweede", "Noch ein Fall …", vak="ZR Ia")
        p2 = klausur.start(s, 1, c2)
        klausur.bewaar(p2, "", "Kurz.")
        klausur.beoordeel(s, p2, "nl")
        g = klausur.steeds_gemist(s, 1)
        eerste = g[0]
        assert eerste.ref.nummer == "122" and eerste.steeds and eerste.gemist == 2 and len(eerste.casussen) == 2 and eerste.kaart_id
        assert all(x.titel != "Anspruch aus § 433 Abs. 1 S. 1 BGB" for x in g)  # wat goed ging staat er niet
        # opnieuw beoordelen vervangt de problemen, maar laat staan waar een kaart aan hangt
        klausur._beoordeel(pid, "nl", s)
        assert s.query(CasusProbleem).filter_by(poging_id=pid).count() == 3 + 2


def test_fout_van_claude_blijft_zichtbaar(bgb, nep, monkeypatch):
    nep(BEOORDELING)
    monkeypatch.setattr(settings, "llm_budget_usd", 0.0)
    with database.session() as s:
        c = klausur.maak(s, 1, "Budget", "Ein Fall.")
        p = klausur.start(s, 1, c)
        with pytest.raises(ValueError):
            klausur.beoordeel(s, p, "nl")  # nog niets geschreven
        klausur.bewaar(p, "skizze", "")
        klausur.beoordeel(s, p, "nl")
        assert p.status == "fout" and "budget" in p.fout.lower() and p.beoordeling is None


def test_genereren_en_musterloesung(bgb, nep):
    nep({"titel": "Der Irrtum", "sachverhalt": "V schreibt 890 statt 980 €.", "fallfrage": "Kann K Lieferung verlangen?",
         "normen": ["§ 119 Abs. 1 BGB", "§ 433 Abs. 1 S. 1 BGB"], "skizze": BEOORDELING["skizze"]})
    with database.session() as s:
        c = klausur.genereer(s, 1, "Anfechtung", "ag", "ZR Ia", "§ 119 BGB", "kort", "nl")
        assert (c.status, c.herkomst, c.geverifieerd) == ("klaar", "claude", False)
        assert c.titel == "Der Irrtum" and c.fallfrage and c.skizze and c.usd > 0
        cid = c.id
    nep({"musterloesung": "## A. Anspruch aus § 433 Abs. 1 S. 1 BGB\n\nK könnte …"})
    with database.session() as s:
        c = s.get(Casus, cid)
        klausur.muster(s, c, "nl")
        assert c.muster_status == "klaar" and c.musterloesung.startswith("## A.")
        html = klausur.Koppelaar(s).md(c.musterloesung)
        assert '<a href="/artikelen/DE/433?lid=Abs.%201%20S.%201">§ 433 Abs. 1 S. 1 BGB</a>' in html
    nep({"titel": "", "sachverhalt": "", "fallfrage": "", "normen": [], "skizze": []})
    with database.session() as s:
        c = klausur.genereer(s, 1, "Leeg", "ag")
        assert c.status == "fout" and c.fout
