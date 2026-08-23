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