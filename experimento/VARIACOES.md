# Variações controladas do experimento

Cada linha corresponde a um commit que altera `ci-mode.json` e/ou o código.
Após publicar no GitHub, preencher `run_id` e `commit_sha` reais.

| # | variation_label | execution_mode | pip_cache | run_slow_tests | force_test_failure | force_lint_failure | commit_message sugerida | run_id | commit_sha | status |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 01-baseline-verde | parallel | true | false | false | false | feat: baseline verde do experimento | | | |
| 02 | 02-teste-falhando | parallel | true | false | true | false | test: forcar falha de teste | | | |
| 03 | 03-correcao-teste | parallel | true | false | false | false | fix: remover falha forcada de teste | | | |
| 04 | 04-mais-testes | parallel | true | false | false | false | test: ampliar suite com 15 casos | | | |
| 05 | 05-teste-lento | parallel | true | true | false | false | test: habilitar teste lento | | | |
| 06 | 06-cache-on | parallel | true | false | false | false | ci: cache pip habilitado | | | |
| 07 | 07-cache-off | parallel | false | false | false | false | ci: cache pip desabilitado | | | |
| 08 | 08-paralelo | parallel | true | false | false | false | ci: jobs lint e test em paralelo | | | |
| 09 | 09-sequencial | sequential | true | false | false | false | ci: test depende de lint | | | |
| 10 | 10-ordem-invertida | inverted | true | false | false | false | ci: lint apos testes | | | |
| 11 | 11-falha-lint | sequential | true | false | false | true | ci: falha intencional de lint | | | |
| 12 | 12-artefato-grande | parallel | true | false | false | false | ci: relatorio extra no artefato | | | |
| 13 | dispatch-paralelo | dispatch-parallel | parallel | true | false | false | workflow_dispatch manual | | | |
| 14 | dispatch-sequencial | dispatch-sequential | sequential | true | false | false | workflow_dispatch manual | | | |

## Como aplicar cada variação

1. Editar [`ci-mode.json`](../ci-mode.json) conforme a linha.
2. Se a variação exigir mudança de código (ex.: #04 já inclui `tests/test_variacoes.py`), commitar junto.
3. `git push origin main` e aguardar o workflow.
4. Copiar `run_id` da URL: `https://github.com/<owner>/ponderada-cicd-lab/actions/runs/<run_id>`.
