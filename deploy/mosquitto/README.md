# Broker MQTT seguro

O listener aceita apenas MQTT sobre TLS 1.3 na porta 8883. Cada cliente precisa
de certificado emitido pela CA local; o `CN` vira o usuário da ACL. O hub pode
ler e publicar toda a árvore v1, enquanto cada ESP32 fica restrito ao próprio
nó: publica telemetria/estado/alarme/ACK e lê somente comandos destinados a ele.

Certificados e chaves não pertencem ao Git. Em produção, monte:

- `/mosquitto/config/certs/ca.crt`;
- `/mosquitto/config/certs/server.crt`;
- `/mosquitto/config/certs/server.key`;
- um certificado/chave por identidade declarada em `growhub.acl`.

O teste `scripts/test_mosquitto_tls.sh` cria uma CA efêmera, sobe Mosquitto
2.0.22 em contêiner, confirma uma publicação autorizada e comprova que um nó
não publica no espaço de outro. Nenhuma chave de teste é preservada.
