# Backlog Synoptikon / Wunderkammer

Opgeschreven op 29-10-2026, uit Pieters eigen opsomming. Geldt voor beide repo's
(`~/wunderkammer` en `~/synoptikon`); veel punten raken ze allebei.

Per punt: **wat** (Pieters woorden, samengevat), **waar** (wat er nu staat, nagekeken in de code),
**aanpak** (mijn voorstel, nog niet besloten) en **omvang** (klein = halve dag, midden = een dag of twee,
groot = meer, of eerst uitzoeken).

## Voorgestelde volgorde

Wat elke dag in de weg zit eerst, dan wat de Klausur ZR Ia (19-02-2027) dient, dan de verkenningen.

1. [Kalk: wachtrij](#1-kalk-wachtrij-bij-het-opzoeken) — klein, dagelijkse ergernis
2. [ECLI en vindplaats echt ophalen](#2-ecli-en-vindplaats-echt-ophalen-en-zelf-kunnen-verbeteren) — midden, dit is de schermafbeelding
3. [Bewaren met vak in één tik](#3-bewaren-met-vak-in-één-tik) — klein
4. [Betere kaarten uit Synoptikon](#4-betere-kaarten-uit-synoptikon) — midden
5. [Markeren in een artikel of uitspraak](#5-markeren-in-een-artikel-of-uitspraak) — midden, voedt 4
6. [Overzicht van wat je bewaarde, met samenhang](#6-overzicht-van-wat-je-bewaarde-met-samenhang) — midden
7. [Onderwerpen: artikelen die je samen leest](#7-onderwerpen-artikelen-die-je-samen-leest) — midden
8. [Tekst erin, kaarten eruit](#8-tekst-erin-kaarten-eruit) — groot
9. [Kalk: zinnen en wat je niet begreep](#9-kalk-zinnen-en-wat-je-niet-begreep) — midden
10. [Wereldkaart voor stelsels en vergelijking](#10-wereldkaart-voor-stelsels-en-vergelijking) — midden
11. [De andere vaardigheden in Wunderkammer](#11-de-andere-vaardigheden-in-wunderkammer) — nog te snijden
12. [Wetten en rechtspraak los bewaren](#12-wetten-en-rechtspraak-los-bewaren) — open vraag
13. [Eén app voor de rechtenstudie, en Obsidian-doeken](#13-één-app-voor-de-rechtenstudie-en-obsidian-doeken) — verkennen
14. [Andere AI's uitzoeken](#14-andere-ais-uitzoeken) — verkennen

---

## 1. Kalk: wachtrij bij het opzoeken

**Wat.** Doorgaan met toevoegen terwijl een vorig woord nog laadt; opzoeken duurt soms lang.

**Waar.** `frontend/src/routes/calque/kalk/+page.svelte`: `zoek()` en `bewaar()` beginnen met
`if (!t || bezig) return;`, en `bezig` is één toestand voor de hele pagina. Elke knop staat
`disabled={!!bezig}`. Eén opzoeking tegelijk, invoer op slot.

**Aanpak.** `bezig` van één vlag naar een lijst opzoekingen: elk ingetypt woord wordt meteen een regel in
een rijtje (status *zoekt* → *klaar* → bewaard of weg), het veld leegt direct en houdt de focus. De
server kant kan blijven zoals hij is; het is vooral frontend. Resultaten komen binnen in de volgorde
waarin ze klaar zijn, niet in de volgorde van invoer, dus elke regel toont zijn eigen woord. Bij 'kaal'
(`/calque/kalk` op een computer) mag het rijtje de typografie niet verdringen: één regel per wachtend
woord, zoals de wachtenden nu al staan.

**Omvang.** Klein.

## 2. ECLI en vindplaats echt ophalen (en zelf kunnen verbeteren)

**Wat.** Bij `ECLI:EU:C:2015:806` zei Claude 'Niet vastgesteld', terwijl de EUR-Lex-link wél naar het
goede arrest leidde. Die informatie moet gewoon opgehaald worden. En als het misgaat: zelf kunnen
verbeteren.

**Waar.** `synoptikon/services/opzoeken.py`. Er is geen enkele deterministische ECLI-route: `uitspraken()`
zoekt alleen in de eigen `Bron`-tabel, daarna gaat alles naar `met_claude()` → `claude.loop(...,
max_zoekacties=3)`. Vandaar 'het maximum aantal webzoekopdrachten was bereikt'. Er zijn wél importers
die hier precies voor gemaakt zijn: `importers/cellar.py` en `importers/eurlex.py`. Een opzoeking is
achteraf niet te bewerken: `Opzoeking.resultaat` wordt alleen door `_vul()` geschreven.

**Aanpak.** Twee dingen, los van elkaar bruikbaar.

- *Herkenner vóór Claude.* Een ECLI is een vast formaat (`ECLI:<land>:<gerecht>:<jaar>:<nummer>`). Die
  parsen en per land ophalen: `EU` via CELLAR/EUR-Lex (`uri=ecli:…` bestaat al in `services/eu_logica.py`),
  `NL` via de open data van rechtspraak.nl, `DE`/`FR` via hun eigen vindplaats. Daaruit komen zaaknaam,
  zaaknummer, datum, gerecht en de link — feiten, niet geraden. Pas als dat niets geeft, Claude. Hetzelfde
  geldt voor CELEX-nummers.
- *Zelf verbeteren.* Een opzoeking met een laag zekerheidsniveau krijgt een knop 'kloppend maken': citeer,
  zaaknaam, vindplaats en URL in een formulier; opgeslagen wordt het een gewone `Bron` met `bron: "eigen"`
  in plaats van `"claude"`, zodat de waarschuwing 'niet geverifieerd' verdwijnt. Dat is ook de plek om een
  EUR-Lex-link te plakken en de tekst te laten ophalen.

**Omvang.** Midden (de herkenner per land is stapsgewijs: EU eerst, dat is jouw geval).

## 3. Bewaren met vak in één tik

**Wat.** Nu moet je te veel zelf kiezen bij het opslaan; dat wil je niet elke keer.

**Waar.** `synoptikon/templates/_opzoeking.html`: het bewaarformulier is een `<select>` met álle
leerlijsten plus een knop. `Leerlijst` heeft al een veld `vak` ("ZR Ia", "Sachenrecht"; leeg = Jura,
`models.py:725`) en `examen`. Dus het begrip 'vak' bestaat, maar je kiest nog steeds een lijst.

**Aanpak.** Eén knop die bewaart in het vak waar je mee bezig bent, met de keuze eronder in plaats van
ervoor. Wat 'waar je mee bezig bent' betekent: het laatst gekozen vak op het profiel onthouden, en zo
mogelijk afleiden uit wat je opzoekt (een BGB-artikel hoort bij ZR Ia, een arrest van het HvJ niet).
Vak wisselen blijft één tik, maar is dan een correctie en geen voorwaarde. De vakken komen uit
Wunderkammer (`app/jura/faecher.py`), zodat je ze op één plek onderhoudt.

**Open vraag.** 'Vak of project' — zijn 'project' en 'vak' hetzelfde ding (een leerlijst met een vak),
of wil je daarnaast iets niet-vakgebondens (bv. een Aldus-stuk)?

**Omvang.** Klein, zodra de vraag hierboven beantwoord is.

## 4. Betere kaarten uit Synoptikon

**Wat.** De kaarten die in Wunderkammer aankomen moeten echt goede flashcards zijn.

**Waar.** `synoptikon/services/leren.py`, klasse `Bouwer.zijden()`. Zes soorten (`artikel`, `kern`,
`plaats`, `tegenhanger`, `arrest`, `feiten`). Bij `artikel` is de achterkant de hele wettekst; bij
`arrest` is de achterkant `antwoord` + de hele kerntekst + feiten. Dat is leesbaar, maar het zijn geen
kaarten die je kunt beantwoorden: één kaart vraagt te veel tegelijk.

**Aanpak.** Een kaart = één feit.

- Een lang artikel niet als één brok, maar per lid (of per voorwaarde) een kaart; Synoptikon kent de
  structuur al via `WettekstArtikel`.
- Bij arresten de *rechtsregel* op de achterkant en de kerntekst als samenhang eronder, niet andersom.
  Dat hangt aan punt 5 (zelf aanduiden waar de regel staat) en aan het vak-filter uit punt 2: dezelfde
  uitspraak levert in ZR Ia een andere regel op dan in GÖ.
- Clozes voor opsommingen van voorwaarden ('Tatbestandsmerkmale'), zodat typen mogelijk wordt.
  Wunderkammer kan dat al (`app/typing.py`), de kaart moet alleen zo gebouwd worden.
- Laten zien wat eruit komt vóór je bewaart: de voorkant en achterkant tonen in het bewaarvenster.

**Omvang.** Midden. Begin bij arrestkaarten — dat is de soort die nu het minst werkt.

## 5. Markeren in een artikel of uitspraak

**Wat.** Meteen kunnen duiden welke onderdelen van een artikel nuttig zijn. En bij een oordeel zelf het
deel aanwijzen waar de voor dat vak relevante rechtsregel staat.

**Waar.** Bestaat nog niet. `Bron.tekst` en `WettekstArtikel.tekst` zijn platte tekst; `templates/
artikel.html` en `bron_detail.html` tonen die via `md.render`. Er is geen model voor een markering.

**Aanpak.** Nieuw model `Markering` (bron of artikel, tekenbereik, vak, soort: *kern* / *voorwaarde* /
*let op*, eigen notitie). Selecteren met de muis of je vinger, dan een klein menu. Twee opbrengsten:
de markering is te zien bij het teruglezen, én een gemarkeerd stuk is het materiaal voor een kaart
(punt 4). Het bereik opslaan als tekstaanhaling (quote + context) in plaats van als index, dan overleeft
een markering een nieuwe versie van de wettekst.

**Omvang.** Midden.

## 6. Overzicht van wat je bewaarde, met samenhang

**Wat.** Er is geen plek waar je je opgeslagen oordelen en artikelen samen ziet, en de samenhang ertussen.

**Waar.** Wat er is: `/bronnen` (lijst), `/artikelen` (lijst), `/leren` (leerlijsten), `/begrippen`
(begrippenkaart met getypeerde relaties) en `services/graaf.py`. De samenhang zit dus al in de data
(correspondentietabel, begrippen, thema's), maar er is geen pagina die 'mijn materiaal' als één geheel
toont.

**Aanpak.** Eén pagina per vak: de bewaarde artikelen, de bewaarde uitspraken en de verbanden die
Synoptikon al kent (welk arrest gaat over welk artikel, welke artikelen horen bij hetzelfde thema).
Eerst als lijst met groepen — die is bruikbaar op de telefoon — en daarnaast de graafweergave die er al
is. Dit is de pagina waar punt 7 (onderwerpen) en punt 12 (los bewaren) landen.

**Omvang.** Midden.

## 7. Onderwerpen: artikelen die je samen leest

**Wat.** Artikelen kunnen selecteren die samen gelezen moeten worden in een bepaald onderwerp.

**Waar.** `Thema` bestaat al in de correspondentietabel (`services/correspondentie.py`), maar als
vergelijkingsas tussen stelsels, niet als leesset binnen één stelsel.

**Aanpak.** Kijken of dit hetzelfde ding is als `Thema` met een andere weergave, of een eigen model
verdient ('leesset': geordende rij artikelen, uitspraken en eigen notities, met een reden per onderdeel).
Mijn voorkeur: eigen model, want de volgorde en het 'waarom staat dit erbij' zijn hier de kern, en die
horen niet in de vergelijkingstabel. Een leesset kan daarna in één tik een leerlijst worden.

**Omvang.** Midden.

## 8. Tekst erin, kaarten eruit

**Wat.** Een stuk tekst in Synoptikon zetten en Claude de toepasselijke artikelen laten opzoeken,
verbinden, en er goede flashcards van maken.

**Waar.** De bouwstenen staan er: `services/onderzoek.py` (Claude met zoekacties en een schema),
`services/claude.py` (gereedschappen `artikel_lezen`, `wet_zoeken`, `wetteksten_doorzoeken`,
`eigen_bronnen_doorzoeken`), `services/notities.py` (een notitie wordt kaartvoorstellen),
`templates/voorstellen.html`. Wat ontbreekt is de weg van een vrije lap tekst (college-aantekening,
Folie, arrestsamenvatting) naar voorstellen die je één voor één goed- of afkeurt.

**Aanpak.** Tekst plakken → Claude haalt er de verwijzingen uit (met de bestaande herkenner, niet op
gevoel), zoekt de artikelen lokaal op, en stelt per begrip een kaart voor. Alles als *voorstel*, nooit
direct bewaard — zelfde regel als in Wunderkammer. Hangt aan punt 4: pas als de kaartvorm goed is, is
het de moeite om ze automatisch te laten maken.

**Omvang.** Groot. Doen na 4 en 5.

## 9. Kalk: zinnen en wat je niet begreep

**Wat.** In Kalk ook zinnen kunnen toevoegen, en aanduiden welk woord of welke woorden je niet begreep —
en of dat aan de grammatica lag of aan de woordenschat.

**Waar.** `backend/app/calque/kalk.py` en `enrich.py`. Nu is de invoer één woord of woordgroep; er is al
een veld `context` (de zin eromheen) op de opzoekroute, maar de zin is bijwerk, niet het onderwerp.

**Aanpak.** De zin wordt het item; de woorden die je aantikt worden de kaarten. Bij 'grammatica' iets
anders dan een woordkaart: de constructie als onderwerp (bv. een Konjunktiv II, een naamvalsrectie), met
de zin als voorbeeld. Dat is een nieuwe soort in Calque, geen woord — hier moet ik eerst uitzoeken wat
die kaart precies vraagt voordat ik bouw.

**Omvang.** Midden tot groot; de zin-met-aangetikte-woorden is midden, de grammaticakaart moet eerst
ontworpen.

## 10. Wereldkaart voor stelsels en vergelijking

**Wat.** Een wereldkaart voor de stelselselectie, en ook voor comparatistische overzichten.

**Waar.** `synoptikon/templates/_stelselkiezer.html`: nu per regio inklapbaar met vinkjes, uit
`seed/regios.py`; elk `Stelsel` heeft een `familie`. Synoptikon heeft geen kaartbibliotheek; Wunderkammer
wel (MapLibre + OpenFreeMap, zie CLAUDE.md).

**Aanpak.** Voor de kiezer is MapLibre te zwaar: één SVG-wereldkaart met landen op stelselcode, gekleurd
naar rechtsfamilie, aantikken = aan- of uitzetten. Werkt offline en op de telefoon. Dezelfde kaart is
daarna de weergave voor een vergelijking: kleur de landen naar het antwoord op de rechtsvraag.

**Omvang.** Midden (de landgrenzen als vereenvoudigde SVG zijn het meeste werk; kan uit Natural Earth,
publiek domein).

## 11. De andere vaardigheden in Wunderkammer

**Wat.** De andere vaardigheden moeten verder worden ontwikkeld.

**Waar.** `backend/app/calque/skills.py`: acht vaardigheden (woorden, lijsten, lezen, luisteren, spreken,
schrijven, schrift, calques ontdekken), elk met een dagdoel en één tik vanaf het kabinet. 'Woorden',
'lijsten' en 'schrift' hebben echte inhoud; lezen, luisteren, spreken en schrijven leunen op
`spreek.py` en op wat er toevallig aan materiaal is.

**Open vraag.** Dit punt is nog te breed om in te plannen. Welke vaardigheid zit je het meest dwars —
luisteren, schrijven, of lezen? Dan snijd ik daar een echte taak uit.

## 12. Wetten en rechtspraak los bewaren

**Wat.** "Wetten en rechtspraak moeten los ook opgeslagen kunnen worden."

**Open vraag.** Twee lezingen, en ze leiden tot ander werk: (a) een wet of uitspraak bewaren zonder dat
er meteen een kaart of leerlijst aan hangt — gewoon 'dit wil ik bewaren', met vak; of (b) wetten en
rechtspraak als twee aparte bewaarplekken, elk met hun eigen overzicht, in plaats van samen onder
`Bron`. In beide gevallen raakt dit punt 6.

## 13. Eén app voor de rechtenstudie, en Obsidian-doeken

**Wat.** Een app bouwen die Wunderkammer en Synoptikon samenbrengt voor de rechtenstudie; Obsidian-doeken
(canvas) meer gebruiken.

**Aanpak.** De koppeling bestaat al (`synoptikon/services/wk.py` seint, Wunderkammer haalt op via
`/api/wk/kaarten`; één aanmelding via `sso.py` op `.regoort.me`). Wat er niet is, is één plek waar je
'rechten' doet. Voor ik hier iets bouw wil ik weten wat je mist als je nu tussen de twee heen en weer
gaat — een derde app erbij maakt het onderhoud zwaarder, terwijl een gezamenlijke pagina (bv. punt 6,
met de dagtaak van Wunderkammer erin) hetzelfde zou kunnen doen.

**Obsidian-doeken** is een eigen vraag: wil je dat Synoptikon of Wunderkammer een canvas-bestand kan
schrijven (dat kan: `.canvas` is JSON), of gaat dit over je eigen manier van werken in Obsidian?

## 14. Andere AI's uitzoeken

**Wat.** Andere AI's uitzoeken.

**Aanpak.** Dit is een vergelijking, geen bouwtaak. Zinvol als ik weet waarvoor: goedkoper opzoeken
(waar nu `effort: low` Sonnet staat), een model dat zelf kan zoeken op juridische bronnen, een lokaal
model voor spraak in Calque, of iets anders. Zeg je waarvoor, dan zet ik de opties met prijs en
geschiktheid op een rij.
