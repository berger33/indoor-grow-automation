# Vistas realistas conceituais

Estas imagens ajudam a visualizar o sistema montado. Elas foram geradas a partir
do escopo de engenharia em 2026-08-23; não retratam um protótipo já fabricado.

| Arquivo | Intenção visual |
|---|---|
| `ESTACAO_COMPACTA_VERTICAL_CONCEITUAL.webp` | vista principal corrigida: seis canais e dois tanques de 50 L empilhados em níveis independentes |
| `CLIMA_CONCEITUAL.webp` | exaustor, umidificador, sensores na copa, bandeja e dreno |

## O que é vinculante

Use estas imagens somente para compreender organização, acesso e aparência
geral. Para comprar ou montar, prevalecem nesta ordem:

1. BOM liberada e matriz de compatibilidade;
2. P&ID e unifilar as-built;
3. desenho mecânico cotado;
4. esquema, layout, pinagem e chicotes da revisão liberada;
5. tutorial e checklist de comissionamento.

## Limitações conhecidas

- formas e dimensões dos tanques são ilustrativas até medir os recipientes reais;
- a imagem mostra `TK-101` sobre `TK-201`, mas cada caixa usa prateleira e
  plataforma próprias; não existe apoio sobre a tampa do tanque inferior;
- conexões, válvulas e linhas visuais não constituem o P&ID;
- suportes de frascos/agitadores serão detalhados em desenho mecânico;
- gabinete fechado não mostra a segregação interna CA/SELV;
- sensores aparecem em posições representativas, que serão cotadas no as-built;
- nenhuma imagem autoriza ligação elétrica, escolha de proteção ou fabricação;
- iluminação foi deliberadamente omitida e não integra o sistema.

As imagens serão substituídas/complementadas por fotografias da montagem
validada antes da release v1.0.

## Direção usada na geração

- vista geral: estação compacta, exatamente seis frascos de 1 L e seis
  peristálticas, duas caixas de 50 L empilhadas, quadro seco elevado, painel
  hidráulico lateral, exaustão e umidificação;
- vista de clima: tenda 80 × 80 cm, exaustor, umidificador externo, sensores de
  temperatura/UR/CO₂/folha, bandeja, dreno e detecção de vazamento;
- em todas: sem luminárias, drivers, dimmers ou controles de iluminação; sem
  marcas, texto miúdo, rede exposta ou água sobre o quadro.

### Revisão compacta vertical

A revisão compacta foi gerada por edição da vista anterior e refinada com os
quadros do painel original como referência de disposição. O envelope A0 passou
a no máximo 900 × 600 × 2.000 mm. O painel seco/HMI e as seis peristálticas
ficam no alto à esquerda; os seis recipientes em duas fileiras de três ficam à
direita; `TK-101` e `TK-201` ocupam níveis sobrepostos e independentes; o
manifold usa uma faixa lateral molhada. A imagem preserva tenda, exaustão e
umidificação e omite integralmente iluminação.

Vistas incompatíveis com o contrato empilhado foram removidas da revisão
corrente. Versões anteriores continuam recuperáveis apenas pelo histórico Git.

Essa disposição é a direção A0 do projeto; cotas e componentes continuam
dependentes da medição física e dos desenhos vinculantes.
