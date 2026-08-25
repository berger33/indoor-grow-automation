# Entrega explicada — tarefas 01 a 30

Este documento é o mapa simples da entrega. Ele mostra o que cada parte faz,
como conferi-la sem acionar cargas e o limite da evidência existente.

## Como interpretar o estado

- **Software local aprovado:** código, teste ou build passou no Quality Gate.
- **Preparado para CI:** o artefato existe, mas o contêiner/build externo ainda
  precisa passar no GitHub em checkout limpo.
- **A0/HOLD físico:** desenho ou tutorial existe, mas não autoriza compra final,
  fabricação, ligação em 127 V nem operação com químicos.

## 1–9 — controle, firmware e HIL virtual

| # | O que foi entregue e como funciona | Como verificar agora | Limite seguro |
|---:|---|---|---|
| 1 | O umidificador só liga com leitura válida, nível suficiente e nenhum vazamento. Há histerese, anti-ciclo, timeout absoluto retido e rearme explícito. | Rode `python -m unittest tests.test_humidity_control -v`. | Modelo/plaqueta, nível real e ensaio de aquecimento seguem em HOLD. |
| 2 | O CO₂ é classificado como normal, alerta, crítico ou indisponível. A classe não possui nenhuma função de injeção. | Rode `python -m unittest tests.test_co2_monitor -v`. | Apenas monitorar/alertar; cilindro, solenóide ou injeção estão fora da v1. |
| 3 | Existem projetos PlatformIO separados para fertirrigação, clima, segurança e HIL nativo. Dependências estão fixadas por versão/commit. | Siga `firmware/README.md` e execute `pio run` em cada diretório. | Build ESP32 real precisa passar no CI e depois na placa correta. |
| 4 | O núcleo inicia saídas em OFF antes do enable, usa watchdog, heartbeat, reset seguro e vazamento retido. Reinício nunca restaura o último comando. | Execute `python scripts/run_firmware_hil.py`. | Watchdog e polaridades precisam ser medidos na PCB física. |
| 5 | DS18B20, BME280, MLX90614, ultrassom e HX711 validam faixa, timeout, desconexão, offset, tara e unidade. | Rode os testes `test_ds18b20`, `test_bme280`, `test_mlx90614`, `test_ultrasonic_level` e `test_hx711`. | Endereços, geometria e coeficientes reais ainda exigem calibração. |
| 6 | pH e EC Atlas tratam códigos de retorno, payload inválido, faixa e compensação térmica. Falha nunca vira leitura válida. | Rode `test_atlas_ph`, `test_atlas_ec` e `test_chemistry`. | Sondas, padrões e ACKs de calibração reais continuam obrigatórios. |
| 7 | A fertirrigação valida estoque/capacidade, dosa canais em ordem, mistura, corrige EC por diluição e pH em pulsos limitados. | Rode `test_nutrient_batch`, `test_pump_calibration`, `test_ec_dilution` e `test_ph_control`. | Receita é cadastrada pelo operador; o sistema não recomenda dose agronômica. |
| 8 | Mistura, irrigação, dreno, umidade e exaustão são máquinas de estado com timeout e intertravamentos. Exaustão prevalece em conflito climático. | Rode os testes dos módulos em `hub/growhub/control`. | Vazão, altura, corrente e feedback reais ainda não foram medidos. |
| 9 | Seis cenários HIL virtuais cobrem boot, sensor, rede, vazamento, timeout e reinício; todos terminam com saídas OFF. | Execute `pio run --project-dir firmware/hil --target exec` ou o fallback do gate. | HIL virtual não substitui HIL físico nem teste com água. |

## 10–20 — comunicação e Raspberry Pi

| # | O que foi entregue e como funciona | Como verificar agora | Limite seguro |
|---:|---|---|---|
| 10 | A árvore `grow/v1/<estação>/<nó>/<direção>/<função>` separa telemetria, estado, alarme, comando e ACK. | Rode `python -m unittest tests.test_mqtt_topics -v`. | Apenas a versão 1 é aceita; wildcard em payload/tópico concreto é rejeitado. |
| 11 | Comandos usam UUID, sequência monotônica, validade de 15 s, QoS 1 e ACK/NACK estrito. Duplicata não repete a ação. | Rode `test_mqtt_commands` e `test_mqtt_gateway`. | Sem broker ou sem ACK, o resultado é falha/timeout, nunca sucesso presumido. |
| 12 | Mosquitto exige TLS 1.3 mútuo; a ACL limita cada ESP32 ao próprio nó. | Rode `scripts/test_mosquitto_tls.sh` em host com Docker. | Certificados efêmeros do teste não são certificados de produção. |
| 13 | Duas migrações Alembic criam estações, sensores, telemetria, configuração, usuários, alarmes, auditoria e operação. | Rode `alembic upgrade head` com banco de teste; a suíte também usa SQLite isolado. | Backup deve anteceder toda migração no equipamento. |
| 14 | O gateway valida tópico/envelope, confere o nó proprietário e grava cada UUID/sequência uma vez. Retenção e capacidade estão documentadas. | Consulte `docs/TELEMETRIA_E_RETENCAO.md` e rode `test_persistence`. | 3,45/8,61 GiB por ano são previsões, não medições do Pi. |
| 15 | A API lista estações, saúde, sensores, qualidade, idade e histórico bruto/agregado. | Depois do login, use `/api/v1/stations`, `/sensors` e `/history`. | Leitura ausente ou antiga é exibida como degradada/falha. |
| 16 | Endpoints validam e persistem setpoints, receitas e até cinco agendas de irrigação. | Rode `python -m unittest tests.test_operations_api -v`. | Valores fora das faixas seguras ou agendas inválidas são recusados. |
| 17 | Sessão assinada, senha com hash/salt, perfis leitor/operador/admin e auditoria de comando ficam no banco. | Teste login e perfis com `test_security_realtime` e `test_sql_operations`. | Produção exige proxy HTTPS; a API não deve ser exposta diretamente. |
| 18 | WebSocket sequencia eventos, permite reconexão com `last_event_id` e mantém buffer limitado; assinante lento perde primeiro o evento mais antigo. | Rode o teste WebSocket em `test_operations_api` e `test_security_realtime`. | O buffer é de retomada operacional, não substitui o histórico PostgreSQL. |
| 19 | Compose ARM64 sobe PostgreSQL, Mosquitto e hub com limites, healthchecks, segredos por arquivo, backup e restauração protegida. | Siga `docs/RASPBERRY_PI_OPERACAO.md`. | Consumo, temperatura, SSD, backup restaurado e boot precisam ser medidos no Pi real. |
| 20 | Agenda e override EKAZA saíram do JSON para tabelas SQL; migração tem dry-run e recusa sobrescrita. | Rode `test_sql_lighting_store` e `scripts/migrate_lighting_state.py --dry-run`. | Exige quatro IDs `switch.*` reais e homologação de 100 ciclos por canal. |

