# Revisão dirigida — agitação dos seis concentrados

## Fontes primárias

- trecho de 14,87 s anexado em 2026-08-23, extraído aproximadamente de
  01:46–02:01 do vídeo de atualização do autor;
- vídeo completo `Update on My Automated Garden System`, 05:56;
- [repositório original do autor](https://github.com/ledgardener/gardenAutomation);
- [lista de peças original](https://github.com/ledgardener/gardenAutomation/blob/master/parts_list_with_links.md).

O vídeo e o repositório são usados como evidência histórica. A solução própria
mantém o princípio, mas acrescenta proteção mecânica, feedback e intertravamento.

## Evidência quadro a quadro do trecho anexado

| Tempo do trecho | O que é defensável observar |
|---:|---|
| 00:00–00:02 | quadro original aberto à esquerda e seis frascos em duas fileiras de três à direita |
| 00:02–00:06 | cada frasco repousa sobre uma ventoinha axial quadrada em suporte próprio |
| 00:06–00:10 | o apresentador remove o frasco superior esquerdo sem desmontar os demais; o líquido mostra movimento de mistura |
| 00:10–00:14,87 | o tablet retorna à tela de controle; o detalhe não permite ler todos os estados |

A barra magnética e os ímãs do rotor não ficam legíveis no trecho. Esses itens
não foram inferidos pela aparência: são confirmados pela lista oficial.

## Componentes confirmados pelo autor

| Item original | Quantidade | Declaração publicada |
|---|---:|---|
| Arctic F8 PWM, 80 mm | 6 | ventoinhas dos agitadores; o autor informa que as opera em velocidade total |
| barra magnética PTFE tipo C | 6 | uma barra dentro de cada frasco |
| ímã para frasco | 12 | dois ímãs colados em cada rotor para movimentar a barra |
| placa de relés de oito canais | 1 | liga/desliga solenoides e agitadores magnéticos |

O MPN atual da referência visual é `AFACO-080P2-GBA01`, mas ele ainda depende
de amostra. Uma alternativa só será aceita se for 12 VCC, 80 × 80 × 25 mm,
possuir saída de tacômetro e passar no ensaio de rotação com o conjunto
ímã/barra/frasco realmente adquirido.

## Adaptação segura para este projeto

1. derivar 12 VCC da fonte SELV de 24 VCC por conversor protegido em trilho DIN;
2. usar seis ventoinhas, dois ímãs balanceados por rotor e seis barras PTFE;
3. operar o banco somente em liga/desliga e velocidade total na v1.0;
4. ler individualmente os seis sinais de tacômetro;
5. iniciar os agitadores antes da dosagem e aguardar tempo de pré-mistura;
6. inibir a receita se qualquer canal necessário não confirmar rotação;
7. manter o banco ativo durante toda a dosagem sequencial;
8. desligar o banco antes de liberar retirada de qualquer frasco;
9. usar guarda rígida entre rotor/ímãs e o fundo do frasco;
10. recalibrar a bomba somente com o mesmo frasco, tubo e condição de mistura.

Não será copiada a montagem com ímãs expostos e cola sem especificação. O suporte
final deve conter fragmentos em eventual descolamento e impedir contato manual
com o rotor.

## Pontos não identificados / HOLD

- dimensões, material, grau, massa, polaridade e adesivo dos dois ímãs;
- tamanho exato da barra PTFE tipo C;
- distância entre rotor, placa de guarda e fundo do frasco;
- rotação mínima que mantém cada concentrado homogêneo sem introduzir ar;
- temperatura da ventoinha e do líquido após operação prolongada;
- resistência química do frasco, tampa, tubo e barra para cada produto;
- corrente de partida e sinal de tacômetro da amostra adquirida;
- retenção do frasco contra vibração e derrubamento.

Esses parâmetros serão congelados somente após ensaio com água e, depois, com
amostra química compatível e SDS disponível. A imagem ou o anúncio não liberam
compra em lote.
