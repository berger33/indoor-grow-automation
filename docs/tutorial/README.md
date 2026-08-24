# Tutorial de montagem — índice e contrato editorial

> **Status:** estrutura aprovada; capítulos serão liberados junto com os gates de
> hardware. Não compre nem energize o conjunto usando documentos A0/HOLD.

O objetivo deste tutorial é permitir que uma pessoa sem experiência prévia
entenda o sistema, confira as peças e execute todas as etapas permitidas. Rede
127 V, dimensionamento, proteções e testes correspondentes continuam sendo
responsabilidade de profissional habilitado.

## Sequência obrigatória

| Etapa | Capítulo | Resultado verificável | Libera |
|---:|---|---|---|
| 00 | segurança, escopo e responsabilidades | usuário identifica zonas e atividades proibidas | leitura dos demais capítulos |
| 01 | inventário e inspeção de recebimento | cada MPN/lote/foto/teste registrado | separação de kits |
| 02 | [estrutura e zonas seca/molhada](02-estrutura-e-zonas.md) | suporte nivelado e distâncias aprovadas | montagem de tanques |
| 03 | [tanques empilhados e plataformas de pesagem](03-reservatorios-e-plataformas.md) | níveis independentes, contenção e tara repetível | hidráulica |
| 04 | bombas, válvulas e tubulação | teste de estanqueidade sem eletrônica | dosagem |
| 05 | [frascos, agitadores e peristálticas](05-frascos-dosadoras-agitadores.md) | seis linhas identificadas e sem sifão | sensores químicos |
| 06 | pH, EC, temperatura, boias e vazamento | leituras/estados brutos plausíveis | quadro SELV |
| 07 | controladora, fontes e chicotes SELV | continuidade/polaridade aprovadas sem CA | firmware |
| 08 | instalação 127 V por profissional | laudo, PE, DR, isolação e proteções aprovados | energização controlada |
| 09 | gravação e provisionamento ESP32 | nós em safe boot e diagnosticáveis | hub |
| 10 | Raspberry Pi, MQTT, API e painel | instalação limpa reproduzida | calibração |
| 10A | [integração lógica com tomadas EKAZA](10a-integracao-tomadas-ekaza.md) | estados remotos confirmados sem carga no rack | agenda de luz remota |
| 11 | calibração guiada | massa, bombas, pH e EC dentro da tolerância | HIL |
| 12 | teste seco, HIL e piloto com água | todas as falhas críticas injetadas | primeira batelada |
| 13 | primeira batelada supervisionada | relatório aprovado sem alarme pendente | operação assistida |
| 14 | manutenção e resposta a falhas | cronograma e procedimentos acessíveis | operação continuada |

## Padrão obrigatório de cada capítulo

Cada capítulo deverá conter:

1. objetivo e resultado final fotografado;
2. pré-requisitos e gates que precisam estar aprovados;
3. peças por identificador da BOM, ferramentas e EPIs;
4. riscos e tarefas exclusivas de profissional habilitado;
5. desenho técnico vinculante e imagem realista apenas ilustrativa;
6. passos numerados, uma ação física por passo;
7. foto ou render do estado esperado nos pontos de inspeção;
8. teste de aceitação quantitativo e evidência a registrar;
9. erros comuns, diagnóstico e como retornar ao estado seguro;
10. limpeza, descarte e próxima etapa liberada.

Valores químicos e receitas de nutrientes não serão tratados como universais.
O operador informa produtos, concentrações e limites conforme fabricante e
orientação agronômica aplicável.

## Área Ajuda do painel

O painel mobile-first reproduzirá este índice e abrirá o capítulo compatível com
a tela atual. Alarmes terão instruções curtas de estado seguro e link para o
procedimento completo. A Ajuda será instalada localmente no Raspberry Pi e
continuará disponível sem internet.

O modo de ajuda não poderá:

- liberar um intertravamento;
- ocultar alarme latched;
- alterar dose, timeout ou proteção;
- orientar ligação de rede sem profissional;
- confundir imagem conceitual com desenho as-built.

## Validação do tutorial

Antes da v1.0, uma montagem limpa deverá ser executada usando somente BOM,
arquivos de fabricação e estes capítulos. Toda dúvida, passo implícito ou peça
ausente retorna ao backlog. A versão validada receberá fotos da montagem real e
hashes dos artefatos exatos usados.
