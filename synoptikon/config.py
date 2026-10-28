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

    # Eén aanmelding met de andere apps op het domein (sso.py): gedeeld geheim (≥ 32 tekens, hetzelfde als WK_SSO_SECRET
    # in Wunderkammer) en het cookiedomein, bijv. ".regoort.me". Leeg = uit.
    sso_geheim: str | None = field(default_factory=lambda: _env("SYNOPTIKON_SSO_SECRET"))
    sso_domein: str | None = field(default_factory=lambda: _env("SYNOPTIKON_SSO_DOMEIN"))

    # Claude (services/claude.py): opzoeken op /opzoeken en rechtsvergelijkend onderzoek bij een vraag. Zonder sleutel
    # werkt alles behalve die twee. Het maandbudget is een harde grens; daarboven weigert de app elke aanroep.
    anthropic_api_key: str | None = field(default_factory=lambda: _env("SYNOPTIKON_ANTHROPIC_API_KEY") or _env("ANTHROPIC_API_KEY"))
    claude_model: str = field(default_factory=lambda: _env("SYNOPTIKON_CLAUDE_MODEL", "claude-opus-5-5"))
    llm_budget_usd: float = field(default_factory=lambda: float(_env("SYNOPTIKON_LLM_BUDGET_USD", "20")))

    # Kaarten uit notities (services/notities.py): een kopie van de notitiemap (scripts/notities.sh zet die in
    # data/notities) en per map het vak in Wunderkammer, "Zivilrecht 1A=ZR Ia; Kapitalmarktrecht=W". Mappen zonder vak
    # worden overgeslagen. Leeg = uit.
    notities_dir: Path = field(default_factory=lambda: Path(_env("SYNOPTIKON_NOTITIES_DIR", "") or Path(_env("SYNOPTIKON_DATA_DIR", "./data")) / "notities").resolve())
    notities_vakken: str = field(default_factory=lambda: _env("SYNOPTIKON_NOTITIES_VAKKEN", ""))

    # Standaardtaal voor vertalingen in de synopse.
    ui_lang: str = field(default_factory=lambda: _env("SYNOPTIKON_UI_LANG", "nl"))

    @property
    def db_path(self) -> Path:
        return self.data_dir / "synoptikon.db"

    @property
    def wetteksten_dir(self) -> Path:
        return self.data_dir / "wetteksten"


settings = Settings()
