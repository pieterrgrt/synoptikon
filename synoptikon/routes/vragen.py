from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse, RedirectResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..db import get_session
from ..models import Antwoord, AntwoordBron, Begrip, Bron, Concordantie, Notitie, Stelsel, Vraag, VraagBegrip
from ..services import export
from ..services.helpers import actieve_stelsels, leeg_naar_none, unieke_slug
from . import render

router = APIRouter()


def _laad_vraag(db: Session, slug: str) -> Vraag:
    vraag = db.scalar(
        select(Vraag)
        .where(Vraag.slug == slug)
        .options(
            selectinload(Vraag.antwoorden).selectinload(Antwoord.bronnen).selectinload(AntwoordBron.bron).selectinload(Bron.vertalingen),
            selectinload(Vraag.antwoorden).selectinload(Antwoord.bronnen).selectinload(AntwoordBron.bron).selectinload(Bron.systematiek),
            selectinload(Vraag.antwoorden).selectinload(Antwoord.stelsel),
            selectinload(Vraag.begrippen).selectinload(VraagBegrip.begrip).selectinload(Begrip.relaties_uit),
            selectinload(Vraag.begrippen).selectinload(VraagBegrip.begrip).selectinload(Begrip.relaties_in),
            selectinload(Vraag.notities),
        )
    )
    if vraag is None:
        raise HTTPException(404, "Vraag niet gevonden")
    return vraag


def _concordanties_voor(db: Session, vraag: Vraag) -> list[Concordantie]:
    """Concordanties waarvan oud of nieuw nummer in een citeertitel van de vraag voorkomt."""
    alle = db.scalars(select(Concordantie)).all()
    citeertitels = {ab.bron.citeertitel for a in vraag.antwoorden for ab in a.bronnen}
    treffers = []
    for c in alle:
        for ct in citeertitels:
            if (c.nieuw and c.nieuw in ct and c.wet in ct) or (c.oud in ct and c.wet in ct):
                treffers.append(c)
                break
    return treffers


@router.get("/")
def index(request: Request, db: Session = Depends(get_session)):
    vragen = db.scalars(select(Vraag).order_by(Vraag.gewijzigd.desc()).options(selectinload(Vraag.antwoorden))).all()
    gebieden: dict[str, list[Vraag]] = {}
    for v in vragen:
        gebieden.setdefault(v.rechtsgebied or "Overig", []).append(v)
    return render(request, "index.html", gebieden=gebieden, aantal=len(vragen))


@router.get("/vragen/nieuw")
def vraag_nieuw(request: Request, db: Session = Depends(get_session)):
    return render(request, "vraag_form.html", vraag=None, stelsels=actieve_stelsels(db))


@router.post("/vragen/nieuw")
def vraag_maak(
    request: Request,
    titel: str = Form(...),
    omschrijving: str = Form(""),
    rechtsgebied: str = Form(""),
    tags: str = Form(""),
    db: Session = Depends(get_session),
):
    vraag = Vraag(
        titel=titel.strip(),
        slug=unieke_slug(db, titel),
        omschrijving=leeg_naar_none(omschrijving),
        rechtsgebied=leeg_naar_none(rechtsgebied),
        tags=leeg_naar_none(tags),
    )
    for st in actieve_stelsels(db):
        vraag.antwoorden.append(Antwoord(stelsel_code=st.code))
    db.add(vraag)
    db.flush()
    return RedirectResponse(f"/vragen/{vraag.slug}", status_code=303)


