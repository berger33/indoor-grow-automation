# Changelog

Todas as mudanças relevantes serão registradas neste arquivo. O projeto segue
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e pretende adotar
versionamento semântico a partir da primeira release.

## [Não publicado]

### Adicionado

- estrutura inicial do repositório;
- especificação de referência e seis pranchas técnicas;
- decisões iniciais de arquitetura e segurança;
- backlog executável por fases.
- portão local e CI com compilação Python, 29 testes e scan de segredos;
- modelo imutável de amostras com unidade, timestamp e qualidade;
- validação de plausibilidade e política de telemetria stale;
- contrato MQTT de telemetria v1 com codec estrito e schema JSON;
- templates estruturados de issue e pull request;
- política de branches, commits e releases;
- atualizações semanais de Actions e dependências Python via Dependabot.
- modelo de cargas ambientais configuráveis com corrente medida, de placa ou
  estimada;
- escopo v1 restrito a fertirrigação, irrigação, clima, segurança, hub e tutorial;
- base elétrica fixa 127 V/60 Hz sem qualquer circuito de iluminação;
- revisão dirigida do vídeo V1 de hardware com evidências por timestamp;
- BOM A0 de quadro, controladora, seis frascos, dois tanques, hidráulica,
  sensores, atuadores, contenção e hub;
- matriz de 15 funções comandadas e controladora redimensionada para 16 canais;
- registradores `SN74HCT595`, safe enable e atualização atômica das saídas;
- manifestos de I/O, netlist e parâmetros de fabricação da PCB SELV 200 × 120 mm;
- validação automática de 248 referências e da matriz de atuadores;
- laudo preliminar e desenhos técnicos atualizados para `A0/REWORK/HOLD`;
- três visualizações realistas conceituais da estação, fertirrigação e clima;
- índice de tutorial em 15 etapas e capítulo inicial de segurança.
- taxonomia canônica para timeout, CRC, desconexão, calibração e falhas de
  protocolo dos sensores;
- filtros configuráveis de mediana, média móvel e debounce digital;
- decodificadores testáveis para DS18B20, BME280, MLX90614, Atlas EZO-pH e
  Atlas EZO-EC;
- compensação térmica validada para circuitos de pH/EC e normalização de EC;
- calibração persistível de plataformas HX711 e estimativa ultrassônica de
  volume com filtro e zona morta;
- detecção de vazamento retida até confirmação seca e rearme explícito;
- diagnóstico de divergência climática e cálculo de VPD foliar com alerta de
  condensação.
- estudo detalhado da disposição compacta do painel original, incluindo a
  ambiguidade entre seis frascos e sete cabeçotes aparentes;
- direção vertical em rack de envelope A0 1.200 × 600 × 2.000 mm;
- nova visualização realista compacta com seis canais e dois tanques de 50 L;
- implantação, planta baixa, elevação, P&ID hidráulico, projeto elétrico e
  planta de instalações em seis novas pranchas Rev A;
- caderno multidisciplinar com hierarquia documental e gates para A1;
- estrutura mecânica do rack incorporada à BOM com ancoragem e contenção em
  estado HOLD;
- tutorial A0 de montagem seca, inspeção dimensional e segregação das zonas;
- validador de integridade para oito pranchas SVG integrado ao Quality Gate.
- simuladores determinísticos para todos os tipos de sensor, com injeção de
  falhas canônicas;
- diagnóstico por leitura e resumo de saúde da estação com sensores ausentes;
- máquina local `BOOT/IDLE/MANUAL/BATCH/ALARM` com alarme retido;
- timeout absoluto de atuador que comandos repetidos não conseguem prorrogar;
- supervisor de vazamento integrado ao corte local e rearme seco explícito;
- inicialização de GPIO por polaridade com enable posterior ao estado seguro;
- watchdog local, motivo de reset e heartbeat sequenciado do hub;
- política de perda de rede que interrompe modos ativos e rejeita comandos;
- exclusão mútua retida de pH+ e pH−;
- orçamento de dosagem por evento, janela horária e janela diária;
- ADR do núcleo fail-safe e tutorial de inventário/inspeção de recebimento.
- agenda semanal de tomadas Wi-Fi com timezone, períodos cruzando meia-noite e
  override manual com expiração;
- cliente da API REST do Home Assistant para entidades `switch`, com token
  somente em runtime e confirmação após o comando;
- reconciliador que compara estado desejado e observado sem repetir comandos;
- ADR e tutorial de pareamento/homologação das tomadas EKAZA, mantendo toda a
  alimentação e fiação de iluminação fora da estação.

### Segurança

- rejeição de identificadores, unidades e números não finitos;
- rejeição de campos MQTT ausentes, extras ou com tipos ambíguos;
- scanner impede tokens, chaves privadas e segredos atribuídos.
- falhas de aquisição preservam valor e timestamp brutos para diagnóstico;
- vazamento não é apagado automaticamente quando o sensor volta a indicar seco.
- alarme local não pode ser limpo pelo painel enquanto a causa física persiste;
- novo comando não renova o timeout absoluto de uma saída energizada;
- perda do hub não deixa `MANUAL` ou `BATCH` operando sem supervisão;
- pedido simultâneo de pH+ e pH− desenergiza ambos e bloqueia nova dose.
- falha ou divergência de tomada remota permanece explícita e nunca interfere
  nos intertravamentos de fertirrigação, hidráulica ou clima.
