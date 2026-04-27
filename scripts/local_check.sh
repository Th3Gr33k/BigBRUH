#!/usr/bin/env bash
set -euo pipefail

printf "[1/4] Checking required tools...\n"
command -v docker >/dev/null || { echo "docker missing"; exit 1; }
docker compose version >/dev/null || { echo "docker compose plugin missing"; exit 1; }
command -v python >/dev/null || { echo "python missing"; exit 1; }

printf "[2/4] Rendering compose config...\n"
docker compose -f infra/compose/docker-compose.yml config >/dev/null

printf "[3/4] Building backend image...\n"
docker compose -f infra/compose/docker-compose.yml build backend >/dev/null

printf "[4/4] Done. Local environment looks runnable.\n"
