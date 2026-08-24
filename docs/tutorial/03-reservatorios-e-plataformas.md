# Etapa 03 — Reservatórios empilhados e plataformas de pesagem

> Estado: `A0/HOLD`. Este capítulo prepara gabaritos e uma montagem mecânica sem
> líquidos. Não compre o rack definitivo, não encha os tanques e não coloque uma
> pessoa sob `TK-101` enquanto carga, prateleiras, ancoragem e contenção não
> tiverem laudo e ensaio.

## Resultado desta etapa

Ao final, o conjunto deverá ter esta ordem, de cima para baixo:

1. `TK-101`: água de origem, 50 L, sobre `PL1` e `LV1`;
2. `CT2`: bandeja estanque sob o nível superior, com dois drenos independentes;
3. espaço frontal/lateral para tampa, tubos e manutenção;
4. `TK-201`: mistura/rega, 50 L, sobre `PL2` e `LV2`;
5. `CT1`: bacia inferior com pelo menos 110 L de volume livre demonstrado.

Os dois tanques ficam no mesmo prumo. Eles **não** ficam lado a lado e nenhuma
parte de `TK-101`, `PL1` ou `LV1` pode apoiar em `TK-201` ou em sua tampa.

![Elevação dos dois níveis](../../desenhos/REV-A-05_ELEVACAO_PAINEL_COMPACTO.svg)

## Registros obrigatórios antes de fabricar

Crie uma ficha para cada tanque e preencha sem arredondar:

| Medida | TK-101 | TK-201 | Como medir |
|---|---:|---:|---|
| largura máxima do corpo |  |  | trena no ponto mais largo |
| profundidade máxima do corpo |  |  | incluir alças e passa-muros |
| altura com tampa fechada |  |  | piso de apoio até topo |
| altura necessária para remover a tampa |  |  | medir o curso real |
| massa vazio, sem acessórios |  |  | balança conferida |
| massa de bombas/sondas/tubos apoiados |  |  | pesar conjunto seco |
| posição dos passa-muros |  |  | cotar a partir de duas faces |
| material e marcação do plástico |  |  | fotografar símbolo e etiqueta |

Pare se qualquer tanque ultrapassar o envelope A0 de 700 × 450 mm. Não compre
uma caixa apenas porque o anúncio diz “50 litros”: confirme dimensão externa,
material, tampa, rigidez e possibilidade de reposição.

## Caminho de carga — explicação simples

O peso precisa seguir este caminho:

```text
água → tanque → plataforma PL → quatro células → prateleira LV → rack
     → pés/piso + ancoragem antitombamento
```

Mangueira, eletroduto, bandeja, tanque vizinho e painel não podem criar um
segundo caminho. Se uma mangueira rígida levantar ou puxar a plataforma, a
leitura de massa ficará errada mesmo que o sensor eletrônico esteja calibrado.

## Montagem seca por ordem

1. Confirme que a Etapa 02 foi aprovada e que o rack está vazio, nivelado e
   ancorado conforme o responsável estrutural.
2. Instale `CT1` na base. Meça o volume geométrico e desconte tudo que ocupará
   espaço interno. O resultado deve ser tratado como cálculo provisório, não
   como capacidade aprovada.
3. Instale `LV2` conforme o manual do rack. Registre modelo, posição, fixadores
   e carga nominal mínima de 100 kg.
4. Apoie um gabarito rígido de `PL2` e quatro simuladores de célula. Use pontos
   de apoio simétricos e batentes de sobrecarga que não encostem em condição
   normal.
5. Coloque o gabarito vazio de `TK-201`. Abra e remova a tampa; depois retire o
   tanque pela frente. Nenhum movimento pode exigir soltar `LV1`.
6. Marque a folga de serviço acima de `TK-201`. Inclua tampa, sondas, bomba,
   passa-muros e raio mínimo das mangueiras.
7. Instale `LV1` sem tocar em `TK-201`. Registre a carga nominal mínima de
   100 kg e a distância até as colunas do rack.
8. Posicione `CT2` e confirme inclinação positiva até duas saídas separadas. Um
   dreno não pode depender do outro nem passar sobre o quadro seco.
9. Apoie o gabarito de `PL1` e quatro simuladores de célula. Verifique que os
   drenos de `CT2` não empurram a plataforma.
10. Coloque o gabarito vazio de `TK-101`. Abra a tampa, retire-o pela frente e
    confira que a operação não exige apoiar peso em `TK-201`.
11. Passe duas mangueiras transparentes provisórias de `CT2` até `CT1`, com
    queda contínua, fixação visível e acesso para limpeza.
12. Etiquete `TK-101/PL1/LV1/CT2` e `TK-201/PL2/LV2/CT1` nas duas laterais.

Nesta etapa, “gabarito” significa peça sem líquido e sem função hidráulica. Não
use sacos, baldes ou pessoas como peso improvisado.

## Ensaios que bloqueiam o enchimento

| Ensaio | Critério mínimo | Evidência |
|---|---|---|
| rack | capacidade ≥ 250 kg distribuídos | documento do fabricante |
| LV1 | capacidade ≥ 100 kg e flecha aceita pelo projeto | laudo/ensaio |
| LV2 | capacidade ≥ 100 kg e flecha aceita pelo projeto | laudo/ensaio |
| desacoplamento PL1 | pressão leve em TK-201 não muda leitura de PL1 | registro de bancada |
| desacoplamento PL2 | pressão leve em TK-101 não muda leitura de PL2 | registro de bancada |
| extração | cada gabarito vazio sai pelo próprio nível | vídeo frontal |
| tampa | curso completo sem colisão | foto com medida |
| CT2 dreno A | escoa a vazão de ensaio com B bloqueado | vídeo/volume/tempo |
| CT2 dreno B | escoa a vazão de ensaio com A bloqueado | vídeo/volume/tempo |
| CT1 | volume livre medido ≥ 110 L | relatório de enchimento graduado |
| tombamento | aprovado com TK-101 na condição cheia de projeto | laudo estrutural |

O ensaio de água de `CT1/CT2` só ocorre depois de rack, ancoragem e materiais
serem aprovados. Faça-o sem eletrônica instalada e com caminho de esvaziamento
definido. Água limpa é o único fluido permitido no comissionamento mecânico.

## Erros que exigem desmontagem

- apoiar a prateleira superior na tampa do tanque inferior;
- usar uma única plataforma para pesar os dois tanques;
- instalar células de carga sobre arame, madeira flexível ou superfície torta;
- perfurar o tanque antes de congelar posição de plataforma e contenção;
- contar o volume nominal de `CT1` sem descontar obstáculos;
- unir os dois drenos de `CT2` antes do ponto em que uma obstrução possa ser
  detectada e limpa;
- prender mangueira curta ou rígida diretamente à tampa sobre a balança;
- planejar remoção de tanque cheio por uma pessoa;
- adicionar qualquer componente de iluminação ao rack.

## Estado seguro ao interromper

Remova todos os gabaritos, deixe as plataformas sem carga, identifique a
pendência e impeça enchimento por etiqueta física. Não tente corrigir instabilidade
com água, contrapeso, calço solto ou amarração improvisada.

## Liberação da Etapa 04

A hidráulica só poderá ser roteada quando as cotas as-built de `TK-101`,
`TK-201`, `PL1`, `PL2`, `LV1`, `LV2`, `CT1` e `CT2` estiverem incorporadas às
folhas 04–06, e os ensaios estruturais e de contenção acima tiverem aprovação.
