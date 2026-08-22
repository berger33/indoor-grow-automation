# ADR 0004 — Faixa diária de commits da automação

- **Status:** aceito
- **Data:** 2026-08-22

## Contexto

As instruções operacionais trazem duas faixas: 15–50 commits por sessão na regra
central e 5–25 no loop diário. Cumprir literalmente ambas só é possível entre
15 e 25. Contagem não pode incentivar mudanças artificiais.

## Decisão

Usar 15–25 commits reais como alvo normal. Encerrar abaixo da faixa quando não
houver trabalho genuíno desbloqueado ou quando o portão de qualidade impedir
avanço. Nunca dividir artificialmente uma mudança nem fabricar commits.

## Consequências

- as duas instruções são atendidas quando existe trabalho suficiente;
- o diário registra a contagem real e a causa de qualquer exceção;
- segurança, coesão e testes continuam superiores à meta numérica.
