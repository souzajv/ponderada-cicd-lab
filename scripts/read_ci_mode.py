#!/usr/bin/env python3
"""Lê ci-mode.json e imprime outputs no formato do GitHub Actions."""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> None:
    path = Path(os.environ.get("CI_MODE_PATH", "ci-mode.json"))
    mode = json.loads(path.read_text(encoding="utf-8"))

    out = os.environ.get("GITHUB_OUTPUT")
    if not out:
        print(json.dumps(mode, indent=2))
        return

    mapping = {
        "execution_mode": mode.get("execution_mode", "parallel"),
        "pip_cache": str(mode.get("pip_cache", True)).lower(),
        "run_slow_tests": str(mode.get("run_slow_tests", False)).lower(),
        "force_test_failure": str(mode.get("force_test_failure", False)).lower(),
        "force_lint_failure": str(mode.get("force_lint_failure", False)).lower(),
        "variation_label": mode.get("variation_label", "unknown"),
    }
    with open(out, "a", encoding="utf-8") as fp:
        for key, value in mapping.items():
            fp.write(f"{key}={value}\n")


if __name__ == "__main__":
    main()
