# ADR 0008 — Núcleo local fail-safe

- Status: aceito
- Data: 2026-08-24

## Contexto

Fertirrigação reúne água, concentrados e atuadores capazes de permanecer
ligados após falha de software ou rede. O notebook/hub e o painel não podem ser
a única camada de segurança. Também não é aceitável que um novo comando renove
indefinidamente o tempo máximo de uma bomba.

## Decisão

O controlador ESP32 aplicará localmente, antes de qualquer integração MQTT:

1. estados explícitos `BOOT`, `IDLE`, `MANUAL`, `BATCH` e `ALARM`;
2. `ALARM` retido até desaparecimento comprovado da causa e rearme explícito;
3. MOSFETs inicializados em LOW e relés ativos em LOW inicializados em HIGH;
4. timeout absoluto por acionamento, sem renovação por comando repetido;
5. vazamento confirmado como corte local imediato;
6. watchdog independente do heartbeat do hub;
7. perda do hub bloqueando novos comandos e interrompendo `MANUAL`/`BATCH`;
8. exclusão mútua elétrica e lógica de pH+ e pH−;
9. orçamento persistente por canal para evento, hora e dia.

O código Python desta revisão é o modelo executável e a referência dos testes.
A implementação ESP32 deverá reproduzir as mesmas transições e vetores antes de
ser conectada a atuadores reais.

## Consequências

- O painel não consegue ignorar um intertravamento local.
- Reiniciar o hub não rearma alarmes nem zera orçamentos de dose.
- Clima essencial mantém fallback local próprio e prioridade sobre comandos
  incompatíveis de fertirrigação.
- Persistência de orçamento, motivo de reset e alarme ainda precisa ser definida
  no firmware antes de HIL.
- Nenhuma destas decisões libera operação autônoma antes do teste com água.
