"""Leerlijsten en kaarten.

Een kaart bewaart alleen waar ze over gaat (een artikel, een arrest of een eigen vraag) en wat je er zelf bij schrijft.
Voor- en achterkant worden telkens opnieuw opgebouwd uit de actuele wettekst, systematiek en correspondentietabel:
een nieuwe versie van de wet komt zo vanzelf op de kaart, hier en in Wunderkammer.
"""
from __future__ import annotations

import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .. import md
from ..i18n import _, in_taal, rechtstaal
from ..models import ARRESTSOORTEN, ARTIKELSOORTEN, FASEN, Bron, Kaart, KaartStand, Leerlijst, Markering, Profiel, Stelsel, now
from . import correspondentie as corr
from . import markeringen as mk
from . import wk  # noqa: F401  (seint Wunderkammer na een wijziging in de kaarten)
from .artikelen import Ref


KERN_MAX = 500  # tekens van de kerntekst die als samenhang onder de rechtsregel komen


def _inkorten(tekst: str, max_tekens: int = KERN_MAX) -> str:
    """Tot een zinseinde (of woord) onder `max_tekens`, met …; korter blijft zoals het is."""
    tekst = re.sub(r"\s+", " ", tekst).strip()
    if len(tekst) <= max_tekens:
        return tekst
    kop = tekst[:max_tekens]
    zin = max(kop.rfind(". "), kop.rfind("; "))
    return (kop[:zin + 1] if zin > max_tekens // 2 else kop[:kop.rfind(" ")]) + " …"


LID_MIN = 400  # een artikel korter dan dit (tekens) blijft één kaart
_LID_HAAK = re.compile(r"^[ \t]*\((\d+[a-z]?)\)[ \t]+", re.M)  # (1) Text …  (BGB, GG, EU)
_LID_PUNT = re.compile(r"^[ \t]*(\d+[a-z]?)\.[ \t]+", re.M)  # 1. Text …  (BW)


def leden(tekst: str) -> list[tuple[str, str]]:
    """De leden van een artikel als [(nummer, tekst)]; leeg als het geen opeenvolgende leden 1, 2, … heeft.

    Alleen de eerste opmaak telt: '(1) …' of '1. …'; genummerde onderdelen binnen een lid ('1. …' in § 823 Abs. 2) blijven in
    het lid."""
    for patroon in (_LID_HAAK, _LID_PUNT):
        m = list(patroon.finditer(tekst or ""))
        nrs = [x.group(1) for x in m]
        if len(m) >= 2 and nrs[0] == "1" and [int(re.match(r"\d+", n).group()) for n in nrs] == sorted({int(re.match(r"\d+", n).group()) for n in nrs}):
            return [(n, tekst[x.start():(m[i + 1].start() if i + 1 < len(m) else len(tekst))].strip()) for i, (n, x) in enumerate(zip(nrs, m))]
    return []


@dataclass
class Zijden:
    voor: str  # markdown
    achter: str  # markdown
    url: str | None  # pad in Synoptikon om verder te lezen
    regel: str = ""  # voorbeeld van een arrest: de rechtsregel uit je markeringen, als voorstel
    kaarten: int = 1  # voorbeeld: hoeveel kaarten er bij ☆ uit komen (één per lid bij een lang artikel)


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


def _sleutel(soort, stelsel, wet, nummer, doel, bron_id, zaak, vraag, lid=None) -> tuple:
    """Waar een kaart over gaat: het artikel (en lid), het arrest (bron of zaaknaam) of, bij een vrije kaart, de vraag."""
    if soort in ARTIKELSOORTEN:
        return (soort, stelsel, wet or None, nummer, doel) + ((lid,) if lid else ())
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
    per_lid: bool = False,
    **velden,
) -> list[Kaart]:
    """Kaarten van de gekozen soorten; een kaart die al in de lijst staat (zelfde soort en onderwerp) komt er niet nog eens bij.

    `per_lid`: een lang artikel met leden wordt één artikelkaart per lid (één kaart = één feit), tenzij het hele artikel
    al in de lijst staat."""
    bestaand = {_sleutel(k.soort, k.stelsel_code, k.wet, k.nummer, k.doel_stelsel, k.bron_id, k.zaak, k.vraag, k.lid) for k in lijst.kaarten}
    velden = {k: (v.strip() or None) if isinstance(v, str) else v for k, v in velden.items()}
    if bron is not None:
        velden.setdefault("zaak", None)
        velden["zaak"] = velden["zaak"] or bron.citeertitel
        velden["vindplaats"] = velden.get("vindplaats") or bron.vindplaats
        if not velden.get("antwoord") and bron.id:  # de rechtsregel die je in de uitspraak aanwees (voor het vak van de lijst)
            velden["antwoord"] = mk.kern_tekst(db, lijst.profiel_id, bron.id, lijst.vak) or None
    uit = []
    for soort in soorten:
        for doel in (doelen or [None]) if soort == "tegenhanger" else [None]:
            if soort in ARTIKELSOORTEN and ref is None or soort in ARRESTSOORTEN and not (bron or velden.get("zaak")):
                continue
            hele = _sleutel(soort, ref.stelsel if ref else None, ref.wet if ref else None, ref.nummer if ref else None, doel,
                            bron.id if bron else None, velden.get("zaak"), velden.get("vraag"))
            if hele in bestaand:
                continue
            for lid in (leden_van(db, ref) if per_lid and soort == "artikel" else None) or [None]:
                sleutel = hele + ((lid,) if lid else ())
                if sleutel in bestaand:
                    continue
                bestaand.add(sleutel)
                k = Kaart(uid=nieuwe_uid(), lijst=lijst, soort=soort, doel_stelsel=doel, bron=bron, lid=lid, **velden)
                if ref is not None and soort in ARTIKELSOORTEN:
                    k.stelsel_code, k.wet, k.nummer = ref.stelsel, ref.wet, ref.nummer
                db.add(k)
                uit.append(k)
    db.flush()
    return uit


def leden_van(db: Session, ref: Ref) -> list[str]:
    """Lidnummers van een lang artikel (korter dan LID_MIN tekens of zonder leden: leeg)."""
    t = corr.Context(db).tekst(ref)
    return [n for n, _t in leden(t.tekst)] if t and t.tekst and len(t.tekst) > LID_MIN else []


class Bouwer:
    """Bouwt de zijden van kaarten; houdt wettekst en plaatsers per verzoek vast."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.ctx = corr.Context(db)
        self.namen = {s.code: s.naam for s in db.scalars(select(Stelsel)).all()}
        self._thema_s: dict[tuple, list] = {}
        self._mk: dict[int, list] = {}

    def _markeringen(self, k: Kaart, ref: Ref) -> list:
        """Wat je in dit artikel aanwees voor het vak van de lijst van de kaart (een kaart die nog niet bewaard is: niets)."""
        if k.lijst is None:
            return []
        if k.lijst.profiel_id not in self._mk:
            self._mk[k.lijst.profiel_id] = list(self.db.scalars(select(Markering).where(
                Markering.profiel_id == k.lijst.profiel_id, Markering.bron_id.is_(None), Markering.stelsel_code.is_not(None))))
        return mk.voor_vak([m for m in self._mk[k.lijst.profiel_id] if (m.stelsel_code, m.wet or None, m.nummer) == (ref.stelsel, ref.wet or None, ref.nummer)],
                           k.lijst.vak)

    def _artikel(self, ref: Ref):
        return corr.wettekst_artikel(self.db, ref)

    def _kop(self, ref: Ref, wa) -> str:
        return f"**{ref.citeer}**" + (f" · {wa.opschrift}" if wa and wa.opschrift else "")

    def _tekst(self, ref: Ref, wa, lid: str | None = None) -> str:
        t = self.ctx.tekst(ref)
        if not (t and t.tekst):
            return _("(geen wettekst ingelezen)")
        # Een kaart voor één lid toont alleen dat lid; is het lid uit een nieuwe versie van de wet verdwenen, dan het hele artikel.
        return next((x for n, x in leden(t.tekst) if n == lid), t.tekst) if lid else t.tekst

    def zijden(self, k: Kaart) -> Zijden:
        """De twee zijden van een kaart, opgebouwd in de rechtstaal.

        De vaste zinnen ('Wat staat erin?') horen bij de wettekst en niet bij de interface: wie de Duitse AEUV
        leert, leest er geen Nederlandse vraag boven."""
        with in_taal(rechtstaal()):
            return self._zijden(k)

    def _zijden(self, k: Kaart) -> Zijden:
        ref = ref_van(k)
        wa = self._artikel(ref) if ref else None
        url = ref.url if ref else (f"/bronnen/{k.bron_id}" if k.bron_id else None)
        voor = achter = ""
        if k.soort == "artikel" and ref:
            lid = f" {_('lid {lid}', lid=k.lid)}" if k.lid else ""
            voor = k.vraag or f"**{ref.citeer}**{lid}\n\n{_('Wat staat erin?')}"
            ms = self._markeringen(k, ref)
            # De kern en voorwaarden die je aanwees staan vet; een 'let op' komt als regel eronder.
            achter = f"{self._kop(ref, wa)}{lid}\n\n{mk.markeer_md(self._tekst(ref, wa, k.lid), ms)}"
            achter += "".join(f"\n\n*{_('Let op')}:* {m.notitie or m.quote}" for m in ms if m.soort == "let_op" and (not k.lid or m.quote in self._tekst(ref, wa, k.lid)))
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
            kern = f"> {_inkorten(k.bron.tekst)}" if k.bron and k.bron.tekst else ""
            feiten = f"*{_('Feiten')}:* {k.feiten}" if k.feiten else ""
            regel = k.antwoord or ""
            if k.soort == "arrest":
                # Eén feit per kaart: de rechtsregel is het antwoord; feiten en kerntekst staan eronder als samenhang.
                voor = k.vraag or f"{titel}\n\n{_('Welke rechtsregel volgt uit dit arrest?')}"
                samenhang = "\n\n".join(d for d in (feiten, kern) if d)
                if regel:
                    achter = regel + (f"\n\n*{_('Samenhang')}*\n\n{samenhang}" if samenhang else "")
                else:  # nog geen rechtsregel aangeduid: dan is de kerntekst het beste wat er is
                    achter = samenhang or _("(schrijf bij deze kaart de rechtsregel)")
            else:
                voor = k.vraag or f"{k.feiten or _('(schrijf bij deze kaart de feiten)')}\n\n{_('Welk arrest?')}"
                achter = "\n\n".join(d for d in (titel, regel, kern) if d)
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


def voorbeeld(db: Session, soort: str, ref: Ref | None = None, bron: Bron | None = None, **velden) -> Zijden:
    """De zijden van een kaart die nog niet bestaat (het bewaarvenster): een kaart die niet in de sessie komt."""
    lid = leden_van(db, ref) if ref is not None and soort == "artikel" else []
    k = Kaart(soort=soort, bron=bron, lid=lid[0] if lid else None, **velden)
    if ref is not None:
        k.stelsel_code, k.wet, k.nummer = ref.stelsel, ref.wet, ref.nummer
    z = Bouwer(db).zijden(k)
    z.kaarten = len(lid) or 1
    return z


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
