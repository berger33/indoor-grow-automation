# Controladora Rev A

## Estado da revisão

`A0 / HOLD` — especificação elétrica e lógica criada; ainda não há esquema
KiCad, layout roteado, Gerber ou autorização de fabricação.

Esta pasta é a fonte de verdade pré-EDA:

- `BOM.csv`: componentes do sistema e da PCB;
- `pcb-parameters.json`: stack-up, regras e limites;
- `io-map.csv`: pinagem lógica e estado de boot;
- `netlist.csv`: conectividade funcional a ser reproduzida no esquema.

## Limite arquitetural

A PCB recebe 24 VCC, 5 VCC e 3,3 VCC. Rede 127/220 V é proibida. Cargas CA são
comutadas por contatores externos com bobina 24 VCC. As oito saídas da placa são
low-side, no máximo 1 A por canal e 4 A agregados; bombas maiores usam interface
externa.

Os canais pH/EC ficam em carriers Atlas isolados e externos. Sinais I²C longos
não saem do gabinete; sensores distantes devem usar nó ESP32 local ou barramento
diferencial.

## Estado seguro

U2 (`SN74AHCT244`) permanece em alta impedância porque `BUFFER_OE` tem pullup de
10 kΩ. Somente GPIO26 alto satura Q9 e habilita as saídas. Cada gate possui
pulldown independente. Isso reduz acionamento acidental durante boot, mas não
substitui o E-stop físico, fusíveis, contatores e lógica local de timeout.

## Próximo gate

1. desenhar esquema no KiCad a partir do netlist;
2. associar footprints às amostras físicas recebidas;
3. executar ERC;
4. posicionar/rotear segundo `pcb-parameters.json`;
5. executar DRC e inspeção 3D;
6. cruzar BOM/netlist/centroid;
7. fabricar uma unidade A0 e ensaiar antes de congelar A1.
