from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def save_markdown_report(metrics: pd.DataFrame, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Evaluation Metrics", ""]
    lines.append(metrics.to_markdown(index=False))
    Path(path).write_text("\n".join(lines), encoding="utf-8")


def plot_predictions(y_true: pd.Series, predictions: dict[str, pd.Series], output_dir: str) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 4))
    plt.plot(y_true.reset_index(drop=True), label="Actual")
    for name, series in predictions.items():
        plt.plot(series.reset_index(drop=True), label=name)
    plt.legend()
    plt.title("Actual vs Predicted")
    plt.tight_layout()
    plt.savefig(Path(output_dir) / "actual_vs_pred.png")


def plot_residuals(y_true: pd.Series, predictions: dict[str, pd.Series], output_dir: str) -> None:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 4))
    for name, series in predictions.items():
        residuals = y_true.reset_index(drop=True) - series.reset_index(drop=True)
        plt.plot(residuals, label=name)
    plt.axhline(0, color="black", linewidth=1)
    plt.legend()
    plt.title("Residuals")
    plt.tight_layout()
    plt.savefig(Path(output_dir) / "residuals.png")
