"""Databaseverbinding, schema en full-text-index.

SQLite met FTS5, gemotiveerd in README.md. De FTS-tabellen zijn externe-
inhoudstabellen (`content=`) die via triggers synchroon blijven met de
gewone tabellen; zo kost zoeken geen extra opslag van de teksten.
"""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from .config import settings
from .models import Base

_engine = None
_SessionLocal: sessionmaker[Session] | None = None


def engine():
    global _engine, _SessionLocal
    if _engine is None:
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        # timeout: een bulkimport schrijft lang door; andere schrijvers wachten dan in plaats van "database is locked"
        _engine = create_engine(f"sqlite:///{settings.db_path}", future=True, connect_args={"timeout": 60})

        @event.listens_for(_engine, "connect")
        def _pragmas(dbapi_conn, _record):
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA synchronous=NORMAL")
            cur.close()

        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)
    return _engine


def session_factory() -> sessionmaker[Session]:
    engine()
    assert _SessionLocal is not None
    return _SessionLocal


@contextmanager
def session() -> Iterator[Session]:
    s = session_factory()()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def get_session() -> Iterator[Session]:
    """FastAPI-dependency."""
    s = session_factory()()
    try:
        yield s
        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


# De tokenizer unicode61 met remove_diacritics 2 vouwt é/è/ë samen met e en
# ü met u, zodat "delivrance" ook "délivrance" vindt en "Ubergabe" "Übergabe".
_FTS_DDL = """
CREATE VIRTUAL TABLE IF NOT EXISTS vraag_fts USING fts5(
    titel, omschrijving, rechtsgebied, tags,
    content='vraag', content_rowid='id',
    tokenize="unicode61 remove_diacritics 2"
);
CREATE TRIGGER IF NOT EXISTS vraag_ai AFTER INSERT ON vraag BEGIN
    INSERT INTO vraag_fts(rowid, titel, omschrijving, rechtsgebied, tags)
    VALUES (new.id, new.titel, new.omschrijving, new.rechtsgebied, new.tags);
END;
CREATE TRIGGER IF NOT EXISTS vraag_ad AFTER DELETE ON vraag BEGIN
    INSERT INTO vraag_fts(vraag_fts, rowid, titel, omschrijving, rechtsgebied, tags)
    VALUES ('delete', old.id, old.titel, old.omschrijving, old.rechtsgebied, old.tags);
END;
CREATE TRIGGER IF NOT EXISTS vraag_au AFTER UPDATE ON vraag BEGIN
    INSERT INTO vraag_fts(vraag_fts, rowid, titel, omschrijving, rechtsgebied, tags)
    VALUES ('delete', old.id, old.titel, old.omschrijving, old.rechtsgebied, old.tags);
    INSERT INTO vraag_fts(rowid, titel, omschrijving, rechtsgebied, tags)
    VALUES (new.id, new.titel, new.omschrijving, new.rechtsgebied, new.tags);
END;

CREATE VIRTUAL TABLE IF NOT EXISTS bron_fts USING fts5(
    citeertitel, titel, tekst, vindplaats, opmerking,
    content='bron', content_rowid='id',
    tokenize="unicode61 remove_diacritics 2"
);
CREATE TRIGGER IF NOT EXISTS bron_ai AFTER INSERT ON bron BEGIN
    INSERT INTO bron_fts(rowid, citeertitel, titel, tekst, vindplaats, opmerking)
    VALUES (new.id, new.citeertitel, new.titel, new.tekst, new.vindplaats, new.opmerking);
END;
CREATE TRIGGER IF NOT EXISTS bron_ad AFTER DELETE ON bron BEGIN
    INSERT INTO bron_fts(bron_fts, rowid, citeertitel, titel, tekst, vindplaats, opmerking)
    VALUES ('delete', old.id, old.citeertitel, old.titel, old.tekst, old.vindplaats, old.opmerking);
END;
CREATE TRIGGER IF NOT EXISTS bron_au AFTER UPDATE ON bron BEGIN
    INSERT INTO bron_fts(bron_fts, rowid, citeertitel, titel, tekst, vindplaats, opmerking)
    VALUES ('delete', old.id, old.citeertitel, old.titel, old.tekst, old.vindplaats, old.opmerking);
    INSERT INTO bron_fts(rowid, citeertitel, titel, tekst, vindplaats, opmerking)
    VALUES (new.id, new.citeertitel, new.titel, new.tekst, new.vindplaats, new.opmerking);
END;

CREATE VIRTUAL TABLE IF NOT EXISTS begrip_fts USING fts5(
    term, definitie, vindplaats,
    content='begrip', content_rowid='id',
    tokenize="unicode61 remove_diacritics 2"
);
CREATE TRIGGER IF NOT EXISTS begrip_ai AFTER INSERT ON begrip BEGIN
    INSERT INTO begrip_fts(rowid, term, definitie, vindplaats)
    VALUES (new.id, new.term, new.definitie, new.vindplaats);
END;
CREATE TRIGGER IF NOT EXISTS begrip_ad AFTER DELETE ON begrip BEGIN
    INSERT INTO begrip_fts(begrip_fts, rowid, term, definitie, vindplaats)
    VALUES ('delete', old.id, old.term, old.definitie, old.vindplaats);
END;
CREATE TRIGGER IF NOT EXISTS begrip_au AFTER UPDATE ON begrip BEGIN
    INSERT INTO begrip_fts(begrip_fts, rowid, term, definitie, vindplaats)
    VALUES ('delete', old.id, old.term, old.definitie, old.vindplaats);
    INSERT INTO begrip_fts(rowid, term, definitie, vindplaats)
    VALUES (new.id, new.term, new.definitie, new.vindplaats);
END;

CREATE VIRTUAL TABLE IF NOT EXISTS antwoord_fts USING fts5(
    kern, analyse,
    content='antwoord', content_rowid='id',
    tokenize="unicode61 remove_diacritics 2"
);
CREATE TRIGGER IF NOT EXISTS antwoord_ai AFTER INSERT ON antwoord BEGIN
    INSERT INTO antwoord_fts(rowid, kern, analyse) VALUES (new.id, new.kern, new.analyse);
END;
CREATE TRIGGER IF NOT EXISTS antwoord_ad AFTER DELETE ON antwoord BEGIN
    INSERT INTO antwoord_fts(antwoord_fts, rowid, kern, analyse) VALUES ('delete', old.id, old.kern, old.analyse);
END;
CREATE TRIGGER IF NOT EXISTS antwoord_au AFTER UPDATE ON antwoord BEGIN
    INSERT INTO antwoord_fts(antwoord_fts, rowid, kern, analyse) VALUES ('delete', old.id, old.kern, old.analyse);
    INSERT INTO antwoord_fts(rowid, kern, analyse) VALUES (new.id, new.kern, new.analyse);
END;

CREATE VIRTUAL TABLE IF NOT EXISTS wettekst_artikel_fts USING fts5(
    nummer, opschrift, tekst,
    content='wettekst_artikel', content_rowid='id',
    tokenize="unicode61 remove_diacritics 2"
);
CREATE TRIGGER IF NOT EXISTS wa_ai AFTER INSERT ON wettekst_artikel BEGIN
    INSERT INTO wettekst_artikel_fts(rowid, nummer, opschrift, tekst) VALUES (new.id, new.nummer, new.opschrift, new.tekst);
END;
CREATE TRIGGER IF NOT EXISTS wa_ad AFTER DELETE ON wettekst_artikel BEGIN
    INSERT INTO wettekst_artikel_fts(wettekst_artikel_fts, rowid, nummer, opschrift, tekst)
    VALUES ('delete', old.id, old.nummer, old.opschrift, old.tekst);
END;
CREATE TRIGGER IF NOT EXISTS wa_au AFTER UPDATE ON wettekst_artikel BEGIN
    INSERT INTO wettekst_artikel_fts(wettekst_artikel_fts, rowid, nummer, opschrift, tekst)
    VALUES ('delete', old.id, old.nummer, old.opschrift, old.tekst);
    INSERT INTO wettekst_artikel_fts(rowid, nummer, opschrift, tekst) VALUES (new.id, new.nummer, new.opschrift, new.tekst);
END;

CREATE VIRTUAL TABLE IF NOT EXISTS eu_handeling_fts USING fts5(
    celex, nummer, roepnaam, titel,
    content='eu_handeling', content_rowid='rowid',
    tokenize="unicode61 remove_diacritics 2"
);
CREATE TRIGGER IF NOT EXISTS eu_ai AFTER INSERT ON eu_handeling BEGIN
    INSERT INTO eu_handeling_fts(rowid, celex, nummer, roepnaam, titel) VALUES (new.rowid, new.celex, new.nummer, new.roepnaam, new.titel);
END;
CREATE TRIGGER IF NOT EXISTS eu_ad AFTER DELETE ON eu_handeling BEGIN
    INSERT INTO eu_handeling_fts(eu_handeling_fts, rowid, celex, nummer, roepnaam, titel)
    VALUES ('delete', old.rowid, old.celex, old.nummer, old.roepnaam, old.titel);
END;
CREATE VIRTUAL TABLE IF NOT EXISTS eu_titel_fts USING fts5(
    titel,
    content='eu_titel', content_rowid='rowid',
    tokenize="unicode61 remove_diacritics 2"
);
CREATE TRIGGER IF NOT EXISTS eut_ai AFTER INSERT ON eu_titel BEGIN
    INSERT INTO eu_titel_fts(rowid, titel) VALUES (new.rowid, new.titel);
END;
CREATE TRIGGER IF NOT EXISTS eut_ad AFTER DELETE ON eu_titel BEGIN
    INSERT INTO eu_titel_fts(eu_titel_fts, rowid, titel) VALUES ('delete', old.rowid, old.titel);
END;
CREATE TRIGGER IF NOT EXISTS eut_au AFTER UPDATE ON eu_titel BEGIN
    INSERT INTO eu_titel_fts(eu_titel_fts, rowid, titel) VALUES ('delete', old.rowid, old.titel);
    INSERT INTO eu_titel_fts(rowid, titel) VALUES (new.rowid, new.titel);
END;
CREATE TRIGGER IF NOT EXISTS eu_au AFTER UPDATE ON eu_handeling BEGIN
    INSERT INTO eu_handeling_fts(eu_handeling_fts, rowid, celex, nummer, roepnaam, titel)
    VALUES ('delete', old.rowid, old.celex, old.nummer, old.roepnaam, old.titel);
    INSERT INTO eu_handeling_fts(rowid, celex, nummer, roepnaam, titel) VALUES (new.rowid, new.celex, new.nummer, new.roepnaam, new.titel);
END;
"""


