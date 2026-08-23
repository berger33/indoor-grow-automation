# Revisão dirigida — vídeo V1 de hardware (16:36)

- Arquivo revisado: `My DIY Home Assistant Garden Automation System — Pt.1 — Hardware`
- Duração verificada: 16:36
- Data da revisão dirigida: 2026-08-23
- Objetivo: confirmar o arranjo físico útil ao escopo de fertirrigação,
  irrigação e clima, sem importar a automação de iluminação.

Esta revisão complementa `ESPECIFICACAO_REFERENCIA.md`. Foram inspecionados o
vídeo completo, quadros em intervalos de 10 s e quadros de transições relevantes.
A resolução do anexo é 640 × 360; códigos que não ficam legíveis não foram
inferidos.

## Linha do tempo confirmada

| Tempo | Evidência visual/narrada útil | Decisão para o projeto próprio |
|---:|---|---|
| 00:00–00:47 | estação vertical com tablet, caixa das dosadoras, duas prateleiras de frascos e dois totes preto/amarelo | separar interface, dosagem e reservatórios em módulos identificáveis |
| 00:48–01:14 | alimentação por osmose reversa e linha azul de água | aceitar reservatório de origem cheio manualmente ou por entrada protegida; RO não é obrigatória |
| 01:15–01:34 | válvula solenoide na entrada e corte de água | usar válvula normalmente fechada e corte independente do software |
| 01:28–02:19 | tote superior, boia mecânica, tampa perfurada e tubulações | reservatório de origem de 50 L com limite alto físico e tampa removível |
| 01:40–02:19 | segundo recipiente/tote e circulação entre níveis | reservatório de mistura/rega de 50 L separado da água de origem |
| 02:20–02:49 | discos/plataforma sob o tote e passagem de sondas pela tampa | medir massa com plataforma de quatro células; suportes de sonda devem preservar imersão e manutenção |
| 02:35–03:15 | linhas de bomba e transferência/mistura | dimensionar cada bomba por vazão e altura reais, não pela aparência do vídeo |
| 03:16–03:43 | plataforma de pesagem sob reservatório | massa é a medição primária de volume; boias funcionam como limites independentes |
| 03:44–04:18 | seis cabeçotes peristálticos e seis frascos de concentrado em duas fileiras | adotar seis canais de 1 L, removíveis, etiquetados e calibrados individualmente |
| 04:19–05:00 | nós em protoboard dentro do cultivo | substituir protoboard/Dupont por PCB, conectores travados e nó local adequado à umidade |
| 05:01–05:29 | exaustor de duto, controlador e intervenção no comando | exaustor do usuário permanece liga/desliga até existir manual; 0–10 V só para modelo futuro comprovado |
| 05:30–06:12 | vasos, bandejas azuis de coleta, linhas de rega e dreno | documentar emissores, bandeja de contenção, retorno/dreno e timeout hidráulico |
| 05:40–06:11 | pequenos ventiladores/discos e linhas em recipientes auxiliares | manter agitação/umidificação como subsistemas separados e testáveis |
| 06:13–06:38 | umidificador ultrassônico caseiro e reposição de água | preferir módulo protegido contra nível baixo e comandado por interface isolada |
| 06:39–07:05 | iluminação do cultivo | observação histórica; completamente fora do escopo executável da v1.0 |
| 07:20–09:00 | retorno à estação e descrição do conjunto | preservar manutenção frontal e caminho de mangueiras visível |
| 09:10–10:06 | Raspberry Pi mostrado em mãos | hub local permanece Raspberry Pi, instalado em caixa seca e ventilada |
| 10:07–12:17 | gabinete aberto com fonte, controladores, relés, drivers e fiação densa | não copiar a fiação ponto a ponto; criar PCB, bornes, chicotes e segregação documentados |
| 12:18–14:35 | demonstração de relés, drivers, ESP32/Mega e distribuição | funções devem ter identificador, fusível/limite e estado seguro; a marca de módulos ilegíveis permanece aberta |
| 14:36–15:06 | chicote sob o reservatório e sensores no piso | usar quatro zonas de vazamento com retenção de alarme e teste periódico |
| 15:07–15:58 | mangueiras no painel, tomadas e sensores ambientais | aplicar laços de gotejamento, alívio de tração e separação entre zona molhada e quadro seco |
| 16:10–16:29 | tablet com comandos manuais e cabeçotes de bomba | painel final deve permitir teste individual temporizado e mostrar comando versus resultado físico |

## Inventário físico consolidado para a réplica

| Grupo | Quantidade-base | Observação de projeto |
|---|---:|---|
| Recipiente de concentrado | 6 × 1 L | cada linha recebe etiqueta nas duas extremidades e calibração própria |
| Bomba peristáltica | 6 | pH−, aditivos/nutrientes e pH+ são configuração, não receita fixa |
| Reservatório de água | 1 × 50 L | tampa, tara, limite alto e contenção secundária |
| Reservatório mistura/rega | 1 × 50 L | pesagem, mistura, sondas e limite contra transbordo |
| Bomba hidráulica | 4 funções | transferência, mistura, irrigação e dreno; modelos dependem de curva hidráulica |
| Válvula normalmente fechada | 2 funções | entrada/corte geral e transferência, sujeitas ao P&ID final |
| Plataforma de pesagem | 2 | quatro células por reservatório na configuração planejada |
| Sensor pH/EC/temperatura | 1 conjunto | canais isolados e compensação térmica validada |
| Sensor de vazamento | 4 zonas | fio rompido/ausência de heartbeat deve ser diagnosticável |
| Nó climático | 1 | temperatura, UR, VPD, CO₂ e temperatura foliar opcional |
| Exaustão | 1 | equipamento atual somente liga/desliga |
| Umidificação | 1 | com anti-ciclo, timeout e proteção contra operação a seco |
| Hub | 1 Raspberry Pi | banco, MQTT, API, painel, histórico e backup local |

## Adaptações deliberadas

- O vídeo usa totes comerciais de capacidade não legível. A réplica usa os dois
  volumes de 50 L confirmados pelo responsável, sem alegar equivalência de modelo.
- Os frascos vistos lembram potes de vidro. A seleção final exigirá tampa
  compatível, retenção de mangueira e resistência química; aparência não aprova
  material.
- Protoboards, Dupont, relés genéricos e tomadas Wi-Fi do protótipo não são
  copiados como solução final.
- A iluminação não integra software, hardware, BOM ou tutorial.
- O layout vertical é preservado como princípio, mas quadro e eletrônica ficam
  acima, lateralmente afastados e fora de qualquer caminho provável de vazamento.

## Pontos ainda não identificados no vídeo

- modelos e curvas das quatro bombas hidráulicas;
- capacidade nominal dos totes mostrados;
- diâmetros, materiais e comprimentos de todas as mangueiras;
- materiais das vedações das válvulas;
- massa nominal das células de carga e dimensões da plataforma;
- marcas/modelos legíveis de relés, drivers e módulos internos;
- potência e proteção de nível do umidificador ultrassônico;
- custo, consumo e precisão metrológica do conjunto.

Esses itens permanecem gates de engenharia e não devem ser preenchidos com um
produto apenas visualmente semelhante.
