# Etapa 01 — inventário e conferência de recebimento

## Objetivo

Separar componentes por subsistema, registrar rastreabilidade e impedir que uma
peça errada ou danificada avance para montagem. Esta etapa não autoriza compra
em lote: use apenas amostras destinadas a medição e ensaio enquanto a revisão
estiver `A0/HOLD`.

## Antes de começar

- conclua a etapa 00 e mantenha toda alimentação desconectada;
- abra a BOM em `docs/hardware/rev-a/BOM_SISTEMA.md`;
- prepare câmera, paquímetro, etiquetas, marcador e sacos antiestáticos;
- use luvas adequadas ao inspecionar recipientes que transportarão químicos;
- não conecte fontes, bombas, válvulas ou placas à rede 127 V.

## Crie seis caixas de conferência

1. `ELE-SELV`: controladora, ESP32, sensores, módulos e chicotes de baixa tensão.
2. `DOS-01..06`: um kit individual por recipiente, dosadora e linha química.
3. `HYD`: bombas, válvulas, tubos, uniões, filtros e drenos.
4. `TANQUES`: reservatórios de água e mistura, tampas e contenções.
5. `CLIMA`: sensores, exaustão, umidificação e respectivos drivers externos.
6. `HUB`: Raspberry Pi, armazenamento, fonte homologada e rede local.

Iluminação e tomadas da automação existente não entram em nenhuma caixa.

## Registro obrigatório por item

Para cada linha recebida, anote:

| Campo | Como conferir |
|---|---|
| identificador BOM | deve coincidir com a revisão do documento |
| fabricante e MPN | fotografe embalagem e marcação da peça |
| quantidade | conte sem usar a nota fiscal como única evidência |
| lote/data code | registre quando existir |
| dimensões | meça corpo, terminais, furos e conectores críticos |
| tensão/corrente | copie somente da plaqueta/datasheet do MPN exato |
| estado | aprovado, quarentena ou rejeitado |
| evidência | nome do arquivo de foto e responsável pela inspeção |

Nunca substitua um componente apenas porque “parece igual”. Registre a proposta
em quarentena para revisão da BOM, corrente, footprint e compatibilidade química.

## Ensaios de recebimento sem energização

1. Verifique trincas, corrosão, terminais tortos, vedação e sinais de uso.
2. Compare polaridade, pinagem e quantidade de vias com a documentação.
3. Meça o componente físico antes de congelar qualquer footprint da PCB.
4. Confirme que tubos, vedações e recipientes possuem material declarado.
5. Encha tanques e contenções somente com água, fora da zona elétrica, para
   procurar deformação e vazamento inicial.
6. Pese cada reservatório vazio e registre a tara provisória.
7. Mantenha sondas de pH/EC nas condições de armazenamento do fabricante.

Ensaios energizados, corrente de partida e isolamento pertencem aos capítulos
posteriores e aos profissionais indicados na etapa 00.

## Critério de aceitação

A etapa é aprovada somente quando:

- [ ] todos os itens recebidos possuem foto, MPN, quantidade e estado;
- [ ] nenhum item em quarentena foi usado para definir footprint ou chicote;
- [ ] os seis canais de dosagem estão fisicamente separados e identificados;
- [ ] os dois reservatórios são de 50 L e suas dimensões reais foram registradas;
- [ ] danos, divergências e ausências viraram pendência rastreável;
- [ ] não houve energização nem contato de eletrônica com água;
- [ ] a BOM continua marcada como A0/HOLD até os gates de engenharia.

O resultado desta etapa é um relatório de recebimento, não um conjunto liberado
para montagem elétrica ou operação química.
