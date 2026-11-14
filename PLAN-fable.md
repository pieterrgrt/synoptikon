# Plan: zeven modules voor studie en praktijk

Geschreven op 14-11-2026, vóór het bouwen. Volgorde A → G; elke module is een eigen branch `fable/<letter>-<naam>` en
een eigen PR. De branches stapelen: B bouwt op A, C op B, enzovoort (ze delen `db.py`, de catalogi in `i18n/`, het menu
en de README, dus los van elkaar zouden ze elkaar bij elke merge in de weg zitten). Merge ze dus in volgorde; GitHub zet
de volgende PR vanzelf op `main` zodra de vorige branch weg is.

Stand van `main` bij het begin: 303 tests groen.

## Wat voor alle modules geldt

| Onderwerp | Keuze |
|---|---|
| Werkplek | Eigen worktree (`~/orca/workspaces/synoptikon/fable`), eigen venv. De serverkopie `~/synoptikon` blijft op `main` en schoon; de container en `data/synoptikon.db` blijven onaangeroerd. Proeven op een kopie in `/tmp/syn-fable/` (alleen-lezen gekopieerd). |
| Migratie | Nieuwe tabellen via `Base.metadata.create_all`, nieuwe kolommen via `_NIEUWE_KOLOMMEN` in `db.py`. Alles is toevoegen; niets wordt hernoemd of verwijderd, dus een oude en een nieuwe container kunnen naast elkaar op dezelfde database. |
| Claude | Alleen via `services/claude.loop` (budget, `llm_gebruik`, fallbacks, lokale wettekst-tools). Geen webzoekacties in de nieuwe taken: de Klausur lost men op met de wet alleen. Uitvoer altijd als JSON-schema, zonder recursie en zonder min/max (dat ondersteunt de API niet): bomen gaan als platte lijst met een `niveau`. Alles wat Claude levert draagt `geverifieerd = False` of `status = voorstel` tot Pieter het goedkeurt. `claude-fable-5-2` ($8/$40) erbij in `PRIJZEN`. |
| Achtergrondwerk | Zoals opzoeken en onderzoek: een rij met `status` (wacht · bezig · klaar · fout), een thread, en `data-bezig` op de pagina die het blok ververst. |
| Citaties in lopende tekst | Nieuw: `services/citaties.py`, een scanner die in vrije tekst alle verwijzingen vindt (ook "§§ 280 I, III, 281 BGB") en ze met `artikelen.lees` tot `Ref`s maakt. A gebruikt hem om normen te koppelen, C breidt hem uit met de taal van de wet zelf, D met ECLI, CELEX, roepnamen en EU-handelingen. |
| Interface | Server-side HTML, vanilla JS in eigen bestanden (geen inline scripts), mobile-first; printweergaven op A5 via `@page`. Geen wervende introregels: titel, inhoud, en waar nodig het voorbehoud of de bediening. |
| i18n | Alle tekst via `_()`; nl is de sleutel, de/fr/it/en/es in `i18n/*.json`. `tests/test_i18n.py` blijft groen. |
| Rollen | Nieuwe POST-routes vallen buiten `_LEZER_POST`: een lezer (medestudent) kan lezen maar geen Claude-kosten maken. |
| Menu | "Klausur" en "Schemata" in het hoofdmenu; Termijnen, Citatiecontrole, Dossiers en Wijzigingen onder ⋯. |

## A. Klausurtrainer (`fable/a-klausurtrainer`)

**Datamodel**

- `casus`: profiel (leeg = voor iedereen: de voorbeeldcasussen), titel, sachverhalt, fallfrage, onderwerp, niveau
  (`ag` · `klausur2` · `klausur5`), vak, normen (JSON), herkomst (`eigen` · `claude` · `seed`), geverifieerd,
  status/fout (genereren), skizze (JSON: de verwachte Prüfungspunkte, verborgen tot na het inleveren),
  musterloesung (markdown) met eigen status, model, usd.
- `casus_poging`: casus, profiel, modus (`oefenen` · `klausur`), skizze, uitwerking, begonnen, limiet (minuten),
  gewerkt (seconden), revisie (tegen overschrijven vanaf een ander apparaat), ingeleverd, status, beoordeling (JSON
  volgens `klausur.BEOORDELING`), fout, model, usd.
