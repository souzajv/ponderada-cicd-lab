# ponderada-cicd-lab

Experimento de **métricas de pipeline CI/CD** com GitHub Actions, inspirado no
Analyzer Service do projeto G01 (Jacto Drones OS).

## Objetivo

Medir e analisar desempenho, estabilidade e gargalos de um pipeline real com:

- instalação de dependências
- lint (ruff)
- testes automatizados (pytest)
- geração de artefatos (`junit.xml`, `run-metrics.json`)
- coleta via script Python consultando a API do GitHub

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `src/analyzer/` | Mini-motor de análise de telemetria |
| `tests/` | Suíte pytest com variações controladas |
| `.github/workflows/` | Pipeline instrumentado |
| `experimento/` | Registro das 12+ variações |
| `entregaveis/` | Scripts de coleta, gráficos e relatório |

## Uso local

```bash
pip install -r requirements-dev.txt
ruff check src tests
pytest -m "not slow" -v
```

## Modo do experimento

O arquivo [`ci-mode.json`](ci-mode.json) controla cada execução:

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

## Entregáveis

Ver [`entregaveis/README.md`](entregaveis/README.md).
