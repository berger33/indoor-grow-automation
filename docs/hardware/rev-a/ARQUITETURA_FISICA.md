# Arquitetura física-alvo da estação

Este documento fixa a organização funcional derivada do vídeo V1 e adaptada aos
volumes informados. Dimensões cotadas só serão congeladas depois da medição dos
tanques e do local.

## 1. Zonas físicas

| Zona | Conteúdo | Regra de posicionamento |
|---|---|---|
| A — quadro seco | proteções CA, fontes, controladora, bornes e E-stop | parede, acima e lateralmente afastado dos tanques |
| B — dosagem | seis frascos de 1 L, seis agitadores e seis peristálticas | prateleira frontal, removível e com contenção própria |
| C — água | reservatório de origem de 50 L, plataforma e boias | base rígida, nivelada, dentro de contenção |
| D — mistura | reservatório de mistura/rega de 50 L, plataforma, sondas e bomba | base rígida, tampa acessível e sem apoiar tubos na balança |
| E — hidráulica | bombas, válvulas, manifold, uniões e dreno | painel molhado separado, peças substituíveis sem desmontar o quadro |
| F — cultivo | emissores, bandeja de coleta, dreno e sensores climáticos | nenhum equipamento de rede exposto à névoa/rega |
| G — hub | Raspberry Pi, rede e armazenamento | caixa seca, ventilada e acessível para backup |

Mangueiras nunca passam sobre as zonas A ou G. Cabos que sobem de uma zona
molhada formam laço de gotejamento antes do prensa-cabo.

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

## 6. Estado da arquitetura

`A0 / REWORK`: a fronteira e as funções estão definidas; capacidade de I/O,
barramento e layout serão atualizados antes de iniciar KiCad. As imagens
realistas do repositório são auxílio visual, não substituem P&ID, unifilar,
desenho cotado, BOM ou inspeção profissional.
