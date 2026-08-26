# Diário de progresso

Uma entrada é adicionada ao fim de cada sessão autônoma de desenvolvimento.

## 2026-08-22

- Commits: 32
- Itens concluídos: fundação do repositório; licença; README; especificação e
  pranchas; quatro ADRs; backlog; portão de qualidade; scanner de segredos; CI;
  modelo de sensores; plausibilidade; staleness; contrato MQTT v1 e seus testes;
  publicação no GitHub; templates de colaboração; política de branches/releases;
  atualização automatizada de dependências; modelo configurável de cargas; base
  elétrica 127 V; BOM e controladora SELV A0; validador de hardware; desenhos e
  laudo preliminar Rev A.
- Decisões tomadas: monorepo; intertravamentos locais; FastAPI/MQTT/PostgreSQL/
  React/PlatformIO; faixa diária de 15–25 commits reais; instalação física fixa
  em 127 V/60 Hz; rede CA fora da PCB; exaustor atual somente liga/desliga;
  ausência deliberada de seletor 127/220 V.
- Bloqueios/pendências: plaquetas de luminárias/exaustor, dimensões/alturas dos
  reservatórios, aterramento/percurso de cabos, footprints físicos, ERC/DRC,
  protótipo, teste térmico, HIL e piloto com água.
- Próximos passos: criar esquema KiCad após receber amostras; modelar falhas de
  sensor; implementar filtro de mediana e média móvel configurável.

## 2026-08-23

- Commits: 21
- Itens concluídos: revisão dirigida do vídeo V1 de 16:36; escopo v1 sem
  iluminação; limpeza do backlog, decisões, README e domínio elétrico; base
  127 V revisada; BOM ampliada com seis frascos, dois tanques, hidráulica e
  contenção; matriz de 15 atuadores; controladora A0 redimensionada para 16
  saídas; validador e 48 testes; laudo/unifilar/zonas atualizados; três vistas
  realistas; índice do tutorial e etapa inicial de segurança.
- Decisões tomadas: iluminação permanece integralmente separada; projeto físico
  fixo 127 V/60 Hz sem seletor; PCB somente SELV; 16 saídas por registradores
  `SN74HCT595` com OE seguro; cargas desconhecidas ou acima de 1 A usam driver
  externo; imagens realistas são conceituais e desenhos as-built prevalecem.
- Bloqueios/pendências: plaqueta/modelo do exaustor e do umidificador; dimensões
  dos tanques/frascos; percurso, altura e vazão hidráulicos; abastecimento
  manual ou RO; aterramento/circuito; amostras e footprints; escolha do
  barramento climático; KiCad ERC/DRC; protótipo, HIL e piloto com água.
- Próximos passos: modelar falhas dos sensores; decidir RS-485 versus CAN para o
  nó de clima; fechar P&ID e seleção de bombas após receber as medições físicas.

Esta entrada substitui, para trabalho futuro, todas as menções a iluminação e
plaquetas de luminárias registradas na sessão de 2026-08-22; o histórico anterior
foi preservado apenas para rastreabilidade.

### Continuação autônoma — núcleo de sensores

- Commits: 16
- Itens concluídos: falhas canônicas de aquisição; mediana; média móvel;
  debounce; modelos DS18B20, BME280, MLX90614, Atlas pH, Atlas EC e HX711;
  compensação térmica; nível ultrassônico; vazamento latched; divergência
  climática; VPD foliar; changelog e diário.
- Decisões tomadas: preservar amostra bruta em toda falha; não rearme automático
  de vazamento; VPD negativo permanece visível como risco de condensação;
  compensação de pH é enviada ao circuito Atlas com temperatura validada.
- Bloqueios/pendências: permanecem os HOLDs físicos de plaquetas, dimensões,
  hidráulica, aterramento, footprints, ERC/DRC, protótipo, HIL e piloto com água.
- Próximos passos: criar simuladores determinísticos; publicar diagnóstico de
  qualidade/idade; iniciar máquina de estados local BOOT/IDLE/MANUAL/BATCH/ALARM.

### Continuação dirigida — painel vertical compacto

- Commits: 15
- Itens concluídos: estudo detalhado do painel do vídeo; ADR do rack vertical;
  nova imagem realista; implantação; planta baixa; elevação; P&ID; projeto
  elétrico; rotas de instalações; validação automática dos SVG; caderno de
  pranchas; arquitetura; BOM estrutural; tutorial de montagem seca; índices e
  histórico.
- Decisões tomadas: envelope A0 de 1.200 × 600 × 2.000 mm; seis canais de
  concentrado apesar do sétimo cabeçote não identificado na referência; dois
  tanques lado a lado na base; quadro seco no alto à esquerda; tubos no lado
  molhado; CA não replica a régua de tomadas visível no vídeo.
