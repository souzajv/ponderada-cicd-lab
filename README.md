# ponderada-cicd-lab

![CI Pipeline Metrics Experiment](https://github.com/souzajv/ponderada-cicd-lab/actions/workflows/ci.yml/badge.svg)

Este repositório documenta um experimento individual de métricas de pipeline CI/CD com GitHub Actions. O código base é um mini-projeto inspirado no [Analyzer Service](src/analyzer/) do Kombi, o projeto do grupo G01 (Jacto Drones OS).

**Autor:** João Victor Souza (`souzajv`)  
**Curso:** Engenharia de Software, INTELI (ESMD10)

## Índice

- [Início rápido para o professor](#inicio-rapido)
- [Conformidade com o enunciado](#conformidade)
- [Entregáveis obrigatórios (7 itens)](#entregaveis)
- [Métricas coletadas](#metricas)
- [Variações do experimento (14 runs)](#variacoes)
- [Gráficos e evidências](#graficos)
- [Relatório e análise](#relatorio)
- [Como reproduzir](#reproducao)
- [Estrutura do repositório](#estrutura)
- [Projeto de código (mini-analyzer)](#codigo)

## Início rápido para o professor

Se você vai corrigir a entrega, estes links levam direto ao que importa.

| O que você precisa | Link direto |
|---|---|
| Folha de entrega (1 página) | [entregaveis/ENTREGA.md](entregaveis/ENTREGA.md) |
| Relatório técnico completo | [entregaveis/relatorio-tecnico.md](entregaveis/relatorio-tecnico.md) |
| Tabela de execuções reais (run_id, SHA, status) | [experimento/VARIACOES.md](experimento/VARIACOES.md) |
| Dados para análise (CSV limpo) | [entregaveis/dados/pipeline_metricas_limpo.csv](entregaveis/dados/pipeline_metricas_limpo.csv) |
| Pipeline no GitHub Actions | [Actions](https://github.com/souzajv/ponderada-cicd-lab/actions) |

## Conformidade com o enunciado

A seção a seguir resume, item a item, como a entrega atende ao que foi pedido. Cada linha aponta para evidência verificável no repositório.

### Tarefa: pipeline GitHub Actions

| Requisito | Status | Evidência |
|---|---|---|
| Instalação de dependências | OK | `pip install -r requirements-dev.txt` em todos os jobs ([ci.yml](.github/workflows/ci.yml)) |
| Lint / análise estática | OK | `ruff check src tests` |
| Testes automatizados | OK | `pytest` + `junit.xml` + cobertura |
| Geração de artefato | OK | `pipeline-metrics-{run_id}` e `pipeline-report-{run_id}` |
| Coleta de métricas no pipeline | OK | `export_run_metrics.py`, `export_lint_metadata.py`, job `report` |
| >= 12 execuções com variações | OK (14) | [VARIACOES.md](experimento/VARIACOES.md) |

### Variações controladas (exemplos do enunciado)

| Variação pedida | Label no experimento | run_id (exemplo) |
|---|---|---|
| Teste passando | `01-baseline-verde` | [27112464101](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112464101) |
| Teste falhando | `02-teste-falhando` | [27112466672](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112466672) |
| Mais testes | `04-mais-testes` | [27112472129](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112472129) |
| Teste lento | `05-teste-lento` | [27112474712](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112474712) |
| Cache ON / OFF | `06-cache-on` / `07-cache-off` | [27112477570](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112477570) / [27112480695](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112480695) |
| Jobs paralelos | `08-paralelo` | [27112483564](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112483564) |
| Jobs sequenciais | `09-sequencial` | [27112486298](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112486298) |
| Ordem dos jobs invertida | `10-ordem-invertida` | [27112489037](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112489037) |
| Falha de lint | `11-falha-lint` | [27112491871](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112491871) |

### Métricas mínimas coletadas

| Métrica (enunciado) | Campo / arquivo |
|---|---|
| Tempo total do workflow | `workflow_duration` em [pipeline_metricas_limpo.csv](entregaveis/dados/pipeline_metricas_limpo.csv) |
| Tempo de cada job | `job_name`, `job_duration` |
| Tempo de cada etapa (step) | [pipeline_steps.csv](entregaveis/dados/pipeline_steps.csv) |
| Status (sucesso/falha) | `status` |
| Quantidade de testes | `test_count` |
| Testes com falha | `test_failures` |
| Tempo médio dos testes | `test_duration_avg_s` |
| Número do commit | `commit_sha` |
| Data e hora | `timestamp` |
| Mensagem do commit | `commit_message` |
| *Opcional:* lead time | `lead_time_s` |
| *Opcional:* tamanho artefatos | `artifact_size_bytes` |

O schema mínimo do enunciado (`run_id,commit_sha,commit_message,status,workflow_duration,job_name,job_duration,test_count,test_failures,timestamp`) está contido no CSV limpo.

### Parte de codificação e visualização

| Requisito | Status | Arquivo |
|---|---|---|
| Script Python consultando API GitHub | OK | [coletar_metricas_pipeline.py](entregaveis/coletar_metricas_pipeline.py) |
| Base CSV/JSON (não cópia manual) | OK | [dados/](entregaveis/dados/) |
| 4 gráficos obrigatórios | OK | [graficos/01 a 04](entregaveis/graficos/) |
| 8 perguntas de análise no relatório | OK | [relatorio-tecnico.md §4](entregaveis/relatorio-tecnico.md) |

### Relatório: requisitos obrigatórios

| Requisito | Onde |
|---|---|
| Prints ou links das execuções | Links em [VARIACOES.md](experimento/VARIACOES.md) e [evidencias/](entregaveis/evidencias/) |
| IDs reais dos workflows | Coluna `run_id` no CSV e tabela VARIACOES |
| Commits reais | Coluna `commit_sha` e `git log` |
| Explicação das variações | [VARIACOES.md](experimento/VARIACOES.md) e [ci-mode.json](ci-mode.json) |
| Gráficos a partir dos dados coletados | [graficos/](entregaveis/graficos/) |
| >= 2 resultados inesperados | [relatorio §6](entregaveis/relatorio-tecnico.md) |
| Hipótese vs observado | [hipoteses.md](experimento/hipoteses.md) e [relatorio §7](entregaveis/relatorio-tecnico.md) |
| Limitações do experimento | [relatorio §4.7](entregaveis/relatorio-tecnico.md) |

## Entregáveis obrigatórios (7 itens)

| # | Entregável | Link |
|---|---|---|
| 1 | Repositório GitHub | https://github.com/souzajv/ponderada-cicd-lab |
| 2 | YAML do GitHub Actions | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) e [no GitHub](https://github.com/souzajv/ponderada-cicd-lab/blob/main/.github/workflows/ci.yml) |
| 3 | Script de coleta das métricas | [entregaveis/coletar_metricas_pipeline.py](entregaveis/coletar_metricas_pipeline.py) |
| 4 | Base de dados CSV/JSON | [pipeline_metricas_limpo.csv](entregaveis/dados/pipeline_metricas_limpo.csv), [pipeline_steps.csv](entregaveis/dados/pipeline_steps.csv), [pipeline_metricas.json](entregaveis/dados/pipeline_metricas.json) |
| 5 | Gráficos produzidos | [entregaveis/graficos/](entregaveis/graficos/) |
| 6 | Relatório técnico Markdown | [entregaveis/relatorio-tecnico.md](entregaveis/relatorio-tecnico.md) |
| 7 | Como reproduzir o experimento | [entregaveis/reproducao.md](entregaveis/reproducao.md) |

O índice detalhado dos entregáveis está em [entregaveis/README.md](entregaveis/README.md).

## Métricas coletadas

Depois que o pipeline roda no GitHub, a coleta acontece pela API REST, usando o token do `gh auth token`.

```bash
cd entregaveis
pip install -r requirements-viz.txt
python coletar_metricas_pipeline.py --repo souzajv/ponderada-cicd-lab
```

| Arquivo | Uso |
|---|---|
| `pipeline_metricas_limpo.csv` | **Análise principal** (runs válidos, sem jobs skipped) |
| `pipeline_metricas.csv` | Dataset completo para auditoria |
| `pipeline_steps.csv` | Duração por step dentro de cada job |
| `dados/raw/run-*.json` | Cache bruto da API |

Scripts auxiliares: [gerar_graficos_pipeline.py](entregaveis/gerar_graficos_pipeline.py) e [gerar_evidencias.py](entregaveis/gerar_evidencias.py).

## Variações do experimento (14 runs)

Cada variação é controlada por [ci-mode.json](ci-mode.json) e pelo script [aplicar_variacao.py](scripts/aplicar_variacao.py). A documentação completa das execuções está em [experimento/VARIACOES.md](experimento/VARIACOES.md). As hipóteses registradas antes do experimento estão em [experimento/hipoteses.md](experimento/hipoteses.md).

## Gráficos e evidências

### Gráficos obrigatórios (enunciado)

| # | Gráfico | Arquivo |
|---|---|---|
| 1 | Tempo total do pipeline por execução | [01_tempo_total_por_execucao.png](entregaveis/graficos/01_tempo_total_por_execucao.png) |
| 2 | Tempo por job ou etapa | [02_tempo_por_job.png](entregaveis/graficos/02_tempo_por_job.png) |
| 3 | Taxa de sucesso e falha | [03_taxa_sucesso_falha.png](entregaveis/graficos/03_taxa_sucesso_falha.png) |
| 4 | Testes por duração do pipeline | [04_testes_vs_duracao.png](entregaveis/graficos/04_testes_vs_duracao.png) |

### Gráficos extras

| # | Gráfico | Arquivo |
|---|---|---|
| 5 | Cache ON vs OFF | [05_cache_on_vs_off.png](entregaveis/graficos/05_cache_on_vs_off.png) |
| 6 | Lead time por run | [06_lead_time_por_run.png](entregaveis/graficos/06_lead_time_por_run.png) |
| 7 | Breakdown por step | [07_steps_breakdown.png](entregaveis/graficos/07_steps_breakdown.png) |

### Evidências visuais

O enunciado aceita prints ou links. Esta entrega inclui os dois: links reais de cada execução em [VARIACOES.md](experimento/VARIACOES.md) e painéis visuais gerados a partir da API em [entregaveis/evidencias/](entregaveis/evidencias/).

## Relatório e análise

| Documento | Conteúdo |
|---|---|
| [relatorio-tecnico.md](entregaveis/relatorio-tecnico.md) | Análise completa: 8 perguntas, DORA, inesperados, hipóteses, limitações |
| [ENTREGA.md](entregaveis/ENTREGA.md) | Folha resumo para correção rápida |

O relatório inclui fundamentação em **Martin Fowler** (CI, Deployment Pipeline, Test Pyramid) mapeada às evidências do experimento. Veja a [seção 10 do relatório](entregaveis/relatorio-tecnico.md#10-fundamentação-teórica-martin-fowler).

## Como reproduzir

O passo a passo detalhado está em [entregaveis/reproducao.md](entregaveis/reproducao.md). Em resumo:

```bash
git clone https://github.com/souzajv/ponderada-cicd-lab.git
cd ponderada-cicd-lab/entregaveis
pip install -r requirements-viz.txt
GITHUB_TOKEN=$(gh auth token) python coletar_metricas_pipeline.py --repo souzajv/ponderada-cicd-lab
python gerar_graficos_pipeline.py
python gerar_evidencias.py
```

## Estrutura do repositório

| Pasta / arquivo | Conteúdo |
|---|---|
| [`src/analyzer/`](src/analyzer/) | Mini-motor de análise de telemetria (tema G01) |
| [`tests/`](tests/) | Suíte pytest com variações controladas |
| [`.github/workflows/`](.github/workflows/) | Pipeline instrumentado |
| [`experimento/`](experimento/) | Variações, hipóteses e evidências do experimento |
| [`entregaveis/`](entregaveis/) | Coleta, gráficos, relatório e dados |
| [`ci-mode.json`](ci-mode.json) | Configuração de cada variação |
| [`scripts/`](scripts/) | Automação (coleta CI, variações, export) |

## Projeto de código (mini-analyzer)

Para validar o código localmente antes de subir uma variação:

```bash
pip install -r requirements-dev.txt
ruff check src tests
pytest -m "not slow" -v
```

O modo do experimento é definido em [ci-mode.json](ci-mode.json):

```json
{
  "execution_mode": "parallel",
  "pip_cache": true,
  "run_slow_tests": false,
  "force_test_failure": false,
  "force_lint_failure": false,
  "variation_label": "01-baseline-verde"
}
```

## Diferenciação

Este experimento mede métricas de pipeline CI/CD no GitHub Actions. O foco é distinto de abordagens centradas em telemetria de voo ou em outras plataformas de CI.
