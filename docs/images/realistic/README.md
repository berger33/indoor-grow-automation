# Vistas realistas e técnicas conceituais

Estas imagens foram geradas em PNG e validadas byte a byte em 2026-08-23. O
portão de qualidade rejeita assinatura, CRC, dados comprimidos ou dimensões
inválidas e também proíbe novas referências a WebP nesta pasta.

As três vistas principais receberam uma faixa inferior renderizada de forma
determinística. Ela fixa os nomes `pH Down`, `CalMag`, `Micro`, `Bloom`,
`Veg (Grow)` e `pH Up`, as quantidades do banco de agitação e a fronteira da
iluminação remota; essa faixa prevalece sobre qualquer microtexto ilustrativo.

| Arquivo | Uso | O que deve aparecer |
|---|---|---|
| `01_ESTACAO_COMPLETA_REALISTA.png` | fotografia conceitual do sistema pronto | seis frascos, seis agitadores, seis dosadoras, dois tanques de 50 L empilhados, manifold, tenda, exaustor e umidificador |
| `02_VISTA_TECNICA_CONJUNTO_ABERTO.png` | vista técnica frontal do conjunto | quadro aberto, dosagem/agitação, hidráulica e dois níveis de tanque independentes |
| `03_QUADRO_CONTROLE_ABERTO_REALISTA.png` | estimativa visual do quadro aberto | controladora ESP32, distribuição/fusíveis, conversores SELV, bornes, hub Raspberry Pi separado e rotas de cabos |
| `CLIMA_CONCEITUAL.png` | relação espacial do clima | exaustão, umidificação, sensores e contenção do cultivo |

## Leitura correta da vista do quadro

A imagem aberta representa classes de componentes, não modelos liberados nem um
layout de fabricação. O projeto próprio **não usa Arduino Mega**: o ESP32 local
assume o controle de campo e o Raspberry Pi executa MQTT, API, banco e painel em
compartimento ventilado separado. A organização pretendida é:

1. entrada e distribuição de 24 VCC protegidas;
2. conversor isolado 24→12 VCC para os seis agitadores;
3. conversor 24→5 VCC para lógica/hub conforme a revisão liberada;
4. controladora SELV com ESP32 removível e 16 saídas protegidas;
5. entradas digitais, analógicas, 1-Wire, fluxo, pH e EC;
6. bornes com ponteiras e uma função por condutor;
7. seis saídas de 12 V e seis retornos de tacômetro dos agitadores;
8. Raspberry Pi com armazenamento e Ethernet em caixa seca ventilada.

## O que é vinculante

As imagens servem para visualizar aparência, acesso e ocupação. Para comprar,
fabricar ou montar, prevalecem, nesta ordem:

1. BOM liberada e matriz de compatibilidade;
2. P&ID e unifilar as-built;
3. desenho mecânico cotado;
4. esquema, layout, pinagem e chicotes da revisão liberada;
5. tutorial e checklist de comissionamento.

## Limitações conhecidas

- tubulação e componentes visuais não substituem o P&ID;
- rótulos e microdetalhes gerados não definem tensão, MPN ou pinagem;
- formas dos tanques são ilustrativas até medir os recipientes adquiridos;
- nenhum desenho autoriza ligação em 127 V, compra em lote ou fabricação;
- nenhuma carga de iluminação integra o rack; somente tomadas EKAZA/Tuya são
  acessadas logicamente pelo hub, conforme ADR 0008.
- fotos reais substituirão estes conceitos depois do protótipo, HIL e piloto
  supervisionado somente com água.

As imagens serão substituídas/complementadas por fotografias da montagem
validada antes da release v1.0.

## Direção de geração

As três vistas novas usaram o modo integrado de geração/edição de imagens. Os
prompts fixaram rack máximo de 900 × 600 × 2.000 mm, seis canais de 1 L, seis
ventoinhas agitadoras de 80 mm, seis dosadoras, `TK-101` e `TK-201` de 50 L em
níveis independentes, segregação seco/molhado, Raspberry Pi, ESP32 e ausência
total de iluminação. Resultados com contagem ou tensão visual incorreta foram
descartados antes desta revisão.
