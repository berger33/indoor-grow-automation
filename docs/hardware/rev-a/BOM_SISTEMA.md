# BOM do sistema DIY

Arquivo mestre importável: [`hardware/controller-rev-a/BOM.csv`](../../../hardware/controller-rev-a/BOM.csv).

Esta BOM substitui a configuração industrial Rev A. O nome do diretório foi
mantido para preservar links e histórico, mas **não existe PCB customizada nem
painel industrial no escopo ativo**.

## Premissas da estimativa

- preços de planejamento em reais, consultados por classe de produto em agosto
  de 2026;
- fornecedores indicados por tipo, sem travar anúncio ou vendedor;
- frete, ferramentas, nutrientes, notebook e serviço elétrico não incluídos;
- estante e caixas podem ser novas ou usadas, desde que íntegras e compatíveis;
- todo item marcado `VALIDAR` exige conferência física antes de instalar;
- componentes analógicos baratos exigem calibração frequente e não oferecem a
  mesma estabilidade de uma interface laboratorial isolada.

## Lista completa

| Item | Qtd. | Característica necessária | Onde procurar | Unitário | Subtotal |
|---|---:|---|---|---:|---:|
| ESP32 DevKit genérico | 1 | GPIO de 3,3 V; variante de 30 ou 38 pinos documentada | Mercado Livre, AliExpress, loja de robótica | R$ 55 | R$ 55 |
| Módulo relé 8 canais | 1 | 5 V, optoacoplado, entrada compatível com 3,3 V, ativo em LOW | Mercado Livre, AliExpress, loja de robótica | R$ 40 | R$ 40 |
| Módulo MOSFET 4 canais | 2 | MOSFET lógico, PWM, 12 V, entrada 3,3 V | Mercado Livre, AliExpress, loja de robótica | R$ 25 | R$ 50 |
| Placa perfurada e bornes | 1 kit | soldável, conectores firmes e removíveis | Mercado Livre, loja local | R$ 30 | R$ 30 |
| Fonte 12 V / 15 A | 1 | proteção contra curto; corrente final confirmada por medição | Mercado Livre, loja de eletrônica | R$ 90 | R$ 90 |
| Conversor 12→5 V / 3 A | 1 | buck ajustável; saída medida em 5,0 V | Mercado Livre, AliExpress | R$ 15 | R$ 15 |
| Porta-fusíveis e fusíveis DC | 8 | valores escolhidos pela corrente medida | loja automotiva/elétrica | R$ 2,50 | R$ 20 |
| Bomba peristáltica 12 V | 6 | 30–100 mL/min, tubo substituível | Mercado Livre, AliExpress, loja de robótica | R$ 55 | R$ 330 |
| Bomba de água 12 V | 3 | mistura, irrigação e drenagem | loja de aquário, Mercado Livre | R$ 25 | R$ 75 |
| Kit pH analógico com sonda | 1 | BNC e saída limitada a 0–3,3 V | Mercado Livre, loja de robótica | R$ 110 | R$ 110 |
| Kit EC analógico com eletrodo | 1 | faixa útil cobrindo 0–20 mS/cm; não usar sensor de solo | Mercado Livre, loja de robótica | R$ 120 | R$ 120 |
| DHT22/AM2302 | 1 | sensor digital de temperatura/UR | Mercado Livre, loja de robótica | R$ 35 | R$ 35 |
| Sensor de vazamento | 2 | saída digital compatível com 3,3 V | Mercado Livre, AliExpress | R$ 10 | R$ 20 |
| Boia de nível | 2 | contato seco NO/NC, material compatível | loja de aquário, Mercado Livre | R$ 15 | R$ 30 |
| Caixa organizadora 40–50 L | 2 | tampa, plástico lavável e sem trinca | loja de utilidades, Mercado Livre | R$ 40 | R$ 80 |
| Pote de vidro ~1 L | 6 | tampa íntegra e identificação individual | supermercado, loja de utilidades | R$ 10 | R$ 60 |
| Estante aramada | 1 | quatro prateleiras e capacidade declarada adequada | loja local, Mercado Livre, OLX | R$ 150 | R$ 150 |
| Fundo de madeira selada | 1 | 6–10 mm, todas as faces protegidas | marcenaria, loja de material | R$ 30 | R$ 30 |
| Tubo peristáltico sobressalente | 1 kit | diâmetro da bomba e material compatível | loja técnica, Mercado Livre | R$ 35 | R$ 35 |
| Tubos e conexões de água | 1 kit | abraçadeiras, registros e dreno sem estrangulamento | loja de aquário/irrigação | R$ 70 | R$ 70 |
| Fios, terminais e etiquetas | 1 kit | bitola pela corrente e crimpagem firme | loja elétrica/automotiva | R$ 35 | R$ 35 |
| Caixa plástica de projeto | 1 | isolante, fechada e com alívio de tração | Mercado Livre, loja elétrica | R$ 25 | R$ 25 |
| Botão de parada local | 1 | contato NF em baixa tensão | Mercado Livre, loja elétrica | R$ 15 | R$ 15 |
| Copo/proveta graduada | 1 | 500 mL ou maior, uso exclusivo | loja de utilidades/laboratório | R$ 20 | R$ 20 |
| Bandeja de contenção | 1 | base maior que os reservatórios | loja de utilidades/construção | R$ 40 | R$ 40 |
| Soluções de calibração | 1 kit | pH 4/7 e padrão EC adequado, dentro da validade | loja de aquário/laboratório | R$ 40 | R$ 40 |
| **Total estimado** |  |  |  |  | **R$ 1.620** |