@router.get("/vragen/{slug}")
def synopse(request: Request, slug: str, vertaling: str | None = None, db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    stelsels = actieve_stelsels(db)
    # Alle bronnen, voor het koppelformulier; gegroepeerd per stelsel.
    alle_bronnen = db.scalars(select(Bron).order_by(Bron.stelsel_code, Bron.soort, Bron.citeertitel)).all()
    gekoppeld = {ab.bron_id for a in vraag.antwoorden for ab in a.bronnen}
    alle_begrippen = db.scalars(select(Begrip).order_by(Begrip.stelsel_code, Begrip.term)).all()
    gekoppelde_begrippen = {vb.begrip_id for vb in vraag.begrippen}
    return render(
        request,
        "synopse.html",
        vraag=vraag,
        stelsels=stelsels,
        vertaal_taal=vertaling,
        alle_bronnen=[b for b in alle_bronnen if b.id not in gekoppeld],
        alle_begrippen=[g for g in alle_begrippen if g.id not in gekoppelde_begrippen],
        concordanties=_concordanties_voor(db, vraag),
    )


@router.get("/vragen/{slug}/bewerken")
def vraag_bewerken(request: Request, slug: str, db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    return render(request, "vraag_form.html", vraag=vraag, stelsels=actieve_stelsels(db))


@router.post("/vragen/{slug}/bewerken")
def vraag_opslaan(
    request: Request,
    slug: str,
    titel: str = Form(...),
    omschrijving: str = Form(""),
    rechtsgebied: str = Form(""),
    tags: str = Form(""),
    db: Session = Depends(get_session),
):
    vraag = _laad_vraag(db, slug)
    vraag.titel = titel.strip()
    vraag.omschrijving = leeg_naar_none(omschrijving)
    vraag.rechtsgebied = leeg_naar_none(rechtsgebied)
    vraag.tags = leeg_naar_none(tags)
    # Zorg dat elk actief stelsel een (leeg) antwoord heeft.
    bestaand = {a.stelsel_code for a in vraag.antwoorden}
    for st in actieve_stelsels(db):
        if st.code not in bestaand:
            vraag.antwoorden.append(Antwoord(stelsel_code=st.code))
    return RedirectResponse(f"/vragen/{vraag.slug}", status_code=303)


@router.post("/vragen/{slug}/verwijderen")
def vraag_verwijderen(slug: str, db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    db.delete(vraag)
    return RedirectResponse("/", status_code=303)


@router.get("/vragen/{slug}/antwoord/{code}")
def antwoord_bewerken(request: Request, slug: str, code: str, db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    antwoord = vraag.antwoord_voor(code)
    if antwoord is None:
        stelsel = db.get(Stelsel, code)
        if stelsel is None:
            raise HTTPException(404)
        antwoord = Antwoord(vraag=vraag, stelsel_code=code)
        db.add(antwoord)
        db.flush()
    return render(request, "antwoord_form.html", vraag=vraag, antwoord=antwoord)


@router.post("/vragen/{slug}/antwoord/{code}")
def antwoord_opslaan(
    slug: str,
    code: str,
    kern: str = Form(""),
    analyse: str = Form(""),
    db: Session = Depends(get_session),
):
    vraag = _laad_vraag(db, slug)
    antwoord = vraag.antwoord_voor(code)
    if antwoord is None:
        antwoord = Antwoord(vraag=vraag, stelsel_code=code)
        db.add(antwoord)
    antwoord.kern = leeg_naar_none(kern)
    antwoord.analyse = leeg_naar_none(analyse)
    return RedirectResponse(f"/vragen/{slug}#{code}", status_code=303)


@router.post("/vragen/{slug}/bron/koppel")
def bron_koppel(
    slug: str,
    bron_id: int = Form(...),
    rol: str = Form(""),
    notitie: str = Form(""),
    db: Session = Depends(get_session),
):
    vraag = _laad_vraag(db, slug)
    bron = db.get(Bron, bron_id)
    if bron is None:
        raise HTTPException(404, "Bron niet gevonden")
    antwoord = vraag.antwoord_voor(bron.stelsel_code)
    if antwoord is None:
        antwoord = Antwoord(vraag=vraag, stelsel_code=bron.stelsel_code)
        db.add(antwoord)
        db.flush()
    if not any(ab.bron_id == bron.id for ab in antwoord.bronnen):
        antwoord.bronnen.append(
            AntwoordBron(bron=bron, rol=leeg_naar_none(rol), notitie=leeg_naar_none(notitie), volgorde=len(antwoord.bronnen))
        )
    return RedirectResponse(f"/vragen/{slug}#{bron.stelsel_code}", status_code=303)


@router.post("/vragen/{slug}/bron/{ab_id}/bewerken")
def bron_koppeling_bewerken(
    slug: str,
    ab_id: int,
    rol: str = Form(""),
    notitie: str = Form(""),
    volgorde: int = Form(0),
    db: Session = Depends(get_session),
):
    ab = db.get(AntwoordBron, ab_id)
    if ab is None or ab.antwoord.vraag.slug != slug:
        raise HTTPException(404)
    ab.rol = leeg_naar_none(rol)
    ab.notitie = leeg_naar_none(notitie)
    ab.volgorde = volgorde
    return RedirectResponse(f"/vragen/{slug}#{ab.antwoord.stelsel_code}", status_code=303)


@router.post("/vragen/{slug}/bron/{ab_id}/ontkoppel")
def bron_ontkoppel(slug: str, ab_id: int, db: Session = Depends(get_session)):
    ab = db.get(AntwoordBron, ab_id)
    if ab is None or ab.antwoord.vraag.slug != slug:
        raise HTTPException(404)
    code = ab.antwoord.stelsel_code
    db.delete(ab)
    return RedirectResponse(f"/vragen/{slug}#{code}", status_code=303)


@router.post("/vragen/{slug}/begrip/koppel")
def begrip_koppel(slug: str, begrip_id: int = Form(...), db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    if db.get(Begrip, begrip_id) is None:
        raise HTTPException(404)
    if not any(vb.begrip_id == begrip_id for vb in vraag.begrippen):
        vraag.begrippen.append(VraagBegrip(begrip_id=begrip_id))
    return RedirectResponse(f"/vragen/{slug}#begrippen", status_code=303)


@router.post("/vragen/{slug}/begrip/{begrip_id}/ontkoppel")
def begrip_ontkoppel(slug: str, begrip_id: int, db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    for vb in list(vraag.begrippen):
        if vb.begrip_id == begrip_id:
            db.delete(vb)
    return RedirectResponse(f"/vragen/{slug}#begrippen", status_code=303)


@router.post("/vragen/{slug}/notitie")
def notitie_toevoegen(slug: str, tekst: str = Form(...), stelsel_code: str = Form(""), db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    vraag.notities.append(Notitie(tekst=tekst.strip(), stelsel_code=leeg_naar_none(stelsel_code)))
    return RedirectResponse(f"/vragen/{slug}#notities", status_code=303)


@router.post("/vragen/{slug}/notitie/{notitie_id}/verwijderen")
def notitie_verwijderen(slug: str, notitie_id: int, db: Session = Depends(get_session)):
    n = db.get(Notitie, notitie_id)
    if n is None or n.vraag.slug != slug:
        raise HTTPException(404)
    db.delete(n)
    return RedirectResponse(f"/vragen/{slug}#notities", status_code=303)


# --- export ---------------------------------------------------------------


@router.get("/vragen/{slug}/export.md")
def export_md(slug: str, vertaling: str | None = "nl", db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    inhoud = export.vraag_naar_markdown(vraag, vertaal_taal=vertaling)
    return PlainTextResponse(
        inhoud,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{vraag.slug}.md"'},
    )


@router.get("/vragen/{slug}/print")
def print_weergave(request: Request, slug: str, vertaling: str | None = "nl", db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    return render(request, "print.html", vraag=vraag, vertaal_taal=vertaling, concordanties=_concordanties_voor(db, vraag), pdf=False)


@router.get("/vragen/{slug}/export.pdf")
def export_pdf(request: Request, slug: str, vertaling: str | None = "nl", db: Session = Depends(get_session)):
    vraag = _laad_vraag(db, slug)
    from ..main import templates

    html = templates.get_template("print.html").render(
        request=request, vraag=vraag, vertaal_taal=vertaling, concordanties=_concordanties_voor(db, vraag), pdf=True
    )
    try:
        pdf = export.html_naar_pdf(html, base_url=str(request.base_url))
    except RuntimeError as e:
        raise HTTPException(501, str(e))
    return Response(pdf, media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="{vraag.slug}.pdf"'})
