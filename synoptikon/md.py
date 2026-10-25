"""Markdown → HTML voor analyses, notities en definities."""
from __future__ import annotations

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
