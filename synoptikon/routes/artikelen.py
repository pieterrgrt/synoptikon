"""Artikelen: opzoeken, plaats in de systematiek en corresponderende artikelen.

`/artikelen/NL/3:84` toont waar art. 3:84 BW in het BW staat, de thema's
waarin het voorkomt en per thema de artikelen uit de andere stelsels, elk met
hun eigen plaats in hun eigen systematiek.
"""
from __future__ import annotations

from collections import OrderedDict
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_session
from ..i18n import _
from ..models import Correspondentie, CorrespondentieArtikel, Stelsel, Systematiek, Wettekst, WettekstArtikel
from ..services import correspondentie as corr
from ..auth import huidig_profiel
from ..services import eu, leren, wetboek, zoeken
from ..services.artikelen import Ref, herken, lees, sleutel
from ..models import RECHTSFAMILIES
from ..services.helpers import actieve_stelsels, leeg_naar_none, stelsels_per_code
from ..services.stelselkeuze import ook_uit, stelselkeuze
from . import markeringen, render

router = APIRouter()


def _codes(db: Session, request: Request) -> list[str]:
    """Alle actieve stelsels, mijn stelsels eerst."""
    return [s.code for s in stelselkeuze(db, request).alle]


@router.get("/artikelen")
def overzicht(request: Request, q: str = "", stelsel: str = "", familie: str = "", db: Session = Depends(get_session)):
    kandidaten: list[tuple[Ref, object]] = []
    treffers = []
    if q.strip():
        kandidaten = corr.zoek_artikel(db, q, stelsel or None)
        if len(kandidaten) == 1:
            return RedirectResponse(kandidaten[0][0].url, status_code=303)
        if not kandidaten:
            treffers = [(Ref(wa.wettekst.stelsel_code, wa.nummer, wa.wettekst.wet), wa, s) for wa, s in zoeken.wetsartikelen(db, q, stelsel)]
    thema_s = corr.alle_correspondenties(db)
    groepen: OrderedDict[str, list[Correspondentie]] = OrderedDict()
    for c in thema_s:
        groepen.setdefault(c.rechtsgebied or "Overig", []).append(c)
    # Kolommen: mijn stelsels die in een thema voorkomen (plus ?ook=); de andere onder 'meer stelsels…'.
    ook = ook_uit(request)
    keuze = stelselkeuze(db, request, ook)
    stelsels = keuze.alle
    gebruikt = {a.stelsel_code for c in thema_s for a in c.artikelen}
    kolommen = [s for s in keuze.eigen if s.code in gebruikt] or keuze.eigen
    overige_kolommen = [s for s in keuze.overig if s.code in gebruikt]
    families_in_tabel = [k for k in RECHTSFAMILIES if any(s.familie == k for s in kolommen)]
    if familie in RECHTSFAMILIES:
        kolommen = [s for s in kolommen if s.familie == familie]
    return render(
        request,
        "artikelen.html",
        q=q,
        f_stelsel=stelsel,
        f_familie=familie if familie in RECHTSFAMILIES else "",
        families_in_tabel=families_in_tabel,
        kandidaten=kandidaten,
        treffers=treffers,
        groepen=groepen,
        kolommen=kolommen,
        overige_kolommen=overige_kolommen,
        ook=ook,
        stelsels=stelsels,
        aantal=len(thema_s),
    )


# --- thema's ------------------------------------------------------------------------


@router.get("/artikelen/thema/{cid}")
def thema(request: Request, cid: int, db: Session = Depends(get_session)):
    c = db.get(Correspondentie, cid)
    if c is None:
        raise HTTPException(404)
    ctx = corr.Context(db)
    # Lege kolommen alleen voor mijn stelsels; een ander stelsel verschijnt zodra het een artikel in het thema heeft.
    keuze = stelselkeuze(db, request)
    stelsels = keuze.alle
    kolommen = corr.per_stelsel(ctx, c, keuze.codes)
    per_code = stelsels_per_code(db)
    namen = {code: st.naam for code, st in per_code.items()}
    return render(request, "thema.html", c=c, kolommen=kolommen, namen=namen, per_code=per_code, stelsels=stelsels)