- Bloqueios/pendências: medir tanques, frascos, ambiente, parede e piso; validar
  carga/ancoragem do rack; fechar contenção; medir hidráulica; selecionar bombas;
  projeto elétrico profissional; ERC/DRC; HIL e piloto com água.
- Próximos passos: levantar dimensões reais; converter cotas A0 em as-built;
  desenvolver tutorial de tanques/plataformas e hidráulica.

## 2026-08-24

- Commits: 19
- Itens concluídos: simulador determinístico de todos os sensores; injeção de
  falhas; diagnóstico de qualidade/idade e saúde da estação; estados locais;
  timeout absoluto; corte por vazamento; safe boot de GPIO; watchdog; heartbeat;
  política de perda do hub; bloqueio pH+/pH−; orçamento de dose; ADR fail-safe;
  tutorial 01 de inventário; README, backlog, changelog e diário atualizados.
- Decisões tomadas: modos `MANUAL` e `BATCH` entram em alarme na perda confirmada
  do hub; timeout não pode ser renovado por comando repetido; conflito entre
  pH+ e pH− desenergiza ambos; o Python é a especificação executável que deverá
  ser reproduzida no firmware ESP32 antes de HIL.
- Bloqueios/pendências: persistência no firmware de alarmes, orçamento e motivo
  de reset; amostras e footprints; dimensões/alturas hidráulicas; plaquetas;
  aterramento; ERC/DRC; revisão elétrica; protótipo; HIL e piloto com água.
- Próximos passos: calibrar volume por tempo de cada dosadora; implementar a
  receita de nutrientes como máquina de estados; criar diluição por EC com
  timeout e confirmação por massa.

### Continuação dirigida — tomadas EKAZA

- Commits: 7
- Itens concluídos: agenda semanal com timezone; override temporário; adaptador
  REST do Home Assistant; confirmação de estado observado; reconciliação sem
  comandos redundantes; ADR de isolamento; tutorial de pareamento e homologação;
  escopo, backlog, decisões e histórico atualizados.
- Decisões tomadas: somente o Raspberry Pi possui a credencial do Home Assistant;
  o ESP32, a PCB, o quadro e os chicotes não possuem função de iluminação; falha
  de tomada/nuvem não interfere no controle do cultivo; comando sem confirmação
  é exibido como divergente.
- Bloqueios/pendências: código exato e plaqueta das tomadas; comprovação como
  entidades `switch`; corrente e inrush das quatro luminárias; cem ciclos por
  canal; persistência, execução periódica, API e tela ainda não implementadas.
- Próximos passos: persistir agendas; executar reconciliação com backoff;
  integrar o snapshot à futura API e à tela mobile-first.

### Continuação dirigida — vídeo Parte 2 e quatro mensagens finais

- Commits: 22
- Itens concluídos: revisão integral do anexo de 18:00; calibração volume×tempo;
  correção de pH; receita CalMag/Micro/Bloom/Grow; diluição por EC; mistura;
  até cinco irrigações; dreno; umidificação; exaustão liga/desliga e feedback;
  prioridade climática; perda do hub nos estados energizados; persistência e
  worker EKAZA; modelos do painel; tela React; build no CI; API FastAPI;
  inicializador das quatro entidades; tutorial e rastreabilidade atualizados.
- Decisões tomadas: a funcionalidade do vídeo é referência, não cópia cega;
  elétrica, dimerização e PPFD das luminárias continuam excluídas; somente o
  Raspberry Pi acessa o Home Assistant; o exaustor atual permanece liga/desliga;
  o painel só declara sucesso após confirmação observada.
- Verificação: 229 testes Python aprovados; TypeScript aprovado; build Vite de
  produção aprovado; 255 referências de hardware coerentes; oito pranchas Rev A
  válidas; scanner de segredos aprovado.
- Bloqueios/pendências: IDs/modelos reais das tomadas; corrente/inrush e cem
  ciclos de cada luminária; plaqueta/corrente de partida do exaustor; firmware
  ESP32; persistência PostgreSQL; telas gerais, histórico e gráficos; medições
  hidráulicas; ERC/DRC; protótipo; HIL e piloto supervisionado com água.
- Próximos passos: receber os IDs `switch.*` e plaquetas, homologar EKAZA em
  bancada, portar os laços testados para o firmware e avançar as telas gerais.

### Continuação dirigida — tarefas 01–30 em um ciclo

