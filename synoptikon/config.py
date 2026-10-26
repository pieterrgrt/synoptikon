"""Configuratie uit omgevingsvariabelen.

Alles wat per installatie verschilt (paden, geheimen, API-sleutels) komt
hier vandaan; de rest van de code importeert alleen `settings`.
"""
from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    if value is None or value == "":
        return default
    return value


@dataclass
class Settings:
    # Pad naar de map met de SQLite-database en de lokaal opgeslagen wetteksten.
    data_dir: Path = field(default_factory=lambda: Path(_env("SYNOPTIKON_DATA_DIR", "./data")).resolve())

    # Authenticatie. AUTH_MODE=password (standaard) toont een inlogformulier
    # en zet een ondertekende sessiecookie; AUTH_MODE=none laat alles door en
    # is bedoeld voor achter nginx basic auth. Het wachtwoord staat als
    # scrypt-hash in SYNOPTIKON_PASSWORD_HASH (zie `synoptikon hash-password`).
    auth_mode: str = field(default_factory=lambda: _env("SYNOPTIKON_AUTH_MODE", "password"))
    password_hash: str | None = field(default_factory=lambda: _env("SYNOPTIKON_PASSWORD_HASH"))
    secret_key: str = field(default_factory=lambda: _env("SYNOPTIKON_SECRET_KEY") or secrets.token_hex(32))
    session_days: int = field(default_factory=lambda: int(_env("SYNOPTIKON_SESSION_DAYS", "30")))
    cookie_secure: bool = field(default_factory=lambda: _env("SYNOPTIKON_COOKIE_SECURE", "1") == "1")

    # Légifrance (PISTE). Zonder client-ID/secret slaat de importer netjes over.
    legifrance_client_id: str | None = field(default_factory=lambda: _env("LEGIFRANCE_CLIENT_ID"))
    legifrance_client_secret: str | None = field(default_factory=lambda: _env("LEGIFRANCE_CLIENT_SECRET"))
    legifrance_sandbox: bool = field(default_factory=lambda: _env("LEGIFRANCE_SANDBOX", "0") == "1")

    # Koppeling met Wunderkammer (routes/wunderkammer.py): Bearer-token, minstens 24 tekens; leeg = uit.
    wk_token: str | None = field(default_factory=lambda: _env("SYNOPTIKON_WK_TOKEN"))

    # Standaardtaal voor vertalingen in de synopse.
    ui_lang: str = field(default_factory=lambda: _env("SYNOPTIKON_UI_LANG", "nl"))

    @property
    def db_path(self) -> Path:
        return self.data_dir / "synoptikon.db"

    @property
    def wetteksten_dir(self) -> Path:
        return self.data_dir / "wetteksten"


settings = Settings()
