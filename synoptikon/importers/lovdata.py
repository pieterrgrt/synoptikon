"""NO: Lovdata, de gratis dataset "Gjeldende lover" (api.lovdata.no, NLOD 2.0), geconsolideerd.

`https://api.lovdata.no/v1/publicData/get/gjeldende-lover.tar.bz2` (±6 MB) bevat alle geldende wetten
als XHTML, één bestand per wet (`nl/nl-19180531-004.xml` voor LOV-1918-05-31-4), bijgewerkt met de
wijzigingen. De losse pagina's op lovdata.no zijn niet voor automatisch ophalen bedoeld; de dataset wel.
Eén download per proces, daarna lezen we de wetten uit het geheugen.

Structuur: <section class="section"> met een <h2>/<h3>-kop (Del, Kapittel) en daarin
<article class="legalArticle">, met een kop (<span class="legalArticleValue">"§ 1-1"</span>,
<span class="legalArticleTitle">) en leden (<article class="numberedLegalP">"(1) …"</article> of legalP),
opsommingen als <li data-li-identifier="a)">. Wijzigingsnoten (changesToParent), voetnoten en
voetnootverwijzingen vallen weg.

Nummering: de nieuwere wetten tellen per hoofdstuk met een streepje (`§ 1-1` tvisteloven, `§ 3-1` aksjeloven);
dat is het nummer zoals het in de wet staat. Letters met een spatie: `§ 9 a`.

Versie: "endret ved lov/2025-06-20-106 fra 2026-01-01" (laatste wijziging en inwerkingtreding), of de
datumcode van de wet zelf als ze nooit gewijzigd is.
"""
from __future__ import annotations

import io
import re
import tarfile
import xml.etree.ElementTree as ET

from . import Artikel, Geparseerd
from .http import client

DATASET = "https://api.lovdata.no/v1/publicData/get/gjeldende-lover.tar.bz2"
WEB = "https://lovdata.no/dokument/NL/lov/{id}"
_cache: dict[str, bytes] = {}


def _klasse(el: ET.Element) -> str:
    return el.get("class", "")


def _weg(el: ET.Element) -> bool:
    return _klasse(el) in ("changesToParent", "footnotes", "footnotereference", "legalArticleHeader") or el.tag in ("footer", "sup", "h4", "h5")


def _tekst(el: ET.Element) -> str:
    delen: list[str] = []

    def loop(e: ET.Element) -> None:
        if e.text:
            delen.append(e.text)
        for k in e:
            if not _weg(k) and k.tag not in ("ul", "ol"):
                loop(k)
            if k.tail:
                delen.append(k.tail)

    loop(el)
    return re.sub(r"\s+", " ", "".join(delen)).strip()


def _lid(el: ET.Element) -> str:
    """Eén ledd: de tekst, met opsommingen elk op een eigen regel ("a) …")."""
    regels = [_tekst(el)]
    for lijst in el.iter():
        if lijst.tag not in ("ul", "ol"):
            continue
        for li in lijst.findall("li"):
            teken = li.get("data-li-identifier") or "-"
            regels.append(f"{teken} {_tekst(li)}".strip())
    return "\n".join(r for r in regels if r)


def _nummer(art: ET.Element) -> str | None:
    kop = next((k for k in art if _klasse(k) == "legalArticleHeader"), None)
    waarde = next((s for s in kop.iter("span") if _klasse(s) == "legalArticleValue"), None) if kop is not None else None
    m = re.match(r"§\s*(\d+(?:-\d+)?(?:\s?[a-zæøå](?![a-zæøå]))?)", (waarde.text or "").strip()) if waarde is not None else None
    return re.sub(r"(\d)\s?([a-zæøå])$", r"\1 \2", m.group(1)) if m else None


def _opschrift(art: ET.Element) -> str | None:
    kop = next((k for k in art if _klasse(k) == "legalArticleHeader"), None)
    titel = next((s for s in kop.iter("span") if _klasse(s) == "legalArticleTitle"), None) if kop is not None else None
    return re.sub(r"\s+", " ", "".join(titel.itertext())).strip().rstrip(".") or None if titel is not None else None


def _meta(root: ET.Element, klasse: str) -> str:
    for dd in root.iter("dd"):
        if _klasse(dd) == klasse:
            return re.sub(r"\s+", " ", "".join(dd.itertext())).strip()
    return ""


def parse(data: bytes, id: str, bron_url: str | None = None, titel: str | None = None) -> Geparseerd:
    root = ET.fromstring(data)
    main = next((e for e in root.iter("main")), root)
    artikelen: list[Artikel] = []
    gezien: set[str] = set()

    def loop(el: ET.Element, pad: list[str]) -> None:
        for k in el:
            if _weg(k):
                continue
            if k.tag == "section":
                kop = next((h for h in k if h.tag in ("h2", "h3", "h4", "h5")), None)
                tekst = re.sub(r"\s+", " ", "".join(kop.itertext())).strip().rstrip(".") if kop is not None else ""
                loop(k, [*pad, tekst] if tekst else pad)
            elif k.tag == "article" and _klasse(k) == "legalArticle":
                nr = _nummer(k)
                if nr is None or nr in gezien:
                    continue
                gezien.add(nr)
                leden = [_lid(l) for l in k if l.tag == "article" and _klasse(l) in ("legalP", "numberedLegalP", "defaultP")]
                artikelen.append(Artikel(nummer=nr, tekst="\n\n".join(l for l in leden if l) or "(Opphevet)",
                                         opschrift=_opschrift(k), pad=" › ".join(pad) or None))
            elif k.tag not in ("h1", "h2", "h3", "header"):
                loop(k, pad)

    loop(main, [])
    gewijzigd = _meta(root, "lastChangedBy")
    versie = f"endret ved {gewijzigd}" if gewijzigd else (_meta(root, "legacyID") or id)
    if titel is None:
        titel = _meta(root, "title") or id
    return Geparseerd(wet_id=id, titel=titel, versie=versie, bron_url=bron_url or WEB.format(id=id), artikelen=artikelen,
                      ruw=data, ruw_extensie="xml")


def _bestand(id: str) -> str:
    """'1918-05-31-4' → 'nl/nl-19180531-004.xml'."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})-(\d+)", id)
    if not m:
        raise ValueError(f"onbekende Lovdata-id: {id!r} (verwacht jjjj-mm-dd-nr)")
    return f"nl/nl-{m.group(1)}{m.group(2)}{m.group(3)}-{int(m.group(4)):03d}.xml"


def _dataset() -> dict[str, bytes]:
    if not _cache:
        with client(timeout=300.0) as c:
            r = c.get(DATASET)
            r.raise_for_status()
        with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:bz2") as tar:
            for lid in tar.getmembers():
                if lid.isfile() and lid.name.endswith(".xml"):
                    f = tar.extractfile(lid)
                    if f is not None:
                        _cache[lid.name] = f.read()
    return _cache


def haal_op(id: str, titel: str | None = None) -> Geparseerd:
    """`id`: de datumcode zonder 'LOV-', bijv. '1918-05-31-4' (avtaleloven)."""
    id = id.removeprefix("LOV-").removeprefix("lov/")
    data = _dataset().get(_bestand(id))
    if data is None:
        raise ValueError(f"{id} staat niet in Gjeldende lover")
    return parse(data, id, WEB.format(id=id), titel)