- `casus_probleem`: één rij per Prüfungspunkt of gemist probleem uit een beoordeling: titel, hoofdnorm (stelsel, wet,
  nummer, detail), categorie, status (`gezien` · `deels` · `gemist` · `fout`), uitleg, leervraag, leerantwoord, kaart.
  Hieruit komt het overzicht "wat ik steeds mis".

**Routes** (`/klausur`)

`GET /klausur` overzicht · `GET|POST /klausur/nieuw` (plakken) · `POST /klausur/genereer` (Claude) ·
`GET /klausur/{id}` casus · `POST /klausur/{id}/start` · `GET /klausur/poging/{id}` werkblad ·
`POST …/bewaar` (autosave, JSON) · `POST …/inleveren` · `POST …/beoordeel` · `GET …/stand` (fragment) ·
`GET /klausur/wet` (wettekst zonder eigen aantekeningen) · `GET|POST /klausur/{id}/muster` ·
`POST /klausur/probleem/{id}/kaart` · `GET /klausur/problemen`.

**Schermen**

1. Overzicht: lopende pogingen, casussen, "Nieuwe casus", "Wat ik steeds mis".
2. Nieuwe casus: plakken, of onderwerp + niveau + normen voor Claude.
3. Werkblad: Sachverhalt · Skizze · Uitwerking · Gesetz als tabs op de telefoon, naast elkaar op een laptop. In de
   Klausurmodus verdwijnen menu en zoekveld, loopt de timer (de server bewaart `begonnen`, dus herladen kost geen
   tijd) en is alleen de wettekst bereikbaar. Knoppen in de skizze zetten de vijf groepen Anspruchsgrundlagen neer; een
   deterministische controle waarschuwt als de volgorde niet Vertrag → vertragsähnlich → dinglich → Delikt →
   Bereicherung is.
4. Beoordeling: Notenpunkte, per Prüfungspunkt een regel met Obersatz/Definition/Subsumtion/Ergebnis, stijl
   (Gutachten/Urteil) met citaten, Schwerpunktsetzung, gemiste problemen met "kaartvoorstel"; elke norm is een link naar
   de lokale tekst. De Musterlösung staat op een eigen pagina.
5. Wat ik steeds mis: per norm/probleem hoe vaak gemist, in welke casussen, met kaartvoorstel.

**Hergebruik**: `claude.loop` en de wettekst-tools, `artikelen.herken`/`Ref.url`, `leren.maak_kaarten` met
`status="voorstel"` in de lijst "Klausur · <vak>" (zelfde voorstellenstroom als notities, dus pas na overnemen naar
Wunderkammer), `bezig.js`, `md.render`.

**Risico's**: (1) de beoordeling is zo goed als het model; daarom een vast schema, de wettekst verplicht via de tools
en overal "niet geverifieerd". (2) De eigen voorbeeldcasussen moeten juridisch kloppen: drie klassieke AG-gevallen
(Anfechtung bij verschrijving, Minderjährigenrecht met § 110, Unmöglichkeit met §§ 280 I, III, 283), elk met normen
die tegen de lokale BGB-tekst zijn nagelopen. (3) Tekstverlies op de telefoon: autosave plus een kopie in
`localStorage`.

## B. Prüfungsschemata en Streitstände (`fable/b-schemata`)

**Datamodel**

- `schema`: slug, titel, stelsel, vak, onderwerp, inleiding, geverifieerd, herkomst, versie, profiel (leeg = gedeeld).
- `schema_stap`: schema, ouder, positie, titel, normen (JSON), definitie, toelichting, arresten (JSON), vergelijk
  (eigen aantekening NL/FR), thema (koppeling met de correspondentietabel).
- `schema_stap_streit`: stap ↔ Streitstand.
- `schema_versie`: momentopname van de hele boom (JSON) met datum en opmerking; terugzetten kan.
- `streitstand`: slug, titel, probleem, normen, stellungnahme (eigen), geverifieerd, herkomst.
- `standpunt`: streitstand, positie, label (BGH/Rspr. · h.M. · h.L. · a.A.), stelling, argumenten (JSON), bronnen.
- `kaart` krijgt `schema_id`, `stap_id`, `streit_id` en drie soorten (`schema`, `definitie`, `streit`): de zijden worden
  net als bij artikelkaarten telkens uit het schema opgebouwd, dus een verbeterd schema komt vanzelf in Wunderkammer.

