#!/usr/bin/env bash
# Archief en back-ups naar een Hetzner Storage Box (of elke andere rclone-remote met de naam `storagebox:`).
#
# Gebruik:  scripts/storagebox.sh            (wekelijks via deploy/systemd/synoptikon-storagebox.timer)
# Env:      SYNOPTIKON_DATA_DIR (standaard ./data), SYNOPTIKON_ARCHIEF_DIR (standaard <datamap>/wetteksten),
#           STORAGEBOX_REMOTE (standaard storagebox:synoptikon), STORAGEBOX_BWLIMIT (standaard 4M),
#           BACKUP_DIR (standaard ./backups), BACKUP_KEEP (zie backup.sh)
#
# 1. Een verse back-up van de database (scripts/backup.sh, zonder tar van de wetteksten).
# 2. rclone sync van het archief met de ruwe bestanden naar <remote>/archief; wat lokaal weg is, gaat naar
#    <remote>/oud/<datum> in plaats van te verdwijnen (--backup-dir).
# 3. rclone sync van de back-upmap naar <remote>/backups (dezelfde BACKUP_KEEP als lokaal).
# Alles met --bwlimit, nice en ionice, zodat de server en de lijn er niets van merken.
# Zonder remote `storagebox:` zegt het script dat en stopt het zonder fout.
set -euo pipefail

HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA="${SYNOPTIKON_DATA_DIR:-$HIER/data}"
ARCHIEF="${SYNOPTIKON_ARCHIEF_DIR:-$DATA/wetteksten}"
REMOTE="${STORAGEBOX_REMOTE:-storagebox:synoptikon}"
BWLIMIT="${STORAGEBOX_BWLIMIT:-4M}"
BACKUPS="${BACKUP_DIR:-$HIER/backups}"
NAAM="${REMOTE%%:*}"

if ! command -v rclone >/dev/null 2>&1; then
    echo "rclone ontbreekt; zie README (Back-up → Storage Box)." >&2
    exit 0
fi
if ! rclone listremotes | grep -qx "$NAAM:"; then
    echo "Geen rclone-remote '$NAAM:' ingesteld; niets gesynchroniseerd. Zie README (Back-up → Storage Box)."
    exit 0
fi

LAAG=(nice -n 19 ionice -c 3)
RCLONE=(rclone --bwlimit "$BWLIMIT" --transfers 2 --checkers 4 --low-level-retries 10 --retries 3 --stats-one-line --stats 10m)

BACKUP_ZONDER_WETTEKSTEN=1 "${LAAG[@]}" "$HIER/scripts/backup.sh" "$BACKUPS"

if [[ -d "$ARCHIEF" ]]; then
    "${LAAG[@]}" "${RCLONE[@]}" sync "$ARCHIEF" "$REMOTE/archief" --backup-dir "$REMOTE/oud/$(date +%Y%m%d)"
    echo "archief → $REMOTE/archief"
fi
"${LAAG[@]}" "${RCLONE[@]}" sync "$BACKUPS" "$REMOTE/backups" --include "synoptikon-*.db.gz" --include "wetteksten-*.tar.gz"
echo "back-ups → $REMOTE/backups"
