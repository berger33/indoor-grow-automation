# ADR 0002 — Segurança local independente do hub

- **Status:** aceito
- **Data:** 2026-08-22

## Contexto

O sistema de referência executa parte relevante dos intertravamentos no Home
Assistant. Wi-Fi, MQTT, processo do hub ou banco podem falhar exatamente durante
uma transferência de água ou dosagem química.

## Decisão

Cada nó que controla uma carga capaz de provocar vazamento ou dosagem excessiva
deve aplicar localmente:

1. estado seguro no boot e reset;
2. timeout absoluto por acionamento;
3. limites por dose e por janela de tempo;
4. corte latched por sensor de vazamento;
5. watchdog de hardware;
6. política explícita para perda do heartbeat do hub;
7. parada física independente do software.

O hub pode tornar a operação mais restritiva, mas nunca remover limites físicos
ou locais. O reset de alarme exige permissivos locais; uma mensagem MQTT não
pode forçar uma entrada seca.

## Consequências

- nós precisam manter uma pequena máquina de estados mesmo sem conexão;
- ensaios HIL devem cobrir perda de rede em todas as transições críticas;
- configuração de limites deve ser persistente, validada e protegida contra
  corrupção;
- a instalação continua exigindo DR/GFCI, fusíveis, contenção e transbordo
  passivo: firmware é somente uma camada de defesa.

## Alternativas rejeitadas

- **Falhar mantendo o último comando:** pode deixar bomba ou válvula ativa.
- **Delegar tudo ao hub:** cria ponto único de falha.
- **Usar apenas notificações:** informa o acidente, mas não reduz sua severidade.
