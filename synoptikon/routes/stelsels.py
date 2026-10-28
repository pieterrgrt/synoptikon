from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..db import get_session
from ..i18n import _
from ..models import RECHTSFAMILIES, Antwoord, AntwoordBron, Bron, Stelsel, Systematiek, Vraag
from ..models import Wettekst
from ..services import correspondentie as corr
from ..auth import huidig_profiel
from ..services import leren, wetboek, zoeken
from ..services.artikelen import herken, plaatser, ref_uit_bron
from ..services.helpers import actieve_stelsels, leeg_naar_none, per_familie, stelsels_per_code
from . import render

router = APIRouter()


@router.get("/stelsels")
def overzicht(request: Request, db: Session = Depends(get_session)):
    stelsels = db.scalars(select(Stelsel).order_by(Stelsel.volgorde)).all()
    wetten = {}
    for s in stelsels:
        register = wetboek.wetten(db, s.code)
        ids = {w.id for w in register}
        wetten[s.code] = register + [w for w in wetboek.belangrijk(db, s.code) if w.id not in ids]
    return render(request, "stelsels.html", families=per_familie(stelsels), wetten=wetten,
                  aantallen={s.code: wetboek.aantal_wetten(db, s.code) for s in stelsels})


@router.get("/stelsels/{code}/wetten")
def alle_wetten(request: Request, code: str, q: str = "", p: int = 1, db: Session = Depends(get_session)):
    """Alle wetten van een stelsel (DE: ruim 6.000, EU: ruim 17.000), te doorzoeken op titel of afkorting."""
    stelsel = db.get(Stelsel, code)
    if stelsel is None:
        raise HTTPException(404)
    per = 100
    ws, totaal = wetboek.zoek_wetten(db, code, q, max(1, p), per)
    if q.strip() and totaal == 1:
        return RedirectResponse(f"/stelsels/{code}/wet/{ws[0].id}", status_code=303)
    return render(request, "wetten_zoek.html", stelsel=stelsel, stelsels=actieve_stelsels(db), ws=ws, titels=wetboek.toon_titels(db, ws),
                  totaal=totaal, q=q, p=max(1, p), paginas=(totaal + per - 1) // per)


@router.get("/stelsels/{code}/wet/{wid}")
def wet(request: Request, code: str, wid: int, deel: str = "", artikel: str = "", db: Session = Depends(get_session)):
    """Een wet lezen: inhoudsopgave, of één afdeling met de volledige tekst van haar artikelen.

    Het veld bovenaan neemt een artikelnummer (springt naar het artikel) of woorden (zoekt in de tekst van deze wet).
    """
    w = db.get(Wettekst, wid)
    if w is None or w.stelsel_code != code:
        raise HTTPException(404)
    ih = wetboek.inhoud(db, w)
    if artikel.strip():
        # Ga naar artikel: binnen deze wet, anders via de gewone artikelzoeker.
        nr = artikel.strip()
        for kandidaat in (nr, nr.removeprefix("art.").removeprefix("Art.").removeprefix("§").strip()):
            gevonden = next((d for d in [ih.wortel, *ih.volgorde] if kandidaat in d.artikelen), None)
            if gevonden is not None:
                return RedirectResponse(f"/stelsels/{code}/wet/{wid}?deel={quote(gevonden.sleutel)}#art-{quote(kandidaat)}", status_code=303)
        treffers = zoeken.wetsartikelen(db, nr, code, 60, wettekst_id=w.id)
        if not treffers:
            afk = wetboek.toon_afkorting(w) or ""
            return RedirectResponse(f"/opzoeken?q={quote((nr + ' ' + afk).strip())}&stelsel={code}", status_code=303)
        return render(request, "wetboek.html", stelsel=db.get(Stelsel, code), w=w, ih=ih, d=ih.wortel, wetten=[], aantal_wetten=0,
                      artikelen=[], plek={}, toon_tekst=False, vorige=None, volgende=None, ref=lambda n: wetboek.ref(w, n),
                      zoek=nr, treffers=treffers, bewaarde_refs=_bewaarde(request, db))
    d = wetboek.deel(ih, deel)
    if d is None:
        raise HTTPException(404)
    nummers = wetboek.nummers_onder(d) if d.pad else d.artikelen
    toon_tekst = not d.kinderen or (bool(d.pad) and len(nummers) <= wetboek.MAX_ARTIKELEN)
    arts = wetboek.artikelen(db, w, nummers[: wetboek.MAX_ARTIKELEN * 3] if toon_tekst else d.artikelen)
    # Kopjes tussen de artikelen: het pad onder dit deel, telkens als het verandert.
    plek = {nr: dd for dd in [d, *_onder(d)] for nr in dd.artikelen}
    vorige, volgende = wetboek.buren(ih, d) if d.pad else (None, None)
    return render(
        request,
        "wetboek.html",
        stelsel=db.get(Stelsel, code),
        stelsels=actieve_stelsels(db),
        w=w,
        wetten=wetboek.wetten(db, code),
        aantal_wetten=wetboek.aantal_wetten(db, code),
        ih=ih,
        d=d,
        artikelen=arts,
        plek=plek,
        toon_tekst=toon_tekst,
        vorige=vorige,
        volgende=volgende,
        ref=lambda nr: wetboek.ref(w, nr),
        bewaarde_refs=_bewaarde(request, db),
        in_systematiek=w.kern and w.id in wetboek.plaatsing(db, code).wortel,
    )


def _onder(d):
    for k in d.kinderen:
        yield k
        yield from _onder(k)


@router.post("/stelsels")
def stelsel_maak(
    code: str = Form(...), naam: str = Form(...), taal: str = Form(...), toelichting: str = Form(""), familie: str = Form(""), db: Session = Depends(get_session)
):
    code = code.strip().upper()
    if db.get(Stelsel, code):
        raise HTTPException(400, _("Stelsel bestaat al"))
    volgorde = max([s.volgorde for s in db.scalars(select(Stelsel)).all()] or [0]) + 10
    db.add(
        Stelsel(
            code=code, naam=naam.strip(), taal=taal.strip().lower(), volgorde=volgorde, toelichting=leeg_naar_none(toelichting),
            familie=familie if familie in RECHTSFAMILIES else None,
        )
    )
    return RedirectResponse("/stelsels", status_code=303)


@router.post("/stelsels/{code}/familie")
def stelsel_familie(code: str, familie: str = Form(""), db: Session = Depends(get_session)):
    s = db.get(Stelsel, code)
    if s is None:
        raise HTTPException(404)
    s.familie = familie if familie in RECHTSFAMILIES else None
    return RedirectResponse("/stelsels", status_code=303)


@router.post("/stelsels/{code}/actief")
def stelsel_actief(code: str, actief: str = Form("0"), db: Session = Depends(get_session)):
    s = db.get(Stelsel, code)
    if s is None:
        raise HTTPException(404)
    s.actief = actief == "1"
    return RedirectResponse("/stelsels", status_code=303)


@router.get("/stelsels/{code}")
def systematiek(request: Request, code: str, vraag: str | None = None, artikel: str = "", wet: int | None = None, db: Session = Depends(get_session)):
    stelsel = db.get(Stelsel, code)
    if stelsel is None:
        raise HTTPException(404)
    if wet is not None:
        # Een wet openen: naar haar plek in de systematiek, of naar haar eigen inhoudsopgave als die er niet is.
        wortel = wetboek.plaatsing(db, code).wortel.get(wet)
        doel = f"/stelsels/{code}#knoop-{wortel}" if wortel else f"/stelsels/{code}/wet/{wet}"
        return RedirectResponse(doel, status_code=303)
    alle_knopen = db.scalars(
        select(Systematiek).where(Systematiek.stelsel_code == code).options(selectinload(Systematiek.kinderen), selectinload(Systematiek.bronnen)).order_by(Systematiek.volgorde)
    ).all()
    wortels = [k for k in alle_knopen if k.parent_id is None]
    vraag_obj = db.scalar(select(Vraag).where(Vraag.slug == vraag).options(selectinload(Vraag.antwoorden).selectinload(Antwoord.bronnen).selectinload(AntwoordBron.bron))) if vraag else None
    gemarkeerd: dict[int, list[Bron]] = {}
    los: list[Bron] = []
    if vraag_obj:
        a = vraag_obj.antwoord_voor(code)
        for ab in (a.bronnen if a else []):
            if ab.bron.systematiek_id:
                gemarkeerd.setdefault(ab.bron.systematiek_id, []).append(ab.bron)
            else:
                los.append(ab.bron)
    # Alle bronnen (wet) zonder systematiekknoop, om ze te kunnen plaatsen.
    ongeplaatst = db.scalars(select(Bron).where(Bron.stelsel_code == code, Bron.soort == "wet", Bron.systematiek_id.is_(None))).all()
    vragen = db.scalars(select(Vraag).order_by(Vraag.titel)).all()
    # Knopen die open staan: de paden naar gemarkeerde bronnen, of naar het opgezochte artikel.
    open_ids: set[int] = set()
    for kid in gemarkeerd:
        k = db.get(Systematiek, kid)
        open_ids.update(x.id for x in (k.pad() if k else []))
    gezocht, gemarkeerd_artikel = None, None
    if artikel.strip():
        refs = herken(artikel, code)
        if refs:
            gezocht = refs[0]
            pad = plaatser(db, code, gezocht.wet).pad(gezocht.nummer)
            open_ids.update(k.id for k in pad)
            gemarkeerd_artikel = pad[-1].id if pad else None
    return render(
        request,
        "systematiek.html",
        stelsel=stelsel,
        pl=wetboek.plaatsing(db, code),
        ws={w.id: w for w in wetboek.wetten(db, code)},
        stelsels=actieve_stelsels(db),
        wortels=wortels,
        vraag=vraag_obj,
        vragen=vragen,
        gemarkeerd=gemarkeerd,
        los=los,
        ongeplaatst=ongeplaatst,
        alle_knopen=alle_knopen,
        open_ids=open_ids,
        tellingen=corr.tellingen(corr.Context(db), code),
        artikel=artikel,
        gezocht=gezocht,
        gezocht_knoop=gemarkeerd_artikel if gezocht else None,
        vraag_slug=vraag_obj.slug if vraag_obj else None,
    )


@router.post("/stelsels/{code}/systematiek")
def knoop_maak(code: str, label: str = Form(...), knoopcode: str = Form(""), bereik: str = Form(""), parent_id: str = Form(""), db: Session = Depends(get_session)):
    if db.get(Stelsel, code) is None:
        raise HTTPException(404)
    parent = int(parent_id) if parent_id.strip() else None
    broers = db.scalars(select(Systematiek).where(Systematiek.stelsel_code == code, Systematiek.parent_id.is_(parent) if parent is None else Systematiek.parent_id == parent)).all()
    db.add(
        Systematiek(
            stelsel_code=code,
            parent_id=parent,
            code=knoopcode.strip() or label.strip()[:60],
            label=label.strip(),
            bereik=leeg_naar_none(bereik),
            volgorde=max([b.volgorde for b in broers] or [0]) + 10,
        )
    )
    return RedirectResponse(f"/stelsels/{code}", status_code=303)


@router.post("/stelsels/{code}/plaats")
def bron_plaats(code: str, bron_id: int = Form(...), systematiek_id: str = Form(""), db: Session = Depends(get_session)):
    bron = db.get(Bron, bron_id)
    if bron is None:
        raise HTTPException(404)
    bron.systematiek_id = int(systematiek_id) if systematiek_id.strip() else None
    return RedirectResponse(f"/stelsels/{code}", status_code=303)


@router.post("/stelsels/{code}/plaats-automatisch")
def bronnen_automatisch_plaatsen(code: str, db: Session = Depends(get_session)):
    """Plaatst ongeplaatste wetsbronnen op grond van hun artikelnummer."""
    ctx = corr.Context(db)
    for bron in db.scalars(select(Bron).where(Bron.stelsel_code == code, Bron.soort == "wet", Bron.systematiek_id.is_(None))).all():
        ref = ref_uit_bron(bron)
        pad = ctx.pad(ref) if ref else []
        if pad:
            bron.systematiek_id = pad[-1].id
    return RedirectResponse(f"/stelsels/{code}", status_code=303)


@router.get("/stelsels/{code}/knoop/{knoop_id}")
def knoop(request: Request, code: str, knoop_id: int, db: Session = Depends(get_session)):
    """Eén knoop: wat staat erin, en waar staan de corresponderende artikelen in de andere stelsels?"""
    k = db.get(Systematiek, knoop_id)
    if k is None or k.stelsel_code != code:
        raise HTTPException(404)
    ctx = corr.Context(db)
    stelsels = actieve_stelsels(db)
    eigen = corr.leden_in_knoop(ctx, k)
    thema_s = []
    for c, a in eigen:
        if c not in thema_s:
            thema_s.append(c)
    per_code = stelsels_per_code(db)
    namen = {code: st.naam for code, st in per_code.items()}
    return render(
        request,
        "knoop.html",
        per_code=per_code,
        k=k,
        stelsel=db.get(Stelsel, code),
        eigen=eigen,
        thema_s=thema_s,
        tegenhangers=corr.tegenhangers(ctx, k, [s.code for s in stelsels]),
        namen=namen,
        stelsels=stelsels,
    )


@router.get("/stelsels/{code}/lees/{knoop_id}")
def lees(request: Request, code: str, knoop_id: int, fragment: int = 0, db: Session = Depends(get_session)):
    """De tekst van de artikelen in een systematiekknoop. `fragment=1`: alleen de artikelen direct in de knoop, om in de boom
    open te klappen; anders een pagina met alles eronder (of, bij een groot onderdeel, de onderdelen om uit te kiezen)."""
    k = db.get(Systematiek, knoop_id)
    if k is None or k.stelsel_code != code:
        raise HTTPException(404)
    stelsel = db.get(Stelsel, code)
    pl = wetboek.plaatsing(db, code)
    ws = {w.id: w for w in wetboek.wetten(db, code)}
    if fragment:
        arts = wetboek.artikelen_bij(db, pl.direct.get(k.id, []))
        terug = f"/stelsels/{code}#knoop-{k.id}"
        return render(request, "_wetartikelen.html", stelsel=stelsel, artikelen=arts, ws=ws, koppen={}, terug=terug,
                      bewaarde_refs=_bewaarde(request, db))
    # Alle knopen eronder in boomvolgorde; de knopen met eigen artikelen zijn ook de stappen voor vorige/volgende.
    onder = [k, *_afstammelingen(k)]
    toon_tekst = pl.onder.get(k.id, 0) <= wetboek.MAX_ARTIKELEN
    paren = [p for x in onder for p in pl.direct.get(x.id, [])] if toon_tekst else pl.direct.get(k.id, [])
    arts = wetboek.artikelen_bij(db, paren)
    koppen = {}
    for x in onder[1:]:
        eerste = pl.direct.get(x.id)
        if eerste and toon_tekst:
            koppen[eerste[0]] = [y for y in x.pad() if y not in k.pad()]
    stappen = [x for x in _boomvolgorde(db, code) if pl.direct.get(x.id)]
    i = next((j for j, x in enumerate(stappen) if x.id == k.id), None)
    if i is None:  # knoop zonder eigen artikelen: vorige/volgende rond de eerste knoop eronder
        i = next((j for j, x in enumerate(stappen) if x in onder), None)
    vorige = stappen[i - 1] if i is not None and i > 0 else None
    volgende = None
    if i is not None:
        volgende = next((x for x in stappen[i + 1:] if x not in onder), None)
    return render(
        request,
        "lezen.html",
        stelsel=stelsel,
        k=k,
        pl=pl,
        ws=ws,
        artikelen=arts,
        koppen=koppen,
        toon_tekst=toon_tekst,
        vorige=vorige,
        volgende=volgende,
        terug=f"/stelsels/{code}/lees/{k.id}",
        bewaarde_refs=_bewaarde(request, db),
    )


def _afstammelingen(k: Systematiek):
    for c in k.kinderen:
        yield c
        yield from _afstammelingen(c)


def _boomvolgorde(db: Session, code: str) -> list[Systematiek]:
    wortels = db.scalars(select(Systematiek).where(Systematiek.stelsel_code == code, Systematiek.parent_id.is_(None)).order_by(Systematiek.volgorde)).all()
    uit: list[Systematiek] = []
    for w in wortels:
        uit.append(w)
        uit.extend(_afstammelingen(w))
    return uit


def _bewaarde(request: Request, db: Session) -> set:
    p = huidig_profiel(request)
    return leren.bewaarde_refs(db, p.id if p else 1)
