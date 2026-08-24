# Revisão dirigida — Parte 2: funcionalidade

Fonte: vídeo de 18:00 fornecido em 2026-08-23. Esta revisão compara as funções
demonstradas com o escopo atual. Iluminação e medição PPFD permanecem apenas
como contexto histórico e não geram hardware, API, tela ou backlog do produto.

## Evidências por trecho

| Timestamp | Função observada | Decisão no projeto próprio |
|---|---|---|
| 00:00–00:48 | seis frascos; ventiladores com dois ímãs giram barras magnéticas e mantêm os concentrados misturados | seis F8 de 12 V, doze ímãs, seis barras PTFE, proteção e tacômetro individual |
| 00:49–03:55 | Raspberry Pi/Home Assistant coordena relés, bombas, sensores e comandos de voz | Pi local, MQTT/API e painel web; voz não é requisito de segurança |
| 03:58–04:20 | cinco abas: Home, Calibration, Control, Schedule e Hassio Stats | preservar o fluxo em painel mobile-first, sem cartões de luz |
| 04:20–05:27 | Home mostra duas T/UR, água, pH, EC, nível, dreno/flood e históricos; alerta chega ao telefone | qualidade/idade por leitura, gráficos, alarmes latched e notificação local/remota |
| 05:28–08:58 | Control aciona relés, tomadas, seis peristálticas, alvos de pH/EC, clima e comandos manuais | separar comando/feedback; comandos críticos exigem timeout e auditoria |
| 08:59–12:18 | receita define pH/EC, CalMag/Micro/Bloom/Grow, volume e executa uma batelada | usar CalMag/Micro/Bloom/Veg; pH separado; máquina de estados e limites |
| 12:20–14:39 | Calibration guia pH 7/4/10, EC dry/low/high, PWM/vazão das seis bombas e tara/fator da balança | sessões guiadas, estabilidade, lote/padrão, persistência e validade da calibração |
| 14:40–15:58 | Schedule guarda data, início do cultivo, dia/semana, frequência, duração e até cinco fertirrigações | agenda local de 0–5 eventos com conflito, timezone e recuperação pós-reboot |
| 15:59–17:02 | mesma UI funciona em tablet, desktop e telefone; cartões variam por dispositivo | web responsiva/PWA somente leitura offline; sem app nativo obrigatório |
| 17:03–17:56 | Home Assistant traz add-ons e comunidade, mas configuração completa exige trabalho | instalador ARM64, backup/restauração e tutorial leigo reproduzível |

## Mapa de telas do produto

1. **Visão geral:** pH, EC, temperatura da solução, massa/nível, dois sensores de
   T/UR, VPD, CO₂, vazamentos, dreno e estado físico dos atuadores.
2. **Calibração:** pH, EC, plataformas de massa e seis bombas, com etapa atual,
   valores brutos, tolerância, resultado, lote do padrão e validade.
3. **Controle:** modo, alvos, seis canais nomeados, comando manual temporizado,
   exaustão/umidificação, motivo de inibição e confirmação física.
4. **Agenda:** até cinco irrigações, duração/volume, timezone, próxima execução e
   conflitos; não contém fotoperíodo.
5. **Saúde:** CPU, memória, armazenamento, MQTT, banco, backups, nós e versões.
6. **Alarmes:** ativos, retidos, reconhecidos, causa, ação segura e linha do tempo.

## Lacunas confirmadas e encaminhamento

| Lacuna atual | Backlog/contrato |
|---|---|
| receita ainda não implementada | `F2-011`, `stirrer-contract.json` |
| agenda de cinco eventos ainda não implementada | `F2-014`, `F4-006` |
| calibração guiada incompleta | `F4-004`, `F5-040` |
| comando/feedback físico | `F4-008`, `F2-022` |
| diagnóstico de host/nós | novos itens `F3-015` e `F4-013` |
| notificações de falha | novos itens `F3-016` e `F4-014` |
| histórico de calibração | novos itens `F3-017` e `F4-015` |
| validação de receita e limites | novos itens `F2-025` a `F2-028` |

## Divergências deliberadas de segurança

- o original concentra regras no Home Assistant; o projeto novo mantém
  intertravamentos e timeouts no ESP32 mesmo sem Pi ou Wi-Fi;
- o original permite comando manual direto; aqui todo pulso tem limite, estado
  seguro, auditoria e condição de habilitação;
- o original aproxima 1 kg de água a 1 L; aqui densidade e calibração pertencem
  ao perfil do líquido, sem conversão universal oculta;
- o original limpa parte do alarme por script; aqui vazamento permanece retido
  até condição seca confirmada e rearme explícito;
- o original pode parar o exaustor ao perder PWM; aqui a ventilação mínima possui
  fallback local verificado em comissionamento.

## Pontos não identificados

- tolerância/tempo de estabilidade usados para aceitar cada padrão de pH/EC;
- fabricante, concentração, validade e compatibilidade química dos seis líquidos;
- exatidão real da conversão tempo/PWM→mL ao longo da vida do tubo;
- política quando uma fertirrigação é perdida durante reinicialização;
- confirmação física de que tomada, relé ou bomba realmente acionou;
- retenção de dados, periodicidade de backup e teste de restauração;
- autenticação e autorização entre operadores na interface original.