## 21–26 — painel operacional

| # | O que foi entregue e como funciona | Como verificar agora | Limite seguro |
|---:|---|---|---|
| 21 | Home resume saúde da estação, idade/qualidade dos sensores e motivo dos controles inibidos. | Execute `npm run dev --prefix web` contra API de teste ou `npm run build --prefix web`. | Um cartão verde não libera hardware em HOLD. |
| 22 | Gráficos consultam histórico de pH, EC, massa, nível, temperaturas, UR e VPD. Qualidade acompanha cada amostra. | Abra **Gráficos**, selecione série/período e compare com `/history`. | Não há interpolação que transforme falha em dado válido. |
| 23 | Alarmes mostram severidade, causa, procedimento e confirmação. Mensagem MQTT precisa chegar como alarme retido. | Abra **Alarmes** e rode `test_alarm_contract`/`test_mqtt_gateway`. | Confirmar leitura não remove a causa física nem rearma automaticamente. |
| 24 | O assistente calcula massa e curva de bomba; pH/EC ficam aguardando ACK Atlas e releitura do padrão. | Abra **Calibração** e rode `test_calibration_assistant`. | Nunca marque calibração como aprovada sem referência rastreável. |
| 25 | Operação cadastra receita, inicia/para batelada e edita irrigações; progresso muda somente com estado/ACK. | Abra **Operação** com perfil operador. | Comando enviado, ACK e efeito físico são estados diferentes. |
| 26 | Navegação por teclado, foco visível, `aria-live`, responsividade, movimento reduzido e Ajuda offline foram incluídos. | Rode typecheck/build e `test_panel_quality`; teste também em celular/teclado. | O service worker não armazena respostas privadas da API. |

## 27–30 — tutoriais e preparação de release

| # | O que foi entregue e como funciona | Como verificar agora | Limite seguro |
|---:|---|---|---|
| 27 | Tutoriais 03–05 cobrem tanques/plataformas, hidráulica e seis linhas de dosagem, cada um com diagrama, passos e aceitação. | Leia em ordem pelo `docs/tutorial/README.md`. | Cotas, bombas, tubos e compatibilidade ainda dependem de medição/amostra. |
| 28 | Tutoriais 06–08 cobrem sensores, quadro SELV e instalação CA. A etapa 08 reserva 127 V a profissional habilitado. | Confira riscos, EPIs, evidências e gate ao fim de cada capítulo. | Pessoa leiga não executa projeto, ligação ou ensaio de rede. |
| 29 | Tutoriais 09–11 cobrem gravação dos três ESP32, Pi/painel e calibração de massa, bombas, pH e EC. | Reproduza primeiro sem carga e registre cada resultado solicitado. | Imagens são diagramas/ilustrações, não fotos de montagem homologada. |
| 30 | Tutoriais 12–14 cobrem HIL, água, primeira batelada e manutenção. Há SBOM SPDX e relatório de prontidão. | Rode o gate e consulte `docs/RELATORIO_PRONTIDAO_V1.md` e `docs/SBOM_E_LICENCAS.md`. | Release candidate/v1.0, HIL físico, fotos reais e fechamento jurídico da SBOM continuam pendentes. |

## Sequência de execução recomendada

1. Em um computador de desenvolvimento, instale as dependências e rode
   `python scripts/quality_gate.py`.
2. Revise o PR e aguarde todos os checks remotos, incluindo builds ESP32,
   Mosquitto TLS e Compose.
3. Para conhecer o sistema, siga os tutoriais 00→14 sem pular gates; mantenha
   cargas desconectadas nas etapas de software.
4. Colete as medidas, plaquetas, amostras e certificados listados no relatório
   de prontidão.
5. Somente depois de PCB, instalação profissional, HIL físico e piloto com
   água aprovados, preparar uma release candidate para nova revisão.

O ciclo atual conclui a implementação planejada em software e documentação,
mas o sistema completo permanece **A0/HOLD** até as evidências físicas.
