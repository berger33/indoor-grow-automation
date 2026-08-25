# Base elétrica Rev A — controle, hidráulica e clima em 127 V/60 Hz

> **Estado:** projeto preliminar para revisão por profissional habilitado. Não é
> autorização de compra, montagem ou energização.

## 1. Dados incorporados

| Parâmetro | Valor | Estado |
|---|---:|---|
| Alimentação do local | 127 V, fase-neutro-terra | confirmado pelo responsável |
| Frequência de projeto | 60 Hz | padrão brasileiro; medir no comissionamento |
| Água de origem | reservatório de 50 L | confirmado |
| Solução preparada | reservatório de 50 L | confirmado |
| Concentrados | 6 recipientes de 1 L | confirmado |
| Exaustor atual | motor CA de quatro fios, 110/220 V por religação | inferido da imagem |
| Controle do exaustor atual | liga/desliga | obrigatório até obter plaqueta/manual |
| Iluminação | inexistente neste quadro/projeto | decisão ADR 0006 |

Não será instalado seletor 127/220 V. O quadro terá uma variante física fixa em
127 V. Essa decisão elimina o risco de posição incorreta e simplifica proteção,
identificação e manutenção.

## 2. Fronteira de energia

A PCB recebe somente 24 VCC, 5 VCC e 3,3 VCC. Nenhuma fase ou neutro entra na
placa. As cargas preferenciais são:

- bombas peristálticas e válvulas em 24 VCC;
- bombas hidráulicas em 24 VCC quando a curva selecionada permitir;
- bobinas de contatores em 24 VCC;
- ESP32 em 5 VCC/3,3 VCC;
- exaustor e umidificador em 127 V, comutados externamente.

Se uma bomba adequada existir apenas em 127 V, ela receberá ramal, proteção e
contator próprios no quadro; isso exige revisão do unifilar e da potência antes
da compra.

## 3. Cargas que ainda impedem o dimensionamento final

| Carga | Dado obrigatório | Motivo |
|---|---|---|
| Exaustor atual/futuro | tensão, corrente, potência e corrente de partida | selecionar proteção e contator |
| Umidificador | modelo, potência e corrente de partida | selecionar proteção, contator e anti-ciclo |
| Bombas hidráulicas | tensão, corrente de trabalho/stall e regime | dimensionar fonte, fusível e driver |
| Dosadoras | corrente nominal/stall de cada lote | validar limite por canal e simultaneidade |
| Raspberry Pi | modelo e fonte escolhida | incluir consumo, proteção e autonomia |

O cálculo de corrente só será fechado com valores de plaqueta ou medição. Para
cada carga CA:

```text
I_estimada = P / (127 × FP)
```

Essa expressão é apenas planejamento quando o fator de potência não foi medido.
Corrente medida prevalece sobre plaqueta; plaqueta prevalece sobre estimativa.
Corrente de partida é tratada separadamente.

## 4. Arquitetura preliminar do quadro

| Identificador | Função | Especificação preliminar |
|---|---|---|
| Q0 | seccionamento geral | 2 polos, bloqueável; corrente após memorial final |
| DPS1 | surtos | Tipo 2; `Uc` e arranjo após identificar TT/TN-S |
| IDR1 | fuga à terra | tipo A, 2 polos, 30 mA; corrente coordenada com Q0 |
| QF-F1 | exaustão | curva/corrente após plaqueta do motor |
| QF-H1 | umidificação | curva/corrente após modelo aprovado |
| QF-C1 | fontes de controle | após somar fontes e inrush |
| K-F1 | exaustor atual | contator 24 VCC, somente liga/desliga |
| K-H1 | umidificador | contator 24 VCC, se o modelo não fornecer enable isolado |
| PSU-C | atuação SELV | fonte 24 VCC dimensionada após medir cargas |
| DC-L | lógica | conversor 24→5 V isolado ou fonte certificada equivalente |
| E-STOP | parada local | contatos NF removem alimentação de atuação 24 VCC |

Não há disjuntor, contator, tomada ou borne reservado para luminárias.

## 5. Requisitos de execução

1. circuito dedicado e memorial de cálculo conforme distância, queda de tensão,
   temperatura, agrupamento, capacidade de interrupção e aterramento locais;
2. gabinete de grau IP adequado, placa de montagem e reserva mínima de 30%;
3. canaletas CA e SELV separadas, cruzando a 90° apenas quando inevitável;
4. barramento PE dedicado e massas metálicas equipotencializadas;
5. fase, neutro e terra identificados; neutro nunca usado como PE;
6. fusível por ramal 24 VCC e proteção individual de cada carga CA;
7. prensa-cabos, alívio de tração, terminais tubulares e etiquetas permanentes;
8. quadro acima e lateralmente afastado dos tanques, sem tubulação sobre ele;
9. laço de gotejamento antes de todo cabo que entra no quadro;
10. E-stop físico e proteção contra sobrecorrente independentes de firmware.

DR, DPS, aterramento, disjuntor, seccionamento e isolamento cumprem funções
diferentes e nenhum substitui os demais. A execução de rede deve observar NBR
5410, NR-10 e requisitos da concessionária por profissional habilitado.

## 6. Exaustor atual e futuro

A imagem recebida mostra combinações distintas dos quatro fios para 110 e 220 V.
Isso evidencia religação de enrolamentos, não uma interface PWM/0–10 V nem
“bivolt automático” comprovado.

Para o exaustor atual:

- ligação física fixa em 127 V, executada e isolada por profissional;
- comando somente liga/desliga por contator;
- proteção selecionada pela plaqueta;
- sem dimmer, SSR por corte de fase, PWM ou inversor improvisado;
- tempo mínimo ligado/desligado e feedback por contato auxiliar ou corrente.

Para substituição, é preferível ventilador EC com entrada 0–10 V documentada e
habilitação separada. A interface analógica só poderá ser populada depois de
confirmar manual, referência elétrica e comportamento de falha do modelo.

## 7. Gate de liberação

O quadro permanece `HOLD` até existirem:

- lista final de cargas com plaquetas e correntes de partida;
- distância e método de instalação do circuito;
- esquema de aterramento verificado;
- memorial de cálculo e unifilar revisados por profissional habilitado;
- teste de DR, continuidade do PE, polaridade e isolação;
- ensaio térmico e teste de falhas com cargas simuladas;
- piloto hidráulico somente com água.

## 8. Referências

- [NR-10 — Ministério do Trabalho e Emprego](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/norma-regulamentadora-no-10-nr-10)
- [Fonte Mean Well HDR-60 — especificação oficial](https://www.meanwell.com/Upload/PDF/HDR-60/HDR-60-SPEC.PDF)
- [WEG RDWH tipo A — catálogo oficial](https://www.weg.net/catalog/weg/BR/pt/c/BR_WDC_CIRCUITBREAKER_RDWH/list)
- [ESP32-DevKitC V4 — documentação Espressif](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html)
