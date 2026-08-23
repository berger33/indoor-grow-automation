# Backlog executável

Fonte primária: [`ESPECIFICACAO_REFERENCIA.md`](ESPECIFICACAO_REFERENCIA.md).
Cada item deve caber em um commit coeso. `P0` bloqueia operação segura; `P1`
compõe o MVP; `P2` melhora operação; `P3` é posterior ao v1.0.

## Fase 0 — Fundação

- [x] `F0-001 P0` Inicializar metadados, ignore e licença.
- [x] `F0-002 P0` Documentar visão geral e roadmap no README.
- [x] `F0-003 P0` Incorporar especificação e pranchas de referência.
- [x] `F0-004 P0` Registrar decisão de monorepo e contratos.
- [x] `F0-005 P0` Registrar decisão de segurança local.
- [x] `F0-006 P0` Registrar stack do hub e painel.
- [x] `F0-007 P0` Implantar portão de qualidade executável localmente.
- [x] `F0-008 P0` Implantar scanner de segredos com testes.
- [x] `F0-009 P0` Implantar CI para testes, lint e segredos.
- [x] `F0-010 P1` Criar templates de issue e pull request.
- [x] `F0-011 P1` Documentar política de branches e releases.
- [x] `F0-012 P1` Configurar atualização automatizada de dependências.
- [x] `F0-013 P0` Fixar escopo v1 em fertirrigação, irrigação e clima.
- [x] `F0-014 P0` Excluir iluminação de hardware, software e interface.
- [x] `F0-015 P1` Revisar novamente o vídeo V1 de hardware com timestamps.

## Fase 1 — Núcleo de sensores

- [x] `F1-001 P0` Modelar amostra com valor, unidade, tempo e qualidade.
- [x] `F1-002 P0` Validar envelopes físicos por tipo de sensor.
- [x] `F1-003 P0` Marcar leitura stale por idade máxima.
- [x] `F1-004 P0` Modelar falhas de timeout, CRC, desconexão e calibração.
- [x] `F1-005 P0` Definir contrato versionado de telemetria MQTT.
- [x] `F1-006 P0` Validar schema e rejeitar payload malformado.
- [x] `F1-007 P1` Implementar filtro de mediana configurável.
- [x] `F1-008 P1` Implementar média móvel com janela configurável.
- [x] `F1-009 P1` Implementar debounce de entradas digitais.
- [x] `F1-010 P1` Modelar driver DS18B20 com timeout e faixa física.
- [x] `F1-011 P1` Modelar driver BME280 com offset por dispositivo.
- [x] `F1-012 P1` Modelar driver MLX90614 e temperatura foliar.
- [x] `F1-013 P1` Modelar driver Atlas pH e códigos de erro.
- [x] `F1-014 P1` Modelar driver Atlas EC e códigos de erro.
- [x] `F1-015 P1` Implementar compensação térmica de pH/EC validada.
- [x] `F1-016 P1` Modelar HX711 com tara e fator persistentes.
- [x] `F1-017 P1` Modelar nível ultrassônico com filtro e zona morta.
- [x] `F1-018 P0` Modelar vazamento latched com confirmação multiamostra.
- [x] `F1-019 P1` Detectar divergência entre sensores climáticos.
- [x] `F1-020 P1` Calcular VPD com ar e temperatura foliar.
- [ ] `F1-021 P1` Criar simuladores determinísticos de todos os sensores.
- [ ] `F1-022 P1` Publicar diagnóstico de qualidade/idade de cada leitura.

## Fase 2 — Controle e segurança

