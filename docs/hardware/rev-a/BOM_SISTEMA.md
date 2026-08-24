# BOM consolidada Rev A

Arquivo mestre: [`hardware/controller-rev-a/BOM.csv`](../../../hardware/controller-rev-a/BOM.csv).

> **Decisão de liberação:** `HOLD`. A BOM está consolidada para cotação e
> protótipo, mas não para compra em lote. Itens `HOLD` dependem de dados físicos;
> `PROVISIONAL` exige amostra/ensaio; `APPROVED_CLASS` aprova requisitos, não um
> anúncio específico; `APPROVED_MODEL` fixa fabricante e modelo.

## Escopo

A BOM cobre:

- quadro 127 V/60 Hz e fontes SELV;
- placa controladora Rev A sem tensão de rede;
- seis canais de dosagem para recipientes de 1 L;
- dois reservatórios de 50 L;
- pH, EC, temperatura, umidade, CO₂, nível/peso e vazamento;
- hub Raspberry Pi e interfaces de campo.
- rack vertical de até 900 × 600 × 2.000 mm, duas prateleiras de tanque
  independentes, backboard selado, ancoragem, prateleiras de três frascos,
  clips segregados e contenção em cascata `CT2 → CT1`.

Tubos, conexões, recipientes, plataformas e contenção já aparecem como linhas
`HOLD` no arquivo mestre. As especificações e quantidades finais serão fechadas
depois de receber dimensões/alturas, traçar o P&ID e medir o percurso hidráulico.

## Pacotes de compra

| Pacote | Conteúdo | Estado atual |
|---|---|---|
| Controle | PCB, ESP32, fontes, bornes e proteção SELV | A0/HOLD |
| Dosagem | 6 frascos, 6 peristálticas, 6 agitadores e tubos | amostras/compatibilidade pendentes |
| Hidráulica | 2 tanques, 4 bombas, 2 válvulas, conexões e contenção | dimensões e curva pendentes |
| Química | pH, EC, temperatura, carriers e padrões de calibração | procedência/ensaio pendentes |
| Clima | temperatura/UR, CO₂, folha, exaustor e umidificador | modelos finais pendentes |
| Hub | Raspberry Pi, armazenamento e fonte | classe definida; kit final pendente |
| Estrutura compacta | rack, backboard, ancoragem, prateleiras dos frascos e dois níveis de tanque | carga/flecha, parede, tanques e amostras pendentes |

## Critérios de substituição

Uma alternativa só pode substituir o item principal quando todos os parâmetros
abaixo forem iguais ou melhores e houver ficha técnica rastreável:

1. função e pinagem;
2. tensão, corrente, potência e corrente de partida;
3. encapsulamento e dimensões mecânicas;
4. faixa de temperatura e umidade;
5. isolação, categoria de uso e certificações aplicáveis;
6. material em contato com água/concentrado;
7. disponibilidade de reposição;
8. resultado dos testes de aceitação.

Para DR, DPS, disjuntores, contatores, fontes e bornes de potência, anúncios sem
código exato, fabricante ou datasheet são rejeitados. Shein não apresentou uma
cadeia adequada para itens elétricos críticos e não é fonte aprovada nesta revisão.

## Disponibilidade verificada em 2026-08-22

