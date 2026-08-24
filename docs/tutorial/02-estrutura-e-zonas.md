# Etapa 02 — Estrutura compacta e zonas seca/molhada

> Estado: tutorial A0 para protótipo mecânico. Não compre o rack definitivo,
> não perfure parede e não instale eletricidade enquanto os itens `HOLD` não
> forem medidos e aprovados.

## Objetivo verificável

Ao terminar esta etapa, o rack vazio estará nivelado, estável e dividido em
zonas visíveis. Será possível simular `TK-101` sobre `TK-201`, em níveis
independentes, e retirar cada gabarito pela frente. Nenhuma bomba, eletrônica,
fluido ou cabo CA será instalado.

![Estado visual pretendido](../images/realistic/ESTACAO_COMPACTA_VERTICAL_CONCEITUAL.webp)

## Antes de começar

Confirme no registro da montagem:

- [ ] ambiente medido e fotografado;
- [ ] piso firme, seco e nivelável;
- [ ] parede/material de ancoragem identificados por profissional competente;
- [ ] dimensões externas, tampas e curso de retirada dos dois tanques medidos;
- [ ] seis frascos com tampas e conexões medidos;
- [ ] carga declarada do rack documentada pelo fabricante;
- [ ] cada prateleira de tanque documentada para pelo menos 100 kg e o rack
  documentado para pelo menos 250 kg distribuídos;
- [ ] faixa frontal de 900 mm disponível durante manutenção;
- [ ] desenho `REV-A-03` comparado com o ambiente;
- [ ] nenhum item de iluminação incluído.

Se qualquer caixa estiver vazia, registre a pendência e pare a montagem física.
É permitido montar um gabarito de papelão/fitas no piso para validar espaço.

## Documentos desta etapa

- [implantação compacta](../../desenhos/REV-A-03_IMPLANTACAO_COMPACTA.svg);
- [planta baixa do rack](../../desenhos/REV-A-04_PLANTA_BAIXA_RACK.svg);
- [elevação do painel](../../desenhos/REV-A-05_ELEVACAO_PAINEL_COMPACTO.svg);
- [rotas segregadas](../../desenhos/REV-A-08_INSTALACOES_ROTAS.svg);
- [caderno de pranchas](../hardware/rev-a/CADERNO_PRANCHAS.md).

## Peças e ferramentas

Use os identificadores da BOM, sem substituir por aparência:

| Identificador | Item | Situação A0 |
|---|---|---|
| `RACK1` | rack-alvo de até 900 × 600 × 2.000 mm | HOLD |
| `BP1` | backboard selado removível | provisional |
| `SH1–SH2` | duas prateleiras com retenção de três frascos | HOLD |
| `LV1–LV2` | duas prateleiras estruturais independentes, ≥ 100 kg cada | HOLD |
| `CT2` | bandeja sob `TK-101` com dois drenos gravitacionais | HOLD |
| `CT1` | contenção inferior com ≥ 110 L livres | HOLD |
| `AN1` | ancoragem antitombamento | HOLD |
| `CL1` | clips/canaletas segregados | provisional |

Ferramentas permitidas nesta etapa: trena, esquadro, nível, marcador removível,
torquímetro quando o fabricante do rack fornecer torque, gabaritos de papelão e
EPIs mecânicos. Furadeira e fixadores estruturais só entram após definição de
`AN1` pelo responsável competente.

## Montagem seca passo a passo

1. Marque no piso um retângulo de 900 × 600 mm e, à frente, a faixa livre de
   900 mm. Fotografe a marcação com a trena visível.
2. Marque a tenda de 800 × 800 mm e mantenha o afastamento lateral indicado na
   implantação. Abra a porta da tenda para confirmar que ela não colide.
3. Monte o rack vazio conforme o manual do fabricante, sem improvisar parafuso,
   cortar coluna ou remover travessa.
4. Ajuste os pés e confira nível nos sentidos frontal e lateral. Meta A0:
   desnível máximo de 2 mm por metro.
5. Confira diagonais do retângulo frontal. A diferença entre elas deve ser menor
   ou igual a 5 mm antes de instalar o backboard.
