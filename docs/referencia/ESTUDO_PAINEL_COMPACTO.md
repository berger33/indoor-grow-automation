# Estudo dirigido do painel vertical compacto

## Fontes observadas

- vídeo V1 de hardware, duração 16:36, principalmente 00:00–00:47,
  03:44–05:00, 07:20–09:00 e 15:07–16:29;
- quadro aproximado do conjunto completo, fornecido em 2026-08-23;
- recorte aproximado do painel de dosagem, fornecido em 2026-08-23.

A resolução limita leitura de marcas, diâmetros e medidas. Este estudo registra
somente o que é visualmente defensável e separa observação de adaptação.

## Disposição confirmada

| Elemento observado | Posição relativa | Benefício espacial | Adaptação própria |
|---|---|---|---|
| rack tubular cromado | envelope externo único | usa a altura e mantém módulos no mesmo plano | rack ancorado com carga e estabilidade verificadas |
| painel branco com tablet | metade superior esquerda | comando e dosagem ficam acessíveis em pé | tela no gabinete seco, sem depender dela para segurança |
| cabeçotes peristálticos | sob a tela, matriz compacta | reduz comprimento dos tubos e área frontal | seis canais de concentrado; funções auxiliares vão ao painel hidráulico |
| seis frascos transparentes | duas prateleiras de três, à direita | inspeção visual e troca frontal | seis recipientes de 1 L com bandeja, retenção e identificação |
| seis ventoinhas de 80 mm | uma sob cada frasco | transforma a própria prateleira em banco compacto de agitação magnética | seis módulos protegidos, 12 VCC, dois ímãs balanceados, barra PTFE e tacômetro individual |
| prateleiras de madeira | apoios estreitos, empilhados | aproveita faixa vertical que ficaria vazia | material selado ou suporte lavável, com contenção individual |
| feixes de tubo | laterais, topo e frente | caminho visível facilita diagnóstico | rotas segregadas, clips, raio mínimo e laços de gotejamento |
| tote preto/tampa amarela | nível inferior do rack em tomadas distintas | ocupa praticamente toda a largura útil e sugere uso de níveis, não duplicação horizontal | dois tanques de 50 L empilhados em prateleiras estruturais independentes |
| painel de tomadas | lateral direita | acesso concentrado | não replicado na zona molhada; CA fica em quadro seco profissional |
| backboard de madeira | fundo do rack | oferece plano contínuo de fixação | compensado naval selado ou placa técnica lavável, afastada do piso |

## Contagem e ambiguidade dos cabeçotes

O recorte permite contar **sete cabeçotes aparentes** em distribuição 2–3–2,
enquanto o conjunto de frascos mostra **seis recipientes** em duas fileiras de
três. O vídeo não permite associar com segurança o sétimo cabeçote a uma função.
Não será inventado um sétimo nutriente.

O projeto próprio mantém seis peristálticas de concentrado. Transferência,
mistura, irrigação e dreno ficam no painel hidráulico e são identificados por
função. Uma saída elétrica permanece reserva e bloqueada no firmware.

## Agitação dos frascos

O trecho adicional e a lista oficial eliminam a ambiguidade sobre as peças:
seis Arctic F8 PWM, doze ímãs e seis barras magnéticas PTFE tipo C. O autor opera
as ventoinhas em velocidade total e usa relé para liga/desliga. A adaptação Rev A
preserva essa compactação, mas alimenta o banco por 12 VCC derivado da fonte de
24 VCC, protege os rotores e exige tacômetro individual antes de dosar. A revisão
com timestamps e HOLDs está em
[`REVISAO_AGITACAO_MAGNETICA.md`](REVISAO_AGITACAO_MAGNETICA.md).

## Regras dimensionais derivadas

As seguintes proporções são metas A0, não medidas do equipamento do vídeo:

- largura do painel seco/dosagem: aproximadamente 45% da largura útil;
- largura das duas prateleiras de frascos: aproximadamente 40%;
- corredor lateral para tubos e clips: mínimo 10%;
- tanques e contenção: `TK-101` sobre `TK-201`, em duas camadas estruturais
  independentes, ocupando a metade inferior do rack;
- equipamentos de manutenção frequente entre 750 e 1.650 mm do piso;
- `TK-201` permanece no nível mais baixo; `TK-101` só pode ficar acima quando
  a prateleira, o rack e a ancoragem forem verificados para carga cheia;
- nenhum tubo com líquido acima de entrada de cabo, ventilação ou porta do
  gabinete seco;
- frente livre suficiente para retirar cada tanque do próprio nível, sem
  levantar peso cheio e sem apoiar uma caixa sobre a tampa da outra.

## Melhorias obrigatórias sobre a referência

1. separar fisicamente CA, SELV e fluido;
2. esconder eletrônica em gabinete, preservando manutenção frontal;
3. adicionar contenção sob recipientes e tanques;
4. usar uniões e conectores travados, não protoboard/Dupont;
5. apoiar mangueiras sem transferir força às plataformas de pesagem;
6. criar raio de curvatura e alívio de tração para cada tubo;
7. impedir sifão e retorno cruzado com geometria e válvulas adequadas;
8. manter E-stop e corte físico acessíveis sem alcançar a zona molhada;
9. reservar folga térmica e de manutenção indicada em planta.
10. usar plataformas de pesagem independentes e desacopladas em cada nível;
11. conduzir vazamento do nível superior a uma contenção inferior dimensionada,
    sem permitir gotejamento sobre o tanque de mistura ou a eletrônica.

## Pontos não identificados

- dimensões e capacidade do rack original;
- se os dois totes originais ficam exatamente alinhados no mesmo prumo; a
  filmagem confirma as funções e o princípio vertical, mas não oferece uma
  elevação completa dos dois recipientes no mesmo quadro;
- função do sétimo cabeçote aparente;
- volume/material exato dos frascos e totes;
- tipo, diâmetro e compatibilidade química dos tubos;
- forma de retenção dos frascos durante vibração;
- proteção contra respingo do painel branco;
- carga admissível e ancoragem do rack;
- segregação interna da alimentação mostrada no lado direito.

Esses pontos permanecem `HOLD`; aparência não é evidência de especificação.
