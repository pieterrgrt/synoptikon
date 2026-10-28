"""Leren: leerlijsten met kaarten bij artikelen en arresten, oefenen, en de koppeling met Wunderkammer.

Elke lijst hoort bij één profiel; ook een lezer mag zijn eigen lijsten bijhouden (zie main._LEZER_POST).
"""
from __future__ import annotations

import json
from datetime import date
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..auth import huidig_profiel
from ..db import get_session
from ..i18n import _
from ..models import ARRESTSOORTEN, ARTIKELSOORTEN, KAARTSOORTEN, Bron, Kaart, Leerlijst
from ..services import leren
from ..services.artikelen import Ref, herken
from ..services.correspondentie import thema_s_voor, wettekst_artikel
from ..services.helpers import actieve_stelsels, leeg_naar_none
from . import render

router = APIRouter()

# Vakken uit Wunderkammer (Jura, WiSe 2026/27) als suggestie; eigen vakken komen erbij.
VAKKEN = ("ZR Ia", "W", "GÖ", "UG", "Sachenrecht")


def _pid(request: Request) -> int:
    p = huidig_profiel(request)
    return p.id if p is not None else 1


def _lijst(request: Request, db: Session, lid: int) -> Leerlijst:
    lijst = db.get(Leerlijst, lid)
    if lijst is None or lijst.profiel_id != _pid(request):
        raise HTTPException(404)
    return lijst


def _kaart(request: Request, db: Session, kid: int) -> Kaart:
    k = db.get(Kaart, kid)
    if k is None or k.lijst.profiel_id != _pid(request):
        raise HTTPException(404)
    return k


def _datum(s: str) -> date | None:
    try:
        return date.fromisoformat(s.strip()) if s.strip() else None
    except ValueError:
        return None


def _veilig(terug: str, anders: str) -> str:
    return terug if terug.startswith("/") and not terug.startswith("//") else anders


def _vakken(lijsten: list[Leerlijst]) -> list[str]:
    return sorted({*VAKKEN, *(l.vak for l in lijsten if l.vak)})


@router.get("/leren")
def overzicht(request: Request, db: Session = Depends(get_session)):
    lijsten = leren.lijsten_van(db, _pid(request))
    return render(request, "leren.html", lijsten=lijsten, vakken=_vakken(lijsten), vandaag=date.today())


@router.post("/leren")
def lijst_maak(request: Request, naam: str = Form(...), vak: str = Form(""), examen: str = Form(""), omschrijving: str = Form(""),
               db: Session = Depends(get_session)):
    lijst = Leerlijst(profiel_id=_pid(request), naam=naam.strip()[:120] or _("Nieuwe lijst"), vak=leeg_naar_none(vak),
                      examen=_datum(examen), omschrijving=leeg_naar_none(omschrijving))
    db.add(lijst)
    db.flush()
    return RedirectResponse(f"/leren/{lijst.id}", status_code=303)


@router.get("/leren/nieuw")
def nieuw(request: Request, stelsel: str = "", wet: str = "", nummer: str = "", artikel: str = "", bron: int | None = None,
          lijst: int | None = None, terug: str = "", db: Session = Depends(get_session)):
    """Kaarten maken bij een artikel, een arrest (bron) of vrij."""
    ref = None
    if stelsel and nummer:
        ref = Ref(stelsel.upper(), nummer, wet or None)
    elif artikel.strip():
        refs = herken(artikel, stelsel.upper() or None)
        ref = refs[0] if refs else None
    b = db.get(Bron, bron) if bron else None
    wa = wettekst_artikel(db, ref) if ref else None
    lijsten = leren.lijsten_van(db, _pid(request))
    # Tegenhangers: de stelsels die in de thema's van dit artikel voorkomen.
    doelen = []
    if ref:
        codes = {a.stelsel_code for c, _e in thema_s_voor(db, ref.stelsel, ref.nummer, ref.wet) for a in c.artikelen}
        doelen = [s for s in actieve_stelsels(db) if s.code in codes and s.code != ref.stelsel]
    return render(
        request,
        "kaart_nieuw.html",
        ref=ref,
        wa=wa,
        bron=b,
        lijsten=lijsten,
        gekozen=lijst or (lijsten[0].id if len(lijsten) == 1 else None),
        doelen=doelen,
        vakken=_vakken(lijsten),
        terug=_veilig(terug, ref.url if ref and ref.url else "/leren"),
        soorten=KAARTSOORTEN,
        artikelsoorten=ARTIKELSOORTEN,
        arrestsoorten=ARRESTSOORTEN,
    )