- Commits: 22.
- Itens concluídos em software/documentação: proteção do umidificador;
  monitor de CO₂; três projetos ESP32 e HIL nativo; sensores ambientais e
  químicos; processo de fertirrigação; hidráulica/clima; MQTT/ACK/NACK;
  Mosquitto TLS/ACL; PostgreSQL/Alembic; telemetria/retenção; API e
  configuração; usuários/perfis/auditoria; WebSocket; Compose ARM64 e
  backup/restauração; EKAZA em SQL; todas as telas planejadas; tutoriais
  03–14; SBOM e relatório de prontidão.
- Integração fechada: o runtime recebe telemetria/alarmes MQTT no banco,
  publica comandos QoS 1 com validade de 15 s e atualiza auditoria/batelada
  somente por ACK/NACK. Broker indisponível ou ACK ausente produz falha
  explícita, nunca sucesso presumido.
- Verificação local: 279 testes Python; seis cenários HIL fail-safe; typecheck
  e build Vite; 255 referências de hardware; oito pranchas Rev A; SBOM
  sincronizada; scanner de segredos aprovado.
- Decisões preservadas: nenhuma alteração de escopo; CO₂ continua somente
  monitorado; iluminação continua fora da elétrica e apenas a integração
  lógica EKAZA permanece; merge depende de autorização específica.
- Bloqueios/pendências: checks remotos do PR; medidas e plaquetas; IDs/modelos
  EKAZA e cem ciclos; footprints, ERC/DRC, protótipo e ensaios; Pi/SSD reais;
  HIL físico, piloto com água e primeira batelada; revisão 127 V profissional;
  montagem limpa/fotos reais; SBOM transitiva e licença OneWire conclusiva.
- Próximos passos: abrir PR e aguardar CI; depois, com autorização de merge,
  iniciar somente as atividades físicas desbloqueadas por dados/equipamentos.

## 2026-08-25

### Migração para hardware DIY econômico

- Commits planejados: 15.
- Itens concluídos: README e escopo DIY; BOM/ checklist de R$ 1.620; GPIO e
  atuadores diretos; controlador ESP32 único; DHT22 e pH/EC analógicos; tutorial
  completo; hub documentado para notebook; documentação pesada preservada em
  arquivo histórico; painel atualizado apenas nas referências físicas.
- Decisões tomadas: manter FastAPI, PostgreSQL, Mosquitto, contratos MQTT,
  painel e integração Home Assistant/EKAZA; usar seis MOSFETs para dosagem e
  seis canais de relé; agitação manual dos potes na configuração-base; manter
  timeout absoluto, uma dosadora por vez, pH+/pH− e irrigação/dreno exclusivos.
- Verificação local: 279 testes Python; typecheck e build Vite; compilação
  PlatformIO `native_syntax` do controlador; sete cenários HIL; BOM, mapas,
  arquivo, SBOM e scanner de segredos aprovados.
- Bloqueios físicos: receber e identificar módulos; conferir lógica 3,3 V;
  limitar pH/EC a 3,3 V; medir corrente/vazão; calibrar seis dosadoras e sondas;
  testar estrutura/contenção; executar piloto somente com água e primeira
  receita supervisionada.
- Próximos passos: aguardar o build ESP32 do CI; depois comprar/conferir peças e
  seguir os gates do tutorial sem usar os documentos arquivados como montagem.

## 2026-08-26

- Commits: 7.
- Lacuna fechada: transporte Wi-Fi/MQTT com mTLS entre o ESP32 DIY único e o
  Mosquitto, antes inexistente no firmware.
- Itens concluídos: identidade única `grow-01-controller`; ACL e rotas do hub
  alinhadas ao nó `controller`; TLS 1.2 mínimo sem modo inseguro; sincronização
  de relógio; LWT retido; heartbeat; reconexão limitada; perda real do MQTT
  entregue ao fail-safe; segredos locais ignorados; SBOM e tutorial atualizados.
- Verificação local: 286 testes Python; nove cenários HIL virtuais; compilação
  nativa do controlador; typecheck e build Vite; 49 referências DIY; SBOM e
  scanner de segredos aprovados. O build ESP32 e o ensaio Mosquitto em contêiner
  ficam condicionados ao CI, pois este executor não oferece toolchain nem Docker.
- Decisões tomadas: manter uma única identidade de controlador; aceitar TLS 1.2
  como mínimo compatível e TLS 1.3 quando negociado; não assinar comandos nesta
  entrega para separar transporte de execução segura.
- Bloqueios/pendências: conexão em Wi-Fi/broker físicos; emissão dos
  certificados reais; cinco boots; HIL físico; teste com água; telemetria,
  alarmes, comandos e ACK/NACK ainda não estão transportados pelo firmware.
- Próximos passos: publicar telemetria/alarmes v1; implementar comandos e
  ACK/NACK idempotentes; executar E2E virtual controlador–broker–hub–banco.
