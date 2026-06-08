# Como reproduzir o experimento

Índice geral e mapa de entregáveis: [README principal](../README.md)

## Pré-requisitos

- Conta GitHub com Actions habilitado
- [GitHub CLI](https://cli.github.com/) autenticado (`gh auth login`)
- Python 3.11+
- Git

## 1. Clonar o repositório

```bash
git clone https://github.com/souzajv/ponderada-cicd-lab.git
cd ponderada-cicd-lab
```

## 2. Validar localmente

```bash
pip install -r requirements-dev.txt
ruff check src tests
pytest -m "not slow" -v
```

## 3. Disparar variações no GitHub Actions

Cada variação altera [`ci-mode.json`](../ci-mode.json). Exemplo:

```bash
python scripts/aplicar_variacao.py 09
git add ci-mode.json
git commit -m "ci: variacao 09 jobs sequenciais"
git push origin main
```

A tabela completa de variações está em [`experimento/VARIACOES.md`](../experimento/VARIACOES.md).

Execução manual adicional (sem novo commit):

```bash
gh workflow run "CI Pipeline Metrics Experiment" \
  -f execution_mode=parallel \
  -f pip_cache=true \
  -f run_slow_tests=false
```

## 4. Coletar métricas via API (obrigatório)

```bash
cd entregaveis
pip install -r requirements-viz.txt
export GITHUB_TOKEN="$(gh auth token)"   # PowerShell: $env:GITHUB_TOKEN = gh auth token
python coletar_metricas_pipeline.py --repo souzajv/ponderada-cicd-lab --limit 20
```

Saídas:

- `entregaveis/dados/pipeline_metricas_limpo.csv` (base principal de análise)
- `entregaveis/dados/pipeline_steps.csv` (duração por step)
- `entregaveis/dados/pipeline_metricas.csv` (dataset completo / auditoria)
- `entregaveis/dados/pipeline_metricas.json`
- `entregaveis/dados/raw/run-*.json` (cache bruto da API)

## 5. Gerar gráficos

```bash
python gerar_graficos_pipeline.py
python gerar_evidencias.py
```

O CSV limpo (`pipeline_metricas_limpo.csv`) exclui runs inválidos (0s) e jobs
`skipped`. Steps ficam em `pipeline_steps.csv`.

PNG em `entregaveis/graficos/`.

## 6. Evidências visuais

O enunciado aceita **prints ou links**. Esta entrega usa **ambos**:

1. **Links reais** — cada run em [`experimento/VARIACOES.md`](../experimento/VARIACOES.md) aponta para a execução no GitHub Actions.
2. **Painéis gerados** — `gerar_evidencias.py` monta imagens em `entregaveis/evidencias/` a partir dos dados coletados pela API (run_id, status, duração, jobs). Não são capturas manuais de tela; são evidências estruturadas reproduzíveis.

## 7. Evidências no GitHub

Lista de execuções:

```bash
gh run list --repo souzajv/ponderada-cicd-lab --limit 20
```

Abrir uma execução específica:

```bash
gh run view 27112464101 --repo souzajv/ponderada-cicd-lab --web
```
