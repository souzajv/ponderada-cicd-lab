#!/usr/bin/env python3
"""Atualiza ci-mode.json para a variacao indicada."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

VARIACOES = {
    "01": {
        "execution_mode": "parallel",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "01-baseline-verde",
    },
    "02": {
        "execution_mode": "parallel",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": True,
        "force_lint_failure": False,
        "variation_label": "02-teste-falhando",
    },
    "03": {
        "execution_mode": "parallel",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "03-correcao-teste",
    },
    "04": {
        "execution_mode": "parallel",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "04-mais-testes",
    },
    "05": {
        "execution_mode": "parallel",
        "pip_cache": True,
        "run_slow_tests": True,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "05-teste-lento",
    },
    "06": {
        "execution_mode": "parallel",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "06-cache-on",
    },
    "07": {
        "execution_mode": "parallel",
        "pip_cache": False,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "07-cache-off",
    },
    "08": {
        "execution_mode": "parallel",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "08-paralelo",
    },
    "09": {
        "execution_mode": "sequential",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "09-sequencial",
    },
    "10": {
        "execution_mode": "inverted",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "10-ordem-invertida",
    },
    "11": {
        "execution_mode": "sequential",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": True,
        "variation_label": "11-falha-lint",
    },
    "12": {
        "execution_mode": "parallel",
        "pip_cache": True,
        "run_slow_tests": False,
        "force_test_failure": False,
        "force_lint_failure": False,
        "variation_label": "12-artefato-grande",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("id", choices=sorted(VARIACOES.keys()))
    args = parser.parse_args()

    path = Path("ci-mode.json")
    path.write_text(json.dumps(VARIACOES[args.id], indent=2) + "\n", encoding="utf-8")
    print(f"ci-mode.json atualizado para variacao {args.id}")


if __name__ == "__main__":
    main()
