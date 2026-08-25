#!/usr/bin/env sh
set -eu

read_secret() {
    variable_name="$1"
    file_name="$2"
    if [ ! -r "$file_name" ]; then
        echo "segredo obrigatório ausente: $file_name" >&2
        exit 1
    fi
    value=$(sed -n '1p' "$file_name")
    if [ -z "$value" ]; then
        echo "segredo obrigatório vazio: $file_name" >&2
        exit 1
    fi
    export "$variable_name=$value"
}

read_secret GROWHUB_DATABASE_URL "${GROWHUB_DATABASE_URL_FILE:-/run/secrets/database_url}"
read_secret GROWHUB_SESSION_KEY "${GROWHUB_SESSION_KEY_FILE:-/run/secrets/session_key}"
read_secret GROWHUB_ADMIN_PASSWORD "${GROWHUB_ADMIN_PASSWORD_FILE:-/run/secrets/admin_password}"
read_secret GROWHUB_HA_TOKEN "${GROWHUB_HA_TOKEN_FILE:-/run/secrets/home_assistant_token}"

alembic upgrade head
exec python -m hub.growhub.api
