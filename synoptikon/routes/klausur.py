"""Klausurtrainer (`/klausur`): casussen, het werkblad, de beoordeling en wat je steeds mist (services/klausur.py).

Ook een lezer oefent hier (main._LEZER_POST): eigen casussen, pogingen, beoordelingen en kaartvoorstellen zijn eigen
spullen. Een voorbeeldcasus (`profiel_id` leeg) is gedeelde inhoud: bewerken alleen door een beheerder, een Musterlösung
laten schrijven alleen door een redacteur.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..auth import huidig_profiel, mag_bewerken
from ..db import get_session
from ..i18n import _, taal as interfacetaal
from ..models import ANSPRUCHSGRUPPEN, CASUS_NIVEAUS, Casus, CasusPoging, CasusProbleem
from ..services import claude, klausur
from ..services.vakken import VAKKEN
from . import render

router = APIRouter()


def _pid(request: Request) -> int:
    p = huidig_profiel(request)
    return p.id if p is not None else 1


def _casus(request: Request, db: Session, cid: int, eigen: bool = False) -> Casus:
    c = klausur.van(db, _pid(request), cid)
    if c is None or (eigen and c.profiel_id is None and not _beheerder(request)):
        raise HTTPException(404)
    return c


def _beheerder(request: Request) -> bool:
    p = huidig_profiel(request)
    return p is None or p.is_beheerder


def _poging(request: Request, db: Session, pid: int) -> CasusPoging:
    p = klausur.poging(db, _pid(request), pid)
    if p is None:
        raise HTTPException(404)
    return p


def _fetch(request: Request) -> bool:
    return request.headers.get("x-requested-with") == "fetch"


@router.get("/klausur")
def overzicht(request: Request, db: Session = Depends(get_session)):
    pid = _pid(request)
    alle = klausur.pogingen(db, pid)
    laatste: dict[int, CasusPoging] = {}
    for p in alle:  # nieuwste eerst
        laatste.setdefault(p.casus_id, p)
    return render(request, "klausur.html", casussen=klausur.casussen(db, pid), lopend=[p for p in alle if p.open], laatste=laatste,
                  rest={p.id: klausur.rest_seconden(p) for p in alle if p.open}, gemist=len(klausur.steeds_gemist(db, pid)),
                  note=klausur.note, claude_aan=claude.beschikbaar())


@router.get("/klausur/nieuw")
def nieuw(request: Request, onderwerp: str = "", normen: str = "", vak: str = ""):
    return render(request, "klausur_nieuw.html", niveaus=CASUS_NIVEAUS, vakken=VAKKEN, claude_aan=claude.beschikbaar(),
                  onderwerp=onderwerp[:200], normen=normen[:500], vak=vak[:60])


@router.post("/klausur/nieuw")
def nieuw_opslaan(request: Request, titel: str = Form(""), sachverhalt: str = Form(""), fallfrage: str = Form(""), niveau: str = Form("ag"),
                  vak: str = Form(""), onderwerp: str = Form(""), normen: str = Form(""), db: Session = Depends(get_session)):
    if not sachverhalt.strip():
        return render(request, "klausur_nieuw.html", status_code=400, niveaus=CASUS_NIVEAUS, vakken=VAKKEN, claude_aan=claude.beschikbaar(),
                      onderwerp=onderwerp, normen=normen, vak=vak, fout=_("Plak eerst een Sachverhalt."))
    c = klausur.maak(db, _pid(request), titel, sachverhalt, fallfrage, niveau, vak, onderwerp, normen)
    return RedirectResponse(f"/klausur/{c.id}", status_code=303)


@router.post("/klausur/genereer")
def genereer(request: Request, onderwerp: str = Form(""), niveau: str = Form("ag"), vak: str = Form(""), normen: str = Form(""),
             aanwijzing: str = Form(""), db: Session = Depends(get_session)):
    if not claude.beschikbaar():
        raise HTTPException(503, _("Claude staat uit op deze installatie."))
    if not onderwerp.strip():
        return render(request, "klausur_nieuw.html", status_code=400, niveaus=CASUS_NIVEAUS, vakken=VAKKEN, claude_aan=True,
                      onderwerp=onderwerp, normen=normen, vak=vak, fout=_("Geef een onderwerp op."))
    c = klausur.genereer(db, _pid(request), onderwerp, niveau, vak, normen, aanwijzing, interfacetaal())
    return RedirectResponse(f"/klausur/{c.id}", status_code=303)


@router.get("/klausur/problemen")
def problemen(request: Request, db: Session = Depends(get_session)):
    return render(request, "klausur_problemen.html", gemist=klausur.steeds_gemist(db, _pid(request)))


@router.post("/klausur/probleem/{prid}/kaart")
def probleem_kaart(request: Request, prid: int, terug: str = Form(""), db: Session = Depends(get_session)):
    """Eén tik: van een gemist probleem een kaartvoorstel maken."""
    pr = db.get(CasusProbleem, prid)
    if pr is None or pr.profiel_id != _pid(request):
        raise HTTPException(404)
    k = klausur.kaartvoorstel(db, pr)
    if _fetch(request):
        return JSONResponse({"ok": k is not None, "kaart": k.id if k else None, "lijst": k.lijst_id if k else None})
    terug = terug if terug.startswith("/klausur") else f"/klausur/poging/{pr.poging_id}"
    return RedirectResponse(f"{terug}{'&' if '?' in terug else '?'}voorstel={k.lijst_id if k else 0}#pr-{pr.id}", status_code=303)


@router.get("/klausur/wet")
def wet(request: Request, q: str = "", fragment: int = 0, db: Session = Depends(get_session)):
    """De wettekst voor het werkblad, zonder eigen aantekeningen. `fragment=1`: alleen het blok (voor het paneel)."""
    return render(request, "_klausur_wet.html" if fragment else "klausur_wet.html", w=klausur.wet(db, q))


# --- een poging ---------------------------------------------------------------------------------------------------------


@router.get("/klausur/poging/{pid}")
def poging(request: Request, pid: int, db: Session = Depends(get_session)):
    p = _poging(request, db, pid)
    c = p.casus
    k = klausur.Koppelaar(db)
    if p.open:
        return render(request, "klausur_poging.html", p=p, c=c, rest=klausur.rest_seconden(p), sachverhalt=k.md(c.sachverhalt),
                      fallfrage=k.md(c.fallfrage), groepen=ANSPRUCHSGRUPPEN)
    tekst = f"{p.skizze}\n{p.uitwerking}"
    return render(request, "klausur_resultaat.html", p=p, c=c, w=klausur.weergave(db, p), volgorde=klausur.volgorde(p.skizze),
                  genoemd=klausur.genoemde_normen(db, tekst), stijl=klausur.stijl_telling(p.uitwerking), duur=klausur.duur_minuten(p),
                  skizze_html=k.md(p.skizze), uitwerking_html=k.md(p.uitwerking), sachverhalt=k.md(c.sachverhalt), fallfrage=k.md(c.fallfrage),
                  verwacht=klausur.toon_skizze(db, c.skizze), claude_aan=claude.beschikbaar(), oordeel=klausur.oordeel)


@router.post("/klausur/poging/{pid}/bewaar")
def bewaar(request: Request, pid: int, skizze: str = Form(""), uitwerking: str = Form(""), revisie: str = Form(""),
           db: Session = Depends(get_session)):
    """Tussentijds bewaren. Vanuit JavaScript (autosave): JSON met het nieuwe revisienummer en de resterende tijd."""
    p = _poging(request, db, pid)
    try:
        nieuw = klausur.bewaar(p, skizze, uitwerking, int(revisie) if revisie.isdigit() and _fetch(request) else None)
    except klausur.Conflict:
        return JSONResponse({"ok": False, "conflict": True, "revisie": p.revisie}, status_code=409)
    except ValueError as e:
        if _fetch(request):
            return JSONResponse({"ok": False, "ingeleverd": True, "melding": str(e)}, status_code=409)
        return RedirectResponse(f"/klausur/poging/{pid}", status_code=303)
    if _fetch(request):
        return JSONResponse({"ok": True, "revisie": nieuw, "rest": klausur.rest_seconden(p)})
    return RedirectResponse(f"/klausur/poging/{pid}?bewaard_op=1", status_code=303)


@router.post("/klausur/poging/{pid}/inleveren")
def inleveren(request: Request, pid: int, skizze: str = Form(None), uitwerking: str = Form(None), db: Session = Depends(get_session)):
    p = _poging(request, db, pid)
    if p.open:
        if skizze is not None or uitwerking is not None:
            klausur.bewaar(p, skizze, uitwerking)
        klausur.lever_in(p)
    return RedirectResponse(f"/klausur/poging/{pid}", status_code=303)


@router.post("/klausur/poging/{pid}/beoordeel")
def beoordeel(request: Request, pid: int, db: Session = Depends(get_session)):
    p = _poging(request, db, pid)
    if not claude.beschikbaar():
        raise HTTPException(503, _("Claude staat uit op deze installatie."))
    if p.status not in ("wacht", "beoordelen"):
        try:
            klausur.beoordeel(db, p, interfacetaal())
        except ValueError as e:
            p.fout = str(e)
    return RedirectResponse(f"/klausur/poging/{pid}#beoordeling", status_code=303)


@router.get("/klausur/poging/{pid}/stand")
def stand(request: Request, pid: int, db: Session = Depends(get_session)):
    """Het blok met de beoordeling (de pagina vraagt het op zolang Claude bezig is)."""
    p = _poging(request, db, pid)
    return render(request, "_klausur_beoordeling.html", p=p, c=p.casus, w=klausur.weergave(db, p), claude_aan=claude.beschikbaar(),
                  oordeel=klausur.oordeel)


@router.post("/klausur/poging/{pid}/verwijder")
def poging_weg(request: Request, pid: int, db: Session = Depends(get_session)):
    p = _poging(request, db, pid)
    cid = p.casus_id
    db.delete(p)
    return RedirectResponse(f"/klausur/{cid}", status_code=303)


# --- een casus ----------------------------------------------------------------------------------------------------------


@router.get("/klausur/{cid}")
def casus(request: Request, cid: int, db: Session = Depends(get_session)):
    c = _casus(request, db, cid)
    pid = _pid(request)
    k = klausur.Koppelaar(db)
    eigen = [p for p in c.pogingen if p.profiel_id == pid]
    for p in eigen:
        klausur.sluit_als_tijd_om(p)
    return render(request, "klausur_casus.html", c=c, pogingen=list(reversed(eigen)), sachverhalt=k.md(c.sachverhalt), fallfrage=k.md(c.fallfrage),
                  normen=k.normen(c.normen), niveaus=CASUS_NIVEAUS, vakken=VAKKEN, note=klausur.note, claude_aan=claude.beschikbaar(),
                  mag_wijzigen=c.profiel_id == pid or _beheerder(request))


@router.get("/klausur/{cid}/stand")
def casus_stand(request: Request, cid: int, db: Session = Depends(get_session)):
    c = _casus(request, db, cid)
    k = klausur.Koppelaar(db)
    return render(request, "_klausur_sachverhalt.html", c=c, sachverhalt=k.md(c.sachverhalt), fallfrage=k.md(c.fallfrage), normen=k.normen(c.normen),
                  claude_aan=claude.beschikbaar())


@router.post("/klausur/{cid}/start")
def start(request: Request, cid: int, modus: str = Form("oefenen"), limiet: str = Form(""), db: Session = Depends(get_session)):
    c = _casus(request, db, cid)
    if c.status != "klaar" or not c.sachverhalt:
        raise HTTPException(409, _("Deze casus is nog niet klaar."))
    p = klausur.start(db, _pid(request), c, modus, int(limiet) if limiet.isdigit() and int(limiet) > 0 else None)
    return RedirectResponse(f"/klausur/poging/{p.id}", status_code=303)


@router.post("/klausur/{cid}/bewerk")
def bewerk(request: Request, cid: int, titel: str = Form(""), sachverhalt: str = Form(""), fallfrage: str = Form(""), niveau: str = Form("ag"),
           vak: str = Form(""), onderwerp: str = Form(""), normen: str = Form(""), db: Session = Depends(get_session)):
    c = _casus(request, db, cid, eigen=True)
    c.titel = titel.strip()[:200] or c.titel
    if sachverhalt.strip():
        c.sachverhalt = sachverhalt.strip()[:klausur.MAX_TEKST]
    c.fallfrage = fallfrage.strip() or None
    c.niveau = niveau if niveau in CASUS_NIVEAUS else c.niveau
    c.vak, c.onderwerp = vak.strip()[:60] or None, onderwerp.strip()[:200] or None
    c.normen = klausur.lees_normen(normen)
    return RedirectResponse(f"/klausur/{cid}", status_code=303)


@router.post("/klausur/{cid}/opnieuw")
def opnieuw(request: Request, cid: int, db: Session = Depends(get_session)):
    """Een mislukte casus van Claude opnieuw laten schrijven."""
    c = _casus(request, db, cid, eigen=True)
    if c.herkomst == "claude" and c.status == "fout" and claude.beschikbaar():
        c.status, c.fout = "wacht", None
        db.commit()
        klausur._in_thread(klausur._genereer, c.id, interfacetaal(), db)
    return RedirectResponse(f"/klausur/{cid}", status_code=303)


@router.post("/klausur/{cid}/verwijder")
def verwijder(request: Request, cid: int, db: Session = Depends(get_session)):
    c = _casus(request, db, cid, eigen=True)
    if c.profiel_id is None:  # een voorbeeldcasus verdwijnt niet via de pagina (de seed zet haar terug)
        raise HTTPException(403)
    db.delete(c)
    return RedirectResponse("/klausur", status_code=303)


@router.post("/klausur/{cid}/goedkeuren")
def goedkeuren(request: Request, cid: int, aan: str = Form("1"), db: Session = Depends(get_session)):
    """De Lösungsskizze en Musterlösung zijn nagekeken (of toch niet: `aan=0`)."""
    c = _casus(request, db, cid, eigen=True)
    c.geverifieerd = aan == "1"
    return RedirectResponse(f"/klausur/{cid}/muster", status_code=303)


@router.get("/klausur/{cid}/muster")
def muster(request: Request, cid: int, db: Session = Depends(get_session)):
    c = _casus(request, db, cid)
    pid = _pid(request)
    return render(request, "klausur_muster.html", c=c, verwacht=klausur.toon_skizze(db, c.skizze),
                  muster_html=klausur.Koppelaar(db).md(c.musterloesung), claude_aan=claude.beschikbaar(),
                  ingeleverd=any(p.profiel_id == pid and not p.open for p in c.pogingen), mag_wijzigen=c.profiel_id == pid or _beheerder(request))


@router.get("/klausur/{cid}/muster/stand")
def muster_stand(request: Request, cid: int, db: Session = Depends(get_session)):
    c = _casus(request, db, cid)
    return render(request, "_klausur_muster.html", c=c, muster_html=klausur.Koppelaar(db).md(c.musterloesung), claude_aan=claude.beschikbaar())


@router.post("/klausur/{cid}/muster")
def muster_maak(request: Request, cid: int, db: Session = Depends(get_session)):
    c = _casus(request, db, cid)
    if c.profiel_id is None and not mag_bewerken(request):
        raise HTTPException(403)
    if not claude.beschikbaar():
        raise HTTPException(503, _("Claude staat uit op deze installatie."))
    if c.muster_status not in ("wacht", "bezig"):
        klausur.muster(db, c, interfacetaal())
    return RedirectResponse(f"/klausur/{cid}/muster", status_code=303)
