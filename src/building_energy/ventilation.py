"""Débit d'air à partir du CO2, fuites, conductance de ventilation."""

from __future__ import annotations

from dataclasses import dataclass

from building_energy.parameters import Case


@dataclass(frozen=True)
class Ventilation:
    """Débits et conductance de ventilation."""

    q_mech_m3_s: float
    q_leak_m3_s: float
    q_total_m3_s: float
    h_mech: float
    h_leak: float
    h_vent: float
    specific_flow_l_s_m2: float


def mechanical_flow_m3_s(
    n_people: int,
    co2_l_s_per_person: float,
    indoor_ppm: float,
    outdoor_ppm: float,
) -> float:
    """Débit d'air neuf qui maintient le CO2 intérieur à la limite.

    En régime permanent, le CO2 produit égale le CO2 évacué :
    q * (C_in - C_out) = production.

    Parameters
    ----------
    n_people : int
        Occupants dans tout l'immeuble.
    co2_l_s_per_person : float
        Production, litres par seconde et par personne.
    indoor_ppm : float
        Concentration intérieure maximale.
    outdoor_ppm : float
        Concentration extérieure.

    Returns
    -------
    float
        Débit volumique, m³/s.

    Raises
    ------
    ValueError
        Si l'écart de concentration n'est pas positif.
    """
    if indoor_ppm <= outdoor_ppm:
        raise ValueError("le CO2 intérieur doit dépasser le CO2 extérieur")
    produced_m3_s = n_people * co2_l_s_per_person * 1e-3
    delta = (indoor_ppm - outdoor_ppm) * 1e-6
    return produced_m3_s / delta


def leakage_flow_m3_s(air_changes_per_hour: float, volume_m3: float) -> float:
    """Débit de fuite à partir du taux de renouvellement.

    Parameters
    ----------
    air_changes_per_hour : float
        Renouvellement, h⁻¹.
    volume_m3 : float
        Volume intérieur chauffé.

    Returns
    -------
    float
        Débit, m³/s.
    """
    return air_changes_per_hour * volume_m3 / 3600.0


def conductance_w_per_k(flow_m3_s: float, rho: float, cp: float) -> float:
    """Conductance ρ·cp·q, sans récupération de chaleur.

    Parameters
    ----------
    flow_m3_s : float
        Débit d'air extérieur, m³/s.
    rho : float
        Masse volumique de l'air, kg/m³.
    cp : float
        Capacité thermique massique, J/(kg·K).

    Returns
    -------
    float
        Conductance, W/K.
    """
    return rho * cp * flow_m3_s


def build_ventilation(case: Case, volume_m3: float, atemp_m2: float) -> Ventilation:
    """Ventilation mécanique d'extraction plus les fuites.

    Les deux débits sont additionnés. C'est le cas défavorable pour
    dimensionner le chauffage : l'extraction ne récupère pas la chaleur,
    et les fuites s'y ajoutent. Le sujet demande les deux.

    Parameters
    ----------
    case : Case
        Occupants, CO2, taux de fuite, propriétés de l'air.
    volume_m3 : float
        Volume chauffé.
    atemp_m2 : float
        Surface chauffée, pour le débit spécifique.

    Returns
    -------
    Ventilation
        Débits et conductances.
    """
    q_mech = mechanical_flow_m3_s(
        case.n_people,
        case.co2_per_person_l_s,
        case.co2_indoor_ppm,
        case.co2_outdoor_ppm,
    )
    q_leak = leakage_flow_m3_s(case.air_leakage_ach, volume_m3)
    h_mech = conductance_w_per_k(q_mech, case.rho_air, case.cp_air)
    h_leak = conductance_w_per_k(q_leak, case.rho_air, case.cp_air)
    return Ventilation(
        q_mech_m3_s=q_mech,
        q_leak_m3_s=q_leak,
        q_total_m3_s=q_mech + q_leak,
        h_mech=h_mech,
        h_leak=h_leak,
        h_vent=h_mech + h_leak,
        specific_flow_l_s_m2=(q_mech * 1000.0) / atemp_m2,
    )
