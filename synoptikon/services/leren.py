"""Leerlijsten en kaarten.

Een kaart bewaart alleen waar ze over gaat (een artikel, een arrest of een eigen vraag) en wat je er zelf bij schrijft.
Voor- en achterkant worden telkens opnieuw opgebouwd uit de actuele wettekst, systematiek en correspondentietabel:
een nieuwe versie van de wet komt zo vanzelf op de kaart, hier en in Wunderkammer.
"""
from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import md
from ..i18n import _
from ..models import ARRESTSOORTEN, ARTIKELSOORTEN, FASEN, Bron, Kaart, KaartStand, Leerlijst, Profiel, Stelsel, now
from . import correspondentie as corr
from . import wk  # noqa: F401  (seint Wunderkammer na een wijziging in de kaarten)
from .artikelen import Ref


@dataclass
class Zijden:
    voor: str  # markdown
    achter: str  # markdown
    url: str | None  # pad in Synoptikon om verder te lezen


def nieuwe_uid() -> str:
    return secrets.token_hex(16)


def lijsten_van(db: Session, profiel_id: int) -> list[Leerlijst]:
    return list(db.scalars(select(Leerlijst).where(Leerlijst.profiel_id == profiel_id).options(
        selectinload(Leerlijst.kaarten).selectinload(Kaart.stand)).order_by(Leerlijst.naam)).all())


def ref_van(k: Kaart) -> Ref | None:
    return Ref(k.stelsel_code, k.nummer, k.wet or None) if k.stelsel_code and k.nummer else None


def fase(k: Kaart) -> str | None:
    """Stand in Wunderkammer (sleutel uit FASEN); None als de kaart niet naar Wunderkammer gaat."""
    if not k.actief or k.status or not k.lijst.naar_wk:
        return None
    return k.stand.fase if k.stand else "nieuw"


@dataclass
class Bewaard:
    """Wat er al van een artikel in de leerlijsten staat: de zwakste kaart telt (vastzit gaat voor nieuw)."""
    kaart_id: int
    aantal: int = 0
    fase: str | None = None
    due: datetime | None = None
    missers: int = 0


def bewaarde_refs(db: Session, profiel_id: int) -> dict[tuple[str, str | None, str], Bewaard]:
    """(stelsel, wet, nummer) → Bewaard voor alle artikelen in de lijsten van dit profiel: voor de ster bij een artikel.
    Een dict, zodat `ref in bewaarde_refs` blijft werken."""
    kaarten = db.scalars(select(Kaart).join(Leerlijst).where(
        Leerlijst.profiel_id == profiel_id, Kaart.nummer.is_not(None), Kaart.status.is_(None)).options(
        selectinload(Kaart.stand), selectinload(Kaart.lijst))).all()
    from ..config import settings

    p = db.get(Profiel, profiel_id)
    wk_aan = settings.wk_ingesteld and p is not None and p.wunderkammer
    volgorde = list(FASEN)
    uit: dict[tuple[str, str | None, str], Bewaard] = {}
    for k in kaarten:
        b = uit.setdefault((k.stelsel_code, k.wet or None, k.nummer), Bewaard(k.id))
        b.aantal += 1
        f = fase(k) if wk_aan else None
        if f and (b.fase is None or volgorde.index(f) < volgorde.index(b.fase)):
            b.fase, b.kaart_id = f, k.id
        if k.stand:
            b.missers = max(b.missers, k.stand.missers)
            if k.stand.due and (b.due is None or k.stand.due < b.due):
                b.due = k.stand.due
    return uit


@dataclass
class LijstStand:
    fasen: dict[str, int]  # per fase het aantal kaarten (alleen de lijsten die naar Wunderkammer gaan)
    due: datetime | None  # eerstvolgende herhaling
    nu: int  # nu aan de beurt (of nieuw)

    @property
    def totaal(self) -> int:
        return sum(self.fasen.values())


