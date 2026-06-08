# Hipóteses iniciais do experimento

Registro **antes** das 12+ execuções no GitHub Actions.

## H1 — Cache de dependências

**Hipótese:** habilitar cache pip reduz o tempo dos jobs `lint` e `test` em pelo menos 20%.

**Métrica:** comparar `job_duration` dos jobs de instalação+execução entre variações com `pip_cache=true` e `pip_cache=false`.

## H2 — Paralelismo de jobs

**Hipótese:** modo `parallel` reduz o `workflow_duration` para perto de `max(lint, test)`; modo `sequential` aproxima `lint + test`.

**Métrica:** `workflow_duration` por `run_id` com `execution_mode` anotado no artefato.

## H3 — Volume de testes

**Hipótese:** adicionar 15 testes rápidos aumenta a duração do job `test` de forma quase linear e previsível.

**Métrica:** scatter `test_count` × `workflow_duration`.

## H4 — Teste lento

**Hipótese:** um teste `@slow` com `sleep(3)` torna o job `test` o maior contribuinte do pipeline, independentemente do cache.

**Métrica:** proporção `job_duration(test*) / workflow_duration`.

## H5 — Falhas

**Hipótese:** falhas de lint e de teste são igualmente frequentes quando forçadas; na prática, lint falha mais cedo no modo sequencial.

**Métrica:** contagem de `status=failure` por `variation_label`.
