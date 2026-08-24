# ADR 0007 — Layout vertical compacto com reservatórios empilhados

- Status: aceito para A0; cotas físicas em validação
- Data: 2026-08-23

## Contexto

O painel do vídeo usa um rack vertical para concentrar interface, dosadoras,
frascos e reservatórios em pequena área de piso. A revisão A0 anterior colocou
os dois tanques lado a lado e alargou o rack sem necessidade. O projeto precisa
preservar a eficiência espacial sem copiar improvisos como tomadas na zona
molhada, eletrônica exposta ou tubos sobre circuitos.

## Decisão

Adotar como envelope máximo A0 um rack metálico de **900 mm de largura, 600 mm
de profundidade e 2.000 mm de altura**, sujeito à confirmação dos recipientes
reais. Essa cota não é atribuída ao rack original, cuja dimensão não pôde ser
lida. O rack próprio será dividido verticalmente:

1. base: `TK-201`, reservatório de mistura/rega de 50 L, sobre plataforma de
   pesagem própria e dentro da contenção inferior;
2. nível intermediário: `TK-101`, reservatório de água de 50 L, sobre
   prateleira e plataforma de pesagem independentes;
3. coluna molhada lateral: painel hidráulico removível, bombas, válvulas,
   uniões, sondas e descida da contenção superior;
4. topo esquerdo: gabinete seco, HMI e seis peristálticas acessíveis;
5. topo direito: seis recipientes de 1 L, em duas bandejas de três;
6. perímetro: passagens segregadas de CA, SELV/dados, tubos e dreno.

Rede 127 V permanece em quadro seco fechado e acessível apenas a profissional.
Tubos descem pela lateral molhada e nunca atravessam sobre gabinete, Raspberry
Pi ou bornes. Cada recipiente, cabeçote e tubo pode ser removido pela frente sem
desmontar outro canal. `TK-101` e `TK-201` não se tocam: o tanque superior nunca
usa a tampa, as paredes ou a plataforma do inferior como apoio.

A contenção será em cascata. Uma bandeja estanque sob `TK-101` conduz qualquer
vazamento por dois caminhos gravitacionais inspecionáveis à bacia inferior. A
bacia inferior deverá demonstrar pelo menos 110 L de **volume livre útil**, já
descontados tanque, plataforma, pés e tubulações. Essa solução permanece HOLD
até cálculo geométrico e ensaio de derramamento.

## Consequências

- área de piso-alvo da estação: no máximo 0,54 m², redução de 25% em relação à
  revisão lado a lado de 0,72 m²;
- comprimento de tubos de dosagem e quantidade de cruzamentos são reduzidos;
- a frente inteira precisa permanecer livre para retirada de cada nível;
- tanque cheio não é retirado manualmente: deve ser drenado para massa segura;
- o rack deve ter capacidade documentada mínima de 250 kg distribuídos, cada
  prateleira de tanque deve suportar ao menos 100 kg e a ancoragem antitombamento
  deve ser calculada para a massa elevada de `TK-101`;
- tanques, bandejas e plataformas precisam caber no mesmo prumo de 900 × 600 mm;
- o painel hidráulico recebe proteção contra respingos, mas continua separado
  do gabinete elétrico;
- a imagem realista é ilustrativa; plantas, P&ID, unifilar e as-built prevalecem.

## Gates

O envelope não autoriza compra até medir tanques, recipientes e local. A
liberação exige gabarito físico dos dois níveis, cálculo/ensaio estrutural do
rack e prateleiras, inspeção de tombamento, teste de plataformas sem acoplamento,
ensaio de 110 L livres da contenção em cascata, revisão elétrica, estanqueidade
e montagem piloto somente com água.