# Kolommen die later zijn bijgekomen: (tabel, kolom, type). `create_all` voegt
# geen kolommen toe aan bestaande tabellen, dus dat doet `_migreer`.
_NIEUWE_KOLOMMEN = [
    ("stelsel", "familie", "VARCHAR(20)"),
    ("systematiek", "wet", "VARCHAR(60)"),
    ("wettekst", "wet", "VARCHAR(60)"),
    ("wettekst", "taal", "VARCHAR(5)"),
    ("wettekst", "kern", "BOOLEAN NOT NULL DEFAULT 1"),
    ("wettekst", "stijl", "VARCHAR(8)"),
    ("kaart", "status", "VARCHAR(10)"),
    ("kaart", "herkomst", "VARCHAR(300)"),
]


def _migreer(conn) -> None:
    for tabel, kolom, soort in _NIEUWE_KOLOMMEN:
        bestaand = {r[1] for r in conn.execute(text(f"PRAGMA table_info({tabel})"))}
        if bestaand and kolom not in bestaand:
            conn.execute(text(f"ALTER TABLE {tabel} ADD COLUMN {kolom} {soort}"))


def init_db() -> None:
    """Maakt tabellen, FTS-tabellen en triggers aan, voegt nieuwe kolommen toe en zorgt voor de profielplekken (idempotent)."""
    eng = engine()
    Base.metadata.create_all(eng)
    with eng.begin() as conn:
        _migreer(conn)
        for stmt in _splits_ddl(_FTS_DDL):
            conn.execute(text(stmt))
    _profielen()


def _profielen() -> None:
    """Vijf vaste plekken. Profiel 1 is de beheerder en staat aan; de andere wachten op een naam en wachtwoord."""
    from .models import AANTAL_PROFIELEN, Profiel

    with session() as s:
        for i in range(1, AANTAL_PROFIELEN + 1):
            if s.get(Profiel, i) is None:
                eerste = i == 1
                s.add(Profiel(
                    id=i,
                    gebruikersnaam="beheerder" if eerste else f"profiel{i}",
                    naam="Beheerder" if eerste else f"Profiel {i}",
                    rol="beheerder" if eerste else "lezer",
                    taal=settings.ui_lang if eerste else "nl",
                    actief=eerste,
                ))


def _splits_ddl(ddl: str) -> list[str]:
    """Splitst de DDL in statements; puntkomma's binnen BEGIN…END horen bij de trigger."""
    statements, huidig, in_trigger = [], [], False
    for regel in ddl.splitlines():
        s = regel.strip()
        if not s:
            continue
        huidig.append(regel)
        if s.upper().startswith("CREATE TRIGGER"):
            in_trigger = True
        if in_trigger:
            if s.upper() == "END;":
                statements.append("\n".join(huidig).rstrip(";"))
                huidig, in_trigger = [], False
        elif s.endswith(";"):
            statements.append("\n".join(huidig).rstrip(";"))
            huidig = []
    return statements


def rebuild_fts() -> None:
    """Herindexeert alle FTS-tabellen vanuit de inhoudstabellen."""
    with engine().begin() as conn:
        for tabel in ("vraag_fts", "bron_fts", "begrip_fts", "antwoord_fts", "wettekst_artikel_fts", "eu_handeling_fts", "eu_titel_fts"):
            conn.execute(text(f"INSERT INTO {tabel}({tabel}) VALUES('rebuild')"))
