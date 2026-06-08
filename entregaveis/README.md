# Entregáveis: métricas de pipeline CI/CD

Esta pasta reúne tudo o que a ponderada pede para entrega: dados coletados pela API, gráficos, relatório e instruções de reprodução. O experimento roda no GitHub Actions; a análise é feita offline a partir dos CSVs gerados.

Índice geral do repositório: [README principal](../README.md)  
Checklist de conformidade: [seção Conformidade](../README.md#conformidade)

## Mapa dos entregáveis (7 itens do enunciado)

| # | Entregável | Onde está |
|---|---|---|
| 1 | Link do repositório GitHub | https://github.com/souzajv/ponderada-cicd-lab |
| 2 | YAML do GitHub Actions | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |
| 3 | Script de coleta das métricas | [`coletar_metricas_pipeline.py`](./coletar_metricas_pipeline.py) |
| 4 | Base de dados CSV/JSON | Ver [Bases de dados](#bases-de-dados) abaixo |
| 5 | Gráficos produzidos | [`graficos/`](./graficos/) (7 PNG) |
| 6 | Relatório técnico | [`relatorio-tecnico.md`](./relatorio-tecnico.md) |
| 7 | Como reproduzir | [`reproducao.md`](./reproducao.md) |

## Documentos auxiliares

| Documento | Função |
|---|---|
| [`ENTREGA.md`](./ENTREGA.md) | Folha de entrega em uma página para o professor |
| [`experimento/VARIACOES.md`](../experimento/VARIACOES.md) | 14 runs com run_id, SHA e links reais |
| [`experimento/hipoteses.md`](../experimento/hipoteses.md) | Hipóteses registradas antes do experimento |
| [`evidencias/`](./evidencias/) | Painéis visuais que complementam os links do GitHub |

## Bases de dados

| Arquivo | Descrição |
|---|---|
| [`dados/pipeline_metricas_limpo.csv`](./dados/pipeline_metricas_limpo.csv) | **Principal para análise:** runs válidos, jobs sem `skipped` |
| [`dados/pipeline_steps.csv`](./dados/pipeline_steps.csv) | Duração por step (métrica de tempo de cada etapa) |
| [`dados/pipeline_metricas.csv`](./dados/pipeline_metricas.csv) | Dataset completo, incluindo runs inválidos de auditoria |
| [`dados/pipeline_metricas.json`](./dados/pipeline_metricas.json) | JSON consolidado com jobs e steps |
| [`dados/raw/run-*.json`](./dados/raw/) | Cache bruto da API GitHub |

O schema mínimo do enunciado está contido no CSV limpo, com colunas extras como `test_duration_avg_s`, `lead_time_s` e `artifact_size_bytes`.

## Scripts

| Script | Função |
|---|---|
| [`coletar_metricas_pipeline.py`](./coletar_metricas_pipeline.py) | Consulta a API GitHub e gera CSV/JSON (obrigatório) |
| [`gerar_graficos_pipeline.py`](./gerar_graficos_pipeline.py) | 4 gráficos obrigatórios e 3 extras |
| [`gerar_evidencias.py`](./gerar_evidencias.py) | Painéis visuais de evidência |

Dependências de visualização: [`requirements-viz.txt`](./requirements-viz.txt)

## Gráficos

### Obrigatórios (enunciado)

| Arquivo | Conteúdo |
|---|---|
| [`01_tempo_total_por_execucao.png`](./graficos/01_tempo_total_por_execucao.png) | Tempo total por run |
| [`02_tempo_por_job.png`](./graficos/02_tempo_por_job.png) | Tempo por job |
| [`03_taxa_sucesso_falha.png`](./graficos/03_taxa_sucesso_falha.png) | Taxa sucesso/falha |
| [`04_testes_vs_duracao.png`](./graficos/04_testes_vs_duracao.png) | Testes por duração |

### Extras

| Arquivo | Conteúdo |
|---|---|
| [`05_cache_on_vs_off.png`](./graficos/05_cache_on_vs_off.png) | Comparação de cache |
| [`06_lead_time_por_run.png`](./graficos/06_lead_time_por_run.png) | Lead time |
| [`07_steps_breakdown.png`](./graficos/07_steps_breakdown.png) | Steps mais lentos |

## Reproduzir coleta, gráficos e evidências

```bash
cd entregaveis
pip install -r requirements-viz.txt
python coletar_metricas_pipeline.py --repo souzajv/ponderada-cicd-lab
python gerar_graficos_pipeline.py
python gerar_evidencias.py
```

Detalhes completos em [`reproducao.md`](./reproducao.md).
