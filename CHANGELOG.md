# Changelog

Todas as mudanças relevantes serão registradas neste arquivo. O projeto segue
[Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e pretende adotar
versionamento semântico a partir da primeira release.

## [Não publicado]

### Alterado

- agendas de irrigação sobrepostas, inclusive na virada semanal, agora são
  rejeitadas antes de substituir a configuração válida existente;
- arquitetura física simplificada para notebook, ESP32 único, placa perfurada,
  relés/MOSFETs genéricos, bombas econômicas e recipientes domésticos;
- BOM ativa substituída por checklist cotável de R$ 1.620, com fornecedores por
  categoria e critérios de equivalência sem anúncios inventados;
- pinagem e mapa de atuadores convertidos para 12 GPIO diretos, com saídas
  seguras no boot, exclusão de dosagem e conflito irrigação/dreno;
- operação do hub generalizada para Linux AMD64/ARM64 com Docker;
- tutorial refeito na sequência compra, eletrônica, estrutura, bombas,
  sensores, firmware, hub, água e primeira receita;
- painel passou a descrever DHT22 e módulos analógicos, mantendo o domínio e a
  integração Home Assistant/EKAZA existentes.

### Arquivado

- PCB, Gerbers, netlist, pranchas, laudo, painel industrial, rack sob medida,
  imagens conceituais e tutorial Rev A em `archive/engenharia-pesada/`;
- três firmwares distribuídos e driver Atlas local, substituídos pelo
  controlador DIY único.

### Adicionado

- firmware `controller` com bancos GPIO diretos para seis MOSFETs e seis relés;
- validação nativa do controlador e sete cenários HIL fail-safe;
- validador do orçamento/mapas DIY e inventário automatizado do arquivo.

- umidificador com nível mínimo, timeout absoluto retido e rearme seguro;
- monitor de CO₂ somente leitura, sem qualquer caminho de comando de injeção;
- três firmwares ESP32 PlatformIO e HIL nativo com seis cenários fail-safe;
- drivers/contratos de sensores ambientais e químicos, incluindo compensação
  térmica, qualidade e falhas explícitas;
- contratos MQTT v1 para comando, ACK/NACK e alarmes retidos, com gateway TLS
  ligado ao PostgreSQL, auditoria e WebSocket;
- Mosquitto TLS 1.3 mútuo, ACL por nó e teste de isolamento em contêiner;
- banco operacional PostgreSQL/Alembic, retenção e previsão de capacidade;
- API autenticada de estações, sensores, histórico, configuração, receitas,
  agendas, alarmes, calibração, comandos e auditoria;
- painel Home, gráficos, central de alarmes, calibração, operação, Ajuda
  offline, acessibilidade e reconexão em tempo real;
- Docker Compose ARM64, scripts protegidos de backup/restauração e guia de
  operação do Raspberry Pi;
- persistência SQL e migração sem sobrescrita das agendas/overrides EKAZA;
- tutoriais 03–14 com diagramas, passos, riscos, aceitação e separação clara
  entre ilustração e evidência física;
- SBOM SPDX 2.3 determinística, triagem inicial de licenças e relatório de
  prontidão `A0/HOLD` das tarefas 01–30;
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
- curva volume×tempo por dosadora, correção segura de pH, receita sequencial de
  CalMag/Micro/Bloom/Grow, diluição por EC e mistura periódica;
- agendas de até cinco irrigações, dreno com timeout/pós-tempo e umidificação
  protegida por nível, vazamento, histerese e anti-ciclo;
- controle liga/desliga do exaustor por temperatura/VPD, limites absolutos,
  feedback de corrente/contato e prioridade sobre umidificação;
- persistência atômica, worker com backoff, API FastAPI e inicializador para as
  quatro entidades EKAZA;
- painel React responsivo com agenda, override, estado desejado/observado e
  estados confirmado, divergente ou indisponível;
- revisão integral do vídeo Parte 2 de 18:00, com hash, timestamps, matriz de
  aplicação e adaptações deliberadas;
- validação TypeScript e build Vite incorporados ao Quality Gate e ao CI.

### Segurança

- broker desconectado devolve HTTP 503 e não cria falso estado de fila;
- comando sem ACK/NACK expira em 15 segundos e fica registrado como timeout;
- tópico, estação, nó, função e envelope MQTT precisam corresponder antes
  de persistir leitura, alarme ou confirmação;
- segredos do hub e certificados MQTT são montados em arquivos somente leitura;
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
- lote químico verifica estoque/capacidade antes de iniciar e corta todas as
  saídas diante de intertravamento;
- leitura inválida, timeout ou reserva insuficiente interrompem imediatamente a
  diluição e o dreno mantém alarme retido;
- falha de sensores climáticos adota política degradada/fail-on para exaustão;
- API e painel nunca transformam comando remoto sem confirmação em sucesso.
