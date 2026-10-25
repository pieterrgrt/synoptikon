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


def cmd_import(args) -> int:
    from .importers import bwb, eurlex, gii, legifrance, store

    database.init_db()
    bron = args.stelsel.lower()
    try:
        if args.bestand:
            data = Path(args.bestand).read_bytes()
            if bron == "nl":
                g = bwb.parse(data, args.id)
            elif bron == "de":
                g = gii.parse_zip(data, args.id) if args.bestand.endswith(".zip") else gii.parse(data, args.id)
            elif bron == "eu":
                g = eurlex.parse(data.decode("utf-8", "replace"), args.id)
            else:
                print("Voor FR is alleen de API-import beschikbaar.", file=sys.stderr)
                return 2
        else:
            if bron == "nl":
                g = bwb.haal_op(args.id)
            elif bron == "de":
                g = gii.haal_op(args.id)
            elif bron == "eu":
                g = eurlex.haal_op(args.id, taal=args.taal or "NL")
            elif bron == "fr":
                g = legifrance.haal_op(args.id, nummers=args.artikelen.split(",") if args.artikelen else None, datum=args.datum)
            else:
                print(f"Onbekend stelsel: {args.stelsel}", file=sys.stderr)
                return 2
    except ImportOvergeslagen as e:
        print(e)
        return 0

    with database.session() as s:
        w = store.sla_op(s, bron.upper(), g)
        print(f"{w.stelsel_code} {w.titel} (versie {w.versie}): {len(w.artikelen)} artikelen opgeslagen.")
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
    s = sub.add_parser("import", help="wettekst importeren: nl BWBR…, de bgb, fr LEGITEXT…, eu CELEX")
    s.add_argument("stelsel", choices=["nl", "de", "fr", "eu"])
    s.add_argument("id")
    s.add_argument("--bestand", help="lokaal bestand gebruiken in plaats van downloaden")
    s.add_argument("--artikelen", help="FR: kommagescheiden artikelnummers, bijv. 1196,2276")
    s.add_argument("--datum", help="FR: geldigheidsdatum JJJJ-MM-DD")
    s.add_argument("--taal", help="EU: taalcode van de EUR-Lex-versie (standaard NL)")
    s.set_defaults(fn=cmd_import)
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
