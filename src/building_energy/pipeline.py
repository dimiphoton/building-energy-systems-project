"""Enchaîne enveloppe, climat, bilan et classe énergétique."""

from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from building_energy.balance import (
    balance_temperature,
    design_power_w,
    hourly_frame,
    monthly_kwh,
    season_totals,
    time_constant_days,
)
from building_energy.climate import city_row, dvut_celsius
from building_energy.energy_class import (
    energy_class,
    new_building_limit,
    primary_energy,
)
from building_energy.envelope import Envelope, build_envelope
from building_energy.parameters import Case
from building_energy.ventilation import Ventilation, build_ventilation


def _corrected(
    case: Case,
    envelope: Envelope,
    h_tr: float,
    h_vent: float,
    appliance_w: float,
    people_w: float,
    climate_2017: pd.DataFrame,
    climate_normal: pd.DataFrame,
) -> dict[str, object]:
    """Déficit 2017, facteur de correction, et simulation de l'année type."""
    h_total = h_tr + h_vent
    tb = balance_temperature(case.tin_c, appliance_w, h_total)
    hourly_2017 = hourly_frame(
        climate_2017, case, envelope, h_tr, h_vent, appliance_w, people_w
    )
    hourly_normal = hourly_frame(
        climate_normal, case, envelope, h_tr, h_vent, appliance_w, people_w
    )
    season_2017 = season_totals(hourly_2017, case.tin_c, tb)
    season_normal = season_totals(hourly_normal, case.tin_c, tb)
    # Correction d'année normale des cours : on met le déficit de 2017
    # à l'échelle du rapport des degrés-heures, base = Tb.
    factor = season_normal.degree_hours_tb / season_2017.degree_hours_tb
    corrected_kwh = season_2017.deficit_kwh * factor
    return {
        "tb_c": tb,
        "h_total": h_total,
        "factor": factor,
        "corrected_kwh": corrected_kwh,
        "season_2017": asdict(season_2017),
        "season_normal": asdict(season_normal),
        "hourly_2017": hourly_2017,
        "hourly_normal": hourly_normal,
    }


def _class_block(case: Case, heat_kwh: float, atemp: float, flow: float) -> dict[str, object]:
    detail = primary_energy(case, heat_kwh, atemp)
    limit = new_building_limit(case.ep_new_limit, flow)
    ep = float(detail["ep_kwh_m2"])
    detail["limit_kwh_m2"] = limit
    detail["energy_class"] = energy_class(ep, limit)
    detail["ratio_to_new_building"] = ep / limit
    return detail


def run(
    case: Case,
    dvut: pd.DataFrame,
    climate_2017: pd.DataFrame,
    climate_normal: pd.DataFrame,
) -> dict[str, object]:
    """Calcule le cas complet.

    Parameters
    ----------
    case : Case
        Paramètres, y compris la date de naissance.
    dvut : pd.DataFrame
        Table DVUT Boverket.
    climate_2017, climate_normal : pd.DataFrame
        Températures horaires de l'année du sujet et de l'année type.

    Returns
    -------
    dict
        Résultats sérialisables, plus deux DataFrame horaires sous les clés
        ``hourly_2017`` et ``hourly_normal`` (retirées avant l'export JSON).

    Raises
    ------
    ValueError
        Si l'année du fichier ou la ville ne correspondent pas au cas.
    """
    years = set(climate_2017["year"].astype(int).unique())
    if years != {case.weather_year}:
        raise ValueError(
            f"le fichier 2017 contient les années {sorted(years)}, "
            f"le sujet demande {case.weather_year}"
        )

    place = city_row(dvut, case.cd)
    city = str(place["Ort"])
    if city != "Danderyd":
        raise ValueError(
            f"La ville n° {case.cd} est {city}. Le facteur F_geo du fichier "
            "de config est celui de Danderyd : il faut le mettre à jour."
        )

    envelope = build_envelope(case)
    ventilation = build_ventilation(case, envelope.volume_m3, envelope.atemp_m2)
    appliance_w = case.appliances_w_per_m2 * envelope.atemp_m2
    people_w = case.n_people * case.person_heat_w
    h_total = envelope.h_tr + ventilation.h_vent
    tau_days = time_constant_days(envelope.capacity_j_per_k, h_total)
    n_days, dvut_c = dvut_celsius(place, tau_days)
    gross_w = design_power_w(h_total, case.tin_c, dvut_c)
    # Le sujet demande la puissance sans apports, puis dit de garder
    # quand même les appareils. On publie les deux.
    net_w = gross_w - appliance_w

    base = _corrected(
        case,
        envelope,
        envelope.h_tr,
        ventilation.h_vent,
        appliance_w,
        people_w,
        climate_2017,
        climate_normal,
    )
    official = _class_block(
        case, float(base["corrected_kwh"]), envelope.atemp_m2, ventilation.specific_flow_l_s_m2
    )
    direct = _class_block(
        case,
        float(base["season_normal"]["deficit_kwh"]),  # type: ignore[index]
        envelope.atemp_m2,
        ventilation.specific_flow_l_s_m2,
    )

    delta = case.tin_c - dvut_c
    shares = {
        "walls": envelope.ua_wall * delta,
        "windows": envelope.ua_window * delta,
        "doors": envelope.ua_door * delta,
        "roof": envelope.ua_roof * delta,
        "foundation": envelope.ua_foundation * delta,
        "balconies": envelope.psi_l * delta,
        "ventilation": ventilation.h_vent * delta,
    }

    scenarios = _scenarios(
        case,
        envelope,
        ventilation,
        appliance_w,
        people_w,
        climate_2017,
        climate_normal,
        float(base["corrected_kwh"]),
    )

    return {
        "person": case.name,
        "birth_year": case.birth_year,
        "birth_month": case.birth_month,
        "birth_day": case.birth_day,
        "digits": {"a": case.a, "b": case.b, "c": case.c, "d": case.d},
        "city": city,
        "city_number": case.cd,
        "latitude": float(place["Latitud"]),
        "longitude": float(place["Longitud"]),
        "weather_year": case.weather_year,
        "tin_c": case.tin_c,
        "dvut_c": dvut_c,
        "dvut_days": n_days,
        "time_constant_days": tau_days,
        "u_wall": envelope.u_wall,
        "lambda_mix": envelope.lambda_mix,
        "r_wall": envelope.r_wall,
        "um": envelope.um,
        "envelope": _envelope_dict(envelope),
        "ventilation": _ventilation_dict(ventilation),
        "appliance_w": appliance_w,
        "people_w": people_w,
        "tb_c": float(base["tb_c"]),
        "power_without_gains_w": gross_w,
        "power_with_appliances_w": net_w,
        "design_shares_w": shares,
        "season_2017": base["season_2017"],
        "season_normal_direct": base["season_normal"],
        "correction_factor": float(base["factor"]),
        "heat_deficit_corrected_kwh": float(base["corrected_kwh"]),
        "monthly_2017": monthly_kwh(base["hourly_2017"]),  # type: ignore[arg-type]
        "monthly_normal": monthly_kwh(base["hourly_normal"]),  # type: ignore[arg-type]
        "energy_class": official,
        "energy_class_direct_normal_year": direct,
        "scenarios": scenarios,
        "hourly_2017": base["hourly_2017"],
        "hourly_normal": base["hourly_normal"],
    }


