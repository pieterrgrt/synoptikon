"""Opdrachtregel: `synoptikon <opdracht>` (of `python -m synoptikon.cli`)."""
from __future__ import annotations

import argparse
import getpass
import sys
from pathlib import Path

from . import db as database
from .importers import ImportOvergeslagen


def cmd_init(_args) -> int:
    database.init_db()
    print(f"Database klaar: {database.settings.db_path}")
    return 0


def cmd_seed(args) -> int:
    from .seed import seed

    database.init_db()
    with database.session() as s:
        aantal = seed(s, overschrijf=args.overschrijf)
    print(f"Voorbeeldinhoud geladen ({aantal} vragen).")
    return 0


def cmd_hash_password(args) -> int:
    from .auth import hash_password

    ww = args.wachtwoord or getpass.getpass("Wachtwoord: ")
    if not args.wachtwoord:
        if getpass.getpass("Nogmaals: ") != ww:
            print("Wachtwoorden verschillen.", file=sys.stderr)
            return 1
    print(hash_password(ww))
    return 0


def cmd_profiel(args) -> int:
    from .auth import hash_password
    from .i18n import TALEN
    from .models import ROLLEN, Profiel

    database.init_db()
    with database.session() as s:
        if args.id is None:
            for p in s.query(Profiel).order_by(Profiel.id):
                print(f"{p.id}  {p.gebruikersnaam:<14} {p.naam:<20} {p.rol:<10} {p.taal}  {'aan' if p.actief else 'uit'}"
                      f"{'' if p.wachtwoord_hash else '  (geen eigen wachtwoord)'}")
            return 0
        p = s.get(Profiel, args.id)
        if p is None:
            print(f"Geen profiel {args.id}; er zijn plekken 1–5.", file=sys.stderr)
            return 1
        if args.gebruikersnaam:
            p.gebruikersnaam = args.gebruikersnaam.strip().lower()
        if args.naam:
            p.naam = args.naam
        if args.rol:
            if args.rol not in ROLLEN:
                print(f"Rol is een van: {', '.join(ROLLEN)}", file=sys.stderr)
                return 1
            p.rol = args.rol
        if args.taal:
            if args.taal not in TALEN:
                print(f"Taal is een van: {', '.join(TALEN)}", file=sys.stderr)
                return 1
            p.taal = args.taal
        if args.wachtwoord:
            ww = getpass.getpass("Nieuw wachtwoord: ")
            if len(ww) < 10 or getpass.getpass("Nogmaals: ") != ww:
                print("Minstens 10 tekens, twee keer hetzelfde.", file=sys.stderr)
                return 1
            p.wachtwoord_hash = hash_password(ww)
            p.sessie_versie += 1
        if args.aan:
            p.actief = True
        if args.uit:
            p.actief = False
            p.sessie_versie += 1
        print(f"Profiel {p.id}: {p.gebruikersnaam} · {p.naam} · {p.rol} · {p.taal} · {'aan' if p.actief else 'uit'}")
    return 0


def cmd_import(args) -> int:
    from .importers import boe, bwb, etaamb, eurlex, fedlex, gii, legi, legifrance, legislation_uk, normattiva, store

    database.init_db()
    bron = args.stelsel.lower()
    try:
        if args.bestand:
            pad = Path(args.bestand)
            data = pad.read_bytes() if pad.is_file() else b""
            if bron == "nl":
                g = bwb.parse(data, args.id)
            elif bron == "de":
                g = gii.parse_zip(data, args.id) if args.bestand.endswith(".zip") else gii.parse(data, args.id)
            elif bron == "eu":
                g = eurlex.parse(data.decode("utf-8", "replace"), args.id)
            elif bron == "fr":
                g = legi.parse_map(pad, args.id)  # een map met de uitgepakte LEGI-dump
            elif bron == "it":
                g = normattiva.parse(data, args.id)
            elif bron == "es":
                g = boe.parse(data, args.id)
            elif bron == "ch":
                g = fedlex.parse(data, args.id)
            elif bron == "be":
                g = etaamb.parse(data.decode("utf-8", "replace"), args.id)
            else:
                g = legislation_uk.parse(data, args.id)
        else:
            haal = {
                "nl": lambda: bwb.haal_op(args.id),
                "de": lambda: gii.haal_op(args.id),
                "eu": lambda: eurlex.haal_op(args.id, taal=args.taal or "NL"),
                "fr": lambda: legifrance.haal_op(args.id, nummers=args.artikelen.split(",") if args.artikelen else None, datum=args.datum),
                "it": lambda: normattiva.haal_op(args.id),
                "es": lambda: boe.haal_op(args.id),
                "ch": lambda: fedlex.haal_op(args.id),
                "be": lambda: etaamb.haal_op(args.id),
                "en": lambda: legislation_uk.haal_op(args.id),
            }
            g = haal[bron]()
    except ImportOvergeslagen as e:
        print(e)
        return 0

    with database.session() as s:
        w = store.sla_op(s, bron.upper(), g, args.wet)
        print(f"{w.stelsel_code} {w.titel} (versie {w.versie}): {len(w.artikelen)} artikelen opgeslagen.")
        if args.systematiek:
            _systematiek(s, w)
    return 0