**Routes** (`/schemata`, `/streit`): overzicht per onderwerp, schema lezen (inklapbaar), bewerken per stap (toevoegen,
omhoog/omlaag, weg), versies, goedkeuren, `print` en `export.pdf` (A5, één schema per zijde), "kaarten maken",
"laten opstellen" (Claude); Streitstand lezen/bewerken/goedkeuren.

**Vullen**: `seed/schemata.py`, door mij geschreven aan de hand van de lokale BGB-tekst, alles `geverifieerd=False`:
Anspruchsaufbau § 433 II, Vertragsschluss, Anfechtung, Stellvertretung, Geschäftsfähigkeit, Unmöglichkeit,
Schadensersatz statt der Leistung, Verzug, Rücktritt, c.i.c., AGB-Kontrolle; en de Streitstände die daar het vaakst bij
horen. Bronnen alleen waar ik de vindplaats zeker weet. `synoptikon schemata --controle` loopt elke norm na tegen de
lokale tekst.

**Vergelijken**: per stap de tegenhangers uit de correspondentietabel (`corr.thema_s_voor`) in mijn andere stelsels,
plus de begrippen waarvan de term in de stap voorkomt met hun relaties (faux amis!).

**Risico's**: juridische juistheid van de startset (daarom "niet geverifieerd" en de controle op normen); een boom
bewerken op een telefoon (daarom formulieren per stap, zoals de leessets).

## C. Verweisungsnetz (`fable/c-verweisungen`)

**Datamodel**: `verwijzing`: wettekst (bron, verdwijnt mee met de versie), nummer, lid, naar (stelsel, wet, nummer,
tot, detail), soort (`verweis` · `entsprechend` · `rechtsgrund` · `rechtsfolge` · `definitie` · `unberuehrt` ·
`abweichend`), fragment. `wettekst.verwijzingen_hash`: bij welke stand de verwijzingen berekend zijn.

**Herkennen** (`services/verwijzingen.py`, deterministisch): de scanner uit A met de wet van het artikel als context.
DE: ketens, bereiken, "bis", "ff.", Abs./Satz/Nr., "des Handelsgesetzbuchs", "Vorschriften über …" (alleen als het
opschrift in dezelfde wet precies één keer voorkomt), "entsprechende Anwendung". NL: "artikel 6:162", "artikel 74",
"de artikelen 3:296 tot en met 3:300", "het vorige artikel", "de vorige afdeling". FR: "l'article 1112-1", "aux
articles 1112 à 1112-2", "L. 211-4", "du code de la consommation". EU: "Artikel 6 Absatz 1", andere handelingen op
nummer. Rechtsgrund- en Rechtsfolgenverweisung volgen niet uit de woorden: daarvoor een kleine eigen tabel van
gevallen waar de h.M. vaststaat (§ 951 I 1, § 988, § 684 S. 1 …), zo gemarkeerd.

**Haak**: `bijwerken.Ronde.verwerk` en `store` berekenen de verwijzingen opnieuw als de hash verschilt;
`synoptikon verwijzingen [--stelsel DE] [--alles] [--meet]` voor de eerste keer en voor de meting.