def _scenarios(
    case: Case,
    envelope: Envelope,
    ventilation: Ventilation,
    appliance_w: float,
    people_w: float,
    climate_2017: pd.DataFrame,
    climate_normal: pd.DataFrame,
    base_corrected_kwh: float,
) -> list[dict[str, object]]:
    """Trois gestes simples, plus les trois ensemble."""
    h_tr_windows = envelope.h_tr + (case.measure_window_u - case.u_window) * envelope.window_m2
    h_tr_bridge = envelope.h_tr + (case.measure_psi - case.psi_balcony) * envelope.bridge_length_m
    h_tr_both = (
        envelope.h_tr
        + (case.measure_window_u - case.u_window) * envelope.window_m2
        + (case.measure_psi - case.psi_balcony) * envelope.bridge_length_m
    )
    h_recovery = (
        ventilation.h_mech * (1.0 - case.measure_heat_recovery) + ventilation.h_leak
    )
    variants = [
        ("Triple glazing, U = 1.0 W/(m²·K)", h_tr_windows, ventilation.h_vent),
        ("Heat recovery of 80 % on the exhaust air", envelope.h_tr, h_recovery),
        ("Balcony thermal break, Ψ = 0.20 W/(m·K)", h_tr_bridge, ventilation.h_vent),
        ("All three together", h_tr_both, h_recovery),
    ]
    rows: list[dict[str, object]] = []
    for name, h_tr, h_vent in variants:
        corrected = _corrected(
            case,
            envelope,
            h_tr,
            h_vent,
            appliance_w,
            people_w,
            climate_2017,
            climate_normal,
        )
        heat = float(corrected["corrected_kwh"])
        block = _class_block(case, heat, envelope.atemp_m2, ventilation.specific_flow_l_s_m2)
        rows.append(
            {
                "name": name,
                "heat_deficit_corrected_kwh": heat,
                "saved_kwh": base_corrected_kwh - heat,
                "um": h_tr / envelope.aom_m2,
                "ep_kwh_m2": float(block["ep_kwh_m2"]),
                "energy_class": str(block["energy_class"]),
            }
        )
    return rows


def _envelope_dict(envelope: Envelope) -> dict[str, float]:
    return {
        "floor_area_m2": envelope.floor_area_m2,
        "atemp_m2": envelope.atemp_m2,
        "volume_m3": envelope.volume_m3,
        "facade_gross_m2": envelope.facade_gross_m2,
        "wall_opaque_m2": envelope.wall_opaque_m2,
        "window_m2": envelope.window_m2,
        "door_m2": envelope.door_m2,
        "aom_m2": envelope.aom_m2,
        "bridge_length_m": envelope.bridge_length_m,
        "ua_wall": envelope.ua_wall,
        "ua_window": envelope.ua_window,
        "ua_door": envelope.ua_door,
        "ua_roof": envelope.ua_roof,
        "ua_foundation": envelope.ua_foundation,
        "psi_l": envelope.psi_l,
        "h_tr": envelope.h_tr,
        "capacity_j_per_k": envelope.capacity_j_per_k,
        "window_south_m2": envelope.window_south_m2,
        "window_north_m2": envelope.window_north_m2,
        "window_east_m2": envelope.window_east_m2,
        "window_west_m2": envelope.window_west_m2,
    }


def _ventilation_dict(ventilation: Ventilation) -> dict[str, float]:
    return {
        "q_mech_m3_s": ventilation.q_mech_m3_s,
        "q_leak_m3_s": ventilation.q_leak_m3_s,
        "q_total_m3_s": ventilation.q_total_m3_s,
        "h_mech": ventilation.h_mech,
        "h_leak": ventilation.h_leak,
        "h_vent": ventilation.h_vent,
        "specific_flow_l_s_m2": ventilation.specific_flow_l_s_m2,
    }


def json_ready(result: dict[str, object]) -> dict[str, object]:
    """Retire les tableaux horaires, qui ne vont pas dans le JSON.

    Parameters
    ----------
    result : dict
        Sortie de ``run``.

    Returns
    -------
    dict
        Copie sans les DataFrame.
    """
    return {key: value for key, value in result.items() if not key.startswith("hourly_")}
