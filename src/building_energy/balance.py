"""Température d'équilibre, puissance de dimensionnement, déficit horaire."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from building_energy.climate import degree_hours, heating_season_mask
from building_energy.envelope import Envelope
from building_energy.parameters import Case
from building_energy.solar import solar_gain_w


@dataclass(frozen=True)
class SeasonTotals:
    """Énergies de la saison de chauffe, en kWh, et degrés-heures."""

    hours: int
    transmission_kwh: float
    ventilation_kwh: float
    appliances_kwh: float
    people_kwh: float
    solar_kwh: float
    deficit_kwh: float
    degree_hours_tin: float
    degree_hours_tb: float


def balance_temperature(tin_c: float, appliance_w: float, h_total: float) -> float:
    """Température extérieure où le chauffage s'arrête, sans soleil ni occupants.

    Le sujet demande d'ignorer les personnes et le soleil pour Tb,
    et de garder les appareils.

    Parameters
    ----------
    tin_c : float
        Consigne intérieure, °C.
    appliance_w : float
        Apports des appareils, W.
    h_total : float
        Conductance totale transmission + ventilation, W/K.

    Returns
    -------
    float
        Tb, °C.
    """
    return tin_c - appliance_w / h_total


def design_power_w(h_total: float, tin_c: float, dvut_c: float) -> float:
    """Puissance de chauffage sans aucun apport interne.

    Parameters
    ----------
    h_total : float
        Conductance totale, W/K.
    tin_c : float
        Consigne, °C.
    dvut_c : float
        Température extérieure de dimensionnement, °C.

    Returns
    -------
    float
        Puissance, W.
    """
    return h_total * (tin_c - dvut_c)


def time_constant_days(capacity_j_per_k: float, h_total: float) -> float:
    """Constante de temps C / H, en jours.

    Parameters
    ----------
    capacity_j_per_k : float
        Capacité thermique intérieure, J/K.
    h_total : float
        Conductance totale, W/K.

    Returns
    -------
    float
        Durée, en jours.
    """
    return capacity_j_per_k / h_total / 86400.0


def hourly_frame(
    climate: pd.DataFrame,
    case: Case,
    envelope: Envelope,
    h_tr: float,
    h_vent: float,
    appliance_w: float,
    people_w: float,
) -> pd.DataFrame:
    """Bilan heure par heure. Chaque ligne dure une heure.

    Parameters
    ----------
    climate : pd.DataFrame
        Températures horaires.
    case : Case
        Facteurs solaires des vitrages.
    envelope : Envelope
        Surfaces vitrées par orientation.
    h_tr, h_vent : float
        Conductances, W/K.
    appliance_w, people_w : float
        Apports constants, W.

    Returns
    -------
    pd.DataFrame
        Pertes, apports et déficit, en W. Le déficit est nul quand
        les apports couvrent les pertes : on ne stocke pas le surplus.
    """
    temperature = climate["temperature_c"].to_numpy(dtype=float)
    months = climate["month"].to_numpy(dtype=int)
    delta = case.tin_c - temperature
    solar = solar_gain_w(
        months,
        envelope.window_south_m2,
        envelope.window_north_m2,
        envelope.window_east_m2,
        envelope.window_west_m2,
        case.g_window,
        case.krad_window,
    )
    loss_tr = h_tr * delta
    loss_vent = h_vent * delta
    net = loss_tr + loss_vent - solar - appliance_w - people_w
    return pd.DataFrame(
        {
            "month": months,
            "day": climate["day"].to_numpy(dtype=int),
            "hour": climate["hour"].to_numpy(dtype=int),
            "temperature_c": temperature,
            "loss_tr_w": loss_tr,
            "loss_vent_w": loss_vent,
            "solar_w": solar,
            "appliances_w": np.full(len(climate), appliance_w),
            "people_w": np.full(len(climate), people_w),
            "deficit_w": np.maximum(net, 0.0),
        }
    )


def _kwh(power_w: np.ndarray) -> float:
    """Une ligne = une heure, donc la somme des watts est des Wh."""
    return float(np.asarray(power_w).sum()) / 1000.0


def season_totals(
    hourly: pd.DataFrame,
    tin_c: float,
    tb_c: float,
) -> SeasonTotals:
    """Intègre le bilan sur la saison 15 septembre – 15 mai.

    Parameters
    ----------
    hourly : pd.DataFrame
        Sortie de ``hourly_frame``.
    tin_c : float
        Consigne, base des degrés-heures demandés.
    tb_c : float
        Température d'équilibre, base de la correction climatique.

    Returns
    -------
    SeasonTotals
        Énergies en kWh et degrés-heures.
    """
    mask = heating_season_mask(hourly["month"].to_numpy(), hourly["day"].to_numpy())
    part = hourly.loc[mask]
    return SeasonTotals(
        hours=int(mask.sum()),
        transmission_kwh=_kwh(part["loss_tr_w"]),
        ventilation_kwh=_kwh(part["loss_vent_w"]),
        appliances_kwh=_kwh(part["appliances_w"]),
        people_kwh=_kwh(part["people_w"]),
        solar_kwh=_kwh(part["solar_w"]),
        deficit_kwh=_kwh(part["deficit_w"]),
        degree_hours_tin=degree_hours(hourly["temperature_c"].to_numpy(), tin_c, mask),
        degree_hours_tb=degree_hours(hourly["temperature_c"].to_numpy(), tb_c, mask),
    )


def monthly_kwh(hourly: pd.DataFrame) -> list[dict[str, float]]:
    """Énergies par mois calendaire, pour les graphiques.

    Parameters
    ----------
    hourly : pd.DataFrame
        Bilan horaire.

    Returns
    -------
    list of dict
        Douze mois, énergies en kWh.
    """
    rows: list[dict[str, float]] = []
    for month in range(1, 13):
        part = hourly.loc[hourly["month"] == month]
        rows.append(
            {
                "month": float(month),
                "transmission_kwh": _kwh(part["loss_tr_w"]),
                "ventilation_kwh": _kwh(part["loss_vent_w"]),
                "solar_kwh": _kwh(part["solar_w"]),
                "appliances_kwh": _kwh(part["appliances_w"]),
                "people_kwh": _kwh(part["people_w"]),
                "deficit_kwh": _kwh(part["deficit_w"]),
            }
        )
    return rows