**Schermen**: op de artikelpagina "verweist auf" / "wird verwiesen von" met een kleine graaf (SVG van de server);
`/normenkette`: artikelen kiezen, leden invullen, de citatie samenstellen (`citeren.keten`: "§§ 280 I, III, 281 I 1
BGB").

**Kwaliteit**: `tests/fixtures/verwijzingen/<stelsel>.json` met echte artikelteksten en met de hand gecontroleerde
verwijzingen; de test eist een ondergrens en de PR meldt precisie en recall. Bij twijfel geen verwijzing.

**Risico's**: omvang (440.000 artikelen): standaard de registerwetten en de belangrijke wetten, de rest met `--alles`;
de meting op de kopie bepaalt wat ik aanraad.

## D. Citatiecontrole (`fable/d-citatiecontrole`)

**Datamodel**: `document` (profiel, titel, formaat, tekst, origineel gecomprimeerd, stijl, status) en `citatie`
(document, plaats, ruw, soort, ref, oordeel, bevindingen JSON, correctie, inhoudsoordeel van Claude, besluit).

**Invoer**: plakken, .md, .docx (ook voetnoten: `word/footnotes.xml`), .pdf (nieuw: `pypdf`).

**Controles** (deterministisch): bestaat het artikel lokaal, bestaat het lid, is het vervallen, is het vernummerd
(concordantie; FR 2016), peildatum van de tekst; ECLI en CELEX op vorm en tegen eigen bronnen en de EU-catalogus;
roepnamen; EU-handelingen op nummer en geldigheid. Of de inhoud bij de zin past doet Claude, als voorstel.

**Uitvoer**: de tekst met markeringen, per citatie oordeel en correctie; omzetten naar DE (juristische Zitierweise),
NL (Leidraad) of OSCOLA; terug als .md en .docx (een geüpload .docx wordt in place aangepast, met behoud van opmaak).
"Kaarten eruit": de notitiestroom (`notities`) op deze tekst.

**Risico's**: opmaakverlies in .docx als een citatie over meerdere runs loopt (dan worden die runs samengevoegd);
pdf-tekst is rommelig (afbrekingen), dus daar alleen controleren, niet terugschrijven.

## E. Versies, peildatum en wijzigingen (`fable/e-versies`)

**Datamodel**: `artikel_versie`: stelsel, wet_id, wet, nummer, soort (`gewijzigd` · `vervallen` · `nieuw`), de oude
tekst en het oude opschrift (zlib), versielabel oud en nieuw, vastgesteld (datum van de bijwerking). Alleen
gewijzigde artikelen, dus enkele kB per wetswijziging. `volg` (profiel, stelsel, wet, nummer of hele wet);
`kaart.nagekeken`, `markering.nagekeken`.

**Haak**: `store.werk_bij` en de historietak van `bijwerken.vergelijk` leggen de oude versie vast vóór ze verdwijnt.
`synoptikon versies --uit-bestaande` leidt de geschiedenis af uit de volledige versies die er al staan.

**Schermen**: op de artikelpagina "Versies" met woorddiff en `?peil=2024-01-01`; `/wijzigingen` (deze week, gevolgd of
alles); `/volgen`; "nakijken" bij kaarten en markeringen op een gewijzigd artikel, met de diff.

**Risico's**: de datum van een versie is de datum waarop de bron haar gaf, niet altijd de inwerkingtreding; de
weergave zegt dat erbij.

## F. Termijnen (`fable/f-termijnen`)

Geen database behalve `berekening` (bewaren, later aan een dossier). `services/termijnen/`: `kalender.py`
(feestdagen DE per Bundesland, NL volgens de Algemene termijnenwet), `de.py`, `nl.py`, een register per stelsel zodat
FR en EU kunnen aanhaken. Elke stap: wat, uitkomst, norm (link). `/termijnen` met een formulier per rekenaar en
deelbare URL's; `/termijnen/oefenen`: opgave, zelf rekenen, dan de stappen.

DE: §§ 187–193, §§ 195, 199 (Jahresende, Höchstfristen), Hemmung (§§ 203, 204, 209) en Neubeginn (§ 212), §§ 121, 124,
§§ 355, 356. NL: art. 3:306–3:311 BW, stuiting (3:316–3:319), Algemene termijnenwet.

## G. Dossiers (`fable/g-dossiers`)

Een dossier is een leesset met `soort = dossier`: de geordende onderdelen, de redenen en de knop "In leesset" bij
elk artikel en elke uitspraak bestaan al. Erbij: `leesset.feiten`, `leesset.peildatum`, `leesset.kenmerk`, en per
onderdeel `rubriek` (feit · tijdlijn · rechtsvraag · bron), `datum`, en koppelingen naar berekening, schema en casus.
Uitvoer: memo als .md, .docx en PDF met citaties in de gekozen stijl, bronnenlijst en de peildatum van elke wettekst.

## Vijf volgende stappen

Volgt aan het eind, als duidelijk is wat de modules in de praktijk laten liggen.
