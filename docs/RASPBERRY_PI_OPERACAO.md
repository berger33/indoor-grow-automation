# Raspberry Pi: implantação, consumo, backup e restauração

## O que esta camada faz

O Raspberry Pi hospeda o banco, o broker MQTT e o painel. Ele coordena e
registra a operação, mas **não substitui as proteções locais dos ESP32**: se o
Pi reiniciar, as saídas dos nós voltam desligadas e exigem novo comando válido.

O Compose usa imagens oficiais multi-arquitetura e é compatível com Linux
ARM64. Os limites reservam 768 MiB para PostgreSQL, 128 MiB para Mosquitto e
512 MiB para o hub. Eles são limites, não consumo constante.

## Previsão de energia

Esta é uma estimativa de planejamento, ainda não uma medição:

| Estado | Potência total estimada | Energia em 30 dias |
|---|---:|---:|
| leve | 8 W | 5,76 kWh |
| típico | 12 W | 8,64 kWh |
| pico reservado | 25 W | 18,00 kWh |

Inclui Pi, SSD e margem para rede; não inclui tela, bombas, ventilação ou
iluminação. Confirmar com wattímetro no hardware final e dimensionar fonte/UPS
pela placa efetivamente comprada.

## Preparação simples

1. Instale Raspberry Pi OS 64-bit, Docker Engine e o plugin Compose.
2. Copie `deploy/.env.example` para `deploy/.env`, ajuste endereços/portas e
   preencha `GROWHUB_EKAZA_ENTITIES` com os quatro IDs `switch.*` confirmados,
   separados por vírgula. Não coloque senhas no arquivo. Enquanto os IDs reais
   não forem conhecidos, mantenha vazio e o serviço ficará em bloqueio seguro.
3. Crie `deploy/secrets/` com permissões `0700` e arquivos legíveis apenas pelo
   administrador:
   - `postgres_password`: senha aleatória do usuário do banco;
   - `database_url`: URL completa `postgresql+psycopg://...` correspondente;
   - `session_key`: ao menos 32 bytes aleatórios;
   - `admin_password`: senha inicial forte, com ao menos 12 caracteres; depois
     crie contas individuais e preserve o arquivo somente para recuperação;
   - `home_assistant_token`: token de longa duração do Home Assistant;
   - `certs/`: CA, servidor MQTT e cliente `grow-hub` conforme o README do broker.
4. Execute `docker compose --env-file deploy/.env -f deploy/docker-compose.yml config`.
5. Execute `docker compose --env-file deploy/.env -f deploy/docker-compose.yml up -d --build`.
6. Confira `docker compose -f deploy/docker-compose.yml ps` e abra `/health`.

O painel fica ligado apenas a `127.0.0.1` por padrão. Para acesso pela rede,
adicione proxy HTTPS autenticado; não exponha diretamente a API na internet.

## Backup e restauração

Execute `scripts/backup.sh /mnt/ssd/backups` diariamente. O script produz dump
PostgreSQL e SHA-256, mantendo 30 dias. Copie pelo menos uma réplica para outro
dispositivo e teste a restauração em ambiente separado a cada trimestre.

A restauração é destrutiva e só executa com confirmação explícita:

```bash
scripts/restore.sh /mnt/ssd/backups/growhub-AAAAmmddTHHMMSSZ.dump --confirm
```

Ela verifica o checksum, faz uma cópia pré-restauração, para o hub, recria
somente o banco `growhub`, restaura e religa o serviço. Depois, confirme `/health`,
sensores, alarmes e estado **observado** dos atuadores antes de liberar operação.
