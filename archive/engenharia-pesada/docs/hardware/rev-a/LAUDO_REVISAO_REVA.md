# Laudo preliminar de revisão — hardware Rev A

- Revisão avaliada: `A0-rework`
- Data: 2026-08-23
- Resultado: **HOLD — não liberar fabricação nem energização**
- Risco residual atual: **não aceitável para lote**

## 1. Limite do laudo

Este documento registra uma revisão de engenharia baseada em requisitos,
datasheets, cálculos e manifestos. Não existe nesta revisão esquema/layout KiCad,
Gerber, amostra recebida, ensaio elétrico ou protótipo. Portanto, não foi possível
executar ERC/DRC real nem confirmar footprints, isolação, montagem ou desempenho
térmico.

Risco zero não existe em fabricação eletrônica e não pode ser confirmado por uma
revisão “mental”. O objetivo técnico é reduzir risco, medir o residual e impedir
a liberação enquanto evidências obrigatórias estiverem ausentes.

## 2. Evidências executadas

| Verificação | Resultado |
|---|---|
| JSON dos parâmetros | válido |
| BOM × quantidades/referências | coerente |
| I/O × conectores da BOM | coerente |
| Netlist funcional × BOM | coerente |
| Limites placa/fonte/concorrência | coerentes |
| Testes automatizados do repositório | 48 aprovados |
| Scan de segredos | aprovado |
| ERC KiCad | não executado — esquema ainda não existe |
| DRC KiCad | não executado — layout ainda não existe |
| Fit-check de componentes | não executado — amostras não recebidas |
| Teste térmico/EMC/HIL | não executado — protótipo não existe |

O validador encontrou 248 referências únicas e 14 bloqueios explícitos. Além da
PCB e das proteções, permanecem bloqueados exaustor, umidificador, bombas,
tanques, contenção, plataformas, tubos, conexões e válvulas de retenção.

## 3. Revisão elétrica da PCB

### 3.1 Tensão e isolação

- rede CA é proibida na PCB;
- entrada nominal 24 VCC, máximo de projeto 30 VCC;
- sinais trabalham em 5 VCC/3,3 VCC;
- pH e EC usam carriers isolados externos;
- cargas CA ficam em contatores DIN externos de bobina 24 VCC.

Isso elimina da placa os requisitos de creepage/clearance de 127/220 V, mas não
elimina risco no quadro externo.

### 3.2 Dezesseis saídas indutivas

| Item | Verificação de primeira ordem | Resultado |
|---|---|---|
| MOSFET | STP55NF06L, 60 V, gate lógico | margem sobre 24 V; manter rastreabilidade |
| flyback | SB560, 60 V/5 A | adequado a canal de 1 A; polaridade crítica |
| TVS | SMBJ33A na entrada | compatível em princípio; validar transientes no osciloscópio |
| canal | 1 A máximo | trilha 1,5 mm; confirmar temperatura em protótipo |
| backbone | 4 A de capacidade da placa | cobre 3,0 mm/pour; ensaio de 24 h obrigatório |
| instalação | 2,0 A simultâneos | abaixo da fonte 2,5 A e da placa 4 A |

As seis dosadoras não devem partir juntas. Corrente de stall de cada motor deve
ser medida; corrente nominal de anúncio não é suficiente. Bombas hidráulicas e
banco de agitadores usam driver externo enquanto a corrente não comprovar
compatibilidade com o limite de 1 A por canal.

### 3.3 Estado seguro de boot

Os dois `SN74HCT595` ficam em alta impedância por pullup de `REGISTER_OE`.
GPIO26 só habilita as saídas através de Q17 open-collector, evitando aplicar 5 V
ao ESP32. Cada MOSFET possui pulldown de gate. O firmware ainda deverá:

1. configurar todas as saídas como desligadas;
2. deslocar dezesseis zeros e transferi-los ao latch;
3. validar configuração e sensores de segurança;
4. somente então elevar `OUTPUT_ENABLE`;
5. remover a habilitação no watchdog, alarme ou perda de integridade.

O HIL deve injetar corrupção/interrupção em data, clock e latch. A atualização
serial não é considerada feedback físico de bomba, válvula ou contator.

O E-stop corta a alimentação de atuação fisicamente e não depende desse fluxo.

### 3.4 Entradas 24 V optoisoladas

Com dois resistores de 2,2 kΩ em série e queda de LED aproximada de 1,2 V:

```text
I_LED = (24 - 1,2) / 4.400 = 5,18 mA
P_total = 22,8² / 4.400 = 0,118 W
P_por_resistor ≈ 0,059 W
```

Cada resistor é especificado em 0,25 W. A margem de potência é adequada em
regime nominal; tensão máxima da fonte e temperatura devem integrar o ensaio.
O bin de CTR do opto precisa ser documentado.

