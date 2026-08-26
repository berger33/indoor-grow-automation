# Broker MQTT seguro

O listener aceita apenas MQTT sobre TLS na porta 8883, com TLS 1.2 como versão
mínima para compatibilidade com o ESP32 e TLS 1.3 quando ambos os lados o
negociarem. Cada cliente precisa
de certificado emitido pela CA local; o `CN` vira o usuário da ACL. O hub pode
ler e publicar toda a árvore v1, enquanto o único ESP32 DIY usa o CN
`grow-01-controller`: publica telemetria/estado/alarme/ACK do nó `controller` e
lê somente comandos destinados a esse nó.

Certificados e chaves não pertencem ao Git. Em produção, monte:

- `/mosquitto/config/certs/ca.crt`;
- `/mosquitto/config/certs/server.crt`;
- `/mosquitto/config/certs/server.key`;
- `grow-01-controller.crt` e `grow-01-controller.key` para o ESP32.

O teste `scripts/test_mosquitto_tls.sh` cria uma CA efêmera, sobe Mosquitto
2.0.22 em contêiner, confirma publicação/comando autorizados e comprova que o
controlador não publica fora do próprio espaço. Nenhuma chave de teste é
preservada.

O contêiner do hub monta a mesma pasta em `/run/growhub-mqtt`, usando somente
`ca.crt`, `grow-hub.crt` e `grow-hub.key`. Se o broker estiver desconectado, a
API devolve HTTP 503 e registra `transport_unavailable`; ela nunca informa que
um comando foi enfileirado quando a publicação não ocorreu.
