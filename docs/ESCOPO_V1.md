# Escopo executável da release v1.0

Este documento transforma a referência estudada nas fronteiras do produto que
será construído. Em caso de conflito com uma observação histórica de vídeo, este
escopo e o ADR 0006 prevalecem.

## Resultado esperado

Ao concluir a v1.0, uma pessoa deverá conseguir comprar componentes aprovados,
montar a estação com o tutorial, comissioná-la primeiro com água e operar
fertirrigação e clima localmente sem depender da nuvem.

## Configuração física padrão

| Elemento | Configuração-base | Configurável antes do uso |
|---|---|---|
| Área de cultivo | 0,80 × 0,80 m | quantidade de zonas de irrigação |
| Concentrados | 6 recipientes de 1 L | nome, densidade, limite e ordem de cada canal |
| Água de origem | 1 reservatório de 50 L | tara, massa útil e limites alto/baixo |
| Solução preparada | 1 reservatório de 50 L | tara, massa útil e volume de batelada |
| Estrutura | rack de até 0,90 × 0,60 × 2,00 m; tanques empilhados | cotas as-built, carga, flecha e ancoragem |
| Rede do local | 127 V, 60 Hz | somente após medição e validação profissional |
| Exaustor atual | CA liga/desliga | modelo futuro pode usar 0–10 V documentado |
| Hub | Raspberry Pi local | hostname, retenção, backup e usuários |

Os nomes de produtos químicos vistos no vídeo são exemplos de canais, não uma
receita agronômica. O software exige que o operador cadastre e valide sua própria
receita, concentração e limites.

## Matriz de escopo

| Subsistema | Incluído na v1.0 | Fora da v1.0 |
|---|---|---|
| Dosagem | seis bombas calibradas, receita, limites por evento/hora/dia | recomendação automática de fertilizante |
| Química | pH, EC, temperatura, mistura, espera, correção segura | controle sem sonda válida ou dose ilimitada |
| Hidráulica | enchimento, transferência, mistura, irrigação, dreno, massa/nível | operação sem contenção e sem teste com água |
| Clima | temperatura, UR, VPD, CO₂, exaustão e umidificação | CO₂ injetado no MVP; controle sem plaqueta/manual |
| Segurança | vazamento latched, E-stop, timeout, watchdog, estado seguro | confiar apenas em Wi-Fi, servidor ou UI |
| Hub/painel | MQTT, API, histórico, alarmes, configuração mobile | dependência obrigatória de nuvem |
| Instalação | BOM, chicotes, desenhos, inspeções e tutorial leigo | energização de rede por pessoa não habilitada |
| Iluminação | nenhuma função | acionamento, medição, agenda, dimerização e PPFD |

## Fluxo operacional-alvo

1. confirmar disponibilidade de água e capacidade livre na mistura;
2. transferir a massa de água configurada de `TK-101` (nível superior) para
   `TK-201` (nível inferior), sem confiar apenas na gravidade;
3. misturar e estabilizar temperatura/leituras;
4. dosar cada concentrado sequencialmente, com pausa de homogeneização;
5. verificar EC e diluir apenas dentro dos limites configurados;
6. corrigir pH em pequenos pulsos, nunca pH+ e pH− simultaneamente;
7. aguardar estabilidade e liberar a batelada;
8. irrigar as zonas nos horários/durações configurados;
9. coletar/drenar com timeout e confirmar variação de massa/fluxo;
10. manter clima por histerese/anti-ciclo e registrar todo comando e alarme.

Qualquer vazamento, E-stop, leitura inválida crítica, timeout ou comportamento
incompatível com a variação de massa leva o sistema a estado seguro local.

## Definição de pronto físico

A expressão “pronto para comprar e montar” só poderá aparecer quando todos os
itens abaixo estiverem aprovados:

- BOM com MPN, alternativa, fornecedor e teste de recebimento;
- esquema e PCB com ERC/DRC reais, revisão independente e protótipo aprovado;
- P&ID, unifilar SELV/CA, chicotes e desenhos mecânicos congelados;
- rack, prateleiras independentes, plataformas e contenção em cascata ensaiados;
- ensaio de bancada, térmico, HIL e piloto somente com água;
- tutorial validado por uma montagem limpa feita a partir dos próprios arquivos;
- lista explícita das etapas que exigem eletricista/profissional habilitado;
- release reproduzível do firmware, hub e painel.

Até lá, documentos A0 são material de engenharia e cotação, não autorização de
compra em lote nem de energização.
