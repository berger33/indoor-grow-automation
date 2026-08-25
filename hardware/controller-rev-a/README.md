# Controlador DIY no caminho legado `controller-rev-a`

Este diretório preserva o caminho histórico usado pelo hub, testes e links. Seu
conteúdo ativo agora descreve uma montagem simples em placa perfurada, **sem PCB
customizada**.

## Componentes de controle

- 1 ESP32 DevKit genérico;
- 1 módulo de relé de 8 canais, ativo em nível baixo;
- 2 módulos MOSFET de 4 canais, dos quais 6 canais são usados;
- 1 conversor buck de 12 V para 5 V;
- bornes, fusíveis, resistores de pull e caixa plástica.

A BOM completa está em [`BOM.csv`](BOM.csv). A pinagem vinculante está em
[`io-map.csv`](io-map.csv). O mapa lógico das 12 saídas está em
[`../system/actuator-map.csv`](../system/actuator-map.csv).

## Estados elétricos

Os seis canais MOSFET são ativos em `HIGH` e iniciam em `LOW`. Os seis canais de
relé usados são ativos em `LOW` e iniciam em `HIGH`. O firmware escreve primeiro
o nível inativo e somente depois configura cada pino como saída para reduzir
pulsos durante o boot.

Os canais 7 e 8 do módulo de relé permanecem sem fio e desligados. `OUT12` é um
canal auxiliar bloqueado em software até existir uma função documentada.

## Regras de montagem

1. Não use protoboard sem solda como instalação permanente.
2. Meça 5,0 V na saída do buck antes de conectar módulos.
3. Confirme com multímetro que pH/EC ficam entre 0 e 3,3 V em toda a faixa.
4. Use pulldown nos MOSFETs e resistores externos nas entradas GPIO36/GPIO39.
5. Ligue todos os GND de baixa tensão em comum, seguindo o módulo recebido.
6. Use um fusível dimensionado em cada grupo de bombas.
7. Mantenha cabos analógicos separados dos cabos de motores e relés.
8. Instale eletrônica no alto, dentro da caixa seca, com alças de gotejamento.
9. Teste uma saída por vez com LED ou multímetro antes de conectar bombas.
10. Nunca use as pranchas arquivadas para esta montagem.

## Limite de segurança

O módulo de relé não transforma uma montagem aberta em equipamento seguro para
rede elétrica. Se algum canal comandar 127 V, os bornes e emendas precisam ficar
inacessíveis em caixa fechada com alívio de tração. A alternativa preferível é
usar um aparelho ou tomada pronta e certificada com entrada de comando adequada.
