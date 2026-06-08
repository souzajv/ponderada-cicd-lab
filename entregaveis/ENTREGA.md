# Folha de entrega — Ponderada CI/CD

Índice navegável e checklist de conformidade com o enunciado: [README principal § Conformidade](../README.md#conformidade)

## Links dos 7 entregáveis

| # | Item | Link |
|---|---|---|
| 1 | Repositório GitHub | https://github.com/souzajv/ponderada-cicd-lab |
| 2 | YAML do GitHub Actions | https://github.com/souzajv/ponderada-cicd-lab/blob/main/.github/workflows/ci.yml |
| 3 | Script de coleta | [coletar_metricas_pipeline.py](./coletar_metricas_pipeline.py) |
| 4 | Base CSV/JSON | [pipeline_metricas_limpo.csv](./dados/pipeline_metricas_limpo.csv) · [pipeline_metricas.json](./dados/pipeline_metricas.json) |
| 5 | Gráficos | [graficos/](./graficos/) (7 PNG) |
| 6 | Relatório técnico | [relatorio-tecnico.md](./relatorio-tecnico.md) |
| 7 | Reprodução | [reproducao.md](./reproducao.md) |

## Execuções do experimento (14 runs válidos)

Ver tabela completa em [experimento/VARIACOES.md](../experimento/VARIACOES.md).

| Variação | run_id | Status |
|---|---|---|
| 01 baseline | 27112464101 | success |
| 02 teste falhando | 27112466672 | failure |
| 09 sequencial | 27112486298 | success |
| 08 paralelo | 27112483564 | success |
| 11 falha lint | 27112491871 | failure |

## Reproduzir em um comando

```bash
cd entregaveis && pip install -r requirements-viz.txt && \
  GITHUB_TOKEN=$(gh auth token) python coletar_metricas_pipeline.py --repo souzajv/ponderada-cicd-lab && \
  python gerar_graficos_pipeline.py && python gerar_evidencias.py
```

## Decisão de engenharia para o G01

Com base no experimento: habilitar `app:test` no GitLab do g01 com **lint e test em paralelo** e **cache pip**; ganho estimado de ~12s por pipeline em projeto deste porte.
