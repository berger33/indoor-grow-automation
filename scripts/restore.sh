#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ] || [ "$2" != "--confirm" ]; then
  echo "uso: scripts/restore.sh CAMINHO.dump --confirm" >&2
  exit 2
fi

backup="$1"
if [ ! -r "$backup" ] || [ ! -r "$backup.sha256" ]; then
  echo "backup ou checksum ausente" >&2
  exit 2
fi
sha256sum --check "$backup.sha256"

echo "ATENÇÃO: o banco growhub será substituído. Criando cópia pré-restauração."
scripts/backup.sh ./backups/pre-restore
docker compose --env-file deploy/.env.example -f deploy/docker-compose.yml stop hub
docker compose --env-file deploy/.env.example -f deploy/docker-compose.yml exec -T -u postgres db \
  dropdb --if-exists --username=growhub growhub
docker compose --env-file deploy/.env.example -f deploy/docker-compose.yml exec -T -u postgres db \
  createdb --username=growhub growhub
docker compose --env-file deploy/.env.example -f deploy/docker-compose.yml exec -T -u postgres db \
  pg_restore --exit-on-error --no-owner --username=growhub --dbname=growhub <"$backup"
docker compose --env-file deploy/.env.example -f deploy/docker-compose.yml start hub
echo "restauração concluída; valide /health e o painel antes de operar"