| Classe | Evidência atual | Decisão |
|---|---|---|
| ESP32 DevKitC V4 38 pinos | [Mercado Livre](https://www.mercadolivre.com.br/esp32-wroom-32d-devkit-v4-38-pinos-soldados-imediato/p/MLB65017762) | disponível; validar variante física |
| WEG RDWH tipo A, 30 mA | [catálogo WEG](https://www.weg.net/catalog/weg/BR/pt/c/BR_WDC_CIRCUITBREAKER_RDWH/list) | fornecedor brasileiro obrigatório |
| WEG CWC07, bobina 24 VCC | [catálogo WEG](https://www.weg.net/catalog/weg/BR/pt/Automa%C3%A7%C3%A3o-e-Controle-Industrial/Controls/Partida-e-Prote%C3%A7%C3%A3o-de-Motores/Contatores/Pot%C3%AAncia/Minicontatores-CWC0-e-CW0/Minicontatores-CWC0/MINICONTATOR-AZ-CWC07-10-30C03-7A-24V-DC/p/12486689), [Mercado Livre](https://www.mercadolivre.com.br/mini-contator-tripolar-weg-cwc07-7a-690v-24vdc-para-painel-eletrico/p/MLB47182628) | disponível para exaustor/umidificador; validar inrush |
| Mean Well DDR-15G-5 | [Mean Well Brasil](https://www.meanwellbrasil.com.br/conversores-dcdc/conversor-dcdc-para-montagem-em-trilho-din-15w-entrada-de-9-a-36v-5v-3a), [Mercado Livre](https://produto.mercadolivre.com.br/MLB-6665335170-conversor-dc-dc-meanwell-ddr-15g-5-5v-3a-15w-tipo-trilho-din-_JM) | disponível |
| ADS1115 | [Texas Instruments](https://www.ti.com/product/ADS1115), [Shopee](https://shopee.com.br/Conversor-Anal%C3%B3gico-Digital-ADS1115-16-Bits-Adc-Ardu%C3%ADno-i.457636598.20497412231) | módulo requer ensaio de autenticidade |
| STP55NF06L | [STMicroelectronics](https://www.st.com/en/power-transistors/stp55nf06l.html), [Mercado Livre](https://lista.mercadolivre.com.br/55nf06) | comprar lote rastreável |
| bomba peristáltica 24 V | [loja brasileira, 100/200 mL/min](https://www.hgrprinters.com.br/loja/bomba-peristaltica-ink-pump-3w-100-200ml-min-24v/) | classe adequada; tubo a validar |
| SCD41 | [Sensirion](https://sensirion.com/products/catalog/SCD41) | usar módulo rastreável |
| Atlas EZO pH/EC e isolação | [datasheets Atlas](https://atlas-scientific.com/datasheets-manuals/) | preferencial; custo e marketplace a confirmar |

Links de marketplace são evidência temporal, não fornecedor travado. Antes da
compra, o sistema deverá salvar data, vendedor, código, lote, nota fiscal e foto
da marcação recebida.

## Gargalos já identificados

- clones de ADS1115, ESP32, MOSFET e sensores podem não cumprir datasheet;
- a largura/pinagem de placas “ESP32 38 pinos” varia entre fabricantes;
- STP55NF06 sem sufixo `L` não é substituto automático do `STP55NF06L`;
- vazão de 700–3.000 mL/min é excessiva para correção fina de pH em 50 L;
- tubos comuns podem ser incompatíveis com ácido/base/concentrados;
- contatores só podem ser congelados após medir exaustor e umidificador;
- DPS depende do esquema de aterramento e da concessionária;
- bomba de irrigação depende de altura manométrica e vazão, ainda desconhecidas;
- Atlas em marketplace pode ter procedência incerta e custo elevado;
- gabinete 500 × 400 × 200 mm é envelope preliminar, não desenho final.
- rack de até 900 × 600 × 2.000 mm, capacidade total de 250 kg e 100 kg por
  prateleira de tanque são requisitos A0, não especificação aprovada de anúncio;
- `TK-101` cheio eleva o centro de gravidade; a ancoragem deve ser calculada e
  o rack não pode ser usado sem retenção antitombamento aprovada;
- `CT1` precisa demonstrar ao menos 110 L de volume **livre**, já descontados
  `TK-201`, plataforma, pés e tubos; volume geométrico bruto não basta;
- `CT2` precisa drenar por dois caminhos a `CT1` mesmo com um deles obstruído;
- ancoragem depende do material e estado reais da parede e do piso;
- madeira crua observada na referência não é superfície final aprovada.

## Política de lote

1. comprar uma unidade de cada item provisional;
2. inspecionar marcação/dimensões e executar teste de bancada;
3. montar uma única PCB e um quadro sem cargas reais;
4. testar com cargas resistivas e simuladores;
5. testar hidráulica somente com água;
6. executar piloto supervisionado;
7. congelar revisão, hashes de Gerber e AVL;
8. somente então autorizar quantidade maior que uma.