def lijst_stand(lijst: Leerlijst) -> LijstStand:
    fasen = dict.fromkeys(FASEN, 0)
    due, nu, tijd = None, 0, datetime.now(timezone.utc).replace(tzinfo=None)
    for k in lijst.kaarten:
        f = fase(k)
        if f is None:
            continue
        fasen[f] += 1
        d = k.stand.due if k.stand else None
        if d is not None and d.tzinfo is not None:
            d = d.astimezone(timezone.utc).replace(tzinfo=None)
        if d is None or d <= tijd:
            nu += 1
        elif due is None or d < due:
            due = d
    return LijstStand(fasen, due, nu)


def zwakke_kaarten(db: Session, profiel_id: int, refs: list[Ref] | None = None, limiet: int = 50) -> list[Kaart]:
    """Kaarten die in Wunderkammer vastzitten, zwakste eerst; met `refs` alleen die over deze artikelen."""
    q = (select(Kaart).join(Leerlijst).join(KaartStand).where(Leerlijst.profiel_id == profiel_id, Kaart.status.is_(None),
                                                             Kaart.actief.is_(True), KaartStand.missers > 0)
         .options(selectinload(Kaart.stand), selectinload(Kaart.lijst)).order_by(KaartStand.missers.desc(), Kaart.id))
    if refs is not None:
        sleutels = {(r.stelsel, r.wet or None, r.nummer) for r in refs}
        if not sleutels:
            return []
        q = q.where(Kaart.nummer.in_({n for _s, _w, n in sleutels}))
        return [k for k in db.scalars(q).all() if fase(k) == "vastzit" and (k.stelsel_code, k.wet or None, k.nummer) in sleutels][:limiet]
    return [k for k in db.scalars(q.limit(limiet * 3)).all() if fase(k) == "vastzit"][:limiet]


def bewaarde_bronnen(db: Session, profiel_id: int) -> set[int]:
    return set(db.scalars(select(Kaart.bron_id).join(Leerlijst).where(Leerlijst.profiel_id == profiel_id, Kaart.bron_id.is_not(None))).all())


def _sleutel(soort, stelsel, wet, nummer, doel, bron_id, zaak, vraag) -> tuple:
    """Waar een kaart over gaat: het artikel, het arrest (bron of zaaknaam) of, bij een vrije kaart, de vraag."""
    if soort in ARTIKELSOORTEN:
        return (soort, stelsel, wet or None, nummer, doel)
    if soort in ARRESTSOORTEN:
        return (soort, bron_id) if bron_id else (soort, None, (zaak or "").strip().lower())
    return (soort, (vraag or "").strip().lower())


def maak_kaarten(
    db: Session,
    lijst: Leerlijst,
    soorten: list[str],
    ref: Ref | None = None,
    bron: Bron | None = None,
    doelen: list[str] | None = None,
    **velden,
) -> list[Kaart]:
    """Kaarten van de gekozen soorten; een kaart die al in de lijst staat (zelfde soort en onderwerp) komt er niet nog eens bij."""
    bestaand = {_sleutel(k.soort, k.stelsel_code, k.wet, k.nummer, k.doel_stelsel, k.bron_id, k.zaak, k.vraag) for k in lijst.kaarten}
    velden = {k: (v.strip() or None) if isinstance(v, str) else v for k, v in velden.items()}
    if bron is not None:
        velden.setdefault("zaak", None)
        velden["zaak"] = velden["zaak"] or bron.citeertitel
        velden["vindplaats"] = velden.get("vindplaats") or bron.vindplaats
    uit = []
    for soort in soorten:
        for doel in (doelen or [None]) if soort == "tegenhanger" else [None]:
            sleutel = _sleutel(soort, ref.stelsel if ref else None, ref.wet if ref else None, ref.nummer if ref else None, doel,
                               bron.id if bron else None, velden.get("zaak"), velden.get("vraag"))
            if soort in ARTIKELSOORTEN and ref is None or soort in ARRESTSOORTEN and not (bron or velden.get("zaak")):
                continue
            if sleutel in bestaand:
                continue
            bestaand.add(sleutel)
            k = Kaart(uid=nieuwe_uid(), lijst=lijst, soort=soort, doel_stelsel=doel, bron=bron, **velden)
            if ref is not None and soort in ARTIKELSOORTEN:
                k.stelsel_code, k.wet, k.nummer = ref.stelsel, ref.wet, ref.nummer
            db.add(k)
            uit.append(k)
    db.flush()
    return uit


