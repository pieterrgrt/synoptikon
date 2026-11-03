"""Markdown → HTML voor analyses, notities en definities."""
from __future__ import annotations

import re

from markdown_it import MarkdownIt
from markupsafe import Markup

_md = MarkdownIt("commonmark", {"typographer": True, "linkify": False}).enable(["table", "strikethrough", "replacements", "smartquotes"])
# Juridische teksten gebruiken §, ′ en Franse guillemets; laat de
# typografische vervangingen dat ongemoeid.
_md.options["quotes"] = "“”‘’"


def render(tekst: str | None) -> Markup:
    if not tekst:
        return Markup("")
    return Markup(_md.render(tekst))


def render_inline(tekst: str | None) -> Markup:
    if not tekst:
        return Markup("")
    return Markup(_md.renderInline(tekst))


# --- één lid uitlichten --------------------------------------------------------------------------------------------
# Een wettekst staat per lid als blok: "1. Hij die …" (NL), "(1) Wer …" (DE, CH, EU). Een blok zonder nummer hoort bij
# het lid ervoor (de opsomming onder § 311 Abs. 2). Wordt een lid aangehaald ("6:162 lid 2", "§ 823 Abs. 1"), dan
# krijgt dat lid de nadruk en blijven de andere leesbaar maar stil.

_LID_IN_DETAIL = re.compile(r"(?:\b(?:lid|leden|Abs\.?|Absatz|al\.?|alinéa|comma|apartado|par\.?|para\.?)\s*|^\s*\()(\d+[a-z]?)", re.I)
_LID_BEGIN = re.compile(r"^\s*(?:\((\d+[a-z]?)\)|(\d+[a-z]?)\.\s)")


def lid_uit(detail: str | None) -> str | None:
    """"lid 2" → "2", "Abs. 1 S. 2" → "1", "(1)(a)" → "1"."""
    m = _LID_IN_DETAIL.search(detail or "")
    return m.group(1).lower() if m else None


def render_lid(tekst: str | None, detail: str | None) -> Markup:
    """Als `render`, maar met het lid uit `detail` uitgelicht (class "gekozen"); zonder herkenbaar lid gewoon `render`."""
    n = lid_uit(detail)
    if not tekst or not n:
        return render(tekst)
    groepen: list[list] = []
    stijl = None  # "(" of ".": wie met (1) nummert, heeft onder een lid opsommingen met 1., 2. (§ 311 Abs. 2 BGB)
    for blok in re.split(r"\n\s*\n", tekst):
        m = _LID_BEGIN.match(blok)
        if m and stijl is None:
            stijl = "(" if m.group(1) else "."
        if m and (stijl == "(") == bool(m.group(1)):
            groepen.append([(m.group(1) or m.group(2)).lower(), [blok]])
        elif groepen:
            groepen[-1][1].append(blok)
        else:
            groepen.append([None, [blok]])
    if n not in [g[0] for g in groepen] or len(groepen) < 2:
        return render(tekst)
    delen = []
    for nr, blokken in groepen:
        html = _md.render("\n\n".join(blokken))
        delen.append(f'<div class="lid-blok gekozen" aria-current="true">{html}</div>' if nr == n else f'<div class="lid-blok">{html}</div>')
    return Markup('<div class="met-lid">' + "".join(delen) + "</div>")
