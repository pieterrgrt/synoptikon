"""Eén HTTP-client voor alle importers, beleefd tegenover de bronnen.

* Throttle per host: tussen twee verzoeken aan dezelfde host minstens `SYNOPTIKON_HTTP_TUSSENTIJD` seconden
  (standaard 1), over alle clients en threads heen. Een bulkimport met vier threads haalt dus nog steeds één document
  per seconde per host; parallel loont alleen over verschillende hosts.
* Opnieuw bij 429 en 5xx (`SYNOPTIKON_HTTP_POGINGEN`, standaard 4), met oplopende wachttijd; een `Retry-After` van de
  server gaat voor (tot vijf minuten; langer = opgeven).
* Conditional GET, alleen binnen `with conditioneel() as c:`: dan gaan `If-None-Match`/`If-Modified-Since` mee uit
  het bewaarde ETag/Last-Modified van die URL, en een 304 wordt de uitzondering `Ongewijzigd`. Nieuwe validators
  komen eerst in `c.gezien` en worden pas bewaard met `bevestig(c)`, als de tekst echt is opgeslagen; anders zou een
  mislukte import de volgende keer voor ongewijzigd doorgaan. Opslag: `<datamap>/http_validators.json`.

Het werkt als transport onder httpx, zodat ook doorverwijzingen en `client.stream()` erdoor gaan.
"""
from __future__ import annotations

import json
import os
import random
import threading
import time
from contextlib import contextmanager
from contextvars import ContextVar
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx

UA = "Synoptikon/0.1 (persoonlijke rechtsvergelijkingsapp; httpx)"
_OPNIEUW = {429, 500, 502, 503, 504}
_MAX_WACHT = 300.0


class Ongewijzigd(Exception):
    """304: de bron is niet veranderd sinds de vorige keer (alleen binnen `conditioneel()`)."""


def _tussentijd() -> float:
    return float(os.environ.get("SYNOPTIKON_HTTP_TUSSENTIJD") or 1.0)


def _pogingen() -> int:
    return max(1, int(os.environ.get("SYNOPTIKON_HTTP_POGINGEN") or 4))


# --- throttle --------------------------------------------------------------------------

_slot = threading.Lock()
_volgende: dict[str, float] = {}  # host → vroegste tijdstip (monotonic) voor het volgende verzoek


def _wacht_op(host: str) -> None:
    """Reserveert een tijdvak voor deze host en slaapt tot het zover is (buiten het slot, zodat andere hosts doorgaan)."""
    with _slot:
        nu = time.monotonic()
        moment = max(nu, _volgende.get(host, 0.0))
        _volgende[host] = moment + _tussentijd()
    if moment > nu:
        time.sleep(moment - nu)


def _retry_after(r: httpx.Response) -> float | None:
    waarde = r.headers.get("retry-after")
    if not waarde:
        return None
    try:
        return max(0.0, float(waarde))
    except ValueError:
        pass
    try:
        return max(0.0, parsedate_to_datetime(waarde).timestamp() - time.time())
    except (TypeError, ValueError):
        return None


# --- validators (ETag / Last-Modified) -----------------------------------------------------

class Conditioneel:
    def __init__(self) -> None:
        self.gezien: dict[str, dict[str, str]] = {}


_actief: ContextVar[Conditioneel | None] = ContextVar("synoptikon_conditioneel", default=None)
_cache: dict[str, dict[str, str]] | None = None
_cache_slot = threading.Lock()
_vuil = False


def _cache_pad() -> Path:
    from ..config import settings
    return settings.data_dir / "http_validators.json"


def _validators() -> dict[str, dict[str, str]]:
    global _cache
    with _cache_slot:
        if _cache is None:
            try:
                _cache = json.loads(_cache_pad().read_text())
            except (OSError, ValueError):
                _cache = {}
        return _cache


@contextmanager
def conditioneel():
    c = Conditioneel()
    token = _actief.set(c)
    try:
        yield c
    finally:
        _actief.reset(token)


def bevestig(c: Conditioneel) -> None:
    """De validators van een geslaagde import onthouden (in het geheugen; `bewaar()` schrijft ze weg)."""
    global _vuil
    if not c.gezien:
        return
    v = _validators()
    with _cache_slot:
        v.update(c.gezien)
        _vuil = True


def vergeet(url: str) -> None:
    global _vuil
    v = _validators()
    with _cache_slot:
        if v.pop(url, None) is not None:
            _vuil = True


def bewaar() -> None:
    global _vuil
    if not _vuil or _cache is None:
        return
    pad = _cache_pad()
    with _cache_slot:
        tijdelijk = pad.with_suffix(".tmp")
        tijdelijk.write_text(json.dumps(_cache, separators=(",", ":")))
        tijdelijk.replace(pad)
        _vuil = False


# --- transport -------------------------------------------------------------------------

class Beleefd(httpx.BaseTransport):
    def __init__(self, onder: httpx.BaseTransport) -> None:
        self.onder = onder

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        cond = _actief.get() if request.method == "GET" else None
        url = str(request.url)
        if cond is not None:
            bekend = _validators().get(url) or {}
            if bekend.get("etag"):
                request.headers["If-None-Match"] = bekend["etag"]
            if bekend.get("last_modified"):
                request.headers["If-Modified-Since"] = bekend["last_modified"]
        pogingen = _pogingen()
        for poging in range(pogingen):
            _wacht_op(request.url.host)
            try:
                r = self.onder.handle_request(request)
            except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError):
                if poging == pogingen - 1:
                    raise
                time.sleep(min(_MAX_WACHT, 2 ** poging * 5 + random.random()))
                continue
            if r.status_code in _OPNIEUW and poging < pogingen - 1:
                wacht = _retry_after(r)
                if wacht is None:
                    wacht = 2 ** poging * 5 + random.random()
                if wacht > _MAX_WACHT:
                    return r
                r.close()
                time.sleep(wacht)
                continue
            if cond is not None:
                if r.status_code == 304:
                    r.close()
                    raise Ongewijzigd(url)
                if r.status_code == 200:
                    v = {k: r.headers[h] for k, h in (("etag", "etag"), ("last_modified", "last-modified")) if r.headers.get(h)}
                    if v:
                        cond.gezien[url] = v
            return r
        raise AssertionError("onbereikbaar")

    def close(self) -> None:
        self.onder.close()


def client(**kw) -> httpx.Client:
    kw.setdefault("timeout", 60.0)
    kw.setdefault("follow_redirects", True)
    kw.setdefault("headers", {"User-Agent": UA})
    kw["transport"] = Beleefd(kw.pop("transport", None) or httpx.HTTPTransport(retries=0))
    return httpx.Client(**kw)
