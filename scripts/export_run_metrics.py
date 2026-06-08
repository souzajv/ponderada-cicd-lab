#!/usr/bin/env python3
"""Consolida junit.xml e metadados do workflow em run-metrics.json."""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from pathlib import Path


def parse_junit(path: Path) -> dict:
    if not path.exists():
        return {"test_count": 0, "test_failures": 0, "test_duration_avg_s": 0.0}

    root = ET.parse(path).getroot()
    suites = []
    if root.tag == "testsuites":
        suites = list(root.findall("testsuite"))
    elif root.tag == "testsuite":
        suites = [root]

    total_tests = 0
    total_failures = 0
    total_time = 0.0

    for suite in suites:
        total_tests += int(suite.attrib.get("tests", 0))
        total_failures += int(suite.attrib.get("failures", 0)) + int(suite.attrib.get("errors", 0))
        total_time += float(suite.attrib.get("time", 0.0))

    avg = round(total_time / total_tests, 4) if total_tests else 0.0
    return {
        "test_count": total_tests,
        "test_failures": total_failures,
        "test_duration_avg_s": avg,
        "test_duration_total_s": round(total_time, 3),
    }


def read_step_timings(path: Path) -> dict[str, float]:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {str(k): float(v) for k, v in raw.items()}


def main() -> None:
    reports = Path("reports")
    reports.mkdir(parents=True, exist_ok=True)

    junit_stats = parse_junit(reports / "junit.xml")
    step_timings = read_step_timings(reports / "step-timings.json")

    payload = {
        "run_id": int(os.environ.get("GITHUB_RUN_ID", "0") or 0),
        "commit_sha": os.environ.get("GITHUB_SHA", "unknown"),
        "commit_message": os.environ.get("COMMIT_MESSAGE", ""),
        "workflow": os.environ.get("GITHUB_WORKFLOW", "ci"),
        "status": os.environ.get("WORKFLOW_STATUS", "unknown"),
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "variation_label": os.environ.get("VARIATION_LABEL", "unknown"),
        "execution_mode": os.environ.get("EXECUTION_MODE", "parallel"),
        "pip_cache": os.environ.get("PIP_CACHE", "true").lower() == "true",
        **junit_stats,
        "step_timings": step_timings,
    }

    out = reports / "run-metrics.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"run-metrics.json gerado em {out}")


if __name__ == "__main__":
    main()