@router.post("/artikelen/thema")
def thema_maak(
    titel: str = Form(...),
    rechtsgebied: str = Form(""),
    toelichting: str = Form(""),
    stelsel_code: str = Form(""),
    verwijzing: str = Form(""),
    rol: str = Form(""),
    db: Session = Depends(get_session),
):
    titel = titel.strip()
    if db.scalar(select(Correspondentie).where(Correspondentie.titel == titel)):
        raise HTTPException(400, _("Er bestaat al een thema met deze titel"))
    c = Correspondentie(titel=titel, rechtsgebied=leeg_naar_none(rechtsgebied), toelichting=leeg_naar_none(toelichting))
    db.add(c)
    if stelsel_code and verwijzing.strip():
        _voeg_lid_toe(c, stelsel_code, verwijzing, rol, "")
    db.flush()
    return RedirectResponse(f"/artikelen/thema/{c.id}", status_code=303)


@router.post("/artikelen/thema/{cid}/bewerken")
def thema_opslaan(cid: int, titel: str = Form(...), rechtsgebied: str = Form(""), toelichting: str = Form(""), db: Session = Depends(get_session)):
    c = db.get(Correspondentie, cid)
    if c is None:
        raise HTTPException(404)
    c.titel, c.rechtsgebied, c.toelichting = titel.strip(), leeg_naar_none(rechtsgebied), leeg_naar_none(toelichting)
    return RedirectResponse(f"/artikelen/thema/{c.id}", status_code=303)


@router.post("/artikelen/thema/{cid}/verwijderen")
def thema_verwijderen(cid: int, db: Session = Depends(get_session)):
    c = db.get(Correspondentie, cid)
    if c:
        db.delete(c)
    return RedirectResponse("/artikelen", status_code=303)


def _voeg_lid_toe(c: Correspondentie, stelsel_code: str, verwijzing: str, rol: str, opmerking: str) -> CorrespondentieArtikel:
    ref = lees(stelsel_code, verwijzing)
    if ref is None:
        raise HTTPException(400, _("Kan '{verwijzing}' niet lezen als artikel uit {stelsel}", verwijzing=verwijzing, stelsel=stelsel_code))
    volgorde = max([a.volgorde for a in c.artikelen] or [0]) + 10
    lid = CorrespondentieArtikel(
        stelsel_code=stelsel_code, wet=ref.wet, nummer=ref.nummer, tot=ref.tot, detail=ref.detail,
        rol=leeg_naar_none(rol), opmerking=leeg_naar_none(opmerking), volgorde=volgorde,
    )
    c.artikelen.append(lid)
    return lid


@router.post("/artikelen/thema/{cid}/artikel")
def lid_maak(
    cid: int,
    stelsel_code: str = Form(...),
    verwijzing: str = Form(...),
    rol: str = Form(""),
    opmerking: str = Form(""),
    terug: str = Form(""),
    db: Session = Depends(get_session),
):
    c = db.get(Correspondentie, cid)
    if c is None or db.get(Stelsel, stelsel_code) is None:
        raise HTTPException(404)
    _voeg_lid_toe(c, stelsel_code, verwijzing, rol, opmerking)
    return RedirectResponse(terug if terug.startswith("/") and not terug.startswith("//") else f"/artikelen/thema/{c.id}", status_code=303)


@router.post("/artikelen/koppel")
def koppel(
    thema_id: int = Form(...),
    stelsel_code: str = Form(...),
    verwijzing: str = Form(...),
    rol: str = Form(""),
    opmerking: str = Form(""),
    terug: str = Form(""),
    db: Session = Depends(get_session),
):
    return lid_maak(thema_id, stelsel_code, verwijzing, rol, opmerking, terug, db)


@router.post("/artikelen/thema/{cid}/artikel/{aid}/verwijderen")
def lid_verwijderen(cid: int, aid: int, db: Session = Depends(get_session)):
    a = db.get(CorrespondentieArtikel, aid)
    if a and a.correspondentie_id == cid:
        db.delete(a)
    return RedirectResponse(f"/artikelen/thema/{cid}", status_code=303)


