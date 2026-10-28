"""Unierecht: catalogus, handeling met haar werking en omzetting, en de omzettingsmatrix.

`/eu` doorzoekt en filtert de geldende verordeningen en richtlijnen, met het
repertorium als inhoudsopgave. `/eu/<celex>` toont wat de handeling is
(art. 288 VWEU), wat dat betekent per stelsel, welke nationale maatregelen
de lidstaten meldden en waar zij op artikelniveau in het nationale recht
staat. `/eu/omzetting` is de matrix handeling × stelsel.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..db import get_session
from ..i18n import _
from ..models import EU_SOORTEN, EU_VARIANTEN, OMZETTING_SOORTEN, Omzetting, Stelsel
from ..services import correspondentie as corr
from ..services import eu
from ..services.artikelen import lees
from ..services.eu_logica import status
from ..services.helpers import actieve_stelsels, leeg_naar_none, stelsels_per_code
from . import render

router = APIRouter()

STELSELS_EU = ["NL", "BE", "FR", "IT", "ES", "DE", "EN", "CH"]  # volgorde van de kolommen: rechtsfamilies


@router.get("/eu")
def overzicht(request: Request, q: str = "", soort: str = "", variant: str = "", rubriek: str = "", omgezet: str = "", pagina: int = 1,
              db: Session = Depends(get_session)):
    pagina = max(pagina, 1)
    handelingen, totaal = eu.zoek(db, q, soort, variant, rubriek, bool(omgezet), pagina)
    hoofdstukken, kinderen, tellingen = eu.repertorium_boom(db)
    return render(
        request, "eu.html", q=q, f_soort=soort, f_variant=variant, f_rubriek=rubriek, f_omgezet=bool(omgezet),
        handelingen=handelingen, totaal=totaal, pagina=pagina, paginas=max((totaal + 49) // 50, 1),
        hoofdstukken=hoofdstukken, kinderen=kinderen, tellingen=tellingen, rubriekpad=eu.rubriek_pad(db, rubriek) if rubriek else [],
        EU_SOORTEN=EU_SOORTEN, EU_VARIANTEN=EU_VARIANTEN,
    )


@router.get("/eu/omzetting")
def matrix(request: Request, db: Session = Depends(get_session)):
    handelingen, per = eu.omzettingsmatrix(db)
    per_code = stelsels_per_code(db)
    kolommen = [per_code[c] for c in STELSELS_EU if c in per_code]
    return render(request, "eu_omzetting.html", handelingen=handelingen, per=per, kolommen=kolommen)


@router.get("/eu/{celex}")
def detail(request: Request, celex: str, db: Session = Depends(get_session)):
    h = eu.handeling(db, celex.upper())
    if h is None:
        raise HTTPException(404, _("Handeling niet in de catalogus (synoptikon eu-catalogus)"))
    nims = eu.nims_per_stelsel(h)
    eigen: dict[str, list[Omzetting]] = {}
    for o in h.omzettingen:
        eigen.setdefault(o.stelsel_code, []).append(o)
    st = status(h, {k: len(v) for k, v in nims.items()}, {k: len(v) for k, v in eigen.items()})
    ctx = corr.Context(db)
    paden = {o.id: ctx.pad(o.ref) for o in h.omzettingen if o.nummer}
    per_code = stelsels_per_code(db)
    return render(
        request, "eu_handeling.html", h=h, st=st, nims=nims, eigen=eigen, paden=paden, per_code=per_code,
        kolommen=[c for c in STELSELS_EU if c in per_code], rubrieken=[eu.rubriek_pad(db, c) for c in h.rep_codes],
        OMZETTING_SOORTEN=OMZETTING_SOORTEN, EU_VARIANTEN=EU_VARIANTEN, stelsels=actieve_stelsels(db),
    )


@router.post("/eu/{celex}/omzetting")
def omzetting_maak(
    celex: str,
    stelsel_code: str = Form(...),
    verwijzing: str = Form(""),
    wet_titel: str = Form(""),
    eu_artikel: str = Form(""),
    soort: str = Form("omzetting"),
    opmerking: str = Form(""),
    db: Session = Depends(get_session),
):
    h = eu.handeling(db, celex.upper())
    if h is None or db.get(Stelsel, stelsel_code) is None:
        raise HTTPException(404)
    ref = lees(stelsel_code, verwijzing) if verwijzing.strip() else None
    if verwijzing.strip() and (ref is None or ref.nummer is None):
        raise HTTPException(400, _("Kan '{verwijzing}' niet lezen als artikel uit {stelsel}", verwijzing=verwijzing, stelsel=stelsel_code))
    if ref is None and not wet_titel.strip():
        raise HTTPException(400, _("Geef een artikel of de titel van de wet"))
    volgorde = max([o.volgorde for o in h.omzettingen] or [0]) + 10
    h.omzettingen.append(Omzetting(
        stelsel_code=stelsel_code, wet=ref.wet if ref else None, nummer=ref.nummer if ref else None, tot=ref.tot if ref else None,
        wet_titel=leeg_naar_none(wet_titel), eu_artikel=leeg_naar_none(eu_artikel), soort=soort if soort in OMZETTING_SOORTEN else "omzetting",
        opmerking=leeg_naar_none(opmerking), geverifieerd=True, volgorde=volgorde,
    ))
    return RedirectResponse(f"/eu/{h.celex}#omzetting", status_code=303)


@router.post("/eu/{celex}/omzetting/{oid}/geverifieerd")
def omzetting_verifieer(celex: str, oid: int, db: Session = Depends(get_session)):
    o = db.get(Omzetting, oid)
    if o is None or o.celex != celex.upper():
        raise HTTPException(404)
    o.geverifieerd = not o.geverifieerd
    return RedirectResponse(f"/eu/{o.celex}#omzetting", status_code=303)


@router.post("/eu/{celex}/omzetting/{oid}/verwijderen")
def omzetting_verwijderen(celex: str, oid: int, db: Session = Depends(get_session)):
    o = db.get(Omzetting, oid)
    if o and o.celex == celex.upper():
        db.delete(o)
    return RedirectResponse(f"/eu/{celex.upper()}#omzetting", status_code=303)
