#!/usr/bin/env bash
# Haalt de self-hosted lettertypen opnieuw op (Source Serif 4 en Source Sans 3,
# beide SIL OFL 1.1, Adobe). De bestanden staan al in git; dit script is er
# voor het geval je ze wilt verversen.
set -euo pipefail
DOEL="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/synoptikon/static/fonts"
mkdir -p "$DOEL"
B="https://raw.githubusercontent.com/adobe-fonts"
curl -fsSL -o "$DOEL/SourceSerif4Variable-Roman.ttf.woff2"  "$B/source-serif/release/WOFF2/VAR/SourceSerif4Variable-Roman.ttf.woff2"
curl -fsSL -o "$DOEL/SourceSerif4Variable-Italic.ttf.woff2" "$B/source-serif/release/WOFF2/VAR/SourceSerif4Variable-Italic.ttf.woff2"
curl -fsSL -o "$DOEL/SourceSans3VF-Upright.ttf.woff2"       "$B/source-sans/release/WOFF2/VF/SourceSans3VF-Upright.ttf.woff2"
curl -fsSL -o "$DOEL/SourceSans3VF-Italic.ttf.woff2"        "$B/source-sans/release/WOFF2/VF/SourceSans3VF-Italic.ttf.woff2"
curl -fsSL -o "$DOEL/LICENSE-SourceSerif4.md" "$B/source-serif/release/LICENSE.md"
curl -fsSL -o "$DOEL/LICENSE-SourceSans3.md"  "$B/source-sans/release/LICENSE.md"
ls -la "$DOEL"
