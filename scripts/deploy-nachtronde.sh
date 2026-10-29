#!/usr/bin/env bash
# Eenmalig: de nachtronde van 29 okt 2026 live zetten (stelselkeuze, snelheid, bijwerken, Wunderkammer-koppeling,
# leerlijsten delen en de nieuwe stelsels). Back-up van vóór de deploy: backups/synoptikon-20261029-074300.db.gz.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== container opnieuw bouwen (migraties lopen bij het opstarten)"
docker compose up -d --build
until [ "$(docker inspect -f '{{.State.Health.Status}}' synoptikon)" = healthy ]; do sleep 3; done

echo "== nieuwe stelsels en systematiek"
docker compose exec -T app synoptikon seed

echo "== wetteksten van de nieuwe stelsels (±100 MB, beleefd: 1 verzoek per seconde per site)"
docker compose exec -T app nice -n 19 synoptikon import-alles --systematiek \
    --stelsel at dk fi no se pt jp tw hk ca qc cl br tr || echo "(enkele wetten mislukt; zie hierboven)"

echo "== wekelijks bijwerken en Storage Box inplannen"
mkdir -p ~/.config/systemd/user
for f in deploy/systemd/synoptikon-*.{service,timer}; do ln -sf "$PWD/$f" ~/.config/systemd/user/; done
systemctl --user daemon-reload
systemctl --user enable --now synoptikon-bijwerken.timer synoptikon-storagebox.timer
systemctl --user list-timers | grep synoptikon

echo "klaar. Alle NL-wetten en Franse codes komen in de nachtelijke rondes (bijwerken, max. 4 uur per nacht)."
