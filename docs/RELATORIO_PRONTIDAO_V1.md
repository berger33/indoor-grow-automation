# Relatório de prontidão — ciclo das tarefas 1–30

> **Decisão atual: A0/HOLD — não liberar energização, compra final ou v1.0.**

Este relatório separa software comprovado, artefato preparado para CI e ensaio
físico ainda inexistente. “Implementado” não significa homologado no equipamento.

## Resultado por tarefa

| # | Entrega | Estado verificável neste ciclo |
|---:|---|---|
| 1 | Umidificador | timeout absoluto e nível/vazamento retidos, com testes |
| 2 | CO₂ | estados/alertas somente de leitura; nenhuma saída de injeção |
| 3–4 | Firmware e safe boot | três projetos PlatformIO + núcleo seguro; HIL nativo aprovado, build ESP32 aguardando CI |
| 5–6 | Sensores ambientais/químicos | drivers, qualidade, compensação e falhas cobertos por testes |
| 7–8 | Fertirrigação, hidráulica e clima | máquinas de estado, limites e intertravamentos implementados/simulados |
| 9 | HIL virtual | seis cenários terminam com saídas OFF; HIL físico pendente |
| 10–11 | MQTT e comandos | tópicos v1, UUID, sequência, expiração, deduplicação e ACK/NACK |
| 12 | Broker | TLS 1.3 mútuo + ACL; execução em contêiner aguardando CI |
| 13–18 | Banco, API, segurança e tempo real | Alembic, retenção, perfis, auditoria e replay implementados/testados |
| 19 | Raspberry Pi | Compose ARM64, limites, previsão, backup/restore; hardware real pendente |
| 20 | EKAZA | banco, migração sem sobrescrita, agenda/override e confirmação por releitura |
| 21–26 | Painel | Home, gráficos, alarmes, calibração, operação, acessibilidade e Ajuda offline compilam |
| 27–29 | Tutoriais 03–11 | capítulos e diagramas técnicos publicados; fotos reais/validação limpa pendentes |
| 30 | Tutoriais 12–14, SBOM e prontidão | documentos publicados; SBOM provisória; HIL físico e RC pendentes |

## Evidência automatizada local

- suíte Python com mais de 260 testes;
- seis cenários HIL nativos fail-safe;
- TypeScript e build Vite;
- 255 referências dos manifestos de hardware;
- oito pranchas Rev A validadas;
- scanner de segredos;
- SBOM SPDX sincronizada com os manifests.

O CI remoto ainda precisa comprovar PlatformIO nos três ESP32, Mosquitto com
certificados efêmeros, Compose e o mesmo gate em checkout limpo.

## Bloqueios que a automação não pode preencher

1. medir tanques, percursos hidráulicos, vazão e altura manométrica;
2. receber amostras, congelar footprints, executar ERC/DRC e fabricar PCB;
3. medir corrente/inrush, temperatura e feedback das cargas reais;
4. homologar os quatro IDs/modelos EKAZA em 100 ciclos por canal;
5. montar, inspecionar e fotografar a estação real;
6. executar HIL físico, piloto com água e primeira batelada supervisionada;
7. obter revisão/laudo da instalação 127 V por profissional habilitado;
8. validar os tutoriais em montagem limpa por pessoa sem contexto prévio;
9. completar SBOM transitiva do toolchain/contêineres e resolver OneWire `NOASSERTION`.

## Critério para sair de HOLD

Cada bloqueio deve ter responsável, data, instrumento/amostra, resultado bruto,
tolerância e evidência. Falha não pode ser convertida em aprovação documental.
Somente depois dos gates físicos, CI verde e revisão do PR pode ser criada uma
release candidate. Merge na `main` e qualquer alteração material continuam
dependendo de autorização explícita do proprietário.
