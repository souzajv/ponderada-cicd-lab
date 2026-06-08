# Entregáveis — Métricas de Pipeline CI/CD

Experimento individual de métricas de processo com **GitHub Actions**.

## Mapa dos entregáveis

| # | Entregável | Onde está |
|---|---|---|
| 1 | Link do repositório GitHub | https://github.com/souzajv/ponderada-cicd-lab |
| 2 | YAML do GitHub Actions | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |
| 3 | Script de coleta | [`coletar_metricas_pipeline.py`](./coletar_metricas_pipeline.py) |
| 4 | Base CSV/JSON | [`dados/pipeline_metricas.csv`](./dados/pipeline_metricas.csv) |
| 5 | Gráficos | [`graficos/`](./graficos/) |
| 6 | Relatório técnico | [`relatorio-tecnico.md`](./relatorio-tecnico.md) |
| 7 | Reprodução | [`reproducao.md`](./reproducao.md) |

## Reproduzir coleta e gráficos

```bash
cd entregaveis
pip install -r requirements-viz.txt
python coletar_metricas_pipeline.py --repo <owner>/ponderada-cicd-lab
python gerar_graficos_pipeline.py
```
