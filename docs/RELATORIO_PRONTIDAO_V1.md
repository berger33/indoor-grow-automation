# Relatório de prontidão — arquitetura DIY

> **Decisão atual:** software preservado; montagem física DIY ainda não validada.

## Estado por camada

| Camada | Estado verificável |
|---|---|
| FastAPI, PostgreSQL e Mosquitto | preservados, com testes existentes |
| Painel React | preservado e compilável |
| Contratos MQTT | preservados |
| Home Assistant/EKAZA | preservado; IDs e testes físicos continuam locais |
| BOM DIY | completa, estimada em R$ 1.620 |
| Pinagem | 12 saídas GPIO diretas documentadas |
| Firmware | controlador ESP32 único criado; HIL virtual cobre interlocks essenciais |
| Tutorial | reescrito em dez etapas, do recebimento à primeira receita |
| Engenharia pesada | movida para arquivo histórico e fora do escopo ativo |
| Montagem física | pendente |
| Teste somente com água | pendente |
| Primeira receita | pendente e supervisionada |

## Evidência automatizada esperada

- suíte Python;
- HIL nativo com boot seguro, timeout, vazamento, perda do hub, sensor inválido
  e exclusão de saídas;
- build PlatformIO do `firmware/controller` no CI;
- typecheck e build Vite;
- validação de BOM total entre R$ 1.000 e R$ 1.650;
- doze saídas em OFF no boot e sem referências ativas a expansores/PCB;
- verificação do arquivo histórico;
- SBOM e scanner de segredos.

## Bloqueios físicos reais

1. Comprar/receber os módulos e registrar variantes reais.
2. Confirmar compatibilidade de 3,3 V dos relés/MOSFETs.
3. Medir que pH/EC nunca ultrapassam 3,3 V.
4. Calibrar pH, EC e seis peristálticas.
5. Medir corrente, vazão, altura e aquecimento das bombas.
6. Testar estante, caixas e contenção com água.
7. Executar cinco boots e todos os cenários de falha com cargas simuladas.
8. Executar um ciclo completo apenas com água.
9. Confirmar as entidades EKAZA reais e cem ciclos por canal.
10. Executar a primeira receita real com supervisão.

## Critério de liberação

Não declare o hardware pronto com base apenas em compilação. Cada bloqueio deve
ter data, peça real, medição, tolerância e resultado. Qualquer falha retorna à
etapa anterior do tutorial. O sistema só pode ficar sem supervisão depois de
repetir os ciclos planejados sem falha crítica.
