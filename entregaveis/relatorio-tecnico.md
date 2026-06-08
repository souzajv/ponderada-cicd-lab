# Relatório técnico — Métricas de Pipeline CI/CD

**Projeto:** ponderada-cicd-lab (mini Analyzer inspirado no G01 — Jacto Drones OS)  
**Autor:** João Victor Souza (souzajv)  
**Data do experimento:** 2026-06-08  
**Repositório:** https://github.com/souzajv/ponderada-cicd-lab  
**Workflow:** https://github.com/souzajv/ponderada-cicd-lab/blob/main/.github/workflows/ci.yml

---

## 1. Objetivo

Construir um experimento prático para medir e analisar o comportamento de um pipeline
CI/CD real no **GitHub Actions**, coletando métricas via script Python (API REST),
gerando gráficos e produzindo análise crítica sobre desempenho, estabilidade e gargalos.

Diferente da abordagem de telemetria de voo (simulador PX4), este experimento foca
**exclusivamente no processo de integração contínua**.

## 2. Arquitetura do pipeline

```
push / workflow_dispatch
        │
        ▼
    ┌────────┐
    │ setup  │  lê ci-mode.json → execution_mode, cache, flags de falha
    └────┬───┘
         │
    ┌────┴────────────────────────────────────┐
    │                                         │
 parallel / sequential / inverted             │
    │                                         │
    ▼                                         ▼
 lint ──► test_sequential          test_inverted ──► lint_inverted
    │         (modo sequencial)         (ordem invertida)
    │
    └──► test_parallel (modo paralelo, sem needs em lint)
         │
         ▼
    artefato pipeline-metrics-{run_id}
    (junit.xml + run-metrics.json)
         │
         ▼
 coletar_metricas_pipeline.py → CSV/JSON → gerar_graficos_pipeline.py
```

## 3. Metodologia

1. **Projeto base:** mini-analyzer Python com pytest + ruff (tema alinhado ao módulo G01).
2. **Pipeline:** jobs `setup`, `lint`, `test_*`, `report` com instrumentação de artefatos.
3. **14 execuções reais** documentadas em [`experimento/VARIACOES.md`](../experimento/VARIACOES.md).
4. **Coleta automatizada:** [`coletar_metricas_pipeline.py`](./coletar_metricas_pipeline.py) consulta a API do GitHub (`gh auth token`).
5. **Visualização:** 4 gráficos PNG em [`graficos/`](./graficos/).

### Evidências (links reais)

| Variação | run_id | Link |
|---|---|---|
| Baseline verde | 27112464101 | https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112464101 |
| Teste falhando | 27112466672 | https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112466672 |
| Jobs paralelos | 27112483564 | https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112483564 |
| Jobs sequenciais | 27112486298 | https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112486298 |
| Cache off | 27112480695 | https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112480695 |
| Teste lento | 27112474712 | https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112474712 |

Base de dados: [`dados/pipeline_metricas.csv`](./dados/pipeline_metricas.csv) (95 linhas, 20 runs).

---

## 4. Respostas às perguntas de análise

### 4.1 Qual etapa mais contribuiu para o tempo total do pipeline?

Nos runs em modo **paralelo** (ex.: run `27112464101`), os jobs `lint` (~12s) e
`test_parallel` (~12s) dominam o tempo; o `workflow_duration` (~22s) ≈ `max(lint, test)`
+ overhead do `setup` (~4s).

No modo **sequencial** (run `27112486298`), `workflow_duration` = **34s** ≈ `setup` (4s)
+ `lint` (9s) + `test_sequential` (13s).

No modo **invertido** (run `27112489037`), o tempo subiu para **45s** porque `test_inverted`
(16s) e `lint_inverted` (13s) executam em série após o setup.

**Conclusão:** a etapa de **testes** e a de **instalação+lint** são os maiores
contribuintes; em paralelo, quem manda é o job mais lento entre os dois.

### 4.2 Houve diferença significativa entre execuções com e sem cache?

Comparando runs consecutivos:

| Variação | pip_cache | workflow_duration | lint | test_parallel |
|---|---|---|---|---|
| 06-cache-on | true | 24s | 14s | 14s |
| 07-cache-off | false | 26s | 15s | 17s |

Diferença observada: **~2s no total** (~8%), bem abaixo da hipótese inicial de 20%
([`experimento/hipoteses.md`](../experimento/hipoteses.md)). O projeto é pequeno e o
`pip install` é rápido mesmo sem cache; o ganho do cache pip fica diluído no tempo
de checkout e setup do runner.

### 4.3 O paralelismo reduziu o tempo total? Em que condições?

| Modo | run_id | workflow_duration |
|---|---|---|
| parallel | 27112483564 | **22s** |
| sequential | 27112486298 | **34s** |
| inverted | 27112489037 | **45s** |

O paralelismo reduziu ~**35%** em relação ao sequencial, confirmando H2. Porém, quando
o teste lento está habilitado (run `27112474712`, 27s), o job `test_parallel` passa a
ser o gargalo e o ganho do paralelismo entre lint e test fica menos perceptível no
tempo total.

### 4.4 Quais falhas foram mais frequentes?

Das 20 runs coletadas (incluindo tentativas inválidas):

- **failure:** 14 runs (12 inválidos de YAML + 2 variações intencionais)
- **success:** 6 runs válidos na primeira leva + 14 na segunda ≈ **86% de sucesso**
  nas execuções funcionais

