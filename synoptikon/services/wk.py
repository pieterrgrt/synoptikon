"""Wunderkammer meteen laten weten dat er kaarten veranderd zijn.

Wunderkammer haalt de kaarten elk halfuur op (cron). Bewaar je een artikel, neem je voorstellen over of zet je een lijst
uit, dan seint Synoptikon na de commit `POST <wk>/api/synoptikon/push` met hetzelfde token; Wunderkammer haalt dan op de
achtergrond `/api/wk/kaarten` op, zodat de kaart binnen enkele seconden in het dagpad staat. Mislukt het sein, dan doet
de cron het later alsnog; er gaat niets verloren.

Een paar wijzigingen kort na elkaar (een hele notitie overnemen) worden één sein: de timer wacht VERTRAGING seconden.
Wat Wunderkammer zelf terugmeldt (de stand) en oefenen in Synoptikon (gekend / nog niet) seinen niet.
"""
from __future__ import annotations

import logging
import threading

from sqlalchemy import event, inspect
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Kaart, Leerlijst

log = logging.getLogger(__name__)

VERTRAGING = 2.0  # seconden
# Velden die voor Wunderkammer niets veranderen.
_STIL = {"gekend", "geoefend", "gewijzigd", "stand", "aangemaakt", "kaarten"}

_lock = threading.Lock()
_timer: threading.Timer | None = None


def push_url() -> str:
    return settings.wk_push_url or f"{settings.wk_url}/api/synoptikon/push"


def aan() -> bool:
    return settings.wk_ingesteld and settings.wk_push


def meld() -> None:
    """Over VERTRAGING seconden seinen; een nieuwe melding in de tussentijd schuift het op."""
    global _timer
    if not aan():
        return
    with _lock:
        if _timer is not None:
            _timer.cancel()
        _timer = threading.Timer(VERTRAGING, stuur)
        _timer.daemon = True
        _timer.start()


def stuur() -> bool:
    import httpx

    try:
        r = httpx.post(push_url(), headers={"Authorization": f"Bearer {settings.wk_token}"}, json={}, timeout=10.0)
        if r.status_code >= 400:
            log.info("Wunderkammer antwoordt %s op het sein", r.status_code)
            return False
        return True
    except httpx.HTTPError as e:
        log.info("Wunderkammer niet bereikt (%s); de cron haalt de kaarten later op", e)
        return False


def _veranderd(obj) -> bool:
    staat = inspect(obj)
    return any(a.history.has_changes() for a in staat.attrs if a.key not in _STIL)


@event.listens_for(Session, "after_flush")
def _na_flush(session: Session, _context) -> None:
    if session.info.get("wk_stil"):
        return
    for obj in (*session.new, *session.deleted):
        if isinstance(obj, (Kaart, Leerlijst)):
            session.info["wk_meld"] = True
            return
    for obj in session.dirty:
        if isinstance(obj, (Kaart, Leerlijst)) and _veranderd(obj):
            session.info["wk_meld"] = True
            return


@event.listens_for(Session, "after_commit")
def _na_commit(session: Session) -> None:
    if session.info.pop("wk_meld", False):
        meld()


@event.listens_for(Session, "after_rollback")
def _na_rollback(session: Session) -> None:
    session.info.pop("wk_meld", None)
