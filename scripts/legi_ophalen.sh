#!/usr/bin/env bash
# Haalt de LEGI-database van de DILA op (open data, geen sleutel nodig) en pakt
# alleen de gevraagde codes uit: eerst de volledige dump ("Freemium global",
# ~1,1 GB, gestreamd), dan alle dagelijkse aanvullingen daarna, in volgorde.
# Daarna: synoptikon import fr LEGITEXT000006070721 --bestand <doelmap>
#
#   scripts/legi_ophalen.sh <doelmap> [LEGITEXT…]
#   standaard: Code civil, Code de la consommation, Code de commerce
set -euo pipefail

DOEL=${1:?doelmap}
shift || true
CODES=("${@:-LEGITEXT000006070721 LEGITEXT000006069565 LEGITEXT000005634379}")
read -r -a CODES <<<"${CODES[*]}"
BASIS=https://echanges.dila.gouv.fr/OPENDATA/LEGI
UA="Synoptikon/0.1 (persoonlijke rechtsvergelijkingsapp)"
PATRONEN=()
for c in "${CODES[@]}"; do PATRONEN+=("*${c}*"); done

mkdir -p "$DOEL"
LIJST=$(curl -s -A "$UA" "$BASIS/")
GLOBAAL=$(grep -o 'Freemium_legi_global_[0-9-]*\.tar\.gz' <<<"$LIJST" | sort -u | tail -1)
STEMPEL=${GLOBAAL#Freemium_legi_global_}; STEMPEL=${STEMPEL%%-*}

if [ ! -f "$DOEL/.globaal-$STEMPEL" ]; then
  echo "Volledige dump $GLOBAAL …"
  curl -s -A "$UA" "$BASIS/$GLOBAAL" | tar xz -C "$DOEL" --wildcards "${PATRONEN[@]}" 2>/dev/null || true
  touch "$DOEL/.globaal-$STEMPEL"
fi

# Aanvullingen na de dump, oudste eerst; een al verwerkte aanvulling wordt overgeslagen.
for f in $(grep -o 'LEGI_[0-9]\{8\}-[0-9]\{6\}\.tar\.gz' <<<"$LIJST" | sort -u); do
  d=${f#LEGI_}; d=${d%%-*}
  [ "$d" -le "$STEMPEL" ] && continue
  [ -f "$DOEL/.aanvulling-$d" ] && continue
  curl -s -A "$UA" "$BASIS/$f" | tar xz -C "$DOEL" --strip-components=1 --wildcards "${PATRONEN[@]}" 2>/dev/null || true
  touch "$DOEL/.aanvulling-$d"
done
echo "Klaar: $DOEL"
