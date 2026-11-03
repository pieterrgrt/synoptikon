"""Leessets (`/leren/sets`): artikelen, uitspraken en notities die je samen leest (services/leessets.py).

Onder /leren, zodat ook een lezer zijn eigen sets bijhoudt (main._LEZER_POST). Deze router staat vóór die van leren,
anders vangt `/leren/{lid}` het pad.
"""
from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import huidig_profiel
from ..db import get_session
from ..i18n import _
from ..models import Bron, Leesset, Stelsel
from ..services import leessets
from ..services.artikelen import Ref
from ..services.helpers import actieve_stelsels
from ..services.vakken import VAKKEN
from . import render

router = APIRouter()


def _pid(request: Request) -> int:
    p = huidig_profiel(request)
    return p.id if p is not None else 1


def _set(request: Request, db: Session, sid: int) -> Leesset:
    s = db.get(Leesset, sid)
    if s is None or s.profiel_id != _pid(request):
        raise HTTPException(404)
    return s


def _veilig(terug: str) -> str:
    return terug if terug.startswith("/") and not terug.startswith("//") else ""


def _vakken(sets: list[Leesset]) -> list[str]:
    return sorted({*VAKKEN, *(s.vak for s in sets if s.vak)})


@router.get("/leren/sets")
def overzicht(request: Request, db: Session = Depends(get_session)):
    sets = leessets.van(db, _pid(request))
    return render(request, "leessets.html", sets=sets, vakken=_vakken(sets))


@router.post("/leren/sets")
async def maak(request: Request, db: Session = Depends(get_session)):
    """Een nieuwe set; met `artikel` (stelsel|wet|nummer, herhaald) meteen gevuld, bijvoorbeeld uit een thema op /bewaard."""
    form = await request.form()
    s = leessets.maak(db, _pid(request), str(form.get("naam", "")), str(form.get("vak", "")), str(form.get("omschrijving", "")))
    for a in form.getlist("artikel"):
        stelsel, _s, rest = str(a).partition("|")
        wet, _s, nummer = rest.partition("|")
        if stelsel and nummer:
            leessets.voeg_toe(db, s, ref=Ref(stelsel, nummer, wet or None))
    return RedirectResponse(f"/leren/sets/{s.id}", status_code=303)


@router.get("/leren/sets/kies")
def kies(request: Request, stelsel: str = "", wet: str = "", nummer: str = "", bron: int | None = None, terug: str = "",
         db: Session = Depends(get_session)):
    """Vanaf een artikel of uitspraak: in welke leesset, en waarom."""
    b = db.get(Bron, bron) if bron else None
    ref = Ref(stelsel.upper(), nummer, wet or None) if stelsel and nummer else None
    if ref is None and b is None:
        raise HTTPException(400)
    sets = leessets.van(db, _pid(request))
    return render(request, "leesset_kies.html", sets=sets, ref=ref, bron=b, terug=_veilig(terug), vakken=_vakken(sets))


@router.post("/leren/sets/toevoegen")
def toevoegen(request: Request, leesset: str = Form(""), naam: str = Form(""), vak: str = Form(""), stelsel: str = Form(""),
              wet: str = Form(""), nummer: str = Form(""), bron: str = Form(""), reden: str = Form(""), terug: str = Form(""),
              db: Session = Depends(get_session)):
    b = db.get(Bron, int(bron)) if bron.isdigit() else None
    ref = Ref(stelsel.upper(), nummer, wet or None) if stelsel and nummer else None
    if ref is None and b is None:
        raise HTTPException(400)
    s = _set(request, db, int(leesset)) if leesset.isdigit() else leessets.maak(db, _pid(request), naam, vak)
    leessets.voeg_toe(db, s, ref=ref, bron=b, reden=reden)
    return RedirectResponse(_veilig(terug) or f"/leren/sets/{s.id}", status_code=303)


@router.get("/leren/sets/{sid}")
def leesset(request: Request, sid: int, db: Session = Depends(get_session)):
    s = _set(request, db, sid)
    families = {c: f for c, f in db.execute(select(Stelsel.code, Stelsel.familie)).all()}
    return render(request, "leesset.html", s=s, onderdelen=leessets.lezen(db, s), families=families,
                  vakken=_vakken(leessets.van(db, _pid(request))), stelsels=actieve_stelsels(db))


@router.post("/leren/sets/{sid}")
def opslaan(request: Request, sid: int, naam: str = Form(...), vak: str = Form(""), omschrijving: str = Form(""),
            db: Session = Depends(get_session)):
    s = _set(request, db, sid)
    s.naam = naam.strip()[:120] or s.naam
    s.vak = vak.strip()[:60] or None
    s.omschrijving = omschrijving.strip() or None
    return RedirectResponse(f"/leren/sets/{sid}", status_code=303)


@router.post("/leren/sets/{sid}/verwijder")
def set_verwijderen(request: Request, sid: int, db: Session = Depends(get_session)):
    db.delete(_set(request, db, sid))
    return RedirectResponse("/leren/sets", status_code=303)


@router.post("/leren/sets/{sid}/onderdeel")
def onderdeel_erbij(request: Request, sid: int, invoer: str = Form(""), stelsel: str = Form(""), notitie: str = Form(""),
                    reden: str = Form(""), db: Session = Depends(get_session)):
    """Een artikel ('§ 929 BGB') of een eigen notitie achteraan erbij."""
    s = _set(request, db, sid)
    if invoer.strip():
        ref = leessets.lees_invoer(invoer, stelsel or None)
        if ref is None:
            return RedirectResponse(f"/leren/sets/{sid}?niet={quote(invoer.strip()[:80])}#erbij", status_code=303)
        leessets.voeg_toe(db, s, ref=ref, reden=reden)
    elif notitie.strip():
        leessets.voeg_toe(db, s, notitie=notitie, reden=reden)
    return RedirectResponse(f"/leren/sets/{sid}#erbij", status_code=303)


@router.post("/leren/sets/{sid}/onderdeel/{oid}")
def onderdeel_bewerk(request: Request, sid: int, oid: int, actie: str = Form(""), reden: str = Form(""),
                     notitie: str = Form(""), db: Session = Depends(get_session)):
    """Reden (of notitietekst) opslaan, omhoog, omlaag, of eruit."""
    s = _set(request, db, sid)
    o = next((o for o in s.onderdelen if o.id == oid), None)
    if o is None:
        raise HTTPException(404)
    if actie == "omhoog":
        leessets.verplaats(s, oid, -1)
    elif actie == "omlaag":
        leessets.verplaats(s, oid, 1)
    elif actie == "verwijder":
        leessets.verwijder(db, s, oid)
        return RedirectResponse(f"/leren/sets/{sid}", status_code=303)
    else:
        o.reden = reden.strip() or None
        if o.soort == "notitie" and notitie.strip():
            o.notitie = notitie.strip()
    return RedirectResponse(f"/leren/sets/{sid}#o{oid}", status_code=303)


@router.post("/leren/sets/{sid}/kaarten")
def kaarten(request: Request, sid: int, db: Session = Depends(get_session)):
    """Eén tik: de set wordt kaarten in de leerlijst van het vak."""
    s = _set(request, db, sid)
    lijst, nieuw = leessets.naar_kaarten(db, s)
    return RedirectResponse(f"/leren/{lijst.id}?uit_set={nieuw}", status_code=303)
