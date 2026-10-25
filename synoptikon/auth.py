"""Eén gebruiker, wachtwoord met scrypt-hash en een ondertekende sessiecookie.

Geen externe afhankelijkheden buiten `itsdangerous`: de hash komt uit
`hashlib.scrypt` (stdlib). Na vijf mislukte pogingen wacht de server een
oplopend aantal seconden; voor één gebruiker is dat afdoende tegen
woordenboekaanvallen, zeker achter nginx met TLS.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import time

from fastapi import Request
from itsdangerous import BadSignature, URLSafeTimedSerializer

from .config import settings

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
    try:
        _, salt_s, digest_s = opgeslagen.replace("$", ":").split(":")
        salt = _unb64(salt_s)
        verwacht = _unb64(digest_s)
    except (ValueError, TypeError):
        return False
    digest = hashlib.scrypt(wachtwoord.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return hmac.compare_digest(digest, verwacht)


_serializer = URLSafeTimedSerializer(settings.secret_key, salt="sessie")


def maak_sessie_token() -> str:
    return _serializer.dumps({"u": "ik", "t": int(time.time())})


def sessie_geldig(token: str | None) -> bool:
    if not token:
        return False
    try:
        _serializer.loads(token, max_age=settings.session_days * 86400)
        return True
    except BadSignature:
        return False


def is_ingelogd(request: Request) -> bool:
    if settings.auth_mode == "none":
        return True
    return sessie_geldig(request.cookies.get(COOKIE))


class Vertrager:
    """Houdt mislukte pogingen bij en bepaalt de wachttijd."""

    def __init__(self) -> None:
        self.mislukt = 0
        self.laatste = 0.0

    def wachttijd(self) -> float:
        if self.mislukt < 5:
            return 0.0
        extra = min(2 ** (self.mislukt - 5), 300)
        return max(0.0, self.laatste + extra - time.time())

    def registreer(self, gelukt: bool) -> None:
        if gelukt:
            self.mislukt = 0
        else:
            self.mislukt += 1
            self.laatste = time.time()


vertrager = Vertrager()