class Bouwer:
    """Bouwt de zijden van kaarten; houdt wettekst en plaatsers per verzoek vast."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.ctx = corr.Context(db)
        self.namen = {s.code: s.naam for s in db.scalars(select(Stelsel)).all()}
        self._thema_s: dict[tuple, list] = {}

    def _artikel(self, ref: Ref):
        return corr.wettekst_artikel(self.db, ref)

    def _kop(self, ref: Ref, wa) -> str:
        return f"**{ref.citeer}**" + (f" · {wa.opschrift}" if wa and wa.opschrift else "")

    def _tekst(self, ref: Ref, wa) -> str:
        t = self.ctx.tekst(ref)
        return t.tekst if t and t.tekst else _("(geen wettekst ingelezen)")

    def zijden(self, k: Kaart) -> Zijden:
        ref = ref_van(k)
        wa = self._artikel(ref) if ref else None
        url = ref.url if ref else (f"/bronnen/{k.bron_id}" if k.bron_id else None)
        voor = achter = ""
        if k.soort == "artikel" and ref:
            voor = k.vraag or f"**{ref.citeer}**\n\n{_('Wat staat erin?')}"
            achter = f"{self._kop(ref, wa)}\n\n{self._tekst(ref, wa)}"
        elif k.soort == "kern" and ref:
            omschrijving = k.vraag or (wa.opschrift if wa and wa.opschrift else None) or _("(schrijf bij deze kaart een omschrijving)")
            wet = ref.wet_naam or self.namen.get(ref.stelsel, ref.stelsel)
            voor = f"{omschrijving}\n\n{_('Welk artikel? ({wet})', wet=wet)}"
            achter = f"{self._kop(ref, wa)}\n\n{self._tekst(ref, wa)}"
        elif k.soort == "plaats" and ref:
            pad = self.ctx.pad(ref)
            voor = k.vraag or _("Waar staat {artikel}?", artikel=f"**{ref.citeer}**")
            achter = (" › ".join(x.label for x in pad) if pad else _("(niet in de systematiek geplaatst)")) + (f"\n\n{self._kop(ref, wa)}" if wa else "")
        elif k.soort == "tegenhanger" and ref:
            doel = self.namen.get(k.doel_stelsel or "", k.doel_stelsel or "?")
            voor = k.vraag or f"{self._kop(ref, wa)}\n\n{_('Tegenhanger in {stelsel}?', stelsel=doel)}"
            achter = self._tegenhanger(ref, k.doel_stelsel)
        elif k.soort in ARRESTSOORTEN:
            zaak = k.zaak or (k.bron.citeertitel if k.bron else "?")
            vindplaats = k.vindplaats or (k.bron.vindplaats if k.bron else None)
            titel = f"**{zaak}**" + (f" · {vindplaats}" if vindplaats else "")
            kern = k.bron.tekst if k.bron and k.bron.tekst else None
            regel = k.antwoord or ""
            if k.soort == "arrest":
                voor = k.vraag or f"{titel}\n\n{_('Wat besliste de rechter?')}"
                delen = [regel, f"> {kern}" if kern else "", f"*{_('Feiten')}:* {k.feiten}" if k.feiten else ""]
            else:
                voor = k.vraag or f"{k.feiten or _('(schrijf bij deze kaart de feiten)')}\n\n{_('Welk arrest?')}"
                delen = [titel, regel, f"> {kern}" if kern else ""]
            achter = "\n\n".join(d for d in delen if d) or _("(schrijf bij deze kaart de rechtsregel)")
        else:  # vrij, of een artikelkaart waarvan het artikel ontbreekt
            voor, achter = k.vraag or "?", k.antwoord or ""
        if k.notitie:
            achter += f"\n\n---\n\n{k.notitie}"
        return Zijden(voor, achter, url)

    def _tegenhanger(self, ref: Ref, doel: str | None) -> str:
        sleutel = (ref.stelsel, ref.wet, ref.nummer)
        if sleutel not in self._thema_s:
            self._thema_s[sleutel] = corr.thema_s_voor(self.db, ref.stelsel, ref.nummer, ref.wet)
        regels = []
        for c, _eigen in self._thema_s[sleutel]:
            leden = c.voor(doel or "")
            if not leden:
                continue
            delen = []
            for a in leden:
                if a.nummer is None:
                    delen.append(f"⚖ {(a.opmerking or _('rechtspraak')).split(': ')[0]}")
                else:
                    wa = self._artikel(a.ref)
                    delen.append(f"**{a.ref.citeer}**" + (f" ({wa.opschrift})" if wa and wa.opschrift else ""))
            regels.append(f"- *{c.titel}*: " + "; ".join(delen))
        return "\n".join(regels) if regels else _("Geen tegenhanger in de correspondentietabel.")

    def tegenhangers(self, ref: Ref) -> list[dict]:
        """De artikelen in andere stelsels die volgens de correspondentietabel dezelfde vraag beantwoorden."""
        sleutel = (ref.stelsel, ref.wet, ref.nummer)
        if sleutel not in self._thema_s:
            self._thema_s[sleutel] = corr.thema_s_voor(self.db, ref.stelsel, ref.nummer, ref.wet)
        uit, gezien = [], set()
        for c, _eigen in self._thema_s[sleutel]:
            for a in c.artikelen:
                if a.stelsel_code == ref.stelsel or a.nummer is None or (a.stelsel_code, a.wet, a.nummer, a.tot) in gezien:
                    continue
                gezien.add((a.stelsel_code, a.wet, a.nummer, a.tot))
                uit.append(dict(stelsel=a.stelsel_code, wet=a.wet, nummer=a.nummer, citeer=a.ref.citeer, url=a.ref.url,
                                thema=c.titel, rol=a.rol))
        return uit

    def html(self, k: Kaart) -> tuple[str, str, Zijden]:
        z = self.zijden(k)
        return str(md.render(z.voor)), str(md.render(z.achter)), z


def oefen(db: Session, k: Kaart, gekend: bool) -> None:
    k.gekend = gekend
    k.geoefend = now()


def _datum(s) -> datetime | None:
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d.replace(tzinfo=timezone.utc) if d.tzinfo is None else d.astimezone(timezone.utc)


def zet_stand(db: Session, items: list[dict], alleen_gekoppeld: bool = False) -> int:
    """Stand uit Wunderkammer bijwerken: [{uid, due, stability, reps, lapses, last_review, last_rating}].
    `alleen_gekoppeld`: kaarten van profielen die de koppeling uit hebben gezet blijven buiten beschouwing."""
    q = select(Kaart).where(Kaart.uid.in_([str(i.get("uid")) for i in items if isinstance(i, dict)]))
    if alleen_gekoppeld:
        q = q.join(Leerlijst).join(Profiel, Profiel.id == Leerlijst.profiel_id).where(Profiel.wunderkammer.is_(True))
    per_uid = {k.uid: k for k in db.scalars(q).all()}
    n = 0
    for i in items:
        k = per_uid.get(str(i.get("uid"))) if isinstance(i, dict) else None
        if k is None:
            continue
        st = k.stand or KaartStand(kaart_id=k.id)
        st.due = _datum(i.get("due"))
        st.stabiliteit = i.get("stability")
        st.herhalingen = int(i.get("reps") or 0)
        st.missers = int(i.get("lapses") or 0)
        st.laatst = _datum(i.get("last_review"))
        st.laatste_score = i.get("last_rating")
        st.bijgewerkt = now()
        if k.stand is None:
            db.add(st)
            k.stand = st
        n += 1
    return n
