# Etapa 07 — Hub no notebook

O notebook substitui o Raspberry Pi sem alterar FastAPI, PostgreSQL, Mosquitto,
painel React ou contratos MQTT. O procedimento completo está em
[`docs/HUB_OPERACAO.md`](../HUB_OPERACAO.md).

## Instalação

1. Instale Linux 64-bit e atualize o sistema.
2. Instale Docker Engine e o plugin Compose.
3. Desative suspensão e hibernação automáticas.
4. Coloque o notebook na zona seca e ventilada.
5. Reserve um endereço local estável no roteador.
6. Clone a revisão aprovada e registre o hash.
7. Copie `deploy/.env.example` para `deploy/.env`.
8. Crie segredos e certificados fora do Git.
9. Valide o Compose.
10. Suba banco e broker; espere healthchecks.
11. Suba hub e painel.
12. Acesse `/health` e faça login local.

```bash
cp deploy/.env.example deploy/.env
docker compose --env-file deploy/.env -f deploy/docker-compose.yml config
docker compose --env-file deploy/.env -f deploy/docker-compose.yml up -d --build
docker compose --env-file deploy/.env -f deploy/docker-compose.yml ps
```

## Integração com o ESP32

1. Configure Wi-Fi e certificado sem colocar segredo no firmware/repositório.
2. Confirme o nó online no broker.
3. Confira heartbeat, qualidade e idade das leituras.
4. Envie comando de teste sem carga e espere ACK.
5. Reenvie o mesmo `message_id`; a resposta deve ser idempotente.
6. Envie comando vencido; deve receber NACK.
7. Desligue o notebook durante atuação simulada; o ESP32 deve cortar por perda do hub.
8. Religue e confirme que nenhuma ordem antiga foi repetida.

## Backup e restauração

1. Gere backup do banco e configurações.
2. Copie para outro dispositivo.
3. Restaure em ambiente de teste.
4. Confira usuários, receitas, agendas e calibrações.
5. Registre duração e resultado.

## Gate

- [ ] Notebook não suspende durante operação.
- [ ] Todos os contêineres saudáveis.
- [ ] Painel acessível somente na rede prevista.
- [ ] ESP32 online com horário correto.
- [ ] ACK/NACK e perda do hub testados sem carga.
- [ ] Backup restaurado em ambiente de teste.
