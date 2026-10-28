#!/usr/bin/env bash
# Kaartvoorstellen uit notities: kopieert de notitiemap naar data/notities (de container kan niet bij de
# rclone-mount van de vault) en laat Synoptikon de nieuwe en gewijzigde notities verwerken.
#
# Gebruik:  scripts/notities.sh [--droog] [--max N]      (cron: 's nachts)
# Env:      NOTITIES_BRON (standaard ~/vault/Humboldt), SYNOPTIKON_CONTAINER (standaard synoptikon)
set -euo pipefail

HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BRON="${NOTITIES_BRON:-$HOME/vault/Humboldt}"
DOEL="$HIER/data/notities"
CONTAINER="${SYNOPTIKON_CONTAINER:-synoptikon}"

if [[ ! -d "$BRON" ]]; then
    echo "Notitiemap $BRON niet gevonden (vault niet gemount?)" >&2
    exit 1
fi
mkdir -p "$DOEL"
rsync -a --delete --include='*/' --include='*.md' --exclude='*' --prune-empty-dirs "$BRON/" "$DOEL/"
chmod -R a+rX "$DOEL"
echo "$(date -Is) notities"
docker exec "$CONTAINER" synoptikon notities "$@"
