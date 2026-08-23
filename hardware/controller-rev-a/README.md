# Controladora Rev A

## Estado da revisão

`A0 / REWORK / HOLD` — a revisão de escopo elevou a capacidade necessária de
oito para dezesseis saídas. Ainda não há esquema KiCad, layout roteado, Gerber
ou autorização de fabricação.

Esta pasta é a fonte de verdade pré-EDA:

- `BOM.csv`: componentes do sistema e da PCB;
- `pcb-parameters.json`: stack-up, regras e limites;
- `io-map.csv`: pinagem lógica e estado de boot;
- `netlist.csv`: conectividade funcional a ser reproduzida no esquema.

## Limite arquitetural

A PCB recebe 24 VCC, 5 VCC e 3,3 VCC. Rede 127/220 V é proibida. Cargas CA são
comutadas por contatores externos com bobina 24 VCC. As dezesseis saídas da
placa são low-side, no máximo 1 A por canal e 4 A agregados; bombas maiores usam
interface externa. O mapa funcional está em `hardware/system/actuator-map.csv`.

Na instalação padrão, a fonte HDR-60-24 limita o sistema a 2,5 A. O firmware
deve impor no máximo 2,0 A simultâneos e sequenciar as seis dosadoras. Os 4 A são
capacidade de projeto da distribuição da placa, não autorização para trocar a
fonte sem nova revisão elétrica e térmica.

Os canais pH/EC ficam em carriers Atlas isolados e externos. Sinais I²C longos
não saem do gabinete; sensores distantes devem usar nó ESP32 local ou barramento
diferencial.

## Estado seguro

U13/U14 (`SN74HCT595`) permanecem em alta impedância porque `REGISTER_OE` tem
pullup de 10 kΩ. Somente GPIO26 alto satura Q17 e habilita as saídas. Cada gate
possui pulldown independente. Antes de habilitar, o firmware deve deslocar
dezesseis bits zero e transferi-los ao latch.

O registrador serial reduz o número de GPIO e atualiza todos os canais de forma
atômica. Watchdog, leitura do estado comandado e feedback físico das cargas
continuam obrigatórios; o latch não substitui nenhum deles.

## Próximo gate

1. desenhar esquema no KiCad a partir do netlist;
2. associar footprints às amostras físicas recebidas;
3. executar ERC;
4. posicionar/rotear segundo `pcb-parameters.json`;
5. executar DRC e inspeção 3D;
6. cruzar BOM/netlist/centroid;
7. fabricar uma unidade A0 e ensaiar antes de congelar A1.