def cmd_import_alles(args) -> int:
    """Loopt het register af (importers/register.py); een fout bij één wet stopt de rest niet."""
    from .importers import ImportOvergeslagen, register, store

    database.init_db()
    fouten = 0
    for w in register.WETTEN:
        if args.stelsel and w.stelsel.lower() not in [x.lower() for x in args.stelsel]:
            continue
        try:
            g = register.haal_op(w, args.legi)
        except ImportOvergeslagen as e:
            print(f"overgeslagen: {e}")
            continue
        except Exception as e:  # netwerk, parser: melden en door
            print(f"FOUT {w.stelsel} {w.titel}: {e}", file=sys.stderr)
            fouten += 1
            continue
        with database.session() as s:
            t = store.sla_op(s, w.stelsel, g, w.wet)
            print(f"{w.stelsel} {w.wet or '(hoofdwet)'} · {t.titel} ({t.versie}): {len(t.artikelen)} artikelen")
            if w.systematiek and args.systematiek:
                _systematiek(s, t)
    return 1 if fouten else 0


def cmd_eu_catalogus(args) -> int:
    from .services import eu

    database.init_db()
    with database.session() as s:
        r = eu.werk_catalogus_bij(s, nims=not args.zonder_nims)
    print(f"EU-catalogus: {r['handelingen']} geldende handelingen ({r['nieuw']} nieuw, {r['vervallen']} niet meer geldend verwijderd), "
          f"{r['rubrieken']} rubrieken, {r['nims']} nationale uitvoeringsmaatregelen.")
    return 0


def cmd_vertalingen(args) -> int:
    import json

    from .services import vertalen

    database.init_db()
    with database.session() as s:
        if args.actie == "stand":
            for t, (k, n) in vertalen.stand(s).items():
                print(f"{t}: {k}/{n}")
        elif args.actie == "export":
            print(json.dumps(vertalen.ontbrekend(s, args.taal), ensure_ascii=False, indent=1))
        elif args.actie == "import":
            with open(args.bestand, encoding="utf-8") as f:
                n = vertalen.laad(s, args.taal, json.load(f), herkomst=args.herkomst, overschrijf=args.overschrijf)
            print(f"{n} vertalingen ({args.taal}) opgeslagen.")
        elif args.actie == "seed":
            print(vertalen.laad_seed(s))
    return 0


def cmd_eu_talen(args) -> int:
    from .services import eu

    database.init_db()
    with database.session() as s:
        r = eu.werk_talen_bij(s, args.taal or None)
    print("EU in andere talen: " + ", ".join(f"{k} {v}" for k, v in r.items()))
    return 0


def _systematiek(s, w) -> None:
    from .services.systematiek import bouw_uit_wettekst

    r = bouw_uit_wettekst(s, w)
    print(f"Systematiek {w.stelsel_code} uit {w.titel}: {r.nieuw} knopen toegevoegd, {r.bijgewerkt} bereiken bijgewerkt ({r.artikelen} artikelen met pad).")


def cmd_systematiek(args) -> int:
    from sqlalchemy import select

    from .models import Wettekst

    database.init_db()
    with database.session() as s:
        q = select(Wettekst).where(Wettekst.stelsel_code == args.stelsel.upper(), Wettekst.wet_id == args.id)
        if args.versie:
            q = q.where(Wettekst.versie == args.versie)
        w = s.scalars(q.order_by(Wettekst.opgehaald.desc())).first()
        if w is None:
            print(f"Geen geïmporteerde wettekst {args.stelsel.upper()} {args.id}; importeer eerst met `synoptikon import`.", file=sys.stderr)
            return 1
        _systematiek(s, w)
    return 0


def cmd_rebuild_fts(_args) -> int:
    database.init_db()
    database.rebuild_fts()
    print("Zoekindex opnieuw opgebouwd.")
    return 0


