"""Vertalingen van eigen inhoud bekijken, nakijken en aanvullen."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..db import get_session
from ..i18n import BRONTAAL, TALEN, taal
from ..services import vertalen
from . import render

router = APIRouter()
PER_PAGINA = 20


@router.get("/vertalingen")
def overzicht(request: Request, doel: str = "", toon: str = "ontbrekend", pagina: int = 1, db: Session = Depends(get_session)):
    doel = doel if doel in vertalen.DOELTALEN else (taal() if taal() != BRONTAAL else "fr")
    items = vertalen.bronteksten(db)
    klaar = vertalen.vertalingen(db, doel)
    if toon == "ontbrekend":
        lijst = [b for b in items if b.hash not in klaar]
    elif toon == "machine":
        lijst = [b for b in items if b.hash in klaar and klaar[b.hash].herkomst != "eigen"]
    else:
        lijst = items
    paginas = max(1, -(-len(lijst) // PER_PAGINA))
    pagina = min(max(1, pagina), paginas)
    return render(
        request, "vertalingen.html", doel=doel, toon=toon, stand=vertalen.stand(db),
        items=lijst[(pagina - 1) * PER_PAGINA: pagina * PER_PAGINA], aantal=len(lijst), klaar=klaar,
        pagina=pagina, paginas=paginas, doeltalen=vertalen.DOELTALEN,
    )


@router.post("/vertalingen")
def opslaan(doel: str = Form(...), h: str = Form(...), tekst: str = Form(""), terug: str = Form("/vertalingen"),
            db: Session = Depends(get_session)):
    if doel not in TALEN or doel == BRONTAAL:
        raise HTTPException(400)
    bron = next((b for b in vertalen.bronteksten(db) if b.hash == h), None)
    if bron is None:
        raise HTTPException(404)
    vertalen.zet(db, doel, bron.tekst, tekst, "eigen")
    return RedirectResponse((terug if terug.startswith("/") else "/vertalingen") + f"#v-{h}", status_code=303)
