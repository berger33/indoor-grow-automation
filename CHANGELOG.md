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
- direção vertical em rack de envelope máximo A0 900 × 600 × 2.000 mm, com
  `TK-101` acima de `TK-201` em níveis independentes;
- visualização realista compacta corrigida com seis canais e dois tanques de
  50 L empilhados;
- implantação, planta baixa, elevação, P&ID hidráulico, projeto elétrico e
  planta de instalações em seis novas pranchas Rev A;
- caderno multidisciplinar com hierarquia documental e gates para A1;
- estrutura mecânica incorporada à BOM com rack de 250 kg, prateleiras de
  100 kg, ancoragem e contenção `CT2 → CT1` em estado HOLD;
- tutoriais A0 de montagem seca, níveis independentes, plataformas e contenção;
- validador de integridade para oito pranchas SVG integrado ao Quality Gate.
- contrato executável que rejeita regressão de geometria, apoio compartilhado,
  inclusão de iluminação ou contenção inferior a 110 L livres;
- quatro testes do contrato empilhado, elevando a suíte para 106 testes;
- remoção das duas vistas realistas incompatíveis com a montagem corrente.
- quatro PNGs reais com validação de assinatura, CRC, descompressão e dimensões;
- vistas rotuladas de estação, conjunto aberto e quadro, sem dependência de WebP;
- contrato de seis canais pH Down, CalMag, Micro, Bloom, Veg e pH Up;
- banco de seis ARCTIC F8 12 V, doze ímãs, barras PTFE, proteções e tacômetros;
- intertravamento de dosagem por rotação com alarme retido e 6 testes;
- sequência de referência CalMag → Micro → Bloom → Veg, com pausas de 60 s;
- revisão completa da Parte 2, do vídeo de PCB e do exaustor;
- perfil alvo AC Infinity CLOUDLINE S6 com interface direta mantida em HOLD;
- controle de exaustão por degraus com limites absolutos e fallback diferente de zero;
- ADR de integração lógica com tomadas EKAZA via Home Assistant/Tuya;
- agenda timezone-aware e override temporário das tomadas, sem GPIO ou carga local;
- tutoriais de dosagem/agitação e de integração EKAZA;
- pranchas Rev A de seis canais e quadro SELV aberto, totalizando dez folhas;
- 132 testes unitários, 288 referências de hardware e 24 HOLDs explícitos.

### Segurança

- rejeição de identificadores, unidades e números não finitos;
- rejeição de campos MQTT ausentes, extras ou com tipos ambíguos;
- scanner impede tokens, chaves privadas e segredos atribuídos.
- falhas de aquisição preservam valor e timestamp brutos para diagnóstico;
- vazamento não é apagado automaticamente quando o sensor volta a indicar seco.
- perda de rotação bloqueia a dosadora correspondente e exige rearme explícito;
- perda de controlador ou sensores climáticos não seleciona exaustão zero;
- controle direto do CLOUDLINE permanece bloqueado sem manual/pinagem da amostra;
- iluminação não adiciona relé, borne, cabo ou credencial à PCB/ESP32;
- portão rejeita PNG truncado e qualquer nova referência a WebP.
