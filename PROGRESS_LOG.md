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
  implantação, planta baixa, elevação, P&ID, projeto elétrico, rotas de
  instalações, validação dos SVG, caderno, arquitetura, BOM e tutorial. Os
  artefatos mecânicos foram reemitidos na correção dirigida abaixo.
- Decisões tomadas: seis canais de concentrado apesar do sétimo cabeçote não
  identificado; quadro seco no alto à esquerda; tubos no lado molhado; CA não
  replica a régua de tomadas visível no vídeo.
- Bloqueios/pendências: medir tanques, frascos, ambiente, parede e piso; validar
  carga/ancoragem do rack; fechar contenção; medir hidráulica; selecionar bombas;
  projeto elétrico profissional; ERC/DRC; HIL e piloto com água.
- Próximos passos: levantar dimensões reais; converter cotas A0 em as-built;
  desenvolver tutorial de tanques/plataformas e hidráulica.

### Correção dirigida — reservatórios empilhados

- Commits: 20
- Itens concluídos: confirmação dos limites da evidência do vídeo; ADR corrigido;
  imagem realista substituída; remoção das vistas incompatíveis; implantação,
  planta, elevação, P&ID e rotas reemitidos; arquitetura e caderno consolidados;
  BOM de rack/prateleiras/contenção em cascata; tutoriais 02 e 03; contrato de
  layout e quatro testes; backlog, escopo, decisões e histórico atualizados.
- Decisões tomadas: rack A0 de no máximo 900 × 600 × 2.000 mm; `TK-101` de
  50 L acima de `TK-201` de 50 L; plataformas e prateleiras independentes;
  capacidade mínima de 250 kg no rack e 100 kg por nível; `CT2` com dois drenos
  para `CT1` de 110 L livres. A capacidade dos totes do vídeo permanece não
  identificada; 50 L é requisito do responsável, não dado inferido da imagem.
- Bloqueios/pendências: medir tanques, tampas, local, parede e piso; selecionar
  rack e ancoragem; calcular/ensaiar `CT1/CT2`; congelar plataformas; revisar a
  estrutura e a elétrica profissionalmente; ERC/DRC, protótipo, HIL e piloto
  somente com água.
- Testes: 106 testes unitários; 8 SVG Rev A válidos; 256 referências de hardware
  coerentes; scan de segredos aprovado; 19 itens continuam em HOLD explícito.
- Próximos passos: levantar as dimensões as-built; cotar uma amostra de rack que
  cumpra carga/flecha; iniciar a máquina de estados local e os intertravamentos.

### Continuação dirigida — imagens, dosagem, clima e EKAZA

- Commits: 23
- Itens concluídos: substituição dos WebP truncados por quatro PNGs validados;
  três vistas rotuladas; confirmação de seis F8, doze ímãs e seis barras PTFE;
  contrato pH Down/CalMag/Micro/Bloom/Veg/pH Up; tacômetros e intertravamento de
  rotação; tutorial 05; revisão do vídeo de PCB e da Parte 2; perfil CLOUDLINE
  S6; fallback de exaustão; ADR, agenda e tutorial de tomadas EKAZA; duas novas
  pranchas; backlog, decisões, changelog e diário atualizados.
- Decisões tomadas: `Veg` mantém alias `Grow` do original; agitadores usam 12 V
  em velocidade total; pH fica fora da receita base; CLOUDLINE S6 `AI-CLS6` é o
  alvo, mas controle direto aguarda pinagem da amostra; iluminação não possui
  hardware no rack, porém o hub pode comandar tomadas EKAZA via integração
  oficial Home Assistant/Tuya.
- Bloqueios/pendências: medir frascos, ímãs, barras, tubos, duto, filtros e
  tanques; comprovar Smart Life/Tuya nas tomadas; medir corrente/inrush das
  quatro luminárias; receber S6 e confirmar revisão; ERC/DRC, revisão elétrica,
  protótipo, HIL e piloto somente com água.
- Testes: 132 testes unitários; 10 SVG Rev A; 4 PNG íntegros; 288 referências de
  hardware coerentes; scan de segredos aprovado; 24 HOLDs explícitos.
- Próximos passos: implementar adaptador Home Assistant/Tuya com confirmação;
  criar máquina de estados completa da receita; fechar calibrações e agenda de
  cinco fertirrigações.

Esta entrada supera a decisão anterior de excluir toda integração de luz: a
fronteira elétrica continua absoluta, mas o ADR 0008 autoriza comando lógico das
tomadas EKAZA pelo Raspberry Pi.
