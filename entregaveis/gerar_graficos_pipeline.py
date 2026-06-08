#!/usr/bin/env python3
"""Gera os 4 graficos obrigatorios a partir de pipeline_metricas.csv."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

AQUI = Path(__file__).resolve().parent
DADOS = AQUI / "dados"
GRAFICOS = AQUI / "graficos"
CSV_ENTRADA = DADOS / "pipeline_metricas.csv"


def carregar() -> pd.DataFrame:
    if not CSV_ENTRADA.exists():
        raise SystemExit(f"Arquivo nao encontrado: {CSV_ENTRADA}. Rode coletar_metricas_pipeline.py antes.")
    return pd.read_csv(CSV_ENTRADA)


def grafico_tempo_total_por_execucao(df: pd.DataFrame) -> None:
    runs = (
        df.groupby("run_id", as_index=False)
        .agg(workflow_duration=("workflow_duration", "first"), status=("status", "first"))
        .sort_values("run_id")
    )
    labels = [str(r) for r in runs["run_id"]]
    colors = ["#2ecc71" if s == "success" else "#e74c3c" for s in runs["status"]]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(labels, runs["workflow_duration"], color=colors)
    ax.set_title("Tempo total do pipeline por execucao")
    ax.set_xlabel("run_id")
    ax.set_ylabel("duracao (s)")
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(GRAFICOS / "01_tempo_total_por_execucao.png", dpi=150)
    plt.close(fig)


def grafico_tempo_por_job(df: pd.DataFrame) -> None:
    jobs = df[~df["job_name"].isin(["report", "setup"])].copy()
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
    runs = df.groupby("run_id", as_index=False).agg(status=("status", "first"))
    counts = runs["status"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 6))
    colors = {"success": "#2ecc71", "failure": "#e74c3c"}
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=[colors.get(k, "#95a5a6") for k in counts.index],
    )
    ax.set_title("Taxa de sucesso e falha")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "03_taxa_sucesso_falha.png", dpi=150)
    plt.close(fig)


def grafico_testes_vs_duracao(df: pd.DataFrame) -> None:
    runs = (
        df.groupby("run_id", as_index=False)
        .agg(
            workflow_duration=("workflow_duration", "first"),
            test_count=("test_count", "max"),
            status=("status", "first"),
        )
        .sort_values("test_count")
    )

    colors = ["#2ecc71" if s == "success" else "#e74c3c" for s in runs["status"]]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(runs["test_count"], runs["workflow_duration"], c=colors, s=80, alpha=0.85)
    ax.set_title("Quantidade de testes x duracao do pipeline")
    ax.set_xlabel("quantidade de testes")
    ax.set_ylabel("duracao total (s)")
    fig.tight_layout()
    fig.savefig(GRAFICOS / "04_testes_vs_duracao.png", dpi=150)
    plt.close(fig)


def main() -> None:
    GRAFICOS.mkdir(parents=True, exist_ok=True)
    df = carregar()

    if df.empty:
        raise SystemExit("CSV vazio.")

    grafico_tempo_total_por_execucao(df)
    grafico_tempo_por_job(df)
    grafico_taxa_sucesso_falha(df)
    grafico_testes_vs_duracao(df)

    print("Graficos gerados em", GRAFICOS)
    for png in sorted(GRAFICOS.glob("*.png")):
        print(" -", png.name)


if __name__ == "__main__":
    main()
