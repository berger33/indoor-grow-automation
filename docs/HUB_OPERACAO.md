# Hub no notebook: instalação, operação e recuperação

O hub não depende de Raspberry Pi. Ele roda em qualquer computador Linux
`amd64` ou `arm64` capaz de executar Docker Engine e Docker Compose. A montagem
de referência usa um notebook/netbook reaproveitado, que não entra no custo da
BOM.

O Compose inicia PostgreSQL, Mosquitto e o Grow Hub. A API, contratos MQTT,
painel React e integração Home Assistant/EKAZA permanecem os mesmos.

## Requisitos

- Linux 64-bit atualizado;
- 4 GB de RAM recomendados;
- 20 GB livres para imagens, banco, logs e backup inicial;
- Docker Engine e plugin `docker compose`;
- conexão estável à rede local por cabo ou Wi-Fi;
- relógio sincronizado e timezone `America/Sao_Paulo`;
- notebook configurado para não suspender ao fechar a tampa.

Verifique a arquitetura:

```bash
uname -m
docker version
docker compose version
```

`x86_64` corresponde a `amd64`; `aarch64` corresponde a `arm64`.

## Preparar o notebook

1. Instale uma distribuição Linux suportada pelo Docker.
2. Aplique atualizações do sistema.
3. Instale Docker Engine e Compose pelo repositório oficial da distribuição.
4. Habilite o serviço Docker no boot.
5. Desative suspensão automática, hibernação e desligamento ao fechar a tampa.
6. Reserve IP no roteador ou defina um hostname local estável.
7. Mantenha o notebook em prateleira seca, ventilada e acima dos reservatórios.
8. Não apoie fonte, filtro de linha ou notebook no chão da estufa.

## Configuração inicial

Na raiz do repositório:

```bash
cp deploy/.env.example deploy/.env
docker compose --env-file deploy/.env -f deploy/docker-compose.yml config
```

Preencha apenas o arquivo local `deploy/.env`. Não versione senhas, tokens,
certificados ou IDs privados. Crie os arquivos de segredo exigidos pelo Compose
com permissão mínima e mantenha cópia offline protegida.

Confirme no Home Assistant os IDs reais das tomadas EKAZA antes de preencher a
integração. A ausência dessas entidades não deve impedir fertirrigação ou clima.

## Iniciar

```bash
docker compose --env-file deploy/.env -f deploy/docker-compose.yml up -d --build
docker compose --env-file deploy/.env -f deploy/docker-compose.yml ps
```

Aguarde os healthchecks. Depois verifique:

```bash
docker compose --env-file deploy/.env -f deploy/docker-compose.yml logs --tail=100 hub
docker compose --env-file deploy/.env -f deploy/docker-compose.yml logs --tail=100 broker
```

Falha de banco, broker, migração ou certificado deve aparecer como erro. Não
trate um contêiner apenas “running” como sistema saudável.

## Acesso local

Abra o endereço configurado para o painel somente pela LAN. Por padrão, mantenha
PostgreSQL e MQTT sem exposição externa. Para acesso fora de casa, use VPN ou
reverse proxy autenticado; nunca publique diretamente portas do banco ou broker.

## Operação diária

Antes de liberar agendas:

1. confirme o notebook ligado e sem alerta de bateria/temperatura;
2. confira `docker compose ps`;
3. abra `/health` e o painel;
4. confirme horário correto, nó ESP32 online e leituras recentes;
5. verifique espaço em disco;
6. confira último backup;
7. mantenha a primeira execução do dia supervisionada.

Uma queda do hub não pode manter bomba ligada: o ESP32 aplica timeout absoluto e
entra em estado seguro quando perde o heartbeat durante atuação.

## Atualizar o sistema

1. gere backup do banco e das configurações;
2. registre o commit atual;
3. baixe a revisão aprovada;
4. execute o portão de qualidade;
5. reconstrua as imagens;
6. aplique migrações;
7. verifique healthchecks e painel;
8. teste uma operação sem carga antes de voltar às agendas.

Não atualize firmware, hub e pinagem em momentos diferentes sem registrar a
compatibilidade.

## Backup

O backup precisa incluir:

- dump do PostgreSQL;
- receitas, agendas e calibrações;
- estado da integração EKAZA, sem expor token em arquivo público;
- certificados e segredos em cópia privada;
- hash do commit e data.

Copie o backup para outro dispositivo. Um arquivo deixado apenas no mesmo
notebook não protege contra falha do disco.

## Teste de restauração

1. pare um ambiente de teste isolado;
2. suba banco vazio;
3. restaure o backup;
4. aplique migrações previstas;
5. confira usuários, receitas, calibrações e histórico;
6. confirme que nenhuma saída física é acionada durante a restauração;
7. registre duração e resultado.

Só considere o backup aprovado depois desse teste.

## Retorno após queda de energia

Ao religar:

1. o ESP32 inicia com todas as saídas desligadas;
2. o notebook inicia Docker automaticamente;
3. PostgreSQL e Mosquitto devem ficar saudáveis antes do hub;
4. o painel volta a mostrar a estação;
5. nenhuma ordem anterior é repetida automaticamente;
6. o operador inspeciona água, tubos e alarmes antes de rearmar.

## Diagnóstico rápido

| Sintoma | Verificação |
|---|---|
| painel não abre | `docker compose ps`, log do hub, firewall e endereço local |
| ESP32 offline | Wi-Fi local, broker, certificado, ACL e relógio |
| banco indisponível | healthcheck, espaço em disco e log do PostgreSQL |
| EKAZA indisponível | Home Assistant, entidade `switch`, token e rede; cultivo deve continuar |
| notebook dorme | energia, configuração de tampa/suspensão e serviço Docker no boot |
| disco enchendo | retenção, logs, backups locais duplicados e volume do banco |

## Segurança

- use senha individual e não compartilhe conta administrativa;
- não coloque tokens em issue, screenshot, log ou commit;
- atualize o sistema operacional com janela de manutenção;
- mantenha firewall ativo e portas restritas à LAN;
- deixe notebook e fonte longe de respingos e com ventilação;
- teste o comportamento do ESP32 com o notebook desligado antes do primeiro uso.
