"""Apports solaires lus sur la figure 1 du sujet."""

from __future__ import annotations

import numpy as np

# Irradiation moyenne sur le mois, W/m², lue sur la figure 1
# (Örebro, 60° N, Nevander & Elmarsson 1994). L'ordre est
# sud, nord, est/ouest. Lecture à ± 5 W/m². La courbe est/ouest
# du dessin n'est pas parfaitement symétrique entre janvier et décembre :
# on suit le dessin.
SOLAR_W_PER_M2: dict[int, tuple[float, float, float]] = {
    1: (10, 4, 45),
    2: (30, 8, 100),
    3: (80, 18, 147),
    4: (115, 32, 148),
    5: (140, 58, 142),
    6: (135, 80, 150),
    7: (135, 78, 148),
    8: (145, 55, 140),
    9: (135, 28, 115),
    10: (95, 14, 70),
    11: (35, 6, 28),
    12: (12, 3, 12),
}


def solar_gain_w(
    months: np.ndarray,
    area_south: float,
    area_north: float,
    area_east: float,
    area_west: float,
    g_value: float,
    krad: float,
) -> np.ndarray:
    """Puissance solaire entrant par les vitrages, pour chaque heure.

    La figure donne déjà une moyenne sur toutes les heures du mois.
    On l'applique telle quelle, puis on la multiplie par g et Krad.
    Multiplier ensuite par le nombre d'heures du mois redonne l'énergie,
    comme le demande l'indice du sujet.

    Parameters
    ----------
    months : np.ndarray
        Numéro de mois (1–12) de chaque heure.
    area_south, area_north, area_east, area_west : float
        Surfaces vitrées par orientation, m².
    g_value : float
        Facteur solaire du vitrage.
    krad : float
        Facteur de rayonnement solaire du sujet.

    Returns
    -------
    np.ndarray
        Puissance, W, une valeur par heure.
    """
    south = np.empty(len(months), dtype=float)
    north = np.empty(len(months), dtype=float)
    east_west = np.empty(len(months), dtype=float)
    for month, (s_value, n_value, ew_value) in SOLAR_W_PER_M2.items():
        mask = months == month
        south[mask] = s_value
        north[mask] = n_value
        east_west[mask] = ew_value
    irradiance = (
        area_south * south
        + area_north * north
        + (area_east + area_west) * east_west
    )
    return g_value * krad * irradiance
