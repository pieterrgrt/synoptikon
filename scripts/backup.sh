#!/usr/bin/env bash
# Back-up van de SQLite-database en de opgeslagen wetteksten naar een map
# die je kunt laten synchroniseren (Nextcloud, rsync, …).
#
# Gebruik:  scripts/backup.sh [DOELMAP]      (standaard ./backups)
# Env:      SYNOPTIKON_DATA_DIR (standaard ./data), BACKUP_KEEP (standaard 14),
#           BACKUP_ZONDER_WETTEKSTEN=1: alleen de database (scripts/storagebox.sh spiegelt de wetteksten los)
#
# De database wordt met `sqlite3 .backup` consistent gekopieerd (WAL-veilig);
# ontbreekt sqlite3 op de host, dan via Python. Wetteksten gaan als tar.gz.
set -euo pipefail

HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA="${SYNOPTIKON_DATA_DIR:-$HIER/data}"
DOEL="${1:-$HIER/backups}"
KEEP="${BACKUP_KEEP:-14}"
STEMPEL="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$DOEL"

DB="$DATA/synoptikon.db"
if [[ -f "$DB" ]]; then
    if command -v sqlite3 >/dev/null 2>&1; then
        sqlite3 "$DB" ".backup '$DOEL/synoptikon-$STEMPEL.db'"
    else
        python3 - "$DB" "$DOEL/synoptikon-$STEMPEL.db" <<'PY'
import sqlite3, sys
bron = sqlite3.connect(sys.argv[1]); doel = sqlite3.connect(sys.argv[2])
bron.backup(doel); doel.close(); bron.close()
PY
    fi
    gzip -f "$DOEL/synoptikon-$STEMPEL.db"
    echo "database → $DOEL/synoptikon-$STEMPEL.db.gz"
else
    echo "geen database gevonden op $DB" >&2
fi

if [[ -z "${BACKUP_ZONDER_WETTEKSTEN:-}" ]] && [[ -d "$DATA/wetteksten" ]] && [[ -n "$(ls -A "$DATA/wetteksten" 2>/dev/null)" ]]; then
    tar -czf "$DOEL/wetteksten-$STEMPEL.tar.gz" -C "$DATA" wetteksten
    echo "wetteksten → $DOEL/wetteksten-$STEMPEL.tar.gz"
fi

# Oude back-ups opruimen: bewaar de laatste $KEEP van elke soort.
for patroon in "synoptikon-*.db.gz" "wetteksten-*.tar.gz"; do
    (ls -1t "$DOEL"/$patroon 2>/dev/null || true) | tail -n +"$((KEEP + 1))" | xargs -r rm -f
done
