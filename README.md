# Synoptikon

Persoonlijke webapp voor **functionele rechtsvergelijking**: een rechtsvraag (het
*tertium comparationis*) met de stelsels NL, DE, FR en EU in kolommen naast
elkaar — originele wettekst, optionele vertaling en eigen analyse, duidelijk van
elkaar onderscheiden. Daarnaast een begrippenkaart met getypeerde relaties
(equivalent / deels overlappend / faux ami / geen equivalent), een
stelselweergave die laat zien *waar* een figuur in de systematiek zit,
full-text zoeken in alle talen, snel invoeren op de telefoon, en export naar
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
docker compose up -d --build
docker compose exec app synoptikon seed
```

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
| `systematiek` | Boom per stelsel (Boek › Titel › Afdeling; Buch › Abschnitt › Titel; Livre › Titre › Chapitre). |
| `concordantie` | Oude → nieuwe nummering met datum en grond (art. 1382 → 1240 C. civ.; art. 2014 → 3:86 BW). |
| `wettekst`, `wettekst_artikel` | Lokale kopie van geïmporteerde wetten met versie, datum, herkomst en ruw bestand. |

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
4. **Zoeken** (`/zoeken?q=`): vragen, bronnen, begrippen, analyses en
   geïmporteerde wetteksten; prefix-zoeken, accenten genegeerd; `3:84`,
   `§ 929` en ECLI's werken.
5. **Snel invoeren** (`/invoer`): drie tabbladen (bron, notitie, begrip),
   gekoppeld aan een vraag; één scherm op de telefoon.

Verder: `/bronnen` (lijst, detail met vertalingen), `/concordantie`,
`/wetteksten` (geïmporteerde versies), `/stelsels` (beheer).

## Importers

Alle importers slaan het ruwe bestand op onder `data/wetteksten/<stelsel>/<wet>/<versie>/`
en de artikelen in `wettekst_artikel`. Lezen gebeurt daarna uitsluitend uit
de database; de app doet nooit live-calls.

```bash
synoptikon import nl BWBR0005291        # BW Boek 3 (wetten.overheid.nl, BWB-XML)
synoptikon import nl BWBR0005289        # BW Boek 6
synoptikon import de bgb                # gesetze-im-internet.de, xml.zip
synoptikon import eu 32007R0864 --taal NL   # EUR-Lex HTML op CELEX
synoptikon import fr LEGITEXT000006070721 --artikelen 1112,1196,2276 --datum 2024-01-01
synoptikon import de bgb --bestand ~/Downloads/xml.zip   # uit een lokaal bestand
```

Légifrance gebruikt de PISTE-API (OAuth2 client credentials) met
`LEGIFRANCE_CLIENT_ID` en `LEGIFRANCE_CLIENT_SECRET` uit de omgeving;
`LEGIFRANCE_SANDBOX=1` kiest de sandbox. Zonder sleutel meldt de importer dat
hij overslaat en eindigt met exitcode 0. Omdat de Code civil ~2.800 artikelen
heeft en elk artikel één API-call is, geef je bij voorkeur `--artikelen`.

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
pytest                     # 17 tests: auth, synopse, zoeken, export, invoer, parsers
synoptikon rebuild-fts     # zoekindex opnieuw opbouwen na handmatige DB-ingrepen
synoptikon seed --overschrijf   # voorbeeldvragen opnieuw laden
```

Structuur: `synoptikon/models.py` (datamodel), `db.py` (SQLite + FTS),
`routes/` (één module per weergave), `services/` (zoeken, export, graaf),
`importers/` (BWB, GII, Légifrance, EUR-Lex), `seed/` (voorbeeldinhoud),
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

De wetteksten zijn de geldende officiële teksten; rechtspraak is beperkt tot
de kernoverweging (zo gemarkeerd in `opmerking`). Controleer citaten vóór
gebruik in een werkstuk — daarvoor staat bij elke bron de link.
