#!/usr/bin/env bash
set -euo pipefail

root="${1:-./backups}"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
destination="$root/growhub-$stamp.dump"
mkdir -p "$root"

docker compose --env-file deploy/.env.example -f deploy/docker-compose.yml exec -T -u postgres db \
  pg_dump --format=custom --no-owner --username=growhub growhub >"$destination"
sha256sum "$destination" >"$destination.sha256"
find "$root" -maxdepth 1 -type f -name 'growhub-*.dump*' -mtime +30 -delete
echo "backup criado: $destination"