6. Posicione `CT1` no nível mais baixo e o gabarito de `TK-201` sobre a
   plataforma inferior. Não coloque o segundo gabarito ao lado.
7. Instale provisoriamente `LV1`, a prateleira de `TK-101`, sem usar a tampa ou
   as paredes de `TK-201` como apoio. Use espaçadores/gabaritos para conferir
   abertura da tampa, inspeção e extração frontal do nível inferior.
8. Posicione `CT2`, a plataforma superior e o gabarito de `TK-101`. Confira que
   nenhum pé, tubo ou fixador transmite carga à estrutura de `TK-201`.
9. Marque a coluna lateral do painel hidráulico. Garanta acesso frontal às
   uniões e mantenha livres os dois trajetos de `CT2` até `CT1`.
10. Apresente `BP1` sem fixação definitiva. A borda inferior deve ficar fora da
   contenção e não pode criar caminho de líquido para a zona seca.
11. Marque a zona seca no alto à esquerda e a zona de frascos à direita. Instale
   uma barreira visual temporária entre as rotas.
12. Posicione seis gabaritos de frasco, três em cada prateleira. Retire cada um
    individualmente para cima e para frente.
13. Marque, sem instalar cabos, as canaletas CA, SELV/dados e a lateral molhada.
    Qualquer cruzamento planejado deve ocorrer a 90°.
14. Peça ao responsável estrutural para definir ancoragem, substrato, fixadores
    e torque. Somente depois instale `AN1` e registre fotos antes/depois.
15. Aplique etiquetas temporárias `SECO`, `MOLHADO`, `CA`, `SELV`, `DADOS`,
    `TUBOS` e `DRENO` nas posições das pranchas.

## Inspeção e evidências

Registre estes resultados:

| Ensaio | Critério A0 | Evidência |
|---|---|---|
| largura/profundidade | dentro do envelope aprovado | foto com trena |
| nível | ≤ 2 mm/m em dois eixos | leitura fotografada |
| esquadro | diagonais diferem ≤ 5 mm | duas medidas |
| prateleira LV1 | certificado ≥ 100 kg e sem apoio em TK-201 | ficha/foto lateral |
| prateleira LV2 | certificado ≥ 100 kg e nivelada | ficha/foto lateral |
| extração TK-101 | sai do nível superior após drenagem | vídeo com gabarito vazio |
| extração TK-201 | sai do nível inferior após drenagem | vídeo com gabarito vazio |
| acesso C1–C6 | cada gabarito sai sozinho | checklist assinado |
| faixa frontal | ≥ 900 mm desobstruídos | foto e medida |
| ancoragem | especificação/torque aprovados | laudo ou registro responsável |

As tolerâncias são metas de montagem A0 e podem ficar mais restritivas na A1.

## Erros comuns

- montar frascos diretamente sobre o quadro seco;
- deixar mangueira futura cruzar a porta ou ventilação do gabinete;
- encostar tanque ou tubo na plataforma vizinha;
- apoiar `TK-101` na tampa, nas paredes ou na plataforma de `TK-201`;
- instalar a prateleira superior sem ancorar o rack para a condição cheia;
- bloquear um dos dois trajetos de vazamento entre `CT2` e `CT1`;
- reduzir corredor frontal porque “a tampa ainda abre”;
- usar madeira crua sem selagem e bordas protegidas;
- prender rack pesado apenas em acabamento oco sem cálculo;
- colocar régua de tomadas na lateral molhada como no protótipo de referência.

## Como retornar ao estado seguro

Como não há energia nem fluido nesta etapa, interrompa o trabalho, remova
gabaritos e desmonte somente na ordem indicada pelo fabricante. Não corrija
instabilidade com peso nos tanques ou calços soltos. Registre a não conformidade
e devolva o item correspondente a `HOLD`.

## Liberação da próxima etapa

A etapa 03 só começa após todos os ensaios acima passarem e as dimensões reais
de `TK-101`, `TK-201`, `CT1`, `CT2`, `LV1`, `LV2`, `PL1` e `PL2` entrarem na
revisão do desenho.
