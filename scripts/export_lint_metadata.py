#!/usr/bin/env python3
"""Gera run-metrics.json minimo no job lint (mesmo quando falha)."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path


def main() -> None:
    reports = Path("reports")
    reports.mkdir(parents=True, exist_ok=True)

    payload = {
        "run_id": int(os.environ.get("GITHUB_RUN_ID", "0") or 0),
        "commit_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "commit_message": os.environ.get("COMMIT_MESSAGE", ""),
        "status": os.environ.get("WORKFLOW_STATUS", "unknown"),
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "variation_label": os.environ.get("VARIATION_LABEL", "unknown"),
        "execution_mode": os.environ.get("EXECUTION_MODE", "parallel"),
        "pip_cache": os.environ.get("PIP_CACHE", "true").lower() == "true",
        "test_count": 0,
        "test_failures": 0,
        "test_duration_avg_s": 0.0,
        "source_job": "lint",
    }

    (reports / "run-metrics.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
