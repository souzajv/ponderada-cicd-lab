#!/usr/bin/env python3
"""Gera graficos obrigatorios e extras a partir dos CSVs de metricas."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
GRAFICOS = AQUI / "graficos"
CSV_LIMPO = DADOS / "pipeline_metricas_limpo.csv"
CSV_STEPS = DADOS / "pipeline_steps.csv"


def carregar_jobs() -> pd.DataFrame:
    if not CSV_LIMPO.exists():
        raise SystemExit(f"Arquivo nao encontrado: {CSV_LIMPO}. Rode coletar_metricas_pipeline.py antes.")
    return pd.read_csv(CSV_LIMPO)


def carregar_steps() -> pd.DataFrame:
    if not CSV_STEPS.exists():
        return pd.DataFrame()
    return pd.read_csv(CSV_STEPS)


def runs_resumo(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("run_id", as_index=False)
        .agg(
            workflow_duration=("workflow_duration", "first"),
            status=("status", "first"),
            test_count=("test_count", "max"),
            lead_time_s=("lead_time_s", "first"),
            variation_label=("variation_label", "first"),
            pip_cache=("pip_cache", "first"),
        )
        .sort_values("run_id")
    )


def grafico_tempo_total_por_execucao(df: pd.DataFrame) -> None:
    runs = runs_resumo(df)
    labels = [str(r) for r in runs["run_id"]]
    colors = ["#2ecc71" if s == "success" else "#e74c3c" for s in runs["status"]]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(labels, runs["workflow_duration"], color=colors)
    ax.set_title("Tempo total do pipeline por execucao (runs validos)")
    ax.set_xlabel("run_id")
    ax.set_ylabel("duracao (s)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(GRAFICOS / "01_tempo_total_por_execucao.png", dpi=150)
    plt.close(fig)


def grafico_tempo_por_job(df: pd.DataFrame) -> None:
    jobs = df[~df["job_name"].isin(["report"])].copy()
    jobs = jobs[jobs["job_duration"] > 0]
    pivot = jobs.pivot_table(index="run_id", columns="job_name", values="job_duration", aggfunc="first")
    pivot = pivot.fillna(0).sort_index()

    fig, ax = plt.subplots(figsize=(12, 6))
    pivot.plot(kind="bar", stacked=False, ax=ax)
    ax.set_title("Tempo por job em cada execucao")
    ax.set_xlabel("run_id")
    ax.set_ylabel("duracao (s)")
    ax.legend(title="job", bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "02_tempo_por_job.png", dpi=150)
    plt.close(fig)


def grafico_taxa_sucesso_falha(df: pd.DataFrame) -> None:
    runs = runs_resumo(df)
    counts = runs["status"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 6))
    colors = {"success": "#2ecc71", "failure": "#e74c3c"}
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=[colors.get(k, "#95a5a6") for k in counts.index],
    )
    ax.set_title("Taxa de sucesso e falha (runs validos)")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "03_taxa_sucesso_falha.png", dpi=150)
    plt.close(fig)


def grafico_testes_vs_duracao(df: pd.DataFrame) -> None:
    runs = runs_resumo(df)
    colors = ["#2ecc71" if s == "success" else "#e74c3c" for s in runs["status"]]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(runs["test_count"], runs["workflow_duration"], c=colors, s=80, alpha=0.85)
    ax.set_title("Quantidade de testes x duracao do pipeline")
    ax.set_xlabel("quantidade de testes")
    ax.set_ylabel("duracao total (s)")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "04_testes_vs_duracao.png", dpi=150)
    plt.close(fig)


def grafico_cache_on_vs_off(df: pd.DataFrame) -> None:
    runs = runs_resumo(df)
    runs = runs[runs["pip_cache"].notna()]
    runs["pip_cache"] = runs["pip_cache"].astype(str).str.lower().map({"true": "cache ON", "false": "cache OFF"})
    runs = runs.dropna(subset=["pip_cache"])
    if runs.empty:
        return

    fig, ax = plt.subplots(figsize=(7, 5))
    runs.boxplot(column="workflow_duration", by="pip_cache", ax=ax)
    ax.set_title("Duracao do workflow: cache ON vs OFF")
    ax.set_xlabel("modo de cache")
    ax.set_ylabel("duracao (s)")
    plt.suptitle("")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "05_cache_on_vs_off.png", dpi=150)
    plt.close(fig)


def grafico_lead_time(df: pd.DataFrame) -> None:
    runs = runs_resumo(df)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(runs["run_id"].astype(str), runs["lead_time_s"], color="#3498db")
    ax.set_title("Lead time commit -> conclusao do pipeline")
    ax.set_xlabel("run_id")
    ax.set_ylabel("lead time (s)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(GRAFICOS / "06_lead_time_por_run.png", dpi=150)
    plt.close(fig)


def grafico_steps_breakdown(steps: pd.DataFrame) -> None:
    if steps.empty:
        return
    relevantes = steps[
        steps["step_name"].str.contains("Instalar|pytest|Ruff|Lint|Exportar", case=False, na=False)
    ].copy()
    if relevantes.empty:
        relevantes = steps.copy()

    agg = (
        relevantes.groupby("step_name", as_index=False)["step_duration"]
        .mean()
        .sort_values("step_duration", ascending=True)
        .tail(12)
    )

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(agg["step_name"], agg["step_duration"], color="#9b59b6")
    ax.set_title("Duracao media por step (runs validos)")
    ax.set_xlabel("duracao media (s)")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "07_steps_breakdown.png", dpi=150)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=str(CSV_LIMPO), help="CSV de entrada (default: limpo)")
    args = parser.parse_args()

    GRAFICOS.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.csv)
    steps = carregar_steps()

    if df.empty:
        raise SystemExit("CSV vazio.")

    grafico_tempo_total_por_execucao(df)
    grafico_tempo_por_job(df)
    grafico_taxa_sucesso_falha(df)
    grafico_testes_vs_duracao(df)
    grafico_cache_on_vs_off(df)
    grafico_lead_time(df)
    grafico_steps_breakdown(steps)

    print("Graficos gerados em", GRAFICOS)
    for png in sorted(GRAFICOS.glob("*.png")):
        print(" -", png.name)


if __name__ == "__main__":
    main()