Falhas intencionais e esperadas:

1. **Teste** (variação 02, run `27112466672`): `test_failures=1`, `status=failure`
2. **Lint** (variação 11, run `27112491871`): job `lint` falhou em 11s antes dos testes
   sequenciais

### 4.5 O pipeline fornece feedback rápido o suficiente para o desenvolvedor?

Runs verdes ficaram entre **22s e 34s** (paralelo vs sequencial). Para um projeto
acadêmico pequeno, isso é aceitável. Em modo sequencial com lint falhando (var. 11),
o feedback de lint chega em **~16s** (setup + lint), antes de gastar tempo em testes —
comportamento desejável para fail-fast.

### 4.6 Que melhorias poderiam ser feitas no pipeline?

1. **Unificar jobs de teste** em um único job parametrizado (menos ruído na API de jobs).
2. **Cache de `.pytest_cache`** além do pip, para suítes maiores.
3. **Fail-fast global:** em modo sequencial, não agendar `test` se `lint` falhar (hoje
   `test_sequential` ainda aparece como skipped/failure na API).
4. **Publicar `run-metrics.json` sempre**, inclusive em falhas de lint (hoje var. 11 não
   gerou `variation_label` no artefato).
5. **Matrix strategy** para Python 3.11/3.12 se o analyzer crescer.

### 4.7 Quais limitações existem nos dados coletados?

- Granularidade de **step** dentro do job não foi exportada com precisão (só duração de job).
- Jobs **skipped** aparecem na API com duração 0s ou -1s, poluindo o CSV.
- Artefatos expiram em 90 dias; a coleta local foi feita no mesmo dia.
- Runners `ubuntu-latest` compartilhados introduzem variância (ex.: cache on 24s vs off 26s).
- As 12 primeiras execuções inválidas (0s) entraram na base e precisam ser filtradas
  em análises futuras (`workflow_duration = 0`).

### 4.8 Como essa análise poderia apoiar decisões de engenharia?

- **Manter lint e test em paralelo** neste projeto: economia de ~12s por push.
- **Investir em cache** só compensa quando dependências ou build crescerem; hoje o ROI é baixo.
- **Ordem invertida (test antes de lint)** não se justifica: aumenta latência sem ganho
  de qualidade no nosso fluxo.
- **Métricas DORA:** com lead time de ~25s (commit → pipeline verde em modo paralelo),
  o time tem feedback rápido para corrigir falhas (var. 02 → 03 em um push).

---

## 5. Resultados inesperados

### Inesperado 1 — Primeira leva com 0s e zero jobs

As 12 execuções iniciais (runs `27112372624` … `27112402416`) falharam instantaneamente
sem executar nenhum job. Causa: **composite action local** referenciada de forma inválida
no YAML original. Após simplificar o workflow (commit `846b08a`), todas as variações
passaram a executar normalmente.

**Lição:** validar o workflow com `gh workflow view` e uma execução canário antes da
bateria de experimentos.

### Inesperado 2 — Cache pip quase não impactou

A hipótese H1 previa ≥20% de redução; medimos ~8%. O motivo provável é o tamanho reduzido
de `requirements-dev.txt` e a velocidade dos runners GitHub para `pip install` de poucos
pacotes.

### Inesperado 3 — Modo invertido mais lento que sequencial padrão

Esperava-se que inverter lint/test não piorasse tanto; observamos **45s** vs **34s** porque
ambos os jobs pesados rodam em série e o lint invertido só inicia após o test terminar,
sem sobreposição.

---

## 6. Hipótese inicial vs resultado observado

| Hipótese | Previsto | Observado | Veredito |
|---|---|---|---|
| H1 Cache reduz ≥20% | lint+test muito mais rápidos | ~8% (2s) | **Rejeitada** no contexto atual |
| H2 Paralelo ≈ max(lint,test) | ~22s | 22s (run 08) | **Confirmada** |
| H3 Mais testes = linear | aumento proporcional | 22 testes, ~12s | **Parcial** (suite ainda pequena) |
| H4 Teste lento domina | test >> lint | test 15s vs lint 13s (run 05) | **Parcial** |
| H5 Lint falha antes do test (sequencial) | fail-fast | lint falhou, test não rodou (run 11) | **Confirmada** |

---

## 7. Gráficos gerados

![Tempo total por execução](./graficos/01_tempo_total_por_execucao.png)

![Tempo por job](./graficos/02_tempo_por_job.png)

![Taxa sucesso/falha](./graficos/03_taxa_sucesso_falha.png)

![Testes vs duração](./graficos/04_testes_vs_duracao.png)

---

## 8. Comparação com entrega de referência (colega — G01)

| Aspecto | Colega (`feat/ponderada-metricas`) | Esta entrega |
|---|---|---|
| Objeto | Telemetria de voo (NDJSON) | Métricas de pipeline CI/CD |
| Plataforma | GitLab CI | GitHub Actions |
| Coleta | Parse de arquivo local | API GitHub + artefatos |
| Gráficos | Altitude, bateria, atitude | Tempo, jobs, sucesso, testes×duração |

Abordagens distintas, sem sobreposição de domínio ou código de entrega.

---

## 9. Reprodução

Passo a passo em [`reproducao.md`](./reproducao.md).
