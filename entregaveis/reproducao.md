# Como reproduzir o experimento

Este guia descreve o caminho completo: clonar o repositório, validar localmente, disparar variações no GitHub Actions, coletar métricas pela API e gerar gráficos e evidências.

Índice geral e mapa de entregáveis: [README principal](../README.md)

## Pré-requisitos

- Conta GitHub com Actions habilitado
- [GitHub CLI](https://cli.github.com/) autenticado (`gh auth login`)
- Python 3.11 ou superior
- Git

## 1. Clonar o repositório

```bash
git clone https://github.com/souzajv/ponderada-cicd-lab.git
cd ponderada-cicd-lab
```

## 2. Validar localmente

Antes de empurrar uma variação, vale confirmar que lint e testes passam na máquina local.

```bash
pip install -r requirements-dev.txt
ruff check src tests
pytest -m "not slow" -v
```

## 3. Disparar variações no GitHub Actions

Cada variação altera [`ci-mode.json`](../ci-mode.json). O exemplo abaixo aplica a variação 09 (jobs sequenciais).

```bash
python scripts/aplicar_variacao.py 09
git add ci-mode.json
git commit -m "ci: variacao 09 jobs sequenciais"
git push origin main
```

A tabela completa de variações está em [`experimento/VARIACOES.md`](../experimento/VARIACOES.md).

Para rodar o workflow sem novo commit, use `workflow_dispatch`:

```bash
gh workflow run "CI Pipeline Metrics Experiment" \
  -f execution_mode=parallel \
  -f pip_cache=true \
  -f run_slow_tests=false
```

## 4. Coletar métricas via API (obrigatório)

A coleta consulta a API do GitHub e não deve ser feita manualmente.

```bash
cd entregaveis
pip install -r requirements-viz.txt
export GITHUB_TOKEN="$(gh auth token)"   # PowerShell: $env:GITHUB_TOKEN = gh auth token
python coletar_metricas_pipeline.py --repo souzajv/ponderada-cicd-lab --limit 20
```

Arquivos gerados:

- `entregaveis/dados/pipeline_metricas_limpo.csv` (base principal de análise)
- `entregaveis/dados/pipeline_steps.csv` (duração por step)
- `entregaveis/dados/pipeline_metricas.csv` (dataset completo para auditoria)
- `entregaveis/dados/pipeline_metricas.json`
- `entregaveis/dados/raw/run-*.json` (cache bruto da API)

## 5. Gerar gráficos

```bash
python gerar_graficos_pipeline.py
python gerar_evidencias.py
```

O CSV limpo (`pipeline_metricas_limpo.csv`) exclui runs inválidos (duração 0s) e jobs `skipped`. Os steps ficam em `pipeline_steps.csv`. Os PNGs são salvos em `entregaveis/graficos/`.

## 6. Evidências visuais

O enunciado aceita prints ou links. Esta entrega usa os dois formatos.

Cada run listado em [`experimento/VARIACOES.md`](../experimento/VARIACOES.md) aponta para a execução real no GitHub Actions. Além disso, o script `gerar_evidencias.py` monta imagens em `entregaveis/evidencias/` a partir dos dados da API (run_id, status, duração, jobs). Não são capturas manuais de tela: são painéis estruturados e reproduzíveis.

## 7. Evidências no GitHub

Para listar execuções recentes:

```bash
gh run list --repo souzajv/ponderada-cicd-lab --limit 20
```

Para abrir uma execução específica no navegador:

```bash
gh run view 27112464101 --repo souzajv/ponderada-cicd-lab --web
```
