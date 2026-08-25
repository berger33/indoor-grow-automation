# ADR 0007 — Layout vertical compacto e modular

- Status: aceito para A0; cotas físicas em validação
- Data: 2026-08-23

## Contexto

O painel do vídeo usa um rack vertical para concentrar interface, dosadoras,
frascos e reservatório em pequena área de piso. A primeira visualização própria
separava excessivamente os módulos e ocupava uma parede maior. O projeto precisa
preservar a eficiência espacial sem copiar improvisos como tomadas na zona
molhada, eletrônica exposta ou tubos sobre circuitos.

## Decisão

Adotar como envelope A0 um rack metálico de **1.200 mm de largura, 600 mm de
profundidade e 2.000 mm de altura**, sujeito à confirmação dos recipientes reais.
O rack será dividido verticalmente:

1. base: contenção secundária, duas plataformas e dois tanques de 50 L;
2. centro inferior: painel hidráulico removível, com bombas, válvulas e sondas;
3. centro superior esquerdo: gabinete seco e seis peristálticas acessíveis;
4. centro superior direito: seis recipientes de 1 L, em duas bandejas de três;
5. topo: passagem segregada de chicotes SELV e rede/barramento de comunicação.

Rede 127 V permanece em quadro seco fechado e acessível apenas a profissional.
Tubos descem pela lateral molhada e nunca atravessam sobre gabinete, Raspberry
Pi ou bornes. Cada recipiente, cabeçote e tubo pode ser removido pela frente sem
desmontar outro canal.

## Consequências

- área de piso-alvo da estação: 0,72 m², antes das faixas de manutenção;
- comprimento de tubos de dosagem e quantidade de cruzamentos são reduzidos;
- a frente inteira precisa permanecer livre para retirada dos tanques;
- o rack deve ser ancorado e verificado para carga estática superior a 150 kg;
- tanques, bandeja e plataformas precisam caber no envelope máximo indicado;
- o painel hidráulico recebe proteção contra respingos, mas continua separado
  do gabinete elétrico;
- a imagem realista é ilustrativa; plantas, P&ID, unifilar e as-built prevalecem.

## Gates

O envelope não autoriza compra até medir tanques, recipientes e local. A
liberação exige cálculo/ensaio estrutural do rack, inspeção de tombamento,
capacidade da contenção, revisão elétrica, estanqueidade e montagem piloto com
água.