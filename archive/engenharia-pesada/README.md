# Arquivo histórico — engenharia pesada

Este diretório preserva artefatos da arquitetura Rev A anterior. Eles foram
retirados do escopo ativo em 2026-08-25 quando o projeto migrou para uma estação
DIY simples, com notebook, ESP32, placa perfurada, relés e MOSFETs genéricos.

## Arquivado

| Caminho | Motivo |
|---|---|
| `desenhos/PRANCHA-*` | pranchas conceituais da arquitetura industrial |
| `desenhos/REV-A-*` | rack, painel, PCB, elétrica e implantação sob medida |
| `docs/hardware/rev-a/ARQUITETURA_FISICA.md` | layout de rack e tanques técnicos |
| `docs/hardware/rev-a/BASE_ELETRICA_127V.md` | painel com DR/DPS/contatores dedicados |
| `docs/hardware/rev-a/CADERNO_PRANCHAS.md` | índice dos desenhos Rev A |
| `docs/hardware/rev-a/LAUDO_REVISAO_REVA.md` | laudo preliminar da PCB/painel |
| `docs/adr/0005-*` | decisão antiga de painel CA/SELV |
| `docs/adr/0007-*` | decisão antiga do rack vertical sob medida |
| `docs/tutorial-industrial/` | tutorial antigo de montagem industrial |
| `docs/images-realistic/` | imagens conceituais da estação pesada |
| `hardware/controller-rev-a/netlist.csv` | netlist da PCB customizada |
| `hardware/controller-rev-a/pcb-parameters.json` | regras de fabricação/ERC/DRC |
| `firmware/nos-distribuidos/` | três nós ESP32 e saída por registrador serial |
| `firmware/shared/GrowAtlas.h` | interface Atlas EZO usada apenas pelo nó antigo |

## Regra de uso

Conteúdo arquivado serve somente para histórico e comparação. Não o utilize
para comprar componentes, fabricar placa, escolher pinagem, montar painel ou
energizar a estação atual. Os documentos ativos estão no `README.md`, em
`hardware/`, `firmware/controller/` e `docs/tutorial/`.
