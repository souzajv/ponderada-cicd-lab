#!/usr/bin/env python3
"""Coleta metricas de execucoes do GitHub Actions via API REST.

Autenticacao: GITHUB_TOKEN ou `gh auth token` (gh CLI configurado).

Saidas:
  dados/pipeline_metricas.csv       (completo)
  dados/pipeline_metricas_limpo.csv (runs/jobs validos para analise)
  dados/pipeline_steps.csv          (duracao por step)
  dados/pipeline_metricas.json
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
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
CSV_LIMPO = DADOS / "pipeline_metricas_limpo.csv"
CSV_STEPS = DADOS / "pipeline_steps.csv"
JSON_SAIDA = DADOS / "pipeline_metricas.json"

CAMPOS = [
    "run_id",
    "commit_sha",
    "commit_message",
    "status",
    "workflow_duration",
    "lead_time_s",
    "artifact_size_bytes",
    "job_name",
    "job_duration",
    "test_count",
    "test_failures",
    "test_duration_avg_s",
    "timestamp",
    "variation_label",
    "execution_mode",
    "pip_cache",
]

CAMPOS_STEPS = [
    "run_id",
    "commit_sha",
    "status",
    "variation_label",
    "job_name",
    "step_name",
    "step_number",
    "step_conclusion",
    "step_duration",
    "timestamp",
]

JOBS_IGNORADOS_LIMPO = {"report"}


def obter_token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token.strip()
    gh_paths = [
        "gh",
        r"C:\Program Files\GitHub CLI\gh.exe",
    ]
    for gh in gh_paths:
        try:
            return subprocess.check_output([gh, "auth", "token"], text=True).strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            continue
    raise SystemExit("Token nao encontrado. Configure GITHUB_TOKEN ou `gh auth login`.")


def parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def duracao_segundos(inicio: str | None, fim: str | None) -> float:
    start = parse_iso(inicio)
    end = parse_iso(fim)
    if not start or not end:
        return 0.0
    delta = (end - start).total_seconds()
    return round(max(delta, 0.0), 3)


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


def tamanho_artefatos(session: requests.Session, repo: str, run_id: int) -> int:
    payload = api_get(session, f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts")
    total = 0
    for artifact in payload.get("artifacts", []):
        name = artifact.get("name", "")
        if name.startswith("pipeline-metrics-") or name.startswith("pipeline-report-"):
            total += int(artifact.get("size_in_bytes", 0))
    return total


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
    candidates = [
        a
        for a in payload.get("artifacts", [])
        if a.get("name", "").startswith("pipeline-metrics-")
        or a.get("name", "").startswith("pipeline-report-")
    ]
    if not candidates:
        cache_path.write_text("{}", encoding="utf-8")
        return {}

    metrics: dict = {}
    for artifact in candidates:
        download = session.get(artifact["archive_download_url"], timeout=120)
        download.raise_for_status()
        with zipfile.ZipFile(BytesIO(download.content)) as zf:
            for name in zf.namelist():
                content = zf.read(name)
                if name.endswith("run-metrics.json"):
                    metrics.update(parse_run_metrics_bytes(content))
                if name.endswith("junit.xml"):
                    junit = parse_junit_bytes(content)
                    if junit.get("test_count", 0) > 0:
                        metrics.update(junit)

    cache_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics


def calcular_lead_time(run: dict) -> float:
    commit_ts = (run.get("head_commit") or {}).get("timestamp")
    updated = run.get("updated_at")
    return duracao_segundos(commit_ts, updated)


def montar_steps(
    run_id: int,
    commit_sha: str,
    status: str,
    variation_label: str,
    timestamp: str,
    jobs: list[dict],
) -> list[dict]:
    linhas: list[dict] = []
    for job in jobs:
        job_name = job.get("name", "unknown")
        if job.get("conclusion") == "skipped":
            continue
        for step in job.get("steps", []):
            if step.get("conclusion") == "skipped":
                continue
            linhas.append(
                {
                    "run_id": run_id,
                    "commit_sha": commit_sha,
                    "status": status,
                    "variation_label": variation_label,
                    "job_name": job_name,
                    "step_name": step.get("name", "unknown"),
                    "step_number": step.get("number", 0),
                    "step_conclusion": step.get("conclusion", ""),
                    "step_duration": duracao_segundos(step.get("started_at"), step.get("completed_at")),
                    "timestamp": timestamp,
                }
            )
    return linhas


def job_eh_teste_ativo(job: dict) -> bool:
    name = job.get("name", "")
    return name.startswith("test_") and job.get("conclusion") in {"success", "failure"}


def montar_linhas(
    repo: str,
    runs: list[dict],
    session: requests.Session,
    only_valid: bool,
    min_duration: float,
) -> tuple[list[dict], list[dict], list[dict]]:
    linhas: list[dict] = []
    steps_linhas: list[dict] = []
    RAW.mkdir(parents=True, exist_ok=True)

    for run in runs:
        run_id = run["id"]
        jobs = listar_jobs(session, repo, run_id)
        artifact_metrics = baixar_metricas_artifact(session, repo, run_id)
        artifact_size = tamanho_artefatos(session, repo, run_id)

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
        lead_time_s = calcular_lead_time(run)

        test_count = int(artifact_metrics.get("test_count", 0))
        test_failures = int(artifact_metrics.get("test_failures", 0))
        test_duration_avg_s = float(artifact_metrics.get("test_duration_avg_s", 0.0))
        variation_label = artifact_metrics.get("variation_label", "")
        execution_mode = artifact_metrics.get("execution_mode", "")
        pip_cache = artifact_metrics.get("pip_cache", "")

        if not variation_label:
            variation_label = inferir_variation_label(commit_message)

        steps_linhas.extend(
            montar_steps(run_id, commit_sha, status, variation_label, timestamp, jobs)
        )

        for job in jobs:
            job_name = job.get("name", "unknown")
            if job_name in JOBS_IGNORADOS_LIMPO:
                continue

            is_test_job = job_name.startswith("test")
            linhas.append(
                {
                    "run_id": run_id,
                    "commit_sha": commit_sha,
                    "commit_message": commit_message.replace("\n", " ").strip(),
                    "status": status,
                    "workflow_duration": workflow_duration,
                    "lead_time_s": lead_time_s,
                    "artifact_size_bytes": artifact_size,
                    "job_name": job_name,
                    "job_duration": duracao_segundos(job.get("started_at"), job.get("completed_at")),
                    "test_count": test_count if is_test_job else 0,
                    "test_failures": test_failures if is_test_job else 0,
                    "test_duration_avg_s": test_duration_avg_s if is_test_job else 0.0,
                    "timestamp": timestamp,
                    "variation_label": variation_label,
                    "execution_mode": execution_mode,
                    "pip_cache": pip_cache,
                    "_job_conclusion": job.get("conclusion", ""),
                }
            )

        raw_path = RAW / f"run-{run_id}.json"
        raw_path.write_text(
            json.dumps(
                {
                    "run": run,
                    "jobs": jobs,
                    "artifact_metrics": artifact_metrics,
                    "artifact_size_bytes": artifact_size,
                    "lead_time_s": lead_time_s,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    limpas = filtrar_limpo(linhas, min_duration)
    return linhas, limpas, steps_linhas


def inferir_variation_label(commit_message: str) -> str:
    msg = commit_message.lower()
    if "dispatch-parallel" in msg or "dispatch parallel" in msg:
        return "dispatch-parallel"
    if "dispatch-sequential" in msg or "dispatch sequential" in msg:
        return "dispatch-sequential"
    for token in msg.split():
        if token.startswith("variacao") or token.startswith("variação"):
            continue
    if "variacao" in msg or "variação" in msg:
        for part in msg.replace(":", " ").split():
            if part.isdigit() and len(part) <= 2:
                return f"{int(part):02d}-inferido"
    return ""


def filtrar_limpo(linhas: list[dict], min_duration: float) -> list[dict]:
    limpas: list[dict] = []
    runs_test_ativos: dict[int, set[str]] = {}
    duracao_por_run: dict[int, float] = {}
    for row in linhas:
        rid = row["run_id"]
        duracao_por_run[rid] = max(duracao_por_run.get(rid, 0.0), float(row.get("workflow_duration", 0)))
    runs_validos = {rid for rid, dur in duracao_por_run.items() if dur >= min_duration}

    for row in linhas:
        if row["run_id"] not in runs_validos:
            continue
        run_id = row["run_id"]
        conclusion = row.get("_job_conclusion", "")
        job_name = row["job_name"]
        duration = row["job_duration"]

        if conclusion == "skipped":
            continue
        if duration < 0:
            continue

        if job_name.startswith("test_"):
            if conclusion not in {"success", "failure"}:
                continue
            if duration <= 0 and conclusion != "failure":
                continue
            runs_test_ativos.setdefault(run_id, set()).add(job_name)

        limpas.append({k: v for k, v in row.items() if not k.startswith("_")})

    # Remove test jobs duplicados/skipped com duracao 0 quando ha test ativo
    ativos_por_run = {
        run_id: names for run_id, names in runs_test_ativos.items() if names
    }
    resultado: list[dict] = []
    for row in limpas:
        job_name = row["job_name"]
        if job_name.startswith("test_"):
            ativos = ativos_por_run.get(row["run_id"], set())
            if ativos and job_name not in ativos:
                continue
            if row["job_duration"] <= 0 and row["test_count"] == 0:
                continue
        resultado.append(row)
    return resultado


def salvar(linhas: list[dict], limpas: list[dict], steps: list[dict]) -> None:
    DADOS.mkdir(parents=True, exist_ok=True)

    def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
        with path.open("w", encoding="utf-8", newline="") as fp:
            writer = csv.DictWriter(fp, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    write_csv(CSV_SAIDA, [{k: v for k, v in r.items() if not k.startswith("_")} for r in linhas], CAMPOS)
    write_csv(CSV_LIMPO, limpas, CAMPOS)
    write_csv(CSV_STEPS, steps, CAMPOS_STEPS)
    JSON_SAIDA.write_text(
        json.dumps(
            {
                "jobs": [{k: v for k, v in r.items() if not k.startswith("_")} for r in linhas],
                "jobs_limpo": limpas,
                "steps": steps,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Coleta metricas de pipeline do GitHub Actions")
    parser.add_argument("--repo", required=True, help="owner/repo no GitHub")
    parser.add_argument("--workflow", default="ci.yml", help="Arquivo YAML do workflow")
    parser.add_argument("--limit", type=int, default=30, help="Quantidade maxima de runs")
    parser.add_argument(
        "--only-valid",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Ignorar runs invalidos (duracao < min-duration ou sem jobs)",
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=5.0,
        help="Duracao minima do workflow para considerar run valido",
    )
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

    linhas, limpas, steps = montar_linhas(args.repo, runs, session, args.only_valid, args.min_duration)
    if args.only_valid:
        runs_ok = {r["run_id"] for r in limpas}
        steps = [s for s in steps if s["run_id"] in runs_ok]
    salvar(linhas, limpas, steps)

    runs_validos = len({r["run_id"] for r in limpas})
    print(f"Runs na API     : {len(runs)}")
    print(f"Runs validos    : {runs_validos}")
    print(f"Linhas jobs     : {len(linhas)}")
    print(f"Linhas limpas   : {len(limpas)}")
    print(f"Linhas steps    : {len(steps)}")
    print(f"CSV completo    -> {CSV_SAIDA.relative_to(AQUI)}")
    print(f"CSV limpo       -> {CSV_LIMPO.relative_to(AQUI)}")
    print(f"CSV steps       -> {CSV_STEPS.relative_to(AQUI)}")


if __name__ == "__main__":
    main()
