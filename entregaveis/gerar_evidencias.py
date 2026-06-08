#!/usr/bin/env python3
"""Gera paineis visuais de evidencia a partir dos dados coletados da API."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

AQUI = Path(__file__).resolve().parent
EVIDENCIAS = AQUI / "evidencias"
CSV_LIMPO = AQUI / "dados" / "pipeline_metricas_limpo.csv"
VARIACOES = AQUI.parent / "experimento" / "VARIACOES.md"


def painel_runs(df: pd.DataFrame) -> None:
    runs = (
        df.groupby("run_id", as_index=False)
        .agg(
            status=("status", "first"),
            duration=("workflow_duration", "first"),
            label=("variation_label", "first"),
        )
        .sort_values("run_id")
    )

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis("off")
    ax.set_title("Evidencia: execucoes reais do GitHub Actions\n(souzajv/ponderada-cicd-lab)", fontsize=14)

    linhas = ["run_id | status   | dur(s) | variacao", "-" * 52]
    for _, row in runs.iterrows():
        linhas.append(
            f"{int(row['run_id'])} | {row['status']:<8} | {row['duration']:>5.0f} | {row['label']}"
        )
    ax.text(0.02, 0.95, "\n".join(linhas), va="top", family="monospace", fontsize=9)
    fig.tight_layout()
    fig.savefig(EVIDENCIAS / "01_tabela_runs_reais.png", dpi=150)
    plt.close(fig)


def painel_paralelo_vs_sequencial(df: pd.DataFrame) -> None:
    runs = (
        df.groupby("run_id", as_index=False)
        .agg(
            workflow_duration=("workflow_duration", "first"),
            execution_mode=("execution_mode", "first"),
            variation_label=("variation_label", "first"),
        )
        .dropna(subset=["execution_mode"])
    )
    subset = runs[runs["variation_label"].isin(["08-paralelo", "09-sequencial", "10-ordem-invertida"])]
    if subset.empty:
        subset = runs[runs["execution_mode"].isin(["parallel", "sequential", "inverted"])].head(6)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(subset["variation_label"].astype(str), subset["workflow_duration"], color=["#2ecc71", "#e67e22", "#e74c3c"])
    ax.set_title("Evidencia: paralelo vs sequencial vs invertido")
    ax.set_ylabel("duracao (s)")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(EVIDENCIAS / "02_paralelo_vs_sequencial.png", dpi=150)
    plt.close(fig)


def painel_falhas(df: pd.DataFrame) -> None:
    runs = (
        df.groupby("run_id", as_index=False)
        .agg(
            status=("status", "first"),
            failures=("test_failures", "max"),
            label=("variation_label", "first"),
        )
        .query("status == 'failure'")
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    ax.set_title("Evidencia: execucoes com falha intencional", fontsize=13)
    if runs.empty:
        ax.text(0.1, 0.5, "Nenhuma falha no dataset limpo.", fontsize=12)
    else:
        texto = "\n".join(
            f"run {int(r.run_id)} | {r.label} | test_failures={int(r.failures)}"
            for r in runs.itertuples()
        )
        ax.text(0.05, 0.8, texto, va="top", family="monospace", fontsize=11)
    fig.tight_layout()
    fig.savefig(EVIDENCIAS / "03_runs_com_falha.png", dpi=150)
    plt.close(fig)


def painel_metricas_coletadas(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")
    ax.set_title("Evidencia: metricas coletadas via API (script Python)", fontsize=13)
    campos = [
        "run_id, commit_sha, commit_message, status",
        "workflow_duration, lead_time_s, artifact_size_bytes",
        "job_name, job_duration, test_count, test_failures",
        "test_duration_avg_s, timestamp, variation_label",
    ]
    ax.text(0.05, 0.85, "\n".join(campos), va="top", family="monospace", fontsize=11)
    ax.text(
        0.05,
        0.35,
        f"Linhas no CSV limpo: {len(df)}\nRuns unicos: {df['run_id'].nunique()}",
        va="top",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(EVIDENCIAS / "04_schema_metricas_api.png", dpi=150)
    plt.close(fig)


def main() -> None:
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    if not CSV_LIMPO.exists():
        raise SystemExit("Rode coletar_metricas_pipeline.py antes.")

    df = pd.read_csv(CSV_LIMPO)
    painel_runs(df)
    painel_paralelo_vs_sequencial(df)
    painel_falhas(df)
    painel_metricas_coletadas(df)
    print("Evidencias em", EVIDENCIAS)


if __name__ == "__main__":
    main()