### 3.5 Entradas 4–20 mA

Shunt de 150 Ω:

```text
V_4mA  = 0,004 × 150 = 0,60 V
V_20mA = 0,020 × 150 = 3,00 V
P_20mA = 0,020² × 150 = 0,060 W
```

O resistor de 0,25 W tem margem térmica. ADS1115 a 3,3 V permanece dentro da
faixa nominal até 20 mA; sobrecorrente depende de resistor série, BAT54S e
proteção externa. Esses canais não substituem os carriers isolados de pH/EC.

## 4. Revisão de fabricação

O envelope preliminar passou de 160 × 100 mm para 200 × 120 mm ao incorporar as
15 funções observadas e uma saída reserva. Parâmetros internos usam
trilha/espaço mínimo de 0,20/0,20 mm e vias de
0,30/0,60 mm. Isso é mais conservador que as capacidades publicadas de 0,10/
0,10 mm para 1 oz da JLCPCB e a recomendação de trabalhar acima de 0,15 mm da
PCBWay. Essa comparação indica fabricabilidade geométrica **do conjunto de
regras**, não de um layout ainda inexistente.

Pontos obrigatórios no layout:

- ESP32 na borda com keepout de antena de pelo menos 15 mm, sem cobre/cabos;
- plano GND contínuo em L2, sem sinal cruzando cortes de retorno;
- MOSFETs, diodos e bornes juntos para reduzir laço indutivo;
- ADC/analógico na extremidade oposta aos motores;
- capacitores de desacoplamento adjacentes aos pinos dos CIs;
- clearances de 0,5 mm nas redes 24 V/saídas;
- bornes com acesso de chave e courtyard real;
- furos M3 com keepout e distância de borda;
- test points para 24 V, 5 V, 3,3 V, OE, I²C e cada saída.

Fontes: [capacidades JLCPCB](https://jlcpcb.com/capabilities/pcb-capabilities),
[capacidades PCBWay](https://www.pcbway.com/capabilities.html) e
[DRC do KiCad](https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html).

## 5. Gargalos de lote

| Risco | Probabilidade atual | Impacto | Mitigação/gate |
|---|---|---|---|
| DevKitC “38 pinos” com largura/pinagem diferente | alta | placa inutilizável | receber amostra e criar footprint pela medição |
| componente falsificado de marketplace | média/alta | falha elétrica/metrológica | vendedor rastreável, inspeção e teste de lote |
| MOSFET sem sufixo `L` | média | aquecimento/não acionamento | MPN exato e curva a 5 V |
| motor do fan incompatível com controle | alta se dimerizado | queima/incêndio | somente liga/desliga até manual |
| umidificador sem proteção de nível | desconhecida | sobreaquecimento/dano | modelo com proteção e intertravamento independente |
| erro no latch serial de 16 canais | média no A0 | atuação incorreta | OE seguro, CRC/espelho lógico, watchdog e HIL |
| bomba dosadora rápida demais | média | sobredosagem química | 30–200 mL/min e calibração de 10 ciclos |
| tubo incompatível com pH+/pH− | desconhecida | vazamento/degradação | ensaio químico e material declarado |
| ruído de motor em pH/EC | média | dosagem errada | isolação, segregação, pausa e teste EMC |
| aquecimento de trilhas/bornes | desconhecida | delaminação/falha | teste 24 h a 2 A e teste curto a limite |
| DPS/proteção inadequados ao aterramento | desconhecida | choque/dano por surto | projeto do quadro após identificar TT/TN-S |
| altura/vazão hidráulica desconhecida | alta | bomba errada | medir percurso e selecionar curva da bomba |
| dimensões dos tanques desconhecidas | alta | layout/plataforma incompatíveis | medir os dois tanques antes de cotar mecânica |

## 6. Critério de liberação A1

A revisão poderá mudar de `HOLD` para `PROTOTYPE_RELEASE` somente quando:

- foto legível da plaqueta do exaustor e dados do umidificador estiverem arquivados;
- aterramento, circuito, distância e método dos cabos forem definidos;
- amostras críticas forem medidas e os footprints congelados;
- esquema KiCad passar ERC sem violações não justificadas;
- layout KiCad passar DRC sem violações não justificadas;
- BOM, netlist, footprints e centroid forem cruzados novamente;
- revisão independente elétrica/PCB estiver assinada;
- protótipo A0 passar continuidade, isolamento, polaridade e safe-boot;
- teste térmico de 24 h e transientes indutivos forem aprovados;
- HIL provar timeout, E-stop, vazamento e perda de rede;
- piloto com água provar hidráulica sem produtos químicos.

Mesmo após esses gates, a declaração correta será “risco residual avaliado e
aceito para protótipo/lote”, nunca “risco zero”.
