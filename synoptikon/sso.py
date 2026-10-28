"""Eén aanmelding voor de apps op regoort.me (Synoptikon, Wunderkammer).

Wie in een van de apps inlogt, krijgt naast de eigen sessiecookie een cookie `regoort_sso` op het hoofddomein
(`.regoort.me`). De andere app ziet die cookie, herkent de gebruikersnaam en logt dezelfde gebruiker in zonder
wachtwoord. Uitloggen wist de cookie weer. De cookie bevat alleen de gebruikersnaam en een vervaldatum, getekend met
een gedeeld geheim (HMAC-SHA256); zonder geheim (leeg of korter dan 32 tekens) staat het uit.

Formaat: base64url(JSON {"u", "exp"}) "." base64url(HMAC). Dezelfde module staat in beide apps
(synoptikon/sso.py, wunderkammer backend/app/sso.py); houd ze gelijk.

Op een iPhone heeft elke app op het beginscherm een eigen cookieopslag: daar helpt de cookie niet, en logt elke app
één keer in (met hetzelfde wachtwoord).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time

COOKIE = "regoort_sso"
DAGEN = 90


def _b64(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")


def _unb64(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def aan(geheim: str | None) -> bool:
    return bool(geheim) and len(geheim) >= 32


def maak(gebruiker: str, geheim: str, dagen: int = DAGEN) -> str:
    payload = _b64(json.dumps({"u": gebruiker.strip().lower(), "exp": int(time.time()) + dagen * 86400}).encode())
    return payload + "." + _b64(hmac.new(geheim.encode(), payload.encode(), hashlib.sha256).digest())


def lees(waarde: str | None, geheim: str | None) -> str | None:
    """De gebruikersnaam uit een geldige, niet verlopen cookie, anders None."""
    if not waarde or not aan(geheim) or "." not in waarde:
        return None
    payload, handtekening = waarde.rsplit(".", 1)
    verwacht = _b64(hmac.new(geheim.encode(), payload.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(handtekening, verwacht):
        return None
    try:
        data = json.loads(_unb64(payload))
    except (ValueError, TypeError):
        return None
    if not isinstance(data, dict) or int(data.get("exp", 0)) < time.time():
        return None
    return str(data.get("u") or "") or None


def zet(response, gebruiker: str, geheim: str | None, domein: str | None, secure: bool = True) -> None:
    if aan(geheim):
        response.set_cookie(COOKIE, maak(gebruiker, geheim), max_age=DAGEN * 86400, httponly=True, secure=secure,
                            samesite="lax", path="/", domain=domein or None)


def wis(response, domein: str | None) -> None:
    response.delete_cookie(COOKIE, path="/", domain=domein or None)
