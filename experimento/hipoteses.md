# Hipóteses iniciais do experimento

Este registro foi escrito **antes** das 12 ou mais execuções no GitHub Actions. As hipóteses orientam o que medir e o que comparar depois que os dados chegam.

## H1. Cache de dependências

**Hipótese:** habilitar cache pip reduz o tempo dos jobs `lint` e `test` em pelo menos 20%.

**Métrica:** comparar `job_duration` dos jobs de instalação e execução entre variações com `pip_cache=true` e `pip_cache=false`.

## H2. Paralelismo de jobs

**Hipótese:** o modo `parallel` reduz o `workflow_duration` para perto de `max(lint, test)`; o modo `sequential` aproxima a soma `lint + test`.

**Métrica:** `workflow_duration` por `run_id`, com `execution_mode` anotado no artefato.

## H3. Volume de testes

**Hipótese:** adicionar 15 testes rápidos aumenta a duração do job `test` de forma quase linear e previsível.

**Métrica:** relação entre `test_count` e `workflow_duration` (scatter).

## H4. Teste lento

**Hipótese:** um teste `@slow` com `sleep(3)` torna o job `test` o maior contribuinte do pipeline, independentemente do cache.

**Métrica:** proporção `job_duration(test*) / workflow_duration`.

## H5. Falhas

**Hipótese:** falhas de lint e de teste são igualmente frequentes quando forçadas; na prática, o lint falha mais cedo no modo sequencial.

**Métrica:** contagem de `status=failure` por `variation_label`.
