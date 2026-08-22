# Indoor Grow Automation

Stack open-source para monitoramento e automação de cultivo indoor em pequena
escala, composta por nós ESP32, hub local em Raspberry Pi e painel web
responsivo.

> **Status:** fundação da Fase 1. O projeto ainda não deve comandar cargas reais
> sem a conclusão dos intertravamentos, testes elétricos e comissionamento.

## Objetivos

- adquirir pH, EC, temperatura da solução, temperatura/umidade do ar, nível e
  vazamento com qualidade de dado explícita;
- controlar fertirrigação, correção química, iluminação e clima com limites e
  timeouts locais;
- manter telemetria, API e interface no hub local, sem dependência obrigatória
  de nuvem;
- oferecer documentação suficientemente detalhada para montagem por terceiros;
- preservar operação segura quando Wi-Fi, broker ou servidor falharem.

## Arquitetura planejada

```text
Painel web responsivo
        │ HTTPS / WebSocket
        ▼
Hub Raspberry Pi ── API + banco + MQTT ── Wi-Fi/LAN
        │                                  │
        │                                  ├── ESP32 fertirrigação/pH/EC
        │                                  ├── ESP32 clima/VPD
        │                                  └── ESP32 segurança/I/O
        ▼
Backup, histórico e alertas locais
```

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

Requisito inicial: Python 3.12 ou superior.

```bash
python -m unittest discover -s tests -v
python scripts/quality_gate.py
```

Dependências adicionais serão introduzidas somente quando houver código que as
utilize. Segredos ficam em `.env`, que nunca é versionado.

## Roadmap

1. Núcleo de firmware e modelo confiável de sensores.
2. Controle de fertirrigação, química, clima e segurança.
3. Hub, MQTT, persistência e API.
4. Painel responsivo, histórico, setpoints e alertas.
5. Documentação de montagem, comissionamento e release v1.0.

O detalhamento executável está em [`BACKLOG.md`](BACKLOG.md); as entregas ficam
em [`CHANGELOG.md`](CHANGELOG.md) e o diário em
[`PROGRESS_LOG.md`](PROGRESS_LOG.md).

Contribuições seguem o fluxo de branches, commits, testes e releases descrito
em [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Segurança física

Água e fertilizantes próximos à rede elétrica exigem projeto e execução por
profissional habilitado, aterramento, DR/GFCI, fusíveis/disjuntores, separação
CA/SELV, gabinete apropriado e contenção de vazamentos. Software não substitui
proteções mecânicas e elétricas independentes.

## Hardware Rev A

A primeira revisão própria adota instalação fixa 127 V/60 Hz e mantém toda a
rede CA fora da PCB. O pacote preliminar inclui:

- [base elétrica e cálculo do conjunto de 390 W](docs/hardware/rev-a/BASE_ELETRICA_127V.md);
- [BOM consolidada com disponibilidade e critérios de substituição](docs/hardware/rev-a/BOM_SISTEMA.md);
- [controladora SELV, pinagem, netlist e parâmetros](hardware/controller-rev-a/README.md);
- [laudo preliminar e gates de fabricação](docs/hardware/rev-a/LAUDO_REVISAO_REVA.md).

![Unifilar da variante 127 V](desenhos/REV-A-01_UNIFILAR_127V.png)

![Zonas funcionais da PCB Rev A](desenhos/REV-A-02_PCB_ZONAS.png)

O estado atual é `A0/HOLD`: os arquivos servem para revisão e prototipagem, não
para fabricar lote ou energizar cargas reais.

## Origem da referência

O backlog parte de `ESPECIFICACAO_REFERENCIA.md`, produzido por análise dos
vídeos e do repositório MIT `ledgardener/gardenAutomation`. O código novo não
pressupõe que a PCB experimental publicada esteja validada.

## Licença

MIT. Componentes de terceiros mantêm seus respectivos avisos e licenças.
