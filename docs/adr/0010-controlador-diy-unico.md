# ADR 0010 — Controlador DIY único e hub no notebook

- Estado: aceito
- Data: 2026-08-25
- Substitui no escopo ativo: ADR 0005 e ADR 0007 arquivados

## Contexto

A arquitetura Rev A exigia PCB customizada, registradores/expansores, três nós,
interfaces químicas caras, painel e estrutura sob medida. O custo e a
complexidade deixaram de servir ao objetivo doméstico do projeto.

## Decisão

1. O hub roda no notebook Linux já disponível, usando as mesmas imagens Docker.
2. Um ESP32 DevKit controla toda a estação física.
3. Seis dosadoras usam dois módulos MOSFET genéricos e GPIO direto.
4. Seis atuadores usam um módulo de relé de oito canais ativo em LOW; dois canais
   físicos permanecem desconectados.
5. pH e EC usam interfaces analógicas calibráveis e limitadas a 3,3 V.
6. O clima usa DHT22; CO₂ dedicado e temperatura foliar ficam fora do hardware.
7. Caixas organizadoras, potes e estante aramada substituem tanques/rack sob medida.
8. O hub, contratos MQTT, painel e integração EKAZA permanecem inalterados.
9. Timeout, vazamento, parada local e exclusões de bombas permanecem obrigatórios.
10. Todo ciclo físico começa com carga simulada e depois somente água.

## Consequências

- O orçamento planejado cai para R$ 1.620 sem o notebook.
- A precisão química depende mais de calibração, ruído e manutenção.
- A montagem fica mais fácil de reparar e adaptar.
- O botão local não é E-stop certificado.
- Qualquer trabalho novo em 127 V continua fora da montagem de baixa tensão.
- Pranchas, PCB, laudo e tutorial industrial ficam preservados somente em
  `archive/engenharia-pesada/`.