## Checklist de compra

- [ ] 1 × ESP32 DevKit genérico — Mercado Livre/AliExpress/loja de robótica — R$ 55
- [ ] 1 × módulo relé 8 canais 5 V, optoacoplado e compatível com 3,3 V — R$ 40
- [ ] 2 × módulos MOSFET de 4 canais, entrada lógica de 3,3 V — R$ 50
- [ ] 1 × kit de placa perfurada, bornes e conectores — R$ 30
- [ ] 1 × fonte 12 V / 15 A — R$ 90
- [ ] 1 × conversor buck 12→5 V / 3 A — R$ 15
- [ ] 8 × porta-fusíveis/fusíveis para ramais DC — R$ 20
- [ ] 6 × bombas peristálticas 12 V — R$ 330
- [ ] 3 × bombas de água 12 V — R$ 75
- [ ] 1 × kit analógico de pH com sonda BNC — R$ 110
- [ ] 1 × kit analógico de EC para solução nutritiva — R$ 120
- [ ] 1 × DHT22/AM2302 — R$ 35
- [ ] 2 × sensores de vazamento — R$ 20
- [ ] 2 × boias de nível — R$ 30
- [ ] 2 × caixas organizadoras de 40–50 L — R$ 80
- [ ] 6 × potes de vidro de aproximadamente 1 L — R$ 60
- [ ] 1 × estante aramada de quatro prateleiras — R$ 150
- [ ] 1 × fundo de madeira selada — R$ 30
- [ ] 1 × kit de tubo peristáltico sobressalente — R$ 35
- [ ] 1 × kit de tubos, conexões e abraçadeiras — R$ 70
- [ ] 1 × kit de fios, terminais, termo-retrátil e etiquetas — R$ 35
- [ ] 1 × caixa plástica para a eletrônica — R$ 25
- [ ] 1 × botão de parada local em baixa tensão — R$ 15
- [ ] 1 × copo ou proveta graduada — R$ 20
- [ ] 1 × bandeja de contenção — R$ 40
- [ ] 1 × kit de soluções de calibração de pH/EC — R$ 40
- [ ] **Conferir o total planejado: R$ 1.620**

## O que conferir antes de pagar

1. O relé aceita sinal de 3,3 V sem forçar corrente no ESP32?
2. O módulo é ativo em nível baixo, como espera o firmware?
3. A corrente de partida de cada bomba cabe no MOSFET/relé e na fonte?
4. A saída analógica de pH e EC nunca ultrapassa 3,3 V?
5. O sensor vendido mede EC de líquido, e não umidade/EC de solo?
6. As bombas peristálticas permitem trocar o tubo?
7. O material do tubo e da boia é compatível com o produto utilizado?
8. A estante suporta a massa dos dois recipientes cheios com margem?
9. As caixas cabem na bandeja e podem ser retiradas para limpeza?
10. As soluções de calibração têm lote, valor nominal e validade legíveis?

## Critério de substituição

É permitido trocar marca ou fornecedor quando a alternativa preservar tensão,
função, pinagem, faixa de medição, compatibilidade química e corrente. Atualize
a BOM e o `io-map.csv` se a pinagem mudar. Não trate “parecido” como compatível.

## Agitação dos concentrados

A configuração-base não compra seis agitadores. Antes de iniciar uma receita:

1. retire cada pote da prateleira;
2. confira tampa, rótulo e linha correspondente;
3. agite manualmente conforme as instruções do fabricante do produto;
4. devolva o pote e confirme que o tubo de sucção permaneceu submerso;
5. só então libere a receita no painel.

Um agitador genérico pode ser adicionado no futuro como acessório opcional, mas
não deve consumir um canal sem atualizar BOM, mapa de atuadores e testes.

## Limites desta BOM

O valor é um orçamento de planejamento, não uma cotação garantida. Sensores
analógicos econômicos podem derivar, sofrer ruído das bombas e exigir
recalibração. A primeira montagem deve permanecer supervisionada até demonstrar
repetibilidade, ausência de vazamento e estado seguro após falhas.