- [ ] `F2-001 P0` Modelar estados BOOT/IDLE/MANUAL/BATCH/ALARM.
- [ ] `F2-002 P0` Implementar timeout absoluto de atuador local.
- [ ] `F2-003 P0` Implementar corte local latched por vazamento.
- [ ] `F2-004 P0` Definir estado seguro de todos os GPIO no boot.
- [ ] `F2-005 P0` Implementar watchdog e motivo de reset.
- [ ] `F2-006 P0` Implementar heartbeat e política de perda do hub.
- [ ] `F2-007 P0` Bloquear pH+ e pH− simultâneos.
- [ ] `F2-008 P0` Limitar dosagem por evento, hora e dia.
- [ ] `F2-009 P1` Calibrar curva volume×tempo por bomba.
- [ ] `F2-010 P1` Implementar correção de pH com histerese e espera.
- [ ] `F2-011 P1` Implementar receita de nutrientes como máquina de estados.
- [ ] `F2-012 P1` Implementar diluição por EC com timeout.
- [ ] `F2-013 P1` Implementar mistura periódica por nível.
- [ ] `F2-014 P1` Implementar agenda de até cinco irrigações.
- [ ] `F2-015 P1` Implementar drenagem com timeout e pós-tempo.
- [ ] `F2-016 P1` Implementar umidade com histerese e anti-ciclo.
- [ ] `F2-017 P1` Implementar exaustor por temperatura/VPD.
- [ ] `F2-018 P0` Criar testes de perda de rede em cada estado crítico.
- [ ] `F2-019 P0` Intertravar umidificador por nível mínimo e timeout.
- [ ] `F2-020 P1` Monitorar CO₂ sem comandar injeção no MVP.
- [ ] `F2-021 P1` Definir limites absolutos de temperatura e UR sobre o VPD.
- [ ] `F2-022 P1` Detectar exaustor comandado sem feedback de corrente/contato.
- [ ] `F2-023 P1` Implementar prioridade entre exaustão e umidificação.
- [ ] `F2-024 P2` Modelar módulos opcionais de desumidificação e climatização.

## Fase 3 — Hub e conectividade

- [ ] `F3-001 P0` Criar serviço FastAPI com healthcheck.
- [ ] `F3-002 P0` Definir tópicos MQTT por estação e função.
- [ ] `F3-003 P0` Implementar ACK/NACK idempotente de comandos.
- [ ] `F3-004 P0` Configurar Mosquitto com ACL e TLS.
- [ ] `F3-005 P1` Persistir telemetria no PostgreSQL.
- [ ] `F3-006 P1` Criar migrações iniciais Alembic.
- [ ] `F3-007 P1` Expor API de estações e sensores.
- [ ] `F3-008 P1` Expor API de setpoints e agendas.
- [ ] `F3-009 P1` Expor stream WebSocket de telemetria.
- [ ] `F3-010 P1` Implementar autenticação e perfis de operador.
- [ ] `F3-011 P1` Implementar auditoria de comandos críticos.
- [ ] `F3-012 P1` Criar backup e teste de restauração.
- [ ] `F3-013 P2` Implementar buffer offline e deduplicação.
- [ ] `F3-014 P1` Criar Docker Compose ARM64 do hub.

## Fase 4 — Painel mobile-first

- [ ] `F4-001 P1` Criar shell React responsivo e navegação.
- [ ] `F4-002 P1` Criar tela Home com qualidade das leituras.
- [ ] `F4-003 P1` Criar gráficos de pH, EC, água e clima.
- [ ] `F4-004 P1` Criar assistente de calibração guiada.
- [ ] `F4-005 P1` Criar tela de receita e progresso da batelada.
- [ ] `F4-006 P1` Criar tela de agenda de irrigação.
- [ ] `F4-007 P0` Criar central de alarmes latched e confirmação.
- [ ] `F4-008 P1` Diferenciar comando, estado e feedback físico.
- [ ] `F4-009 P1` Explicar por que controles estão inibidos.
- [ ] `F4-010 P2` Criar comparação de múltiplas tendas.
- [ ] `F4-011 P2` Criar PWA com cache somente de leitura.
- [ ] `F4-012 P1` Cobrir acessibilidade e operação por teclado.

## Fase 5 — Instalação e release