@router.post("/leren/nieuw")
async def nieuw_opslaan(request: Request, db: Session = Depends(get_session)):
    form = await request.form()
    pid = _pid(request)
    lid = str(form.get("lijst") or "")
    if lid == "nieuw" or not lid:
        naam = str(form.get("nieuwe_lijst") or "").strip()
        if not naam:
            raise HTTPException(400, _("Kies een lijst of geef de nieuwe lijst een naam"))
        lijst = Leerlijst(profiel_id=pid, naam=naam[:120], vak=leeg_naar_none(str(form.get("vak") or "")))
        db.add(lijst)
        db.flush()
    else:
        lijst = _lijst(request, db, int(lid))
    ref = None
    if form.get("stelsel") and form.get("nummer"):
        ref = Ref(str(form["stelsel"]), str(form["nummer"]), str(form.get("wet") or "") or None)
    bron = db.get(Bron, int(form["bron"])) if str(form.get("bron") or "").isdigit() else None
    soorten = [s for s in form.getlist("soort") if s in KAARTSOORTEN]
    if not soorten:
        soorten = ["artikel"] if ref else ["arrest"] if bron or form.get("zaak") else ["vrij"]
    velden = {k: str(form.get(k) or "") for k in ("vraag", "antwoord", "notitie", "zaak", "vindplaats", "feiten")}
    if "vrij" in soorten and not velden["vraag"].strip():
        raise HTTPException(400, _("Een vrije kaart heeft een vraag nodig"))
    nieuw = leren.maak_kaarten(db, lijst, soorten, ref=ref, bron=bron, doelen=[str(d) for d in form.getlist("doel")], **velden)
    terug = _veilig(str(form.get("terug") or ""), f"/leren/{lijst.id}")
    teken = "&" if "?" in terug else "?"
    if "#" in terug:
        terug, anker = terug.split("#", 1)
        return RedirectResponse(f"{terug}{teken}bewaard={len(nieuw)}#{anker}", status_code=303)
    return RedirectResponse(f"{terug}{teken}bewaard={len(nieuw)}", status_code=303)


@router.get("/leren/kaart/{kid}")
def kaart(request: Request, kid: int, db: Session = Depends(get_session)):
    k = _kaart(request, db, kid)
    voor, achter, z = leren.Bouwer(db).html(k)
    return render(request, "kaart.html", k=k, voor=voor, achter=achter, z=z, ref=leren.ref_van(k),
                  lijsten=leren.lijsten_van(db, _pid(request)), stelsels=actieve_stelsels(db))


@router.post("/leren/kaart/{kid}")
def kaart_opslaan(request: Request, kid: int, vraag: str = Form(""), antwoord: str = Form(""), notitie: str = Form(""),
                  zaak: str = Form(""), vindplaats: str = Form(""), feiten: str = Form(""), lijst: int = Form(...),
                  doel_stelsel: str = Form(""), actief: str = Form(""), db: Session = Depends(get_session)):
    k = _kaart(request, db, kid)
    k.vraag, k.antwoord, k.notitie = leeg_naar_none(vraag), leeg_naar_none(antwoord), leeg_naar_none(notitie)
    if k.soort in ARRESTSOORTEN:
        k.zaak, k.vindplaats, k.feiten = leeg_naar_none(zaak), leeg_naar_none(vindplaats), leeg_naar_none(feiten)
    if k.soort == "tegenhanger" and doel_stelsel:
        k.doel_stelsel = doel_stelsel
    k.actief = actief == "1"
    if lijst != k.lijst_id:
        k.lijst = _lijst(request, db, lijst)
    return RedirectResponse(f"/leren/kaart/{k.id}?opgeslagen=1", status_code=303)


