# Revisão dirigida — vídeo Parte 2 de funcionalidades (18:00)

> **Referência histórica.** As funções observadas permanecem válidas; a tradução
> para o hardware econômico atual é definida pelo
> [ADR 0010](../adr/0010-controlador-diy-unico.md).

- Arquivo revisado: `My DIY Home Assistant Garden Automation System - Climate Control, Dosing & More. Pt.2_ Functionality.mp4`
- Duração verificada: 18:00
- Resolução do anexo: 640 × 360
- SHA-256: `e68bbe350769b4d10ebc5f4b4b375b1ffe4ec8e5ac56c21bd7e92d945c05828d`
- Data da revisão dirigida: 2026-08-24

Esta revisão responde ao pedido de conferir a segunda parte completa e atualizar
o projeto com as funções ausentes. O vídeo foi inspecionado integralmente e por
quadros. Textos ou modelos que não ficam legíveis não foram inferidos.

## Linha do tempo confirmada

| Tempo aproximado | Evidência funcional | Aplicação segura no projeto próprio |
|---:|---|---|
| 00:00–02:50 | frascos, agitadores magnéticos, dosadoras e acionamentos físicos | seis canais calibrados, etiquetados e dosados em sequência; nenhuma receita é presumida |
| 02:50–03:35 | comando remoto e resposta de relé/tomada | comandos remotos exigem leitura de confirmação; voz não é requisito de segurança |
| 03:35–05:25 | visão geral, sensores e gráficos no Home Assistant | painel local explicita qualidade/idade e consulta histórico do hub |
| 05:25–12:25 | controle de relés, tomadas, pH, EC, receita e clima | separar comando, estado observado e feedback físico; aplicar limites, espera e intertravamentos |
| 07:20–10:45 | alvos de pH/EC e proporções CalMag, Micro, Bloom e Grow | usar lote em mL/L, sequência CalMag→Micro→Bloom→Grow e configuração validada pelo operador |
| 10:45–12:25 | temperatura, umidade, exaustor e automações | exaustor atual somente liga/desliga, com histerese, anti-ciclo e falha segura; PWM fica fora até existir manual compatível |
| 12:25–14:40 | calibração de pH, EC, balança e bombas | persistir data/condição da calibração e rejeitar curva incoerente antes de dosar |
| 14:40–16:10 | data de cultivo, até cinco fertirrigações e agenda de luz | até cinco eventos sem sobreposição; luz somente por tomadas remotas, fora da elétrica da estação |
| 16:10–18:00 | diagnóstico do host e interface responsiva em telas diferentes | API/painel locais devem degradar de forma explícita e nunca inventar dados ou sucesso |

## Funções incorporadas após a revisão

| Função observada | Implementação atual | Estado |
|---|---|---|
| curva volume×tempo das dosadoras | ajuste com três medições, erro máximo, tensão e data | testada em software |
| correção de pH | alvo, banda morta, intervalo de avaliação, espera e pré-condições de nível/mistura | testada em software |
| receita de nutrientes | lote, estoque, capacidade e sequência CalMag/Micro/Bloom/Grow | testada em software |
| ajuste de EC | diluição limitada por capacidade, alvo e timeout absoluto | testada em software |
| mistura periódica | ciclo de 5 min a cada 20 min, inibido por nível/intertravamento | testada em software |
| fertirrigação | zero a cinco eventos diários, timezone, duração e bloqueios | testada em software |
| dreno | confirmação de boia, timeout de 8 min, pós-tempo e alarme retido | testada em software |
| umidificação | histerese, anti-ciclo, nível mínimo, vazamento e limites absolutos | testada em software |
| exaustão | temperatura/VPD, dois sensores, prioridade climática e confirmação de corrente/contato | testada em software; equipamento físico em HOLD |
| tomadas EKAZA | agenda, override, persistência, backoff, API e tela responsiva | implementada; homologação física em HOLD |
| comando versus resultado | modelos distintos de desejado, observado, confirmado, divergente e indisponível | implementado no domínio, API e painel |

## Adaptações deliberadas

- A elétrica das luminárias não foi copiada. As quatro cargas permanecem nas
  tomadas EKAZA existentes; somente o Raspberry Pi conversa com o Home Assistant.
- Nomes CalMag, Micro, Bloom e Grow identificam canais configuráveis. Eles não
  constituem recomendação agronômica nem valores de dose.
- O exaustor atual não foi tratado como PWM/0–10 V sem modelo e manual. A lógica
  entregue é liga/desliga e falha para ventilação ligada quando sensores críticos
  ficam indisponíveis.
- Interfaces de voz, dimerização, PPFD e reprodução visual literal do Lovelace
  não são copiadas. Segurança local, clareza de feedback e operação responsiva
  prevalecem sobre fidelidade estética.
- Nenhuma função testada somente em software está liberada para energizar carga
  real antes de protótipo, HIL, ensaio com água e comissionamento.

## Pendências que dependem do equipamento real

- identificar modelo/plaqueta e as quatro entidades `switch.*` das tomadas EKAZA;
- medir corrente, fator de potência e inrush de cada luminária e executar cem
  ciclos por canal;
- obter modelo, plaqueta, corrente de partida e tipo de comando do exaustor;
- comprovar builds ESP32, API, banco e painel no CI e depois no Raspberry Pi real;
- validar vazão, altura manométrica, volumes, contenção, ERC/DRC, HIL e piloto
  supervisionado apenas com água.

Fonte pública correspondente: [vídeo Parte 2](https://www.youtube.com/watch?v=XjcLWVci6_I)
e [código de referência do autor](https://github.com/ledgardener/gardenAutomation).