- [ ] `F5-001 P0` Fechar BOM com alternativas e correntes.
- [ ] `F5-002 P0` Publicar pinagem e chicotes por revisão.
- [ ] `F5-003 P0` Publicar P&ID e unifilar as-built.
- [ ] `F5-004 P0` Criar guia leigo de montagem mecânica.
- [ ] `F5-005 P0` Criar guia leigo de instalação elétrica segura.
- [ ] `F5-006 P0` Criar assistente de instalação do Raspberry Pi.
- [ ] `F5-007 P0` Criar checklist de comissionamento com água.
- [ ] `F5-008 P0` Executar HIL e piloto supervisionado.
- [ ] `F5-009 P1` Publicar matriz de compatibilidade de hardware.
- [ ] `F5-010 P0` Gerar SBOM e auditar licenças.
- [ ] `F5-011 P0` Publicar release candidate documentada.
- [ ] `F5-012 P0` Publicar v1.0 após critérios de aceitação.
- [x] `F5-013 P0` Documentar variante elétrica fixa 127 V/60 Hz.
- [x] `F5-014 P0` Consolidar BOM A0 com alternativas e status de aprovação.
- [x] `F5-015 P0` Definir I/O, netlist e parâmetros da PCB SELV A0.
- [x] `F5-016 P0` Cruzar automaticamente BOM, I/O e netlist da PCB.
- [ ] `F5-017 P0` Receber amostras e congelar footprints pela medição física.
- [ ] `F5-018 P0` Criar esquema KiCad e zerar violações ERC não justificadas.
- [ ] `F5-019 P0` Rotear PCB KiCad e zerar violações DRC não justificadas.
- [ ] `F5-020 P0` Fabricar uma unidade A0 e executar ensaio elétrico/térmico.
- [ ] `F5-021 P0` Liberar A1 somente após HIL e piloto com água.
- [ ] `F5-022 P0` Congelar matriz de atuadores e capacidade de saídas por nó.
- [ ] `F5-023 P0` Definir plataforma mecânica de oito células para os dois tanques.
- [ ] `F5-024 P0` Medir percurso hidráulico, vazão-alvo e altura manométrica.
- [ ] `F5-025 P0` Selecionar bombas pelas curvas medidas e ensaio de recebimento.
- [ ] `F5-026 P0` Selecionar tubos e vedações por compatibilidade química.
- [ ] `F5-027 P0` Desenhar contenção secundária e trajetos de vazamento.
- [ ] `F5-028 P0` Publicar layout físico cotado da estação em escala.
- [x] `F5-029 P1` Publicar imagens realistas marcadas como ilustrativas.
- [ ] `F5-030 P0` Criar tutorial 01 de inventário e conferência da compra.
- [ ] `F5-031 P0` Criar tutorial 02 de montagem da estrutura seca.
- [ ] `F5-032 P0` Criar tutorial 03 de reservatórios e plataformas de pesagem.
- [ ] `F5-033 P0` Criar tutorial 04 de válvulas, bombas e tubulação.
- [ ] `F5-034 P0` Criar tutorial 05 de frascos, dosadoras e agitadores.
- [ ] `F5-035 P0` Criar tutorial 06 de sondas e sensores de segurança.
- [ ] `F5-036 P0` Criar tutorial 07 do quadro e chicotes SELV.
- [ ] `F5-037 P0` Criar tutorial 08 da instalação CA por profissional habilitado.
- [ ] `F5-038 P0` Criar tutorial 09 de gravação e provisionamento dos ESP32.
- [ ] `F5-039 P0` Criar tutorial 10 de instalação do hub e painel.
- [ ] `F5-040 P0` Criar tutorial 11 de calibração de massa, bombas, pH e EC.
- [ ] `F5-041 P0` Criar tutorial 12 de teste seco, HIL e teste somente com água.
- [ ] `F5-042 P0` Criar tutorial 13 de primeira batelada supervisionada.
- [ ] `F5-043 P0` Criar guia de manutenção, limpeza e armazenamento de sondas.
- [ ] `F5-044 P0` Validar o tutorial em montagem limpa sem conhecimento prévio.
- [ ] `F5-045 P1` Fotografar a montagem validada e substituir imagens conceituais.
