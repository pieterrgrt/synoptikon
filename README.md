# Synoptikon

Persoonlijke webapp voor **functionele rechtsvergelijking**: een rechtsvraag (het
*tertium comparationis*) met de stelsels NL, DE, FR en EU in kolommen naast
elkaar — originele wettekst, optionele vertaling en eigen analyse, duidelijk van
elkaar onderscheiden. Daarnaast een begrippenkaart met getypeerde relaties
(equivalent / deels overlappend / faux ami / geen equivalent), een
stelselweergave die laat zien *waar* een figuur in de systematiek zit, een
correspondentietabel op artikelniveau (bij art. 3:84 BW: § 929 BGB, art. 1196
C. civ., elk met hun plaats in hun eigen wetboek), full-text zoeken in alle talen, snel invoeren op de telefoon, en export naar
Markdown, PDF en JSON.

```
docker compose up -d --build          # app op 127.0.0.1:8765
docker compose exec app synoptikon seed    # twee uitgewerkte voorbeeldvragen
```

## Inhoud

- [Snel beginnen](#snel-beginnen)
- [Keuzes en motivering](#keuzes-en-motivering)
- [Datamodel](#datamodel)
- [Weergaven](#weergaven)
- [Importers](#importers)
- [Export](#export)
- [Back-up](#back-up)
- [Nginx](#nginx)
- [Ontwikkelen](#ontwikkelen)

## Snel beginnen

```bash
cp .env.example .env
openssl rand -hex 32                                  # → SYNOPTIKON_SECRET_KEY
docker compose run --rm app synoptikon hash-password  # → SYNOPTIKON_PASSWORD_HASH
# beide waarden in .env zetten, dan:
sudo chown -R 10001:10001 data      # de container draait als uid 10001
docker compose up -d --build
docker compose exec app synoptikon seed
docker compose exec app synoptikon profiel 1 --gebruikersnaam <naam> --naam <Naam>
```

Inloggen gaat met gebruikersnaam en wachtwoord. Profiel 1 (de beheerder)
logt in met `SYNOPTIKON_PASSWORD_HASH` zolang het geen eigen wachtwoord heeft.

De app luistert alleen op `127.0.0.1:8765`. Data (SQLite-database en opgeslagen
wetteksten) staat in `./data`, gemount als `/data` in de container.

Zonder Docker:

```bash
pip install -e ".[pdf,dev]"
export SYNOPTIKON_AUTH_MODE=none SYNOPTIKON_DATA_DIR=./data
synoptikon init && synoptikon seed
synoptikon serve --reload          # http://127.0.0.1:8000
```

## Keuzes en motivering

**SQLite met FTS5, geen Postgres.** Eén gebruiker, enkele duizenden rijen,
een server die al Nextcloud, Vaultwarden en meer draagt. SQLite kost geen
extra proces of geheugen, de back-up is één bestand, en FTS5 met de
`unicode61`-tokenizer (`remove_diacritics 2`) zoekt accent-ongevoelig over
Nederlands, Duits, Frans en Engels tegelijk — `delivrance` vindt *délivrance*,
`Ubergabe` vindt *Übergabe*. De FTS-tabellen zijn `content=`-tabellen met
triggers, dus de teksten staan niet dubbel opgeslagen. WAL-modus voor
gelijktijdig lezen/schrijven. Postgres zou alleen winnen bij meerdere
gebruikers of >100 MB tekst; dan is de overstap via SQLAlchemy klein.

**FastAPI + Jinja2, server-side gerenderd, vanilla JS.** Geen build-stap, geen
node_modules, geen framework-updates. De drie stukken JavaScript (thema,
kolommen slepen/verbergen, de graaf) zijn samen ~300 regels zonder
afhankelijkheden. De begrippenkaart is een eigen kleine krachtgestuurde layout
in SVG in plaats van d3 — genoeg voor tientallen tot honderden begrippen.

**Eén tabel `bron` voor wet, rechtspraak en literatuur.** De verschillen
(ECLI versus LEGIARTI versus ISBN) zitten in `vindplaats_type` + `vindplaats`.
Drie tabellen zouden elke weergave en de zoekfunctie verdrievoudigen.

**Bronnen hangen aan het Antwoord (Vraag × Stelsel), niet aan de Vraag.** Zo
vervult dezelfde bron (§ 242 BGB, art. 6:162 BW) bij elke vraag een andere
*rol* en krijgt hij een eigen annotatie per context. Dat is het functionele
uitgangspunt in het datamodel zelf.

**Authenticatie: scrypt-hash + ondertekende sessiecookie.** `hashlib.scrypt`
uit de standaardbibliotheek, `itsdangerous` voor de cookie, oplopende
wachttijd na vijf mislukte pogingen. `SYNOPTIKON_AUTH_MODE=none` schakelt het
uit als je de app achter nginx basic auth zet. Strikte CSP (`script-src
'self'`), geen inline scripts, geen externe assets.

**Lettertypen self-hosted.** Source Serif 4 (wetteksten) en Source Sans 3
(interface), beide SIL OFL, als variabele WOFF2 in `synoptikon/static/fonts`.
`scripts/fetch_fonts.sh` ververst ze.

**Pictogram.** De Σ uit Source Serif 4 (gewicht 600, opsz 8) als omtrek in
`static/favicon.svg`, dus onafhankelijk van geïnstalleerde lettertypen; in
dark mode (van browser of systeem) lichtrood op donker, zoals de app zelf.
`favicon.ico` (16/32/48) is daaruit gerenderd, in de lichte variant.
`apple-touch-icon.png` (180) en de manifest-iconen (192/512) zijn ook uit die
omtrek gerenderd, maar met een lichtere Σ (#c8645d) op crème: een beginschermicoon
heeft geen aparte dark-modevariant, en in dark mode viel het donkerrood daar weg. Pas je de SVG aan,
verhoog dan `?v=` in `templates/_iconen.html`. `/favicon.ico` en `/apple-touch-icon.png`
zijn ook zonder login bereikbaar, zodat een startpagina, dashboard of
telefoonbeginscherm het pictogram kan ophalen.

**PDF via WeasyPrint.** Dezelfde HTML als de printweergave; de Pango-
bibliotheken zitten in het Docker-image. Ontbreekt WeasyPrint, dan geeft de
PDF-route een 501 en blijft de rest werken (Markdown en de printweergave met
`Ctrl+P` zijn er altijd).

## Datamodel

| Tabel | Rol |
|---|---|
| `stelsel` | NL, DE, FR, EU actief; IT en EN (common law) aanwezig maar uit. Toevoegen via /stelsels. |
| `vraag` | Het tertium: titel, omschrijving (markdown), rechtsgebied, tags. |
| `antwoord` | Per Vraag × Stelsel: `kern` (één zin) en `analyse` (markdown). |
| `bron` | Wet / rechtspraak / literatuur / soft law: originele tekst, taal, vindplaats, URL, geldigheidsperiode, plaats in de systematiek, optioneel koppeling aan een geïmporteerd wetsartikel. |
| `vertaling` | Per bron per taal; herkomst `eigen` / `officieel` / `literatuur`. |
| `antwoord_bron` | Koppeling met volgorde, rol (hoofdregel, uitzondering, rechtspraak, …) en annotatie. |
| `begrip` | Per stelsel: term, taal, definitie, vindplaats. |
| `begrip_relatie` | `equivalent` · `deels` · `faux_ami` · `geen`, met toelichting. |
| `vraag_begrip` | Welke begrippen bij een vraag horen. |
| `notitie` | Losse notitie bij een vraag, al dan niet voor één stelsel (snel invoeren). |
| `systematiek` | Boom per stelsel: het volledige BW (alle boeken en niveaus, gegenereerd uit de officiële BWB-XML), BGB (Buch › Abschnitt › Titel › Untertitel) en de Code civil (Livre › Titre › Sous-titre › Chapitre › Section › Sous-section) met artikelbereiken. |
| `correspondentie`, `correspondentie_artikel` | Thema (functionele vraag) met per stelsel de artikelen die haar beantwoorden: (stelsel, wet, nummer[–tot]), rol en opmerking. Zonder nummer = geen wettelijke regeling. |
| `concordantie` | Oude → nieuwe nummering met datum en grond (art. 1382 → 1240 C. civ.; art. 2014 → 3:86 BW). |
| `wettekst`, `wettekst_artikel` | Lokale kopie van geïmporteerde wetten met versie, datum, herkomst, ruw bestand en citeerafkorting (`wet`: `OR`, `C. consom.`; leeg = hoofdcodificatie). |
| `eu_handeling`, `eu_repertorium` | Catalogus van het geldende afgeleide Unierecht (verordeningen, richtlijnen, kaderbesluiten; ook gedelegeerd en uitvoering) uit Cellar, met omzettingstermijn en rubrieken van het repertorium. |
| `eu_nim` | Nationale uitvoeringsmaatregelen zoals de lidstaten ze meldden (NL, BE, FR, IT, ES, DE en het VK vóór de Brexit). |
| `opzoeking`, `onderzoek`, `llm_gebruik` | Logboek van Opzoeken, onderzoek door Claude bij een vraag, en elke API-aanroep (voor het maandbudget). |
| `omzetting` | Eigen koppeling op artikelniveau: welk nationaal artikel (of welke wet) welk artikel van een handeling omzet, uitvoert, ernaar verwijst of haar autonoom navolgt; met vlag `geverifieerd`. |

Uitgebreider gemotiveerd in de docstring van `synoptikon/models.py`.

## Weergaven

1. **Synopse** (`/vragen/<slug>`): kolommen per stelsel. Aan/uit en slepen via
   de kolomkoppen; voorkeur per vraag in `localStorage`. Vertaling kiezen
   (`?vertaling=nl`). Per kolom: kern, bronnen (origineel · vertaling ·
   annotatie), analyse, notities. Onderaan begrippen, concordantie en notities.
2. **Begrippenkaart** (`/begrippen`, `?vraag=<slug>` filtert): graaf; faux amis
   rood en dik, "geen equivalent" gestippeld, stelsels als losse kolommen.
   Klik op een knoop voor definitie en relaties; knopen zijn versleepbaar.
3. **Stelselweergave** (`/stelsels/<code>?vraag=<slug>`): systematiekboom met
   de bronnen van een vraag gemarkeerd. Wissel tussen de tabs en je ziet
   § 812 BGB in het Schuldrecht staan waar NL alles in Boek 3 houdt.
4. **Opzoeken** (`/opzoeken?q=`, ook het veld in de kop; `/zoeken` stuurt hierheen): de
   enige zoekingang. Typ wat je hoort: een artikel (`§ 823 BGB`, `Art. 2 GG`,
   `6:162 BW`, `Art. 6 DSGVO`) geeft meteen de tekst met de plaats in de wet;
   een wet (`Grundgesetz`, `StGB`, `AVG`, `Rome I`) de wet zelf, in elk stelsel
   en onder elke naam; een uitspraak de eigen bronnen; daarna EU-handelingen,
   full-text in alle wetteksten (register eerst, te filteren per stelsel) en de
   eigen inhoud. Wat er niet precies bij zit, zoekt Claude op ("Claude laten
   opzoeken"): waar het staat, wat er staat (wettekst altijd uit de lokale
   import, rechtspraak van het web, gemarkeerd) en een korte toelichting. Wat
   je opzoekt komt in "Vandaag opgezocht" (tabel `opzoeking`), het logboek van
   een college; elk item gaat met één tik als kaart naar een leerlijst.
5. **Artikelen** (`/artikelen`, `/artikelen/NL/3:84`): typ een artikelnummer
   (`3:84`, `§ 929`, `art. 1196 C. civ.`, `1112-1`) en zie de plaats in de
   systematiek, de tekst (uit een bron of een geïmporteerde wet) en per thema
   de corresponderende artikelen in de andere stelsels, elk met hun eigen pad.
   `/artikelen` is de volledige correspondentietabel per rechtsgebied;
   `/artikelen/thema/<id>` de synopse van één thema op artikelniveau. Ook
   `/zoeken?q=3:84` en de ⇄-links bij bronnen in de synopse leiden hierheen.
   In de stelselweergave toont ⇄ per knoop hoeveel thema's erin vallen;
   `/stelsels/NL/knoop/<id>` laat zien waar de tegenhangers in de andere
   wetboeken staan (BW 3.4.2 valt in DE uiteen over Sachen- én Schuldrecht).
6. **Unierecht** (`/eu`): de 17.600 geldende verordeningen en richtlijnen,
   doorzoekbaar op roepnaam (AVG, DSA), nummer (2019/771), CELEX of tekst,
   gefilterd op soort en variant en te doorbladeren via het repertorium.
   `/eu/<celex>` toont de werking in de nationale rechtsorde (art. 288–291
   VWEU met de leidende arresten: Variola, Von Colson, Marleasing, Faccini
   Dori, Francovich …), omzettingstermijn en harmonisatieniveau, en per
   stelsel de status (EN: Brexit en assimilated law; CH: autonome
   navolging), de artikelen waarin de handeling is omgezet (met hun plaats
   in de systematiek) en de gemelde maatregelen. `/eu/omzetting` is de matrix
   handeling × stelsel. Omgekeerd toont elke artikelpagina onder "Europese
   herkomst" welke richtlijn het artikel omzet.
7. **Snel invoeren** (`/invoer`): drie tabbladen (bron, notitie, begrip),
   gekoppeld aan een vraag; één scherm op de telefoon.
8. **Wetten** (`/stelsels` → een wet → `/stelsels/<code>/wet/<id>`): per stelsel de
   wetten uit het register en de belangrijkste andere (`wetboek.BELANGRIJK`: GG,
   StGB, ZPO, VwVfG … en VEU, VWEU, Handvest, AVG, Rome I …), plus alle andere
   via "Alle n wetten". Elke wet, ook het BGB en elke EU-handeling, leest zoals
   op Légifrance: inhoudsopgave uit de opschriften van de wettekst zelf (waar de
   bron die niet meegeeft, zoals de Codice civile, uit de systematiek), dan per
   afdeling de volledige tekst, met vorige/volgende afdeling. Het veld bovenaan
   neemt een artikelnummer of woorden (zoekt in deze wet). Bij elk artikel
   ☆ Bewaren.
9. **Bewaren voor Wunderkammer**: ☆ bij elk artikel (leesweergave, systematiek,
   artikelpagina, opzoeken) en elke uitspraak maakt met één tik een kaart in de
   laatst gekozen leerlijst (`POST /leren/snel`; de keuze staat in een cookie);
   ⋯ ernaast kiest kaartsoort en lijst. Lijsten met "naar Wunderkammer" komen
   via `/api/wk/kaarten` in Wunderkammer.
   **Kaarten uit notities**: `scripts/notities.sh` kopieert `~/vault/Humboldt`
   naar `data/notities` (de container kan niet bij de rclone-mount) en draait
   `synoptikon notities`. Elke nieuwe of gewijzigde notitie in een map met een
   vak (`SYNOPTIKON_NOTITIES_VAKKEN`, of `vak:` in de frontmatter;
   `synoptikon: nee` slaat een notitie over) gaat naar Claude, dat elke norm met
   `artikel_lezen` controleert en kaarten voorstelt (artikel, kern, arrest,
   vrij). Ze komen als voorstel in de lijst "Notities · <vak>"; op de
   lijstpagina neem je ze over of wijs je ze af. Alleen overgenomen kaarten gaan
   naar Wunderkammer; afgewezen kaarten worden niet opnieuw voorgesteld. Cron:
   `30 2 * * * ~/synoptikon/scripts/notities.sh >> ~/synoptikon/data/notities.log 2>&1`
   (hoogstens 10 notities per nacht; `--droog` toont wat aan de beurt is).
10. **Onderzoek door Claude** (bij een vraag, of meteen bij "Nieuwe vraag"): kies de
   stelsels; Claude leest de wetteksten via de lokale import (tools
   `artikel_lezen`, `wetteksten_doorzoeken`, `wet_zoeken`,
   `eigen_bronnen_doorzoeken`), zoekt rechtspraak op het web en levert per stelsel
   kern, analyse en bronnen, plus een functionele vergelijking. Lege kernen en
   analyses worden ingevuld en gemarkeerd ("niet geverifieerd"), wetsartikelen
   worden bronnen met de lokale tekst; wat je zelf schreef blijft staan. Draait op
   de achtergrond; de pagina toont de voortgang (tabel `onderzoek`).

### Claude

`SYNOPTIKON_ANTHROPIC_API_KEY` aan = opzoeken en onderzoek aan
(`services/claude.py`). Model `SYNOPTIKON_CLAUDE_MODEL` (standaard
`claude-opus-5-5`), harde grens `SYNOPTIKON_LLM_BUDGET_USD` per kalendermaand
(standaard 20; elke aanroep staat in `llm_gebruik`). Opzoeken draait op effort
`low` met hoogstens 3 webzoekacties (enkele centen), onderzoek op `high` met
hoogstens 12 (meestal enkele dollars). Weigeringen gaan via server-side
`fallbacks: "default"`.

## Profielen en talen

**Profielen.** Vijf vaste plekken (`/beheer/profielen`, alleen de
beheerder). Rollen: beheerder (alles), redacteur (lezen en invoeren), lezer
(alleen lezen; de server weigert elke POST behalve profiel, taal en
uitloggen). Een profiel gaat pas aan met een wachtwoord; een nieuw wachtwoord
of uitzetten hoogt de sessieversie op, waardoor dat profiel overal wordt
uitgelogd. Iedereen beheert zijn eigen naam, taal en wachtwoord op `/profiel`.
Vanaf de server: `synoptikon profiel` (overzicht) en `synoptikon profiel 2
--gebruikersnaam … --rol redacteur --wachtwoord --aan`.

**Talen.** NL, FR, DE, IT, EN en ES. De taal komt uit het profiel, anders
uit een cookie, anders uit de browser (`Accept-Language`); wisselen kan
via het menu ⋯ en op de inlogpagina. Twee lagen (`synoptikon/i18n.py`):

* *Interface*: `_('…')` in templates en code, catalogi in
  `synoptikon/i18n/<taal>.json` met de Nederlandse tekst als sleutel.
  `python -m synoptikon.i18n_teksten fr` toont wat ontbreekt;
  `tests/test_i18n.py` eist dat alles vertaald is.
* *Eigen inhoud* (vragen, analyses, definities, relaties, thema's,
  opmerkingen): ingevoerd in het Nederlands, vertaald via `vt()` uit het
  vertaalgeheugen (tabel `inhoud_vertaling`, sleutel = hash van de
  Nederlandse tekst). Verandert de bron, dan valt de weergave terug op het
  Nederlands. De standaardvertalingen (machine, niet geverifieerd) staan in
  `synoptikon/seed/vertalingen/`; nakijken en aanvullen op `/vertalingen`,
  of `synoptikon vertalingen export --taal fr` → vertalen → `synoptikon
  vertalingen import --taal fr --bestand …`. Een balk bovenaan meldt dat de
  inhoud vertaald is en schakelt naar het origineel.
* *Bron in de oorspronkelijke taal*: wetteksten, termen en citeertitels
  worden nooit vertaald; ze dragen een `lang`-attribuut voor
  schermlezers. EU-titels en repertoriumrubrieken komen in de officiële
  versie uit Cellar (`synoptikon eu-talen`).

Verder: `/bronnen` (lijst, detail met vertalingen), `/concordantie`,
`/wetteksten` (geïmporteerde versies), `/stelsels` (beheer).

## Importers

Alle importers slaan het ruwe bestand op onder `data/wetteksten/<stelsel>/<wet>/<versie>/`
en de artikelen in `wettekst_artikel`. Lezen gebeurt daarna uitsluitend uit
de database; de app doet nooit live-calls.

Het register (`synoptikon/importers/register.py`) bevat per stelsel de
burgerlijke wetboeken en de wetten waarin het Unierecht is omgezet; één
opdracht haalt ze allemaal:

```bash
scripts/legi_ophalen.sh data/legi            # FR: LEGI-dump van de DILA (1,1 GB gestreamd, alleen de codes uitgepakt)
synoptikon import-alles --legi data/legi --systematiek
synoptikon eu-catalogus                      # Cellar: handelingen, repertorium, nationale maatregelen (~1 min)
synoptikon seed                              # laadt o.a. de omzettingstabel
```

| Stelsel | Bron | Wetten | Geconsolideerd |
|---|---|---|---|
| NL | wetten.overheid.nl (BWB-XML) | BW Boek 1–8, 10 | ja |
| DE | gesetze-im-internet.de | BGB, EGBGB, HGB, ProdHaftG, UWG | ja |
| FR | LEGI (DILA, licence ouverte) | Code civil, Code de la consommation, Code de commerce | ja, op vandaag |
| IT | Normattiva (Akoma Ntoso) | Codice civile, Codice del consumo | ja |
| ES | BOE, API datos abiertos | Código Civil, TRLGDCU, Código de Comercio | ja |
| CH | Fedlex (Akoma Ntoso) | ZGB, OR, IPRG, PrHG | ja, laatste geldende stand |
| BE | Staatsblad via etaamb.openjustice.be | nieuw BW Boek 1, 2 (titel 3), 3, 4, 5, 8 | **nee**: tekst zoals bekendgemaakt |
| EN | legislation.gov.uk (CLML) | SGA 1979, SGSA 1982, CRA 2015, UCTA 1977, MA 1967, C(RTP)A 1999, LR(FC)A 1943, LA 1980, CPA 1987, OLA 1957, LPA 1925 | ja |
| GR | lawspot.gr | ΑΚ, Σύνταγμα, ΠΚ, ΕμπΝ, ν. 2251/1994, 2190/1920, 3190/1955, 4548/2018, 4072/2012, 3869/2010, 4624/2019 | ja |
| AT | RIS (BKA), geltende Fassung per wet | ABGB, B-VG, UGB, KSchG, ZPO, IPRG, StGB | ja |
| DK | Retsinformation, LexDania-XML via ELI | grl., aftl., kbl., forbrugeraftalel., EAL, forældelsesl., selskabsl., rpl., strfl. | ja, per lovbekendtgørelse |
| FI | Finlex open data (Akoma Ntoso) | PL, OikTL, KL, KSL, VahL, VanhL, OYL, OK, RL | ja |

**Alle wetten van een bron** (`synoptikon/importers/bulk.py`), naast het register:

```bash
synoptikon import-bulk de          # alle ±6.100 wetten en verordeningen van gesetze-im-internet.de (±30 min)
synoptikon import-bulk eu          # alle ±17.600 geldende EU-handelingen, Duits, geconsolideerd waar mogelijk (±3 uur)
synoptikon import-bulk eu --verdragen   # alleen VEU, VWEU en Handvest, in alle zes talen
```

Een tweede run haalt alleen op wat ontbreekt (EU: ook een nieuwere consolidatie). Bulkwetten staan niet in het
overzicht van Stelsels en niet in de systematiek, maar zijn te vinden via **Alle wetten doorzoeken**
(`/stelsels/DE/wetten`, `/stelsels/EU/wetten`), via de artikelzoeker ("§ 1 PatG", "Art. 6 DSGVO") en de zoekfunctie.

**EU-teksten** komen uit de Cellar van het Publicatiebureau (content negotiation op CELEX); EUR-Lex zelf weigert
geautomatiseerde toegang. Elke EU-wet heeft één interne sleutel ("VWEU", "Rome I", "Verordening 2016/679",
`services/eunamen.py`); getoond wordt de naam in de taal van de interface (AEUV, TFUE, TFEU; DSGVO, RGPD, GDPR) en
bij invoer wordt elke schrijfwijze herkend. De verdragen staan er in zes talen; de rest in het Duits.

Justel (BE) en Légifrance (FR) weigeren geautomatiseerde toegang; de
Belgische tekst komt daarom uit de spiegel van het Staatsblad, en BE Boek 6,
het WER en het oud BW ontbreken. Voor US (UCC, Restatements) en AU (ACL) is
er geen open bron zonder scraping; daar blijft het bij de systematiek. Griekenland heeft geen open officiële
geconsolideerde bron (het Staatsblad geeft alleen de oorspronkelijke ΦΕΚ als pdf); lawspot.gr houdt de teksten bij.
ΚΠολΔ en ΚΠΔ staan daar achter een login en ontbreken.

Losse wetten:

```bash
synoptikon import nl BWBR0005291                       # BW Boek 3
synoptikon import ch cc/27/317_321_377 --wet OR        # Fedlex-ELI
synoptikon import it "urn:nir:stato:decreto.legislativo:2005-09-06;206" --wet "c. cons."
synoptikon import es BOE-A-2007-20555 --wet TRLGDCU
synoptikon import en ukpga/1979/54 --wet "SGA 1979"
synoptikon import fr LEGITEXT000006069565 --wet "C. consom." --bestand data/legi
synoptikon import eu 32007R0864 --taal de              # Cellar, op CELEX
synoptikon import gr astikos-kodikas                   # lawspot.gr
```

De **omzettingstabel** (`synoptikon/seed/omzetting.py`) is eigen
aantekening en laadt met `geverifieerd=False`; de app markeert die regels.
Alle artikelen die erin staan zijn getoetst op bestaan in de geïmporteerde
officiële teksten, niet op inhoud. Wat je zelf controleert of toevoegt
(op `/eu/<celex>`), geldt als geverifieerd.

**Systematiek uit een import.** De BW-boom is volledig (gegenereerd uit de
officiële XML, versies 2024–2026); de BGB-boom gaat tot Untertitel, de Code
civil tot titre (verbintenissenrecht tot sous-section). Een import bevat per artikel het volledige pad; daarmee vul je
de boom aan tot op het laagste niveau, met exacte bereiken:

```bash
synoptikon import nl BWBR0005289 --systematiek   # BW Boek 6, meteen de boom aanvullen
synoptikon systematiek de bgb                     # achteraf, uit de laatst geïmporteerde versie
```

Bestaande knopen worden herkend aan hun eerste twee woorden ("Titel 4",
"Buch 3", "Livre III") en houden hun code, bronnen en correspondenties.

Op de bronpagina kun je de tekst van een geïmporteerd artikel in een bron
overnemen; de bron onthoudt dan uit welke versie de tekst komt. Rechtspraak en
literatuur voer je handmatig in.

## Export

- **Markdown**: `/vragen/<slug>/export.md` — kop, kern per stelsel, bronnen met
  tekst, vertaling en annotatie, analyse, begrippen, notities.
- **PDF**: `/vragen/<slug>/export.pdf` (A4, serif voor wetteksten,
  paginanummers); `/vragen/<slug>/print` is dezelfde opmaak in de browser.
- **Begrippenparen (JSON)**: `/begrippen/export.json`, formaat
  `synoptikon-begrippenparen` versie 1, gedocumenteerd in
  `synoptikon/services/export.py`. Per relatie één paar met `front`, `back`,
  `relation`, `note`, `questions` en `tags`; stabiele `id`. Bedoeld om later in
  Wunderkammer te importeren; er is geen directe koppeling.

## Back-up

```bash
scripts/backup.sh /pad/naar/sync-map     # standaard ./backups
```

Kopieert de database consistent (`sqlite3 .backup`, WAL-veilig) als
`synoptikon-<tijd>.db.gz` en de wetteksten als `wetteksten-<tijd>.tar.gz`,
en bewaart de laatste 14 (`BACKUP_KEEP`). Als cron op de host, bijv.
`17 3 * * * /home/claude/synoptikon/scripts/backup.sh /home/claude/sync/synoptikon`.
Terugzetten: `gunzip` en het bestand als `data/synoptikon.db` terugplaatsen.

## Nginx

`deploy/nginx.synoptikon.conf.example` is een server-block voor
`synoptikon.regoort.me` dat naar `127.0.0.1:8765` proxyt. Het wordt niet
automatisch geïnstalleerd; neem het over in je eigen config en voeg de
hostnaam toe aan je SNI-stream-router. Wil je basic auth op nginx-niveau, zet
dan `SYNOPTIKON_AUTH_MODE=none`.

## Ontwikkelen

```bash
pip install -e ".[pdf,dev]"
pytest                     # 87 tests: auth, synopse, opzoeken, Claude (nep-client), export, invoer, parsers, artikelen, Unierecht
synoptikon rebuild-fts     # zoekindex opnieuw opbouwen na handmatige DB-ingrepen
synoptikon seed --overschrijf   # voorbeeldvragen opnieuw laden
synoptikon seed                 # ook om een bestaande database bij te werken: vult systematiek
                                # en correspondentietabel aan, laat eigen thema's en knopen staan
```

Structuur: `synoptikon/models.py` (datamodel), `db.py` (SQLite + FTS),
`routes/` (één module per weergave), `services/` (zoeken, export, graaf),
`importers/` (BWB, GII, Légifrance, EUR-Lex), `seed/` (voorbeeldinhoud,
systematiekbomen, correspondentietabel), `services/artikelen.py` (nummers
herkennen, sorteren en in de boom plaatsen),
`templates/`, `static/` (CSS, JS, fonts).

### Voorbeeldinhoud

Twee volledig uitgewerkte vragen, elk met kern en analyse per stelsel,
wetteksten met vindplaats en link, kernoverwegingen van de arresten,
eigen vertalingen (gemarkeerd), begrippen met relaties en concordanties:

- **Eigendomsoverdracht roerende zaken** — art. 3:84, 3:86, 3:90, 3:114, 3:115
  BW; §§ 929–932, 433, 812 BGB; art. 1196, 1198, 1583, 1604, 2276 C. civ.;
  art. 345 VWEU, art. 20 Richtlijn 2011/83, DCFR VIII.–2:101, art. 4 CISG.
  Begrippen: levering / Übergabe / délivrance, titel / Kausalgeschäft / titre,
  Einigung, Abstraktionsprinzip / causaal stelsel, bezit / Besitz / possession.
- **Precontractuele aansprakelijkheid** — Baris/Riezenkamp, Plas/Valburg,
  CBB/JPO, art. 6:2 en 6:162 BW; §§ 311 II, 241 II, 280, 242 BGB,
  Linoleumrollen, BGH V ZR 332/94; art. 1112 (beide versies), 1112-1, 1104,
  1240 C. civ., Manoukian; art. 12 Rome II, Tacconi, PECL 2:301.
  Begrippen: c.i.c. in vier stelsels, redelijkheid en billijkheid / Treu und
  Glauben / bonne foi, positief vs. negatief belang, perte de chance.

Daarnaast een **correspondentietabel** van 135 thema's met ruim 500
artikelverwijzingen in NL, DE en FR (rechtshandelingen, vertegenwoordiging,
verjaring, goederen- en zekerhedenrecht, verbintenissen, overeenkomsten,
bijzondere overeenkomsten, onrechtmatige daad, personen-, familie- en
erfrecht), in `synoptikon/seed/correspondenties.py`. Waar een stelsel een
vraag niet in de wet regelt staat dat erbij, met de vindplaats in de
rechtspraak; faux amis en gedeeltelijke overlap zijn als rol gemarkeerd.

De wetteksten zijn de geldende officiële teksten; rechtspraak is beperkt tot
de kernoverweging (zo gemarkeerd in `opmerking`). Controleer citaten vóór
gebruik in een werkstuk — daarvoor staat bij elke bron de link.
