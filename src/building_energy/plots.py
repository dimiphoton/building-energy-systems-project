"""Graphiques du bilan. Fond crème, même teinte que les diapositives."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CREAM = "#f3eee6"
INK = "#1c1610"
ACCENT = "#8a6a12"
BLUE = "#3d5a73"
RED = "#8c3a2f"

MONTHS = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]


def _style(ax: plt.Axes) -> None:
    ax.set_facecolor(CREAM)
    ax.tick_params(colors=INK)
    for spine in ax.spines.values():
        spine.set_color("#d9d0c3")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.yaxis.label.set_color(INK)
    ax.xaxis.label.set_color(INK)
    ax.title.set_color(INK)


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=140, facecolor=CREAM, bbox_inches="tight")
    plt.close(fig)


def plot_duration(hourly: pd.DataFrame, tb_c: float, dvut_c: float, path: Path) -> None:
    """Courbe des températures triées, de la plus froide à la plus douce.

    Parameters
    ----------
    hourly : pd.DataFrame
        Bilan horaire, avec ``temperature_c``.
    tb_c : float
        Température d'équilibre.
    dvut_c : float
        Température de dimensionnement.
    path : Path
        Fichier PNG.
    """
    ordered = np.sort(hourly["temperature_c"].to_numpy())
    hours = np.arange(1, len(ordered) + 1)
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    _style(ax)
    ax.plot(hours, ordered, color=BLUE, linewidth=2.0)
    ax.axhline(tb_c, color=ACCENT, linewidth=1.2, label=f"Balance temperature {tb_c:.1f} °C")
    ax.axhline(dvut_c, color=RED, linewidth=1.2, linestyle="--", label=f"DVUT {dvut_c:.1f} °C")
    ax.set_xlabel("Hours, coldest first")
    ax.set_ylabel("Outdoor temperature (°C)")
    ax.legend(frameon=False, labelcolor=INK)
    _save(fig, path)


def plot_monthly(result: dict[str, object], path: Path) -> None:
    """Déficit de chauffage mois par mois, 2017 et année type.

    Parameters
    ----------
    result : dict
        Sortie de ``run``, clés ``monthly_2017`` et ``monthly_normal``.
    path : Path
        Fichier PNG.
    """
    year_2017 = [row["deficit_kwh"] / 1000.0 for row in result["monthly_2017"]]  # type: ignore[index]
    normal = [row["deficit_kwh"] / 1000.0 for row in result["monthly_normal"]]  # type: ignore[index]
    x = np.arange(12)
    width = 0.38
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    _style(ax)
    ax.bar(x - width / 2, year_2017, width, color=BLUE, label="2017")
    ax.bar(x + width / 2, normal, width, color=ACCENT, label="Typical year 1991–2020")
    ax.set_xticks(x, MONTHS)
    ax.set_ylabel("Heating need (MWh)")
    ax.legend(frameon=False, labelcolor=INK)
    _save(fig, path)


def plot_shares(result: dict[str, object], path: Path) -> None:
    """D'où partent les kilowatts le jour de dimensionnement.

    Parameters
    ----------
    result : dict
        Clé ``design_shares_w``.
    path : Path
        Fichier PNG.
    """
    shares: dict[str, float] = result["design_shares_w"]  # type: ignore[assignment]
    labels = {
        "windows": "Windows",
        "ventilation": "Ventilation and leaks",
        "walls": "Outer walls",
        "balconies": "Balcony slabs",
        "foundation": "Ground floor",
        "doors": "Doors",
        "roof": "Roof",
    }
    order = sorted(shares, key=lambda key: shares[key], reverse=True)
    values = [shares[key] / 1000.0 for key in order]
    names = [labels[key] for key in order]
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    _style(ax)
    colors = [RED if name == "Windows" else BLUE for name in names]
    ax.barh(names[::-1], values[::-1], color=colors[::-1])
    ax.set_xlabel("Design heat loss (kW)")
    _save(fig, path)


def plot_energy_class(result: dict[str, object], path: Path) -> None:
    """Position du bâtiment sur l'échelle A–G.

    Parameters
    ----------
    result : dict
        Bloc ``energy_class``.
    path : Path
        Fichier PNG.
    """
    block = result["energy_class"]
    ep = float(block["ep_kwh_m2"])  # type: ignore[index]
    limit = float(block["limit_kwh_m2"])  # type: ignore[index]
    # Plafonds de classe, en kWh/m². Le dernier tronçon va jusqu'à G.
    ceilings = [0.50, 0.75, 1.00, 1.35, 1.80, 2.35]
    letters = ["A", "B", "C", "D", "E", "F", "G"]
    edges = [0.0] + [item * limit for item in ceilings] + [max(ep * 1.15, 2.6 * limit)]
    palette = ["#2f6b4f", "#4e8a62", "#c4a35a", "#c47b2b", "#b5652a", "#a3532d", "#8c3a2f"]
    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    _style(ax)
    for index, letter in enumerate(letters):
        ax.barh(
            0,
            edges[index + 1] - edges[index],
            left=edges[index],
            height=0.55,
            color=palette[index],
        )
        ax.text(
            (edges[index] + edges[index + 1]) / 2,
            0,
            letter,
            ha="center",
            va="center",
            color="white",
            fontsize=12,
        )
    ax.plot([ep, ep], [-0.45, 0.45], color=INK, linewidth=2)
    ax.set_yticks([])
    ax.set_xlabel("Primary energy number (kWh/m²·year)")
    ax.set_ylim(-0.7, 0.7)
    _save(fig, path)


def write_plots(result: dict[str, object], directory: Path) -> None:
    """Écrit les quatre graphiques du projet.

    Parameters
    ----------
    result : dict
        Sortie de ``run``, DataFrame horaire compris.
    directory : Path
        Dossier de sortie.
    """
    directory.mkdir(parents=True, exist_ok=True)
    plot_duration(
        result["hourly_2017"],  # type: ignore[arg-type]
        float(result["tb_c"]),
        float(result["dvut_c"]),
        directory / "duration-temperature.png",
    )
    plot_monthly(result, directory / "monthly-heating.png")
    plot_shares(result, directory / "design-power-shares.png")
    plot_energy_class(result, directory / "energy-class.png")