# Als laatste: het pad-patroon zou anders /artikelen/thema/… opslokken.
@router.get("/lezen/{stelsel}/{nummer:path}")
def lezen(stelsel: str, nummer: str, wet: str | None = None, db: Session = Depends(get_session)):
    """Vaste ingang voor andere apps (Wunderkammer): het artikel in de leesweergave van zijn wet, anders de artikelpagina."""
    ref = Ref(stelsel.upper(), nummer, wet or None)
    plek = _in_wettekst(db, ref) if db.get(Stelsel, ref.stelsel) else None
    return RedirectResponse(plek["url"] if plek else (ref.url or "/artikelen"), status_code=303)


@router.get("/artikelen/{stelsel}/{nummer:path}")
def artikel(request: Request, stelsel: str, nummer: str, wet: str | None = None, lid: str | None = None,
            db: Session = Depends(get_session)):
    st = db.get(Stelsel, stelsel.upper())
    if st is None:
        raise HTTPException(404)
    ref = Ref(st.code, nummer, wet or None, detail=(lid or "").strip()[:40] or None)
    if corr.wettekst_artikel(db, ref) is None:
        # Geen artikel met precies dit nummer: de invoer lezen ("art. 3:84" → "3:84"). Bijlagen, preambules en
        # protocolartikelen ("Anlage 2", "Präambel", "Protokoll 2 Art. 9") vindt de eerste stap al.
        gelezen = lees(st.code, nummer)
        if gelezen is None or gelezen.nummer is None:
            raise HTTPException(404, _("Onleesbaar artikelnummer"))
        ref = Ref(st.code, gelezen.nummer, wet or None, detail=ref.detail or gelezen.detail)
        if ref.nummer != nummer:
            return RedirectResponse(ref.url, status_code=303)
    ctx = corr.Context(db)
    codes = _codes(db, request)
    thema_s = []
    for c, eigen in corr.thema_s_voor(db, ref.stelsel, ref.nummer, ref.wet):
        thema_s.append((c, eigen, corr.per_stelsel(ctx, c, codes, behalve=eigen[0] if len(eigen) == 1 else None)))
    pad = ctx.pad(ref)
    buren, buren_volledig = _buren(ctx, ref, pad)
    lezen = _in_wettekst(db, ref)
    tekst = ctx.tekst(ref)
    bestaat_niet = _bestaat_niet(db, ref) if tekst is None else None
    versies = corr.taalversies(db, ref)
    getoond = lezen["wet"].taal if lezen else None
    antwoord = render(
        request,
        "artikel.html",
        bestaat_niet=bestaat_niet,
        taalversies=[wa for wa in versies if wa.wettekst.taal != getoond],
        getoonde_taal=getoond,
        **markeringen.context_artikel(db, huidig_profiel(request).id if huidig_profiel(request) else 1, ref, tekst),
        ref=ref,
        stelsel=st,
        pad=pad,
        tekst=tekst,
        thema_s=thema_s,
        concordanties=corr.concordanties_voor(db, ref.stelsel, ref.nummer) if not ref.wet else [],
        gebruik=corr.gebruik(ctx, ref),
        europees=eu.omzettingen_voor_artikel(db, ref),
        buren=buren,
        buren_volledig=buren_volledig,
        lezen=lezen,
        bewaarde_refs=leren.bewaarde_refs(db, huidig_profiel(request).id if huidig_profiel(request) else 1),
        alle_thema_s=db.scalars(select(Correspondentie).order_by(Correspondentie.titel)).all(),
        stelsels=actieve_stelsels(db),
        per_code=stelsels_per_code(db),
    )
    if bestaat_niet:
        antwoord.status_code = 404
    return antwoord


