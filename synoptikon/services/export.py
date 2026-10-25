"""Export van een Vraag naar Markdown en PDF, en van begrippenparen naar JSON.

PDF gaat via WeasyPrint uit dezelfde HTML als de printweergave. WeasyPrint
wordt pas geïmporteerd bij gebruik; ontbreekt het, dan geeft de app een
nette foutmelding en blijft de rest werken.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone

from ..models import Begrip, BegripRelatie, Bron, Vraag


def _bron_kop(b: Bron) -> str:
    kop = b.citeertitel
    if b.titel and b.titel != b.citeertitel:
        kop += f" — {b.titel}"
    return kop


def _bron_meta(b: Bron) -> str:
    delen = []
    if b.vindplaats:
        delen.append(f"{b.vindplaats_type or 'vindplaats'}: {b.vindplaats}")
    if b.geldig_van or b.geldig_tot:
        van = b.geldig_van.isoformat() if b.geldig_van else "…"
        tot = b.geldig_tot.isoformat() if b.geldig_tot else "heden"
        delen.append(f"geldig {van} – {tot}")
    if b.url:
        delen.append(f"<{b.url}>")
    return "; ".join(delen)


def vraag_naar_markdown(vraag: Vraag, stelsels: list[str] | None = None, vertaal_taal: str | None = "nl") -> str:
    regels: list[str] = [f"# {vraag.titel}", ""]
    meta = []
    if vraag.rechtsgebied:
        meta.append(f"**Rechtsgebied:** {vraag.rechtsgebied}")
    if vraag.tag_list:
        meta.append("**Tags:** " + ", ".join(vraag.tag_list))
    if meta:
        regels += ["  ".join(meta), ""]
    if vraag.omschrijving:
        regels += [vraag.omschrijving.strip(), ""]

    for antwoord in vraag.antwoorden:
        if stelsels and antwoord.stelsel_code not in stelsels:
            continue
        regels += [f"## {antwoord.stelsel.naam}", ""]
        if antwoord.kern:
            regels += [f"> {antwoord.kern}", ""]
        if antwoord.bronnen:
            regels += ["### Bronnen", ""]
            for ab in antwoord.bronnen:
                b = ab.bron
                rol = f" *({ab.rol})*" if ab.rol else ""
                regels += [f"#### {_bron_kop(b)}{rol}", ""]
                m = _bron_meta(b)
                if m:
                    regels += [f"<small>{m}</small>", ""]
                if b.tekst:
                    regels += ["> " + b.tekst.strip().replace("\n", "\n> "), ""]
                if vertaal_taal and b.taal != vertaal_taal:
                    v = b.vertaling(vertaal_taal)
                    if v:
                        regels += [f"*Vertaling ({v.herkomst}):* " + v.tekst.strip().replace("\n", " "), ""]
                if ab.notitie:
                    regels += [ab.notitie.strip(), ""]
        if antwoord.analyse:
            regels += ["### Analyse", "", antwoord.analyse.strip(), ""]

    begrippen = [vb.begrip for vb in vraag.begrippen]
    if begrippen:
        regels += ["## Begrippen", ""]
        for g in sorted(begrippen, key=lambda g: (g.stelsel.volgorde, g.term)):
            regels.append(f"- **{g.term}** ({g.stelsel_code})" + (f": {g.definitie.strip()}" if g.definitie else ""))
            for r in g.relaties:
                ander = r.andere(g)
                regels.append(f"  - {r.type_label} → {ander.term} ({ander.stelsel_code})" + (f": {r.toelichting}" if r.toelichting else ""))
        regels.append("")

    if vraag.notities:
        regels += ["## Notities", ""]
        for n in vraag.notities:
            kop = n.aangemaakt.strftime("%Y-%m-%d") + (f" · {n.stelsel_code}" if n.stelsel_code else "")
            regels += [f"**{kop}** — {n.tekst.strip()}", ""]

    regels += ["---", f"*Synoptikon, geëxporteerd {date.today().isoformat()}*", ""]
    return "\n".join(regels)


def html_naar_pdf(html: str, base_url: str) -> bytes:
    try:
        from weasyprint import HTML  # type: ignore
    except ImportError as e:  # pragma: no cover - afhankelijk van systeembibliotheken
        raise RuntimeError("WeasyPrint is niet geïnstalleerd; gebruik de Markdown-export of print de pagina.") from e
    return HTML(string=html, base_url=base_url).write_pdf()


# --- Wunderkammer ---------------------------------------------------------
#
# Formaat (versie 1), bewust eenvoudig en los van Wunderkammer-internals:
#
# {
#   "format": "synoptikon-begrippenparen",
#   "version": 1,
#   "exported": "2026-10-25T12:00:00Z",
#   "pairs": [
#     {
#       "id": "nl:levering|de:Übergabe",
#       "front": {"term": "levering", "system": "NL", "lang": "nl", "definition": "…", "reference": "art. 3:84, 3:90 BW"},
#       "back":  {"term": "Übergabe", "system": "DE", "lang": "de", "definition": "…", "reference": "§ 929 BGB"},
#       "relation": "deels",                       # equivalent | deels | faux_ami | geen
#       "relation_label": "deels overlappend",
#       "note": "…",                               # toelichting bij de relatie
#       "questions": ["eigendomsoverdracht-roerende-zaken"],
#       "tags": ["NL", "DE", "deels", "goederenrecht"]
#     }
#   ]
# }
#
# Een importer maakt per paar één kaart (front → back) of twee (ook omgekeerd);
# `id` is stabiel zolang termen en stelsels niet veranderen.


def _begrip_dict(g: Begrip) -> dict:
    return {
        "term": g.term,
        "system": g.stelsel_code,
        "lang": g.taal,
        "definition": (g.definitie or "").strip() or None,
        "reference": g.vindplaats,
    }


def begrippenparen_json(relaties: list[BegripRelatie]) -> str:
    pairs = []
    for r in relaties:
        vragen = sorted({vb.vraag.slug for vb in r.van.vragen} | {vb.vraag.slug for vb in r.naar.vragen})
        gebieden = sorted({vb.vraag.rechtsgebied for vb in [*r.van.vragen, *r.naar.vragen] if vb.vraag.rechtsgebied})
        pairs.append(
            {
                "id": f"{r.van.taal}:{r.van.term}|{r.naar.taal}:{r.naar.term}",
                "front": _begrip_dict(r.van),
                "back": _begrip_dict(r.naar),
                "relation": r.type,
                "relation_label": r.type_label,
                "note": (r.toelichting or "").strip() or None,
                "questions": vragen,
                "tags": sorted({r.van.stelsel_code, r.naar.stelsel_code, r.type, *gebieden}),
            }
        )
    doc = {
        "format": "synoptikon-begrippenparen",
        "version": 1,
        "exported": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "pairs": pairs,
    }
    return json.dumps(doc, ensure_ascii=False, indent=2)
