"""Vijf profielen, wachtwoorden met scrypt-hash en een ondertekende sessiecookie.

Geen externe afhankelijkheden buiten `itsdangerous`: de hash komt uit
`hashlib.scrypt` (stdlib). Na vijf mislukte pogingen voor een
gebruikersnaam wacht de server een oplopend aantal seconden; voor een
handvol profielen is dat afdoende tegen woordenboekaanvallen, zeker achter
nginx met TLS.

De cookie bevat het profiel-id en de sessieversie van dat profiel. Een nieuw
wachtwoord of het uitzetten van een profiel hoogt de versie op, zodat
bestaande sessies van dat profiel vervallen. Profiel 1 (de beheerder) mag
nog inloggen met `SYNOPTIKON_PASSWORD_HASH` zolang het geen eigen
wachtwoord in de database heeft.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time

from fastapi import Request
from itsdangerous import BadSignature, URLSafeTimedSerializer
from sqlalchemy import func, select

from . import sso
from .config import settings
from .db import session_factory
from .models import Profiel

COOKIE = "synoptikon_sessie"
# Formaat: scrypt:<salt>:<digest>, base64url zonder padding. Bewust geen "$"
# of "=": Docker Compose leest "$x" in .env als variabele en zou de hash
# verminken. Het oude formaat met "$" wordt nog herkend.
_PREFIX = "scrypt:"


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _unb64(s: str) -> bytes:
    s = s.strip()
    s += "=" * (-len(s) % 4)
    # Nieuw formaat is base64url; het oude gebruikte standaard base64 ("+", "/").
    return base64.b64decode(s) if "+" in s or "/" in s else base64.urlsafe_b64decode(s)


def hash_password(wachtwoord: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(wachtwoord.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return _PREFIX + _b64(salt) + ":" + _b64(digest)


def verify_password(wachtwoord: str, opgeslagen: str | None) -> bool:
    opgeslagen = (opgeslagen or "").strip().strip("'\"")
    if not opgeslagen.startswith(("scrypt:", "scrypt$")):
        return False
    delen = opgeslagen.replace("$", ":").split(":")
    if len(delen) == 6:
        # Formaat van Wunderkammer (scrypt:N:r:p:salt:digest, gewone base64): één wachtwoord voor beide apps.
        try:
            n, r, p = (int(x) for x in delen[1:4])
            salt, verwacht = base64.b64decode(delen[4]), base64.b64decode(delen[5])
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(hashlib.scrypt(wachtwoord.encode(), salt=salt, n=n, r=r, p=p, dklen=len(verwacht)), verwacht)
    try:
        _, salt_s, digest_s = opgeslagen.replace("$", ":").split(":")
        salt = _unb64(salt_s)
        verwacht = _unb64(digest_s)
    except (ValueError, TypeError):
        return False
    digest = hashlib.scrypt(wachtwoord.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return hmac.compare_digest(digest, verwacht)


_serializer = URLSafeTimedSerializer(settings.secret_key, salt="sessie")
_DUMMY = hash_password(secrets.token_hex(8))


def maak_sessie_token(p: Profiel) -> str:
    return _serializer.dumps({"p": p.id, "v": p.sessie_versie, "t": int(time.time())})


def _lees_token(token: str | None) -> dict | None:
    if not token:
        return None
    try:
        data = _serializer.loads(token, max_age=settings.session_days * 86400)
    except BadSignature:
        return None
    return data if isinstance(data, dict) else None


def profiel_uit_cookie(token: str | None) -> Profiel | None:
    """Het actieve profiel van een geldige sessiecookie. Cookies van vóór de profielen ({"u": "ik"}) gelden als profiel 1."""
    data = _lees_token(token)
    if data is None:
        return None
    pid, versie = data.get("p", 1), data.get("v", 0)
    with session_factory()() as s:
        p = s.get(Profiel, pid)
        if p is None or not p.actief or p.sessie_versie != versie:
            return None
        s.expunge(p)
        return p


def huidig_profiel(request: Request) -> Profiel | None:
    """Profiel van dit verzoek (één keer opgezocht en bewaard in request.state)."""
    if hasattr(request.state, "profiel"):
        return request.state.profiel
    if settings.auth_mode == "none":
        with session_factory()() as s:
            p = s.get(Profiel, 1)
            if p is not None:
                s.expunge(p)
    else:
        p = profiel_uit_cookie(request.cookies.get(COOKIE))
    request.state.profiel = p
    return p


def profiel_uit_sso(request: Request) -> Profiel | None:
    """Het profiel bij een geldige domeincookie (sso.py), als dat profiel bestaat en aan staat."""
    naam = sso.lees(request.cookies.get(sso.COOKIE), settings.sso_geheim)
    if not naam:
        return None
    with session_factory()() as s:
        p = s.scalars(select(Profiel).where(func.lower(Profiel.gebruikersnaam) == naam)).first()
        if p is None or not p.actief:
            return None
        s.expunge(p)
    request.state.profiel = p
    return p


def is_ingelogd(request: Request) -> bool:
    if settings.auth_mode == "none":
        return True
    return huidig_profiel(request) is not None


def controleer(s, gebruikersnaam: str, wachtwoord: str) -> Profiel | None:
    """Profiel bij gebruikersnaam en wachtwoord, of None. Hoofdletterongevoelig op de naam."""
    p = s.scalars(select(Profiel).where(func.lower(Profiel.gebruikersnaam) == gebruikersnaam.strip().lower())).first()
    if p is None or not p.actief:
        # Toch een hash berekenen, zodat de responstijd niet verraadt of de naam bestaat.
        verify_password(wachtwoord, _DUMMY)
        return None
    opgeslagen = p.wachtwoord_hash or (settings.password_hash if p.id == 1 else None)
    return p if verify_password(wachtwoord, opgeslagen) else None


class Vertrager:
    """Houdt mislukte pogingen per gebruikersnaam bij en bepaalt de wachttijd."""

    def __init__(self) -> None:
        self.mislukt: dict[str, int] = {}
        self.laatste: dict[str, float] = {}

    def wachttijd(self, naam: str = "") -> float:
        naam = naam.strip().lower()
        n = self.mislukt.get(naam, 0)
        if n < 5:
            return 0.0
        extra = min(2 ** (n - 5), 300)
        return max(0.0, self.laatste.get(naam, 0.0) + extra - time.time())

    def registreer(self, gelukt: bool, naam: str = "") -> None:
        naam = naam.strip().lower()
        if gelukt:
            self.mislukt.pop(naam, None)
        else:
            self.mislukt[naam] = self.mislukt.get(naam, 0) + 1
            self.laatste[naam] = time.time()


vertrager = Vertrager()
