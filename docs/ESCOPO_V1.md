# Escopo executável da versão DIY

Este documento prevalece sobre observações históricas em vídeos, pranchas e
ADRs arquivados. O objetivo atual é um sistema doméstico barato, compreensível e
funcional, não uma estação de engenharia industrial.

## Resultado esperado

Uma pessoa deverá conseguir comprar peças comuns, montar a estação pelo
tutorial, executar o hub no próprio notebook, calibrar o conjunto, testar
somente com água e então operar uma primeira receita supervisionada.

## Configuração-base

| Elemento | Configuração |
|---|---|
| Hub | notebook Linux `amd64/arm64` já disponível, com Docker |
| Controlador | 1 ESP32 DevKit genérico em placa perfurada soldada |
| Dosagem | 6 peristálticas 12 V por módulos MOSFET |
| Atuadores | módulo relé 8 canais; 6 usados e 2 desconectados |
| Reservatórios | 2 caixas organizadoras plásticas de 40–50 L |
| Concentrados | 6 potes de vidro de aproximadamente 1 L |
| Estrutura | estante aramada comum e fundo de madeira selada |
| Química | pH e EC analógicos, calibrados localmente |
| Clima | DHT22, exaustão e umidificação por histerese |
| Iluminação | tomadas EKAZA existentes via Home Assistant |
| Orçamento | R$ 1.620 estimados, sem notebook/frete/ferramentas/serviço elétrico |

## Matriz de escopo

| Incluído | Fora do escopo ativo |
|---|---|
| notebook com Docker e serviços existentes | compra de Raspberry Pi |
| ESP32 único e GPIO direto | três nós, `SN74HCT595` e `MCP23017` |
| placa perfurada e módulos prontos | PCB customizada, KiCad, Gerber, ERC/DRC |
| relés e MOSFETs genéricos | controladora industrial de 16 saídas |
| pH/EC analógicos econômicos | Atlas EZO e carriers isolados |
| DHT22 | CO₂ dedicado, MLX90614 e sensores redundantes caros |
| caixas organizadoras e potes comuns | tanques técnicos e plataformas de pesagem |
| estante aramada | rack fabricado sob medida e gabinete IP65 |
| segurança elétrica básica | painel dedicado com DR/DPS/contatores industriais |
| parada local em baixa tensão | E-stop certificado |
| agitação manual periódica | seis agitadores magnéticos dedicados |

O diretório `archive/engenharia-pesada/` guarda a arquitetura anterior apenas
para histórico. Ele não define a montagem atual.

## Funções de software preservadas

- receitas, agendas e calibração;
- limites de dose por evento, hora e dia;
- pH+ e pH− mutuamente exclusivos;
- mistura, irrigação e drenagem com timeout;
- clima por histerese e anti-ciclo;
- telemetria, histórico, alarmes e painel React;
- FastAPI, PostgreSQL, Mosquitto e contratos MQTT v1;
- integração Home Assistant/EKAZA sem acoplamento ao cultivo.

## Segurança mínima obrigatória

- saídas OFF no boot e após reboot;
- timeout absoluto que comando repetido não renova;
- somente uma dosadora por vez;
- irrigação e drenagem mutuamente exclusivas;
- corte por vazamento e botão local;
- fusível nos ramais de 12 V;
- eletrônica fechada, elevada e protegida contra respingos;
- tomada aterrada e proteção DR existente;
- teste completo somente com água antes de qualquer produto;
- primeira receita e primeiras agendas supervisionadas.

Qualquer criação/alteração de cabo ou circuito de 127 V fica fora da montagem
DIY e deve ser feita por pessoa qualificada. Não existe exigência de painel
industrial dedicado.

## Critério de pronto

1. BOM comprada e recebida sem substituição não documentada.
2. Firmware `controller` e HIL compilados.
3. Cinco boots sem pulso de saída.
4. pH/EC limitados a 3,3 V, calibrados e verificados.
5. Dez ciclos medidos por bomba peristáltica.
6. Corrente e aquecimento das bombas/fonte registrados.
7. Vazamento, parada, timeout, perda do hub e reboot aprovados.
8. Ciclo completo somente com água aprovado.
9. Backup do hub restaurado em ambiente de teste.
10. Primeira receita real concluída com supervisão e histórico.

“DIY” significa simplificado e econômico; não significa operar sem proteção,
calibração ou verificação.
