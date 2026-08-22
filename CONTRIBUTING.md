# Como contribuir

Este projeto controla equipamentos próximos a água, fertilizantes e energia.
Contribuições devem ser pequenas, verificáveis e preservar o estado seguro dos
atuadores mesmo quando rede, sensores ou hub falharem.

## Fluxo de branches

- `main` é protegida conceitualmente e deve permanecer executável.
- O trabalho parte do `main` atualizado em uma branch curta.
- Use `codex/<tema>` para trabalho autônomo e `feat/<tema>`, `fix/<tema>`,
  `docs/<tema>` ou `chore/<tema>` para contribuições humanas.
- Uma branch atende a um objetivo coeso e é removida após o merge.
- Mudanças entram por pull request com o portão de qualidade aprovado.

Não faça force-push em `main`. Rebase ou atualize uma branch de trabalho antes
da revisão quando houver conflito.

## Commits

Use Conventional Commits no imperativo:

```text
feat(ph-sensor): adiciona média móvel configurável
fix(fertirrigacao): limita tempo máximo da bomba
test(clima): cobre timeout do sensor de umidade
docs(instalacao): descreve aterramento do gabinete
```

Cada commit deve representar uma unidade completa, testável e de valor próprio.
Não agrupe módulos sem relação e não crie commits apenas para aumentar a contagem.

## Verificação obrigatória

Antes de cada commit:

```bash
python scripts/quality_gate.py
```

O comando verifica whitespace, compilação Python, testes e segredos. Código com
comportamento novo deve incluir teste automatizado. Credenciais pertencem apenas
ao ambiente local; exemplos usam nomes de variáveis sem valores sensíveis.

## Pull requests

O autor deve:

1. relacionar a mudança a um item granular do `BACKLOG.md`;
2. explicar comportamento, limites e modo de falha;
3. anexar evidências sanitizadas de teste;
4. atualizar documentação e changelog quando aplicável;
5. solicitar validação física para mudanças elétricas, hidráulicas ou de PCB.

O merge recomendado é **squash** quando a branch contiver ajustes intermediários.
Commits já atômicos podem ser preservados com rebase merge. Merge commits sem
necessidade devem ser evitados.

## Política de releases

O projeto usa versionamento semântico (`MAJOR.MINOR.PATCH`):

- `PATCH`: correção compatível e sem alteração de contrato público;
- `MINOR`: funcionalidade compatível ou novo hardware opcional;
- `MAJOR`: quebra de API, tópicos MQTT, configuração ou compatibilidade elétrica.

Até a validação integral da Fase 5, versões são `0.y.z`. Candidatas a v1.0 usam
tags `v1.0.0-rc.N`. Uma release estável exige, no mínimo:

- CI aprovada no commit exato da tag;
- changelog e notas de migração atualizados;
- inventário de dependências e licenças;
- procedimento de instalação reproduzido do zero;
- testes de integração, HIL e comissionamento supervisionado;
- ausência de decisões físicas P0 pendentes.

Tags seguem `vMAJOR.MINOR.PATCH` e são criadas somente a partir de `main`. Uma
release não é promovida automaticamente quando envolve compra, fabricação ou
validação de cargas reais.

## Segurança e relato responsável

Desenergize cargas e coloque atuadores em estado seguro antes de testar. Não
publique vulnerabilidades exploráveis, dados de rede ou credenciais em issues.
Use o canal privado de segurança do GitHub quando estiver habilitado; até lá,
abra apenas um relato sem detalhes operacionais e aguarde contato do mantenedor.
