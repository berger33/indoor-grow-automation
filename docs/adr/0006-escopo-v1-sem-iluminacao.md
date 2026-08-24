# ADR 0006 — Escopo v1 sem automação de iluminação

- Estado: parcialmente superado pelo ADR 0008
- Data: 2026-08-23

## Contexto

O sistema de referência automatiza hidráulica, dosagem, clima e iluminação. O
responsável pelo projeto já possui uma automação de iluminação independente e
funcional. Manter luz no novo sistema duplicaria funções, aumentaria a potência
de rede no quadro e criaria dependências desnecessárias de drivers, inrush e
interfaces de dimerização.

A revisão do vídeo V1 de 16:36 confirmou como núcleo útil: reservatório de água,
reservatório de mistura, seis dosadoras, bombas de transferência/mistura/rega/
dreno, válvulas, medição de pH/EC/temperatura, nível por massa, detecção de
vazamento e controle ambiental.

## Decisão

A release v1.0 implementará somente:

1. preparação de solução nutritiva em batelada;
2. correção limitada e intertravada de pH e EC;
3. irrigação e drenagem automáticas;
4. controle e monitoramento de temperatura, umidade, VPD, CO₂ e exaustão;
5. segurança hidráulica, elétrica e operacional;
6. hub local, painel mobile-first, histórico, alertas e tutorial de montagem.

Ficam explicitamente fora do escopo:

- acionamento, dimerização ou alimentação de luminárias;
- fotoperíodo, amanhecer/anoitecer e mapas PPFD;
- cadastro de painéis Yuxinou, potência de luz ou driver de LED;
- contatores, disjuntores, chicotes, conectores ou dimerização de iluminação.

O ADR 0008 posteriormente autorizou somente integração lógica do Raspberry Pi
com as tomadas Wi-Fi EKAZA. A fronteira física deste ADR permanece: circuitos,
cabos, potência e responsabilidades elétricas continuam separados.

## Arquitetura física adotada

- **Estação úmida:** seis recipientes de concentrado de 1 L, reservatório de
  água de 50 L, reservatório de mistura/rega de 50 L, bombas, válvulas e sensores
  químicos/hidráulicos.
- **Nó de clima:** sensores instalados no cultivo e interfaces de baixa tensão
  para exaustor e umidificação; aquecimento, resfriamento e desumidificação são
  opcionais e permanecem desabilitados até haver equipamento compatível.
- **Quadro seco:** proteções de rede e fontes, sempre acima e afastado de
  reservatórios e linhas de vazamento; nenhuma rede CA entra na PCB.
- **Hub local:** Raspberry Pi executando broker, API, banco, painel e alertas.

## Consequências

- a BOM e o unifilar deixam de conter quatro painéis e seus contatores;
- nenhuma agenda de iluminação atua por GPIO, borne ou circuito do rack;
- a capacidade de I/O passa a ser calculada somente pelos atuadores hidráulicos,
  dosadores, agitadores e cargas de clima;
- itens observados no vídeo sobre iluminação permanecem na especificação de
  referência, marcados como não aplicáveis ao backlog executável;
- a potência final do circuito não pode ser congelada antes das plaquetas do
  exaustor, umidificador e bombas de rede que forem efetivamente escolhidos.

## Critério de reversão

O ADR 0008 registra a integração lógica solicitada. Qualquer dimmer, circuito,
medição elétrica ou ligação futura ainda exige novo ADR, BOM e análise elétrica,
sem criar dependência no núcleo de fertirrigação e segurança.
