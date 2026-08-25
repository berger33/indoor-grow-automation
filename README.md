# Indoor Grow Automation

Stack open-source para automatizar fertirrigação, irrigação e ambiente de cultivo
indoor em pequena escala, composta por nós ESP32, hub local em Raspberry Pi e
painel web responsivo.

> **Status:** as tarefas 01–30 estão implementadas em software/documentação e o
> gate local está aprovado. A revisão física permanece `A0/HOLD`: ainda não se
> deve fabricar lote, energizar cargas ou operar com nutrientes.

## Objetivos

- adquirir pH, EC, temperatura da solução, temperatura/umidade do ar, nível e
  vazamento com qualidade de dado explícita;
- controlar fertirrigação, correção química, irrigação e clima com limites e
  timeouts locais;
- manter telemetria, API e interface no hub local, sem dependência obrigatória
  de nuvem;
- oferecer documentação suficientemente detalhada para montagem por terceiros;
- preservar operação segura quando Wi-Fi, broker ou servidor falharem.

**A potência da iluminação não faz parte deste projeto.** As luminárias continuam
nas tomadas Wi-Fi EKAZA existentes. O painel apenas oferece uma integração lógica
opcional via Home Assistant para agenda, comando e confirmação de estado; não há
relé, contator, fiação, PCB, dimerização, PPFD ou credencial no ESP32. Consulte o
[`escopo executável da v1.0`](docs/ESCOPO_V1.md).

## Arquitetura implementada em software

```mermaid
flowchart TD
    UI["Painel React"] -->|"HTTPS + WebSocket"| HUB["Hub Raspberry Pi"]
    HUB --> DB["PostgreSQL"]
    HUB <-->|"MQTT v1 + TLS mútuo"| ESP["3 nós ESP32"]
    HUB <-->|"API local"| HA["Home Assistant + EKAZA"]
    HUB --> BK["Backup e histórico"]
```

O arranjo físico padrão usa seis recipientes de concentrado de 1 L, um
reservatório de água de 50 L e um reservatório de mistura/rega de 50 L. A
revisão dirigida do vídeo de hardware está em
[`docs/referencia/REVISAO_VIDEO_16MIN.md`](docs/referencia/REVISAO_VIDEO_16MIN.md)
e a conferência completa da Parte 2 de funcionalidades está em
[`docs/referencia/REVISAO_VIDEO_PARTE2_FUNCIONALIDADES.md`](docs/referencia/REVISAO_VIDEO_PARTE2_FUNCIONALIDADES.md).

## Estrutura

| Caminho | Responsabilidade |
|---|---|
| `firmware/` | projetos PlatformIO dos nós ESP32 |
| `hub/` | domínio, API, persistência e serviços do Raspberry Pi |
| `web/` | painel mobile-first |
| `hardware/` | esquemas, PCB, gabinetes, chicotes e BOM |
| `docs/` | arquitetura, tutoriais, ADRs e referência estudada |
| `tests/` | testes unitários, integração, simulação e HIL |
| `scripts/` | qualidade, segurança, instalação e manutenção |

## Desenvolvimento local