def cmd_serve(args) -> int:
    import uvicorn

    uvicorn.run("synoptikon.main:app", host=args.host, port=args.port, reload=args.reload, workers=1)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="synoptikon", description="Synoptikon — rechtsvergelijking naast elkaar")
    sub = p.add_subparsers(dest="opdracht", required=True)

    sub.add_parser("init", help="database aanmaken").set_defaults(fn=cmd_init)
    s = sub.add_parser("seed", help="voorbeeldinhoud laden")
    s.add_argument("--overschrijf", action="store_true", help="bestaande voorbeeldvragen vervangen")
    s.set_defaults(fn=cmd_seed)
    s = sub.add_parser("hash-password", help="scrypt-hash maken voor SYNOPTIKON_PASSWORD_HASH")
    s.add_argument("wachtwoord", nargs="?")
    s.set_defaults(fn=cmd_hash_password)
    s = sub.add_parser("profiel", help="profielen tonen of één profiel wijzigen (naam, rol, taal, wachtwoord, aan/uit)")
    s.add_argument("id", type=int, nargs="?", help="plek 1–5; zonder id: overzicht")
    s.add_argument("--gebruikersnaam")
    s.add_argument("--naam")
    s.add_argument("--rol", help="beheerder · redacteur · lezer")
    s.add_argument("--taal", help="nl · fr · de · it · en · es")
    s.add_argument("--wachtwoord", action="store_true", help="nieuw wachtwoord vragen")
    s.add_argument("--aan", action="store_true")
    s.add_argument("--uit", action="store_true")
    s.set_defaults(fn=cmd_profiel)
    s = sub.add_parser("import", help="wettekst importeren: nl BWBR…, de bgb, fr LEGITEXT…, it urn:nir:…, es BOE-A-…, ch cc/…, be <etaamb>, en ukpga/…, eu CELEX")
    s.add_argument("stelsel", choices=["nl", "de", "fr", "it", "es", "ch", "be", "en", "eu"])
    s.add_argument("id")
    s.add_argument("--wet", help="citeerafkorting als het niet de hoofdcodificatie is, bijv. OR, 'C. consom.', TRLGDCU")
    s.add_argument("--bestand", help="lokaal bestand gebruiken in plaats van downloaden (FR: map met de LEGI-dump)")
    s.add_argument("--artikelen", help="FR: kommagescheiden artikelnummers, bijv. 1196,2276")
    s.add_argument("--datum", help="FR: geldigheidsdatum JJJJ-MM-DD")
    s.add_argument("--taal", help="EU: taalcode van de EUR-Lex-versie (standaard NL)")
    s.add_argument("--systematiek", action="store_true", help="na het importeren de systematiekboom aanvullen uit de wettekst")
    s.set_defaults(fn=cmd_import)
    s = sub.add_parser("import-alles", help="alle wetboeken en wetten uit het register importeren")
    s.add_argument("--stelsel", nargs="*", help="alleen deze stelsels, bijv. --stelsel it es")
    s.add_argument("--legi", help="map met de uitgepakte LEGI-dump (scripts/legi_ophalen.sh), nodig voor FR")
    s.add_argument("--systematiek", action="store_true", help="systematiekboom aanvullen waar het register dat aangeeft")
    s.set_defaults(fn=cmd_import_alles)
    s = sub.add_parser("eu-catalogus", help="geldende verordeningen en richtlijnen, repertorium en nationale uitvoeringsmaatregelen ophalen uit Cellar")
    s.add_argument("--zonder-nims", action="store_true", help="nationale uitvoeringsmaatregelen overslaan")
    s.set_defaults(fn=cmd_eu_catalogus)
    s = sub.add_parser("vertalingen", help="vertaalgeheugen voor eigen inhoud: stand, export (ontbrekend), import, seed")
    s.add_argument("actie", choices=["stand", "export", "import", "seed"])
    s.add_argument("--taal", choices=["fr", "de", "it", "en", "es"])
    s.add_argument("--bestand", help="import: JSON {Nederlandse tekst: vertaling}")
    s.add_argument("--herkomst", default="claude", choices=["claude", "eigen"])
    s.add_argument("--overschrijf", action="store_true", help="import: bestaande machinevertalingen vervangen (eigen vertalingen nooit)")
    s.set_defaults(fn=cmd_vertalingen)
    s = sub.add_parser("eu-talen", help="officiële titels en rubrieknamen van de EU-catalogus in fr, de, it, en en es ophalen uit Cellar")
    s.add_argument("--taal", action="append", choices=["fr", "de", "it", "en", "es"], help="alleen deze taal (herhaalbaar)")
    s.set_defaults(fn=cmd_eu_talen)
    s = sub.add_parser("systematiek", help="systematiekboom aanvullen uit een geïmporteerde wettekst: nl BWBR0005291, de bgb, fr LEGITEXT…")
    s.add_argument("stelsel", choices=["nl", "de", "fr", "it", "es", "ch", "be", "en", "eu"])
    s.add_argument("id")
    s.add_argument("--versie", help="specifieke versie (standaard de laatst opgehaalde)")
    s.set_defaults(fn=cmd_systematiek)
    sub.add_parser("rebuild-fts", help="zoekindex opnieuw opbouwen").set_defaults(fn=cmd_rebuild_fts)
    s = sub.add_parser("serve", help="ontwikkelserver starten")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--reload", action="store_true")
    s.set_defaults(fn=cmd_serve)

    args = p.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
