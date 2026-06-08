#!/usr/bin/env python3
"""Arquivo auxiliar para variacao de falha de lint controlada por ci-mode.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    mode = json.loads(Path("ci-mode.json").read_text(encoding="utf-8"))
    if mode.get("force_lint_failure"):
        print("lint probe: falha intencional habilitada em ci-mode.json", file=sys.stderr)
        raise SystemExit(1)
    print("lint probe: ok")


if __name__ == "__main__":
    main()
