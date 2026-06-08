#!/usr/bin/env python3
"""Coleta metricas de execucoes do GitHub Actions via API REST.

Autenticacao: GITHUB_TOKEN ou `gh auth token` (gh CLI configurado).

Saida:
  dados/pipeline_metricas.csv
  dados/pipeline_metricas.json
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import requests

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
RAW = DADOS / "raw"
ARTIFACTS = DADOS / "artifacts"
CSV_SAIDA = DADOS / "pipeline_metricas.csv"
JSON_SAIDA = DADOS / "pipeline_metricas.json"

CAMPOS = [
    "run_id",
    "commit_sha",
    "commit_message",
    "status",
    "workflow_duration",
    "job_name",
    "job_duration",
    "test_count",
    "test_failures",
    "timestamp",
    "variation_label",
    "execution_mode",
    "pip_cache",
]


def obter_token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token.strip()
    try:
        return subprocess.check_output(["gh", "auth", "token"], text=True).strip()
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise SystemExit(
            "Token nao encontrado. Configure GITHUB_TOKEN ou `gh auth login`."
        ) from exc


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def duracao_segundos(inicio: str | None, fim: str | None) -> float:
    start = parse_iso(inicio)
    end = parse_iso(fim)
    if not start or not end:
        return 0.0
    return round((end - start).total_seconds(), 3)


def api_get(session: requests.Session, url: str, params: dict | None = None) -> Any:
    resp = session.get(url, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def listar_workflow_runs(session: requests.Session, repo: str, workflow: str, limit: int) -> list[dict]:
    workflows = api_get(session, f"https://api.github.com/repos/{repo}/actions/workflows")
    workflow_id = None
    for item in workflows.get("workflows", []):
        if item.get("path", "").endswith(workflow) or item.get("name") == workflow:
            workflow_id = item["id"]
            break
    if workflow_id is None:
        raise SystemExit(f"Workflow nao encontrado: {workflow}")

    runs: list[dict] = []
    page = 1
    while len(runs) < limit:
        payload = api_get(
            session,
            f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/runs",
            params={"per_page": min(100, limit), "page": page},
        )
        batch = payload.get("workflow_runs", [])
        if not batch:
            break
        runs.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return runs[:limit]


def listar_jobs(session: requests.Session, repo: str, run_id: int) -> list[dict]:
    payload = api_get(session, f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/jobs")
    return payload.get("jobs", [])


def parse_junit_bytes(data: bytes) -> dict[str, float | int]:
    try:
        root = ET.fromstring(data)
    except ET.ParseError:
        return {"test_count": 0, "test_failures": 0, "test_duration_avg_s": 0.0}

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
    }


def parse_run_metrics_bytes(data: bytes) -> dict:
    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError:
        return {}


def baixar_metricas_artifact(session: requests.Session, repo: str, run_id: int) -> dict:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    cache_path = ARTIFACTS / f"run-{run_id}.json"
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    payload = api_get(session, f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts")
    artifact = next(
        (a for a in payload.get("artifacts", []) if a.get("name", "").startswith("pipeline-metrics-")),
        None,
    )
    if not artifact:
        cache_path.write_text("{}", encoding="utf-8")
        return {}

    download = session.get(artifact["archive_download_url"], timeout=120)
    download.raise_for_status()

    metrics: dict = {}
    with zipfile.ZipFile(BytesIO(download.content)) as zf:
        for name in zf.namelist():
            content = zf.read(name)
            if name.endswith("run-metrics.json"):
                metrics.update(parse_run_metrics_bytes(content))
            if name.endswith("junit.xml") and "test_count" not in metrics:
                metrics.update(parse_junit_bytes(content))

    cache_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics


def montar_linhas(repo: str, runs: list[dict], session: requests.Session) -> list[dict]:
    linhas: list[dict] = []
    RAW.mkdir(parents=True, exist_ok=True)

    for run in runs:
        run_id = run["id"]
        jobs = listar_jobs(session, repo, run_id)
        artifact_metrics = baixar_metricas_artifact(session, repo, run_id)

        started = [job.get("started_at") for job in jobs if job.get("started_at")]
        completed = [job.get("completed_at") for job in jobs if job.get("completed_at")]
        workflow_duration = duracao_segundos(
            min(started) if started else run.get("run_started_at"),
            max(completed) if completed else run.get("updated_at"),
        )

        commit_sha = run.get("head_sha", "")
        commit_message = (run.get("head_commit") or {}).get("message", "") or run.get("display_title", "")
        status = run.get("conclusion") or run.get("status") or "unknown"
        timestamp = run.get("created_at", "")

        test_count = int(artifact_metrics.get("test_count", 0))
        test_failures = int(artifact_metrics.get("test_failures", 0))
        variation_label = artifact_metrics.get("variation_label", "")
        execution_mode = artifact_metrics.get("execution_mode", "")
        pip_cache = artifact_metrics.get("pip_cache", "")

        if not jobs:
            linhas.append(
                {
                    "run_id": run_id,
                    "commit_sha": commit_sha,
                    "commit_message": commit_message.replace("\n", " ").strip(),
                    "status": status,
                    "workflow_duration": workflow_duration,
                    "job_name": "workflow",
                    "job_duration": workflow_duration,
                    "test_count": test_count,
                    "test_failures": test_failures,
                    "timestamp": timestamp,
                    "variation_label": variation_label,
                    "execution_mode": execution_mode,
                    "pip_cache": pip_cache,
                }
            )
            continue

        for job in jobs:
            if job.get("name") == "report":
                continue
            linhas.append(
                {
                    "run_id": run_id,
                    "commit_sha": commit_sha,
                    "commit_message": commit_message.replace("\n", " ").strip(),
                    "status": status,
                    "workflow_duration": workflow_duration,
                    "job_name": job.get("name", "unknown"),
                    "job_duration": duracao_segundos(job.get("started_at"), job.get("completed_at")),
                    "test_count": test_count if job.get("name", "").startswith("test") else 0,
                    "test_failures": test_failures if job.get("name", "").startswith("test") else 0,
                    "timestamp": timestamp,
                    "variation_label": variation_label,
                    "execution_mode": execution_mode,
                    "pip_cache": pip_cache,
                }
            )

        raw_path = RAW / f"run-{run_id}.json"
        raw_path.write_text(
            json.dumps({"run": run, "jobs": jobs, "artifact_metrics": artifact_metrics}, indent=2),
            encoding="utf-8",
        )

    return linhas


def salvar(linhas: list[dict]) -> None:
    DADOS.mkdir(parents=True, exist_ok=True)
    with CSV_SAIDA.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=CAMPOS)
        writer.writeheader()
        writer.writerows(linhas)

    JSON_SAIDA.write_text(json.dumps(linhas, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Coleta metricas de pipeline do GitHub Actions")
    parser.add_argument("--repo", required=True, help="owner/repo no GitHub")
    parser.add_argument("--workflow", default="ci.yml", help="Arquivo YAML do workflow")
    parser.add_argument("--limit", type=int, default=30, help="Quantidade maxima de runs")
    args = parser.parse_args()

    token = obter_token()
    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )

    runs = listar_workflow_runs(session, args.repo, args.workflow, args.limit)
    if not runs:
        raise SystemExit("Nenhuma execucao encontrada.")

    linhas = montar_linhas(args.repo, runs, session)
    salvar(linhas)

    print(f"Runs coletados : {len(runs)}")
    print(f"Linhas geradas : {len(linhas)}")
    print(f"CSV            -> {CSV_SAIDA.relative_to(AQUI)}")
    print(f"JSON           -> {JSON_SAIDA.relative_to(AQUI)}")


if __name__ == "__main__":
    main()
