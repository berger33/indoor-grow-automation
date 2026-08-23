# Arquitetura física-alvo da estação

Este documento fixa a organização funcional derivada do vídeo V1 e adaptada aos
volumes informados. Dimensões cotadas só serão congeladas depois da medição dos
tanques e do local.

![Visualização realista conceitual da estação compacta](../../images/realistic/ESTACAO_COMPACTA_VERTICAL_CONCEITUAL.webp)

O ADR 0007 substitui a disposição excessivamente espalhada da primeira vista
por um rack vertical inspirado no princípio espacial observado no vídeo. O
[`estudo dirigido do painel`](../../referencia/ESTUDO_PAINEL_COMPACTO.md) separa
evidências visuais de adaptações de segurança.

## 1. Zonas físicas

| Zona | Conteúdo | Regra de posicionamento |
|---|---|---|
| A — quadro seco | proteções CA, fontes, controladora, bornes, HMI e E-stop | alto à esquerda, fechado e lateralmente afastado dos frascos |
| B — dosagem | seis frascos de 1 L, seis agitadores e seis peristálticas | duas fileiras de três à direita, com bombas no painel seco adjacente |
| C — água | reservatório de origem de 50 L, plataforma e boias | base rígida, nivelada, dentro de contenção |
| D — mistura | reservatório de mistura/rega de 50 L, plataforma, sondas e bomba | base rígida, tampa acessível e sem apoiar tubos na balança |
| E — hidráulica | bombas, válvulas, manifold, uniões e dreno | travessa central removível, abaixo de dosagem e acima dos tanques |
| F — cultivo | emissores, bandeja de coleta, dreno e sensores climáticos | nenhum equipamento de rede exposto à névoa/rega |
| G — hub | Raspberry Pi, rede e armazenamento | caixa seca, ventilada e acessível para backup |

Mangueiras nunca passam sobre as zonas A ou G. Cabos que sobem de uma zona
molhada formam laço de gotejamento antes do prensa-cabo.

## 1.1 Envelope compacto A0

| Parâmetro | Meta A0 | Estado |
|---|---:|---|
| rack | 1.200 × 600 × 2.000 mm | provisional; confirmar modelo/carga |
| área de piso do rack | 0,72 m² | calculada pelo envelope |
| faixa frontal de manutenção | mínimo 900 mm | conferir no ambiente |
| tanque individual | máximo provisório 500 × 400 mm | HOLD por medição |
| contenção inferior | mínimo 110 L úteis | HOLD por seleção/ensaio |
| carga de projeto do rack | superior a 150 kg | HOLD por cálculo e fabricante |

O rack não poderá ser comprado antes de conferir carga, dimensões dos tanques,
ancoragem e risco de tombamento. O painel de fundo deve ser selado e removível;
madeira crua não é superfície final aprovada.

## 2. Capacidade de atuação

O vídeo usa seis dosadoras, quatro bombas hidráulicas, duas válvulas, agitação,
exaustão e umidificação. Isso exige **15 funções comandadas**, portanto a antiga
premissa de oito saídas não atende ao sistema inteiro.

A controladora A0 será revisada para 16 saídas com habilitação segura única. O
mapa vinculante está em
[`hardware/system/actuator-map.csv`](../../../hardware/system/actuator-map.csv).
Cargas acima de 1 A ou com corrente de partida desconhecida usam driver/contator
externo e fusível próprio; a PCB fornece apenas o comando.

## 3. Aquisição distribuída

- pH, EC, temperatura da solução, massa e boias ficam na estação de mistura;
- detectores de vazamento cobrem dosagem, dois tanques e cultivo/dreno;
- temperatura, UR, CO₂ e temperatura foliar ficam em nó SELV ventilado no
  cultivo, fora do jato do umidificador;
- o nó de clima envia dados por barramento diferencial cabeado ao controlador;
  Wi-Fi/MQTT é telemetria e configuração, não o único caminho de segurança;
- I²C não percorre o ambiente nem cabos longos.

O padrão físico do barramento diferencial ainda será escolhido entre RS-485 e
CAN após análise de cabos, transceptores e firmware. Até essa decisão, nenhum
conector de campo correspondente está liberado para fabricação.

## 4. Fluxo hidráulico funcional

![Visualização realista conceitual da fertirrigação](../../images/realistic/FERTIRRIGACAO_CONCEITUAL.webp)

1. a entrada enche o tanque de água até limite de massa/boia;
2. válvula e bomba transferem a quantidade prevista ao tanque de mistura;
3. a mistura circula enquanto as dosadoras adicionam um canal por vez;
4. pH, EC e temperatura são lidos somente após pausas de homogeneização;
5. uma batelada aprovada alimenta a bomba de irrigação;
6. bandejas coletam retorno, que é drenado ao destino configurado;
7. qualquer divergência de massa, timeout ou vazamento fecha válvulas e desliga
   bombas localmente.

O P&ID final definirá válvulas de retenção, registros manuais, uniões, diâmetros,
sentido de fluxo e pontos de amostragem. A aparência de uma mangueira no vídeo
não é critério de dimensionamento.

## 5. Manutenção incorporada ao layout

- todos os seis frascos saem pela frente sem remover mangueiras de outros canais;
- cabeçotes peristálticos e tubos são substituíveis individualmente;
- sondas podem ser retiradas, limpas e armazenadas sem esvaziar o quadro;
- bombas e válvulas possuem união nos dois lados;
- plataformas de pesagem têm batentes contra sobrecarga e não recebem esforço
  lateral de mangueiras;
- cada cabo, tubo, borne, fusível, canal e sentido de fluxo recebe identificador;
- bandejas e piso permitem testar cada sensor de vazamento sem molhar eletrônica.

![Visualização realista conceitual do subsistema de clima](../../images/realistic/CLIMA_CONCEITUAL.webp)

Consulte as [limitações das vistas realistas](../../images/realistic/README.md)
antes de usar qualquer detalhe visual.

## 6. Estado da arquitetura

`A0 / REWORK / HOLD`: a fronteira, as funções e a direção compacta estão
definidas. A controladora possui envelope de 16 saídas; barramento e footprints
continuam abertos antes do KiCad. O
[`caderno de pranchas`](CADERNO_PRANCHAS.md) reúne implantação, planta baixa,
elevação, P&ID, elétrica e instalações. Imagens realistas são auxílio visual e
não substituem desenho as-built, BOM ou inspeção profissional.