#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
test_root="$(mktemp -d)"
broker_name="grow-mqtt-test-$$"

cleanup() {
  docker rm -f "$broker_name" >/dev/null 2>&1 || true
  rm -rf "$test_root"
}
trap cleanup EXIT

mkdir -p "$test_root/certs" "$test_root/data"
chmod 755 "$test_root" "$test_root/certs"
chmod 777 "$test_root/data"

openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=grow-test-ca" \
  -keyout "$test_root/certs/ca.key" -out "$test_root/certs/ca.crt" >/dev/null 2>&1

issue_certificate() {
  local name="$1"
  openssl req -newkey rsa:2048 -nodes -subj "/CN=$name" \
    -keyout "$test_root/certs/$name.key" -out "$test_root/certs/$name.csr" >/dev/null 2>&1
  openssl x509 -req -days 1 -sha256 -in "$test_root/certs/$name.csr" \
    -CA "$test_root/certs/ca.crt" -CAkey "$test_root/certs/ca.key" -CAcreateserial \
    -out "$test_root/certs/$name.crt" >/dev/null 2>&1
}

issue_certificate server
issue_certificate grow-hub
issue_certificate grow-01-climate
chmod 644 "$test_root/certs"/*.key "$test_root/certs"/*.crt

docker run --rm -d --name "$broker_name" \
  -v "$repo_root/deploy/mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro" \
  -v "$repo_root/deploy/mosquitto/growhub.acl:/mosquitto/config/growhub.acl:ro" \
  -v "$test_root/certs:/mosquitto/config/certs:ro" \
  -v "$test_root/data:/mosquitto/data" \
  eclipse-mosquitto:2.0.22 >/dev/null

broker_ready=false
for _ in $(seq 1 20); do
  if docker logs "$broker_name" 2>&1 | grep -q "Opening ipv4 listen socket"; then
    broker_ready=true
    break
  fi
  sleep 0.25
done
if [[ "$broker_ready" != true ]]; then
  echo "Mosquitto não iniciou no prazo; log do broker:" >&2
  docker logs "$broker_name" >&2 || true
  exit 1
fi

client() {
  local identity="$1"
  shift
  docker run --rm --network "container:$broker_name" \
    -v "$test_root/certs:/certs:ro" eclipse-mosquitto:2.0.22 "$@" \
    --cafile /certs/ca.crt --cert "/certs/$identity.crt" --key "/certs/$identity.key" \
    -h 127.0.0.1 -p 8883
}

client grow-hub mosquitto_pub -r -t grow/v1/grow-01/climate/command/exhaust -m off
received="$(client grow-01-climate mosquitto_sub -C 1 -W 3 -t grow/v1/grow-01/climate/command/exhaust)"
test "$received" = "off"

if client grow-01-climate mosquitto_pub -t grow/v1/grow-01/fertigation/command/mixer -m start; then
  echo "ACL permitiu publicação cruzada proibida" >&2
  exit 1
fi

echo "Mosquitto TLS/ACL: publicação permitida e negação cruzada aprovadas"
