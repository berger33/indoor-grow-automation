# Backlog executável — versão DIY

Fonte de escopo: [`docs/ESCOPO_V1.md`](docs/ESCOPO_V1.md). Itens ligados à PCB,
Gerber, painel industrial, rack sob medida e Atlas EZO foram encerrados por
mudança de direção e preservados apenas no histórico Git/arquivo.

## Fase D0 — Migração de arquitetura

- [x] `D0-001 P0` Substituir objetivo industrial por DIY barato e funcional.
- [x] `D0-002 P0` Definir notebook como hub `amd64/arm64`.
- [x] `D0-003 P0` Consolidar um ESP32, GPIO direto, relés e MOSFETs.
- [x] `D0-004 P0` Publicar pinagem de 12 saídas com estado seguro.
- [x] `D0-005 P0` Arquivar pranchas, PCB, laudo e tutorial pesado.
- [x] `D0-006 P0` Registrar ADR 0010.

## Fase D1 — Compra e montagem

- [x] `D1-001 P0` Publicar BOM estimada entre R$ 1.000 e R$ 1.650.
- [x] `D1-002 P0` Publicar checklist com quantidade, fornecedor e preço.
- [ ] `D1-003 P0` Comprar/receber componentes e registrar variantes.
- [ ] `D1-004 P0` Conferir relé/MOSFET com lógica de 3,3 V.
- [ ] `D1-005 P0` Medir corrente de partida e contínua de cada bomba.
- [ ] `D1-006 P0` Montar placa perfurada soldada e caixa seca.
- [ ] `D1-007 P0` Montar estante, contenção, caixas e potes.
- [ ] `D1-008 P0` Testar carga/estabilidade da estante apenas com água.

## Fase D2 — Firmware e sensores

- [x] `D2-001 P0` Substituir registrador serial por GPIO direto.
- [x] `D2-002 P0` Criar banco de relés ativo em LOW com boot seguro.
- [x] `D2-003 P0` Manter timeout, vazamento, parada e watchdog.
- [x] `D2-004 P0` Testar uma dosadora por vez e exclusão pH+/pH− no HIL.
- [x] `D2-005 P1` Integrar DHT22 e histerese local.
- [x] `D2-006 P1` Definir calibração linear configurável de pH/EC analógicos.
- [ ] `D2-007 P0` Medir saída pH/EC em toda a faixa e limitar a 3,3 V.
- [ ] `D2-008 P0` Calibrar pH/EC com padrões rastreados.
- [ ] `D2-009 P0` Medir dez ciclos de cada peristáltica.
- [ ] `D2-010 P0` Validar pinagem e cinco boots no ESP32 real.
- [x] `D2-011 P0` Conectar o controlador único ao broker por Wi-Fi e MQTT mTLS.
- [ ] `D2-012 P0` Publicar telemetria e alarmes no contrato MQTT v1.
- [ ] `D2-013 P0` Receber comandos com rejeição e ACK/NACK idempotentes.

## Fase D3 — Hub e integração

- [x] `D3-001 P0` Preservar FastAPI, PostgreSQL, Mosquitto e painel React.
- [x] `D3-002 P0` Preservar contratos MQTT v1.
- [x] `D3-003 P0` Documentar operação no notebook.
- [x] `D3-004 P1` Preservar integração Home Assistant/EKAZA.
- [ ] `D3-005 P0` Executar Compose no notebook real e registrar healthchecks.
- [ ] `D3-006 P0` Testar perda/retorno do notebook durante atuação simulada.
- [ ] `D3-007 P0` Restaurar backup em ambiente limpo.
- [ ] `D3-008 P1` Homologar entidades EKAZA e cem ciclos por canal.
- [x] `D3-009 P0` Alinhar identidade, ACL, tópicos e sensores ao nó `controller`.
- [ ] `D3-010 P0` Executar E2E virtual controlador–broker–hub–banco.

## Fase D4 — Comissionamento

- [x] `D4-001 P0` Reescrever tutorial na ordem de montagem real.
- [ ] `D4-002 P0` Executar teste individual das saídas com carga fictícia.
- [ ] `D4-003 P0` Testar vazamento, parada, timeout e reboot com cargas simuladas.
- [ ] `D4-004 P0` Executar ciclo completo somente com água.
- [ ] `D4-005 P0` Corrigir qualquer desvio de volume, ruído ou aquecimento.
- [ ] `D4-006 P0` Executar primeira receita real supervisionada.
- [ ] `D4-007 P1` Repetir agendas supervisionadas até estabilidade documentada.
- [ ] `D4-008 P1` Fotografar a montagem real e atualizar o tutorial.

## Fora do backlog ativo

- PCB customizada e fabricação por Gerber;
- ERC/DRC e netlist Rev A;
- painel dedicado com DR/DPS/contatores;
- gabinete IP65 e rack fabricado sob medida;
- Atlas EZO e carriers isolados;
- CO₂ dedicado, MLX90614 e plataformas de pesagem;
- seis agitadores magnéticos dedicados.

Esses itens só podem retornar mediante nova decisão explícita, orçamento e ADR.
