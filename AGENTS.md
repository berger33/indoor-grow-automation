# Instruções para agentes de desenvolvimento

Estas instruções se aplicam a todo o repositório.

## Fonte e ordem de trabalho

1. Sincronize `main` e leia `README.md`, `BACKLOG.md`, `DECISOES_PENDENTES.md`
   e o último bloco de `PROGRESS_LOG.md`.
2. Consulte `ESPECIFICACAO_REFERENCIA.md` antes de alterar comportamento de
   hardware, controle, painel ou instalação.
3. Escolha o item P0/P1 desbloqueado de maior prioridade.
4. Trabalhe em `codex/daily-AAAA-MM-DD`; nunca use outro repositório como alvo.
5. Se a tarefa não couber em algumas horas, decomponha-a no backlog primeiro.

## Ritmo e commits

- A faixa operacional é **15–25 commits reais por sessão**. Ela é a interseção
  segura entre as duas faixas fornecidas nas instruções originais (15–50 e
  5–25). Qualidade prevalece sobre contagem; não crie preenchimento.
- Use Conventional Commits em português e no imperativo.
- Um commit deve conter uma unidade coesa, teste correspondente quando houver
  comportamento e atualização do item do backlog.
- Registre o total real no diário; jamais arredonde para atingir meta.

## Portão obrigatório antes de cada commit

Execute:

```bash
python scripts/quality_gate.py
```

Não commite se compilação, testes, whitespace ou scan de segredos falhar. Não
adicione credenciais, nem mesmo em exemplos. Arquivos `.env.example` devem ter
somente nomes de variáveis e valores vazios.

Código de firmware só pode ser commitado quando o ambiente PlatformIO
correspondente compilar. Mudanças de painel devem incluir build e testes do
frontend assim que ele existir.

## Segurança e autonomia

- Prefira decisão simples e reversível e registre-a em `docs/adr/`.
- Registre compra, ligação elétrica, fabricação em lote e decisão comercial em
  `DECISOES_PENDENTES.md`; continue em tarefas não bloqueadas.
- Não enfraqueça timeout, limite de dose, intertravamento ou estado seguro para
  fazer um teste passar.
- Não copie código externo sem preservar licença e proveniência.
- Não faça push forçado, não apague histórico e não altere outros repositórios.

## Entrega da sessão

1. Reexecute o portão completo.
2. Atualize `CHANGELOG.md` e `PROGRESS_LOG.md`.
3. Faça push da branch diária e abra PR para `main`.
4. Só habilite merge quando a branch estiver atualizada e todos os checks
   obrigatórios estiverem verdes.
5. Relate bloqueios reais e os próximos 1–3 itens.

