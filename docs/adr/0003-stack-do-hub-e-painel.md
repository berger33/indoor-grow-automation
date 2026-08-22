# ADR 0003 — Stack do hub e painel

- **Status:** aceito
- **Data:** 2026-08-22

## Contexto

O hub precisa caber em Raspberry Pi, funcionar sem nuvem, oferecer API e
histórico e ser compreensível por mantenedores. O painel precisa operar bem em
telefone e tablet. A escolha deve ser reversível enquanto o domínio ainda é
pequeno.

## Decisão

- **Domínio e API:** Python 3.12+ e FastAPI.
- **Mensageria:** MQTT com Mosquitto.
- **Persistência inicial:** PostgreSQL; testes de domínio não dependem do banco.
- **Migrações:** Alembic.
- **Painel:** TypeScript, React e Vite, com PWA apenas depois da UI básica.
- **Empacotamento do hub:** containers Docker Compose compatíveis com ARM64.
- **Firmware:** ESP32 com PlatformIO e framework Arduino inicialmente.

O domínio Python não importará FastAPI, driver de banco ou cliente MQTT. Portas
e adaptadores permitirão testar regras sem hardware e trocar infraestrutura.

## Consequências

- a primeira fase pode avançar com biblioteca padrão e testes rápidos;
- o Raspberry Pi executará API, broker e banco como serviços separados;
- dependências serão fixadas por versão e atualizadas por tarefa específica;
- Home Assistant poderá consumir MQTT/API, mas não será requisito do núcleo;
- imagens ARM64 e consumo de memória devem integrar os critérios de release.

## Alternativas rejeitadas

- **SQLite em produção:** simples, mas menos adequado a múltiplos serviços e
  séries temporais concorrentes; continua útil em testes.
- **Node.js em todo o hub:** viável, mas Python simplifica ferramentas de dados e
  simulação previstas.
- **Dashboard exclusivamente Home Assistant:** dificulta experiência guiada e
  suporte independente para instalação por leigos.
