# Variações controladas do experimento

A tabela abaixo lista as 14 execuções válidas do experimento, realizadas em 2026-06-08. Cada linha traz o `run_id`, o commit e o link direto para o GitHub Actions.

| # | variation_label | run_id | commit_sha | status | link |
|---|---|---|---|---|---|
| 01 | 01-baseline-verde | 27112464101 | e3e3c8a | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112464101) |
| 02 | 02-teste-falhando | 27112466672 | f724b9d | failure | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112466672) |
| 03 | 03-correcao-teste | 27112469375 | ecf658f | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112469375) |
| 04 | 04-mais-testes | 27112472129 | 3eec61b | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112472129) |
| 05 | 05-teste-lento | 27112474712 | 20bc662 | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112474712) |
| 06 | 06-cache-on | 27112477570 | 1a7696f | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112477570) |
| 07 | 07-cache-off | 27112480695 | 5f5e0aa | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112480695) |
| 08 | 08-paralelo | 27112483564 | 89ae72a | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112483564) |
| 09 | 09-sequencial | 27112486298 | ec55d58 | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112486298) |
| 10 | 10-ordem-invertida | 27112489037 | 8cfd2f8 | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112489037) |
| 11 | 11-falha-lint | 27112491871 | 80fbf6a | failure | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112491871) |
| 12 | 12-artefato-grande | 27112494596 | c3a3af5 | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112494596) |
| 13 | dispatch-parallel | 27112496051 | c3a3af5 | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112496051) |
| 14 | dispatch-sequential | 27112496923 | c3a3af5 | success | [run](https://github.com/souzajv/ponderada-cicd-lab/actions/runs/27112496923) |

**Nota:** as 12 primeiras execuções após o push inicial falharam com duração 0s por erro de validação do YAML (composite action inválido). O problema foi corrigido no commit `846b08a` e as variações foram reexecutadas na segunda rodada, listada acima.