Requisitos: Python 3.12 ou superior e Node.js 24 para o painel.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
npm ci --prefix web
python scripts/quality_gate.py
```

O serviço do Raspberry Pi é iniciado com `python -m hub.growhub.api` depois da
configuração descrita no
[`Tutorial 10A`](docs/tutorial/10a-integracao-tomadas-ekaza.md). Segredos ficam
somente no ambiente do serviço e nunca são versionados.

## Roadmap

1. Núcleo de firmware e modelo confiável de sensores.
2. Controle de fertirrigação, química, clima e segurança.
3. Hub, MQTT, persistência e API.
4. Painel responsivo, histórico, setpoints e alertas.
5. Documentação de montagem, comissionamento e release v1.0.

O detalhamento executável está em [`BACKLOG.md`](BACKLOG.md); as entregas ficam
em [`CHANGELOG.md`](CHANGELOG.md) e o diário em
[`PROGRESS_LOG.md`](PROGRESS_LOG.md).

A explicação simples, tarefa por tarefa, está em
[`docs/ENTREGA_TAREFAS_01_30.md`](docs/ENTREGA_TAREFAS_01_30.md). O estado de
liberação e todos os bloqueios físicos estão em
[`docs/RELATORIO_PRONTIDAO_V1.md`](docs/RELATORIO_PRONTIDAO_V1.md).

## Núcleo local executável

O pacote `hub/growhub/control` funciona como especificação testável do firmware:

- estados `BOOT`, `IDLE`, `MANUAL`, `BATCH` e `ALARM` retido;
- corte por vazamento e timeout absoluto de cada atuador;
- inicialização elétrica segura antes de habilitar saídas;
- watchdog e heartbeat sem dependência de nuvem;
- exclusão mútua de pH+ e pH−;
- limites independentes de dose por evento, hora e dia;
- calibração de bombas, receita sequencial, correção de pH/EC, mistura,
  irrigação, dreno, umidificação e exaustão testados por simulação.

Os simuladores em `hub/growhub/simulation` cobrem todos os sensores da v1 e
permitem injetar falhas canônicas sem hardware. O ADR 0008 fixa as invariantes
portadas ao núcleo C++; elas ainda precisam ser verificadas no ESP32 e na PCB
reais antes de qualquer teste com atuadores.

O runtime do hub conecta contratos e operação: persiste telemetria MQTT no
PostgreSQL, recebe alarmes retidos, publica comandos com expiração e atualiza
auditoria/progresso somente após ACK/NACK. Broker desconectado resulta em HTTP
503; comando sem confirmação nunca aparece como executado.

Contribuições seguem o fluxo de branches, commits, testes e releases descrito
em [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Segurança física

Água e fertilizantes próximos à rede elétrica exigem projeto e execução por
profissional habilitado, aterramento, DR/GFCI, fusíveis/disjuntores, separação
CA/SELV, gabinete apropriado e contenção de vazamentos. Software não substitui
proteções mecânicas e elétricas independentes.

## Hardware Rev A

A primeira revisão própria adota instalação fixa 127 V/60 Hz, sem qualquer
ramal de iluminação, e mantém toda a rede CA fora da PCB. O pacote preliminar
inclui:

- [base elétrica de controle, hidráulica e clima](docs/hardware/rev-a/BASE_ELETRICA_127V.md);
- [BOM consolidada com disponibilidade e critérios de substituição](docs/hardware/rev-a/BOM_SISTEMA.md);
- [controladora SELV, pinagem, netlist e parâmetros](hardware/controller-rev-a/README.md);
- [laudo preliminar e gates de fabricação](docs/hardware/rev-a/LAUDO_REVISAO_REVA.md).

A [integração opcional das tomadas EKAZA](docs/tutorial/10a-integracao-tomadas-ekaza.md)
é exclusivamente de software e não altera o hardware Rev A.

![Unifilar da variante 127 V](desenhos/REV-A-01_UNIFILAR_127V.svg)

![Zonas funcionais da PCB Rev A](desenhos/REV-A-02_PCB_ZONAS.svg)

O estado atual é `A0/HOLD`: os arquivos servem para revisão e prototipagem, não
para fabricar lote ou energizar cargas reais.

## Visualização do sistema pronto

![Estação compacta vertical — visualização conceitual](docs/images/realistic/ESTACAO_COMPACTA_VERTICAL_CONCEITUAL.webp)

As [três vistas realistas e suas limitações](docs/images/realistic/README.md)
mostram a aparência pretendida. Elas não substituem desenhos cotados, P&ID,
unifilar ou arquivos de fabricação.

O [caderno multidisciplinar Rev A](docs/hardware/rev-a/CADERNO_PRANCHAS.md)
reúne implantação, planta baixa, elevação, projeto hidráulico, projeto elétrico
e rotas de instalações da disposição vertical compacta.

## Origem da referência

O backlog parte de `ESPECIFICACAO_REFERENCIA.md`, produzido por análise dos
vídeos e do repositório MIT `ledgardener/gardenAutomation`. O código novo não
pressupõe que a PCB experimental publicada esteja validada.

## Licença

MIT. Componentes de terceiros mantêm seus respectivos avisos e licenças.
