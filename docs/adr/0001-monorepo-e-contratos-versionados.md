# ADR 0001 — Monorepo com contratos versionados

- **Status:** aceito
- **Data:** 2026-08-22

## Contexto

Firmware ESP32, hub, painel, documentação e hardware evoluem juntos. Alterar o
formato de telemetria sem coordenar as duas pontas pode deixar o cultivo sem
monitoramento ou produzir comandos incompatíveis.

## Decisão

Manter todos os componentes em um monorepo. Contratos trocados entre nós e hub
terão versão explícita, testes de compatibilidade e fixtures compartilhadas.

Diretórios principais:

- `firmware/`: um projeto PlatformIO por tipo de nó;
- `hub/`: domínio independente de framework, adaptadores e API;
- `web/`: cliente TypeScript responsivo;
- `contracts/`: schemas e exemplos de mensagens;
- `hardware/`: arquivos-fonte e documentação de fabricação;
- `docs/`: tutoriais, decisões e segurança.

## Consequências

- uma mudança de contrato pode ser validada ponta a ponta no mesmo CI;
- releases do conjunto recebem uma versão coordenada;
- o repositório será maior, mas a escala do projeto não justifica múltiplos
  repositórios e pipelines independentes;
- firmware e hub continuam desacoplados por contratos, não por compartilhamento
  de implementação.

## Alternativas rejeitadas

- **Um repositório por componente:** aumenta coordenação e dificulta releases
  reproduzíveis.
- **Home Assistant como núcleo exclusivo:** acelera o protótipo, mas mantém
  intertravamentos dependentes do servidor e dificulta testes determinísticos.
