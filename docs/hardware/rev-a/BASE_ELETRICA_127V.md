# Base elétrica Rev A — instalação 127 V/60 Hz

> **Estado:** projeto preliminar para revisão por profissional habilitado. Não é
> autorização de compra, montagem ou energização.

## 1. Dados confirmados

| Parâmetro | Valor incorporado | Estado |
|---|---:|---|
| Alimentação do local | 127 V, fase-neutro-terra | Confirmado pelo responsável |
| Frequência de projeto | 60 Hz | Padrão brasileiro; medir antes de comissionar |
| Área iluminada padrão | 0,80 × 0,80 m | Confirmado |
| Painéis | Yuxinou: 120 + 120 + 85 + 65 W | Confirmado, total 390 W |
| Água de origem | reservatório de 50 L | Confirmado |
| Solução preparada | reservatório de 50 L | Confirmado |
| Concentrados | 6 × 1 L | Confirmado |
| Exaustor atual | motor CA de quatro fios, 110/220 V por religação | Inferido da imagem |
| Controle do exaustor atual | liga/desliga | Obrigatório até obter plaqueta/manual |

O Brasil opera em 60 Hz. Fontes oficiais consultadas e documentos de instalações
públicas usam 127/220 V a 60 Hz. A tensão real, polaridade, terra e frequência
devem ser medidas no ponto de uso; a documentação não substitui essa inspeção.

## 2. Cálculo do conjunto de iluminação

Potência ativa informada:

```text
P = 2 × 120 W + 85 W + 65 W = 390 W
```

Sem corrente e fator de potência das plaquetas, a corrente exata é desconhecida.
Somente para planejamento, se o fator de potência for explicitamente assumido
como 0,90:

```text
I127 = 390 / (127 × 0,90) = 3,41 A
I220 = 390 / (220 × 0,90) = 1,97 A
```

220 V reduz corrente e queda de tensão, mas não reduz automaticamente a energia
ativa consumida pelos mesmos drivers. Para 390 W, essa redução não compensa o
risco de um seletor de tensão. O projeto físico permanece fixo em 127 V.

O software deve guardar cada painel como carga independente e aceitar:

- potência nominal;
- tensão nominal;
- corrente de plaqueta ou corrente medida;
- fator de potência, quando documentado;
- corrente de partida/inrush;
- tipo de dimerização;
- grupo elétrico, estado comandado e feedback real.

Corrente medida prevalece sobre plaqueta; plaqueta prevalece sobre estimativa.
O sistema nunca deve escolher cabo, disjuntor ou contator apenas pelo valor
estimado.

## 3. Arquitetura recomendada do quadro

Entrada preliminar: circuito dedicado 127 V, 20 A, cobre 2,5 mm². Esses valores
são ponto de partida, não dimensionamento final: distância, queda de tensão,
temperatura, agrupamento, método de instalação, capacidade de interrupção e
aterramento podem exigir outra seção ou proteção.

| Identificador | Função | Especificação preliminar |
|---|---|---|
| Q0 | seccionamento geral | 2 polos, 25 A ou superior, bloqueável |
| DPS1 | surtos | Tipo 2; `Uc` e arranjo definidos após identificar TT/TN-S |
| IDR1 | fuga à terra | tipo A, 2 polos, 25 A ou superior, 30 mA |
| QF-L1 | iluminação | curva e corrente definidas após medir inrush; referência C10 A |
| QF-F1 | exaustão | definido pela plaqueta do motor; referência C6 A |
| QF-C1 | fontes de controle | referência C2 A |
| K-L1…K-L4 | quatro painéis | contatores 24 VCC independentes; categoria/inrush a validar |
| K-F1 | exaustor atual | contator 24 VCC independente, somente liga/desliga |
| PSU-C | controle SELV | Mean Well HDR-60-24, 24 VCC/2,5 A/60 W ou equivalente |
| E-STOP | parada local | cogumelo com contatos NF, cortando energia de atuação 24 VCC |

Requisitos de execução:

1. gabinete metálico ou policarbonato com grau IP adequado e placa de montagem;
2. canaletas CA e SELV separadas, cruzamentos a 90° quando inevitáveis;
3. barramento PE dedicado e todas as massas metálicas equipotencializadas;
4. bornes identificados para fase, neutro e terra; neutro nunca usado como PE;
5. prensa-cabos, alívio de tração, terminais tubulares e etiquetas permanentes;
6. proteção individual por ramal e fusível por canal 24 VCC;
7. nenhum condutor de rede na PCB controladora;
8. quadro acima dos reservatórios, fora de trajetos de vazamento e com laço de
   gotejamento nos cabos.

DR e DPS não substituem aterramento, disjuntor, seccionamento ou isolamento. A
NR-10 exige controle dos riscos e medidas preventivas; a execução deve observar
a NBR 5410 e as regras da concessionária local.

## 4. Exaustor atual e futuro

A imagem fornecida descreve combinações de fios diferentes para 110 e 220 V.
Isso caracteriza religação de enrolamentos, não “bivolt automático” comprovado.
Também não há terceiro fio de comando, entrada analógica ou protocolo.

Para o exaustor atual:

- configuração física única em 127 V, feita e isolada por profissional;
- comando liga/desliga por contator;
- proteção conforme corrente de placa;
- sem PWM, dimmer, SSR aleatório ou inversor de frequência;
- partida mínima, anti-ciclo e feedback por contato auxiliar/corrente.

Para a substituição, preferir ventilador **EC** com entrada 0–10 V documentada,
entrada de habilitação separada e alimentação compatível. A placa Rev A reserva
uma interface isolada 0–10 V opcional, mas ela não será populada/ativada sem o
manual do equipamento escolhido.

## 5. Luminárias e dimerização

As quatro saídas liga/desliga são independentes. Isso permite trocar potências,
desativar um painel e calcular cada ramal sem refazer a PCB. A dimerização não é
universal: drivers podem usar 0–10 V, PWM, resistência externa ou potenciômetro
isolado. O usuário selecionará a interface somente entre opções compatíveis com
o modelo cadastrado; `unknown` mantém apenas liga/desliga.

Até receber fotos das plaquetas/terminais dos drivers Yuxinou, o projeto não
define ligação de dimerização e não calcula inrush de contatores.

## 6. Referências verificadas em 2026-08-22

- [NR-10 — Ministério do Trabalho e Emprego](https://www.gov.br/trabalho-e-emprego/pt-br/acesso-a-informacao/participacao-social/conselhos-e-orgaos-colegiados/comissao-tripartite-partitaria-permanente/normas-regulamentadora/normas-regulamentadoras-vigentes/norma-regulamentadora-no-10-nr-10)
- [Fonte Mean Well HDR-60 — especificação oficial](https://www.meanwell.com/Upload/PDF/HDR-60/HDR-60-SPEC.PDF)
- [WEG RDWH tipo A — catálogo oficial](https://www.weg.net/catalog/weg/BR/pt/c/BR_WDC_CIRCUITBREAKER_RDWH/list)
- [WEG CWC07 24 VCC — catálogo oficial](https://www.weg.net/catalog/weg/BR/pt/Automa%C3%A7%C3%A3o-e-Controle-Industrial/Controls/Partida-e-Prote%C3%A7%C3%A3o-de-Motores/Contatores/Pot%C3%AAncia/Minicontatores-CWC0-e-CW0/Minicontatores-CWC0/MINICONTATOR-AZ-CWC07-10-30C03-7A-24V-DC/p/12486689)
- [ESP32-DevKitC V4 — documentação Espressif](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html)
