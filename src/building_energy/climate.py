"""Fichiers horaires de température et choix du DVUT."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# La liste du cours n'est pas dans le PDF. Elle coïncide avec les lieux
# SMHI du fichier DVUT Boverket, dans l'ordre alphabétique suédois, sans
# Abisko : le numéro 14 tombe alors sur Bjurholm, ce qui recoupe une
# solution publiée du même sujet. Le numéro 29 est donc Danderyd.
SKIPPED_PLACES = ("Abisko",)


def load_temperature(path: Path) -> pd.DataFrame:
    """Lit un CSV horaire année, mois, jour, heure, température.

    Parameters
    ----------
    path : Path
        CSV préparé à partir d'un fichier Sveby.

    Returns
    -------
    pd.DataFrame
        8760 lignes, une par heure.

    Raises
    ------
    ValueError
        Si le fichier n'a pas le bon nombre d'heures.
    """
    frame = pd.read_csv(path)
    needed = {"year", "month", "day", "hour", "temperature_c"}
    missing = needed - set(frame.columns)
    if missing:
        raise ValueError(f"{path} n'a pas les colonnes {sorted(missing)}")
    if len(frame) != 8760:
        raise ValueError(f"{path} devrait avoir 8760 heures, il en a {len(frame)}")
    return frame


def load_dvut(path: Path) -> pd.DataFrame:
    """Lit le CSV DVUT 1991-2020 de Boverket / SMHI.

    Parameters
    ----------
    path : Path
        Fichier ``dvut_1991_2020.csv``.

    Returns
    -------
    pd.DataFrame
        Une ligne par lieu, colonnes ``n-dygn``.
    """
    frame = pd.read_csv(path, sep=";", comment="#", encoding="utf-8-sig")
    frame.columns = [str(column).strip() for column in frame.columns]
    frame["Ort"] = frame["Ort"].astype(str).str.strip()
    return frame


def city_row(dvut: pd.DataFrame, city_number: int) -> pd.Series:
    """Retourne la ligne DVUT du numéro de ville ``cd``.

    Parameters
    ----------
    dvut : pd.DataFrame
        Table DVUT complète.
    city_number : int
        Numéro de ville, à partir de 1.

    Returns
    -------
    pd.Series
        Ligne du lieu.

    Raises
    ------
    ValueError
        Si le numéro sort de la liste.
    """
    names = dvut["Ort"]
    kept = dvut.loc[~names.isin(SKIPPED_PLACES)].reset_index(drop=True)
    if not 1 <= city_number <= len(kept):
        raise ValueError(
            f"numéro de ville {city_number} hors de la liste (1–{len(kept)})"
        )
    return kept.iloc[city_number - 1]


def dvut_celsius(row: pd.Series, time_constant_days: float) -> tuple[int, float]:
    """Choisit le DVUT dont la durée correspond à la constante de temps.

    Le BBR dit de prendre la valeur tabulée du nombre de jours le plus
    proche. En dessous d'un jour on garde 1 jour, au-dessus de 30 jours
    on garde 30 jours (limite du fichier SMHI).

    Parameters
    ----------
    row : pd.Series
        Ligne DVUT d'une ville.
    time_constant_days : float
        Constante de temps du bâtiment, en jours.

    Returns
    -------
    tuple of int, float
        Nombre de jours retenu, et DVUT en °C.
    """
    n_days = int(np.floor(time_constant_days + 0.5))
    n_days = max(1, min(30, n_days))
    column = f"{n_days}-dygn"
    return n_days, float(row[column])


def heating_season_mask(month: np.ndarray, day: np.ndarray) -> np.ndarray:
    """Heures du 15 septembre au 15 mai, les deux bouts inclus.

    Parameters
    ----------
    month, day : np.ndarray
        Mois et jour de chaque heure.

    Returns
    -------
    np.ndarray of bool
        Masque de la saison de chauffe du sujet.
    """
    month = np.asarray(month)
    day = np.asarray(day)
    return (
        ((month == 9) & (day >= 15))
        | (month >= 10)
        | (month <= 4)
        | ((month == 5) & (day <= 15))
    )


def degree_hours(temperature_c: np.ndarray, base_c: float, mask: np.ndarray) -> float:
    """Somme des écarts positifs à une base, en °C·h.

    Parameters
    ----------
    temperature_c : np.ndarray
        Température extérieure horaire.
    base_c : float
        Température de base.
    mask : np.ndarray
        Heures à garder.

    Returns
    -------
    float
        Degrés-heures.
    """
    gap = np.maximum(base_c - np.asarray(temperature_c, dtype=float), 0.0)
    return float(gap[mask].sum())