@router.post("/leren/kaart/{kid}/verwijder")
def kaart_verwijder(request: Request, kid: int, db: Session = Depends(get_session)):
    k = _kaart(request, db, kid)
    lid = k.lijst_id
    db.delete(k)
    return RedirectResponse(f"/leren/{lid}", status_code=303)


@router.post("/leren/kaart/{kid}/oefen")
def kaart_oefen(request: Request, kid: int, gekend: str = Form(...), db: Session = Depends(get_session)):
    leren.oefen(db, _kaart(request, db, kid), gekend == "1")
    return JSONResponse({"ok": True})


@router.get("/leren/{lid}")
def lijst(request: Request, lid: int, db: Session = Depends(get_session)):
    lijst = _lijst(request, db, lid)
    bouwer = leren.Bouwer(db)
    kaarten = [(k, bouwer.zijden(k)) for k in lijst.kaarten]
    lijsten = leren.lijsten_van(db, _pid(request))
    return render(request, "leerlijst.html", lijst=lijst, kaarten=kaarten, vakken=_vakken(lijsten), vandaag=date.today())


@router.post("/leren/{lid}")
def lijst_opslaan(request: Request, lid: int, naam: str = Form(...), vak: str = Form(""), examen: str = Form(""),
                  omschrijving: str = Form(""), naar_wk: str = Form(""), db: Session = Depends(get_session)):
    lijst = _lijst(request, db, lid)
    lijst.naam = naam.strip()[:120] or lijst.naam
    lijst.vak, lijst.examen, lijst.omschrijving = leeg_naar_none(vak), _datum(examen), leeg_naar_none(omschrijving)
    lijst.naar_wk = naar_wk == "1"
    return RedirectResponse(f"/leren/{lid}", status_code=303)


@router.post("/leren/{lid}/verwijder")
def lijst_verwijder(request: Request, lid: int, db: Session = Depends(get_session)):
    db.delete(_lijst(request, db, lid))
    return RedirectResponse("/leren", status_code=303)


@router.get("/leren/{lid}/oefenen")
def oefenen(request: Request, lid: int, welke: str = "alle", db: Session = Depends(get_session)):
    """Stampen: kaart na kaart, omdraaien, 'gekend' of 'nog niet'. Geen planning; die doet Wunderkammer."""
    lijst = _lijst(request, db, lid)
    kaarten = [k for k in lijst.kaarten if k.actief]
    if welke == "nog":
        kaarten = [k for k in kaarten if not k.gekend]
    bouwer = leren.Bouwer(db)
    data = []
    for k in kaarten:
        voor, achter, z = bouwer.html(k)
        data.append(dict(id=k.id, soort=k.soort_label, voor=voor, achter=achter, url=z.url, gekend=k.gekend))
    return render(request, "oefenen.html", lijst=lijst, welke=welke, aantal=len(data),
                  kaarten_json=json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))


@router.get("/leren/{lid}/export.md")
def export(request: Request, lid: int, db: Session = Depends(get_session)):
    lijst = _lijst(request, db, lid)
    bouwer = leren.Bouwer(db)
    delen = [f"# {lijst.naam}\n"]
    if lijst.omschrijving:
        delen.append(lijst.omschrijving + "\n")
    for k in lijst.kaarten:
        z = bouwer.zijden(k)
        delen.append(f"## {k.soort_label}\n\n{z.voor}\n\n**→**\n\n{z.achter}\n")
    naam = quote(f"{lijst.naam}.md")
    return PlainTextResponse("\n".join(delen), media_type="text/markdown; charset=utf-8",
                             headers={"Content-Disposition": f"attachment; filename*=UTF-8''{naam}"})


def bewaard_context(request: Request, db: Session) -> dict:
    """Voor pagina's met artikelen: welke al in een lijst staan (ster)."""
    return {"bewaarde_refs": leren.bewaarde_refs(db, _pid(request))}