def _bestaat_niet(db: Session, ref: Ref) -> dict | None:
    """Is de wet ingelezen en komt dit nummer er niet in voor, dan bestaat het artikel niet (6:999 BW, § 823a BGB):
    de wet, haar versie en de bestaande artikelen ervoor en erna. None als de wet niet ingelezen is."""
    from bisect import bisect_left

    if ref.nummer is None:
        return None
    q = select(Wettekst).where(Wettekst.stelsel_code == ref.stelsel)
    q = q.where(corr._zelfde_wet(ref.wet)) if ref.wet else q.where(Wettekst.wet.is_(None))
    if ref.stelsel == "FR" and not ref.wet:
        q = q.where(Wettekst.wet_id == corr.FR_CODE_CIVIL)
    wetten = db.scalars(q.order_by(Wettekst.opgehaald.desc())).all()
    if not wetten:
        return None
    laatste: dict[str, Wettekst] = {}
    for w in wetten:  # per wet_id (de boeken van het BW) de laatst opgehaalde versie
        laatste.setdefault(w.wet_id, w)
    per_id = {w.id: w for w in laatste.values()}
    rijen = db.execute(select(WettekstArtikel.nummer, WettekstArtikel.wettekst_id).where(WettekstArtikel.wettekst_id.in_(list(per_id)))).all()
    geordend = sorted({(k, nr, wid) for nr, wid in rijen if (k := sleutel(ref.stelsel, nr)) is not None})
    eigen = sleutel(ref.stelsel, ref.nummer)
    vorig = volgend = None
    if eigen is not None and geordend:
        i = bisect_left(geordend, (eigen,))
        vorig = geordend[i - 1] if i > 0 else None
        volgend = geordend[i] if i < len(geordend) else None
    # De wet waarin het nummer had moeten staan: bij het BW het boek van de buren.
    buur = next((b for b in (vorig, volgend) if b and b[1].split(":")[0] == ref.nummer.split(":")[0]), vorig or volgend)
    w = per_id[buur[2]] if buur else next(iter(per_id.values()))
    return {"wet": w, "vorig": Ref(ref.stelsel, vorig[1], ref.wet) if vorig else None,
            "volgend": Ref(ref.stelsel, volgend[1], ref.wet) if volgend else None}


def _in_wettekst(db: Session, ref: Ref) -> dict | None:
    """Waar dit artikel in de geïmporteerde wet staat, en het vorige en volgende artikel daar."""
    wa = corr.wettekst_artikel(db, ref)
    if wa is None:
        return None
    w = wa.wettekst
    ih = wetboek.inhoud(db, w)
    deel = next((d for d in ih.volgorde if wa.nummer in d.artikelen), None)
    vorig, volgend = wetboek.naast(db, wa)
    # Lezen gaat via de systematiek; wat die niet plaatst, via de inhoudsopgave van de wet zelf.
    knoop_id = wetboek.plaatsing(db, w.stelsel_code).plek.get((w.id, wa.nummer))
    knoop = db.get(Systematiek, knoop_id) if knoop_id else None
    if knoop is not None:
        url = f"/stelsels/{w.stelsel_code}/lees/{knoop.id}#art-{quote(wa.nummer)}"
    else:
        url = f"/stelsels/{w.stelsel_code}/wet/{w.id}" + (f"?deel={quote(deel.sleutel)}#art-{quote(wa.nummer)}" if deel else "")
    return {
        "wet": w,
        "deel": deel,
        "knoop": knoop,
        "url": url,
        "vorig": wetboek.ref(w, vorig.nummer) if vorig else None,
        "volgend": wetboek.ref(w, volgend.nummer) if volgend else None,
    }


def _buren(ctx: corr.Context, ref: Ref, pad: list) -> tuple[list[tuple[Ref, bool]], bool]:
    """De andere artikelen uit dezelfde knoop, om verder te bladeren: ([(ref, in een thema)], volledig).

    Uit de geïmporteerde wet: alle artikelen van de knoop, de artikelen die in een thema staan gemarkeerd. Zonder
    wettekst alleen wat in een thema staat (`volledig` is dan False, en de kop zegt dat)."""
    if not pad:
        return [], False
    knoop = pad[-1]
    in_thema = {a.nummer for _c, a in corr.leden_in_knoop(ctx, knoop) if a.tot is None}
    wetten: dict[int, Wettekst | None] = {}
    uit: list[tuple[Ref, bool]] = []
    for wid, nr in wetboek.plaatsing(ctx.db, ref.stelsel).direct.get(knoop.id, []):
        w = wetten[wid] if wid in wetten else wetten.setdefault(wid, ctx.db.get(Wettekst, wid))
        if w is not None and (w.wet or "").lower() == (ref.wet or "").lower() and nr != ref.nummer:
            uit.append((Ref(ref.stelsel, nr, ref.wet), nr in in_thema))
    if uit:
        return uit, True
    uit = [(Ref(ref.stelsel, nr, ref.wet), True) for nr in in_thema if nr != ref.nummer]
    uit.sort(key=lambda p: sleutel(p[0].stelsel, p[0].nummer) or ())
    return uit, False
