"""Nombre d'énergie primaire et classe BBR pour un immeuble."""

from __future__ import annotations

from building_energy.parameters import Case

# Limites de la classe, en part de l'exigence des bâtiments neufs.
# A est en dessous ou égal à 50 %, G est au-dessus de 235 %.
CLASS_LIMITS: tuple[tuple[str, float], ...] = (
    ("A", 0.50),
    ("B", 0.75),
    ("C", 1.00),
    ("D", 1.35),
    ("E", 1.80),
    ("F", 2.35),
)

# c du sujet : 0 chauffage urbain, 1 effet joule, 2 PAC COP 3, 3 PAC COP 5.
# Une PAC air-air ne fait pas l'eau chaude : l'eau chaude reste électrique.
HEATING_SYSTEMS: dict[int, dict[str, float | str | bool]] = {
    0: {
        "name": "district heating",
        "cop": 1.0,
        "weight_heat": "district",
        "dhw_on_heating_system": True,
    },
    1: {
        "name": "direct electric",
        "cop": 1.0,
        "weight_heat": "electricity",
        "dhw_on_heating_system": True,
    },
    2: {
        "name": "air-to-air heat pump, COP 3",
        "cop": 3.0,
        "weight_heat": "electricity",
        "dhw_on_heating_system": False,
    },
    3: {
        "name": "air-to-air heat pump, COP 5",
        "cop": 5.0,
        "weight_heat": "electricity",
        "dhw_on_heating_system": False,
    },
}


def new_building_limit(base_kwh_m2: float, specific_flow_l_s_m2: float) -> float:
    """Exigence EP des logements neufs, avec le supplément de ventilation.

    Le supplément BBR ne s'applique qu'au-dessus de 0,35 L/s·m², et il
    est plafonné à 0,60 L/s·m². En dessous, l'exigence reste le socle.

    Parameters
    ----------
    base_kwh_m2 : float
        Exigence de base, 75 kWh/m² pour un immeuble.
    specific_flow_l_s_m2 : float
        Débit d'air neuf de la ventilation mécanique.

    Returns
    -------
    float
        Exigence, kWh/m²·an.
    """
    if specific_flow_l_s_m2 <= 0.35:
        return base_kwh_m2
    extra = min(specific_flow_l_s_m2, 0.60) - 0.35
    return base_kwh_m2 + 40.0 * extra


def energy_class(ep_kwh_m2: float, limit_kwh_m2: float) -> str:
    """Classe A–G à partir du rapport à l'exigence des bâtiments neufs.

    Parameters
    ----------
    ep_kwh_m2 : float
        Nombre d'énergie primaire du bâtiment.
    limit_kwh_m2 : float
        Exigence d'un bâtiment neuf de même catégorie.

    Returns
    -------
    str
        Lettre A à G.
    """
    ratio = ep_kwh_m2 / limit_kwh_m2
    for name, ceiling in CLASS_LIMITS:
        if ratio <= ceiling:
            return name
    return "G"


def primary_energy(
    case: Case,
    heat_demand_kwh: float,
    atemp_m2: float,
) -> dict[str, float | str | bool]:
    """EP_pet du bâtiment entier, chauffage corrigé compris.

    Seul le chauffage est divisé par F_geo. L'électricité des communs
    et l'eau chaude ne le sont pas. Le COP ne s'applique qu'à la chaleur
    livrée par la PAC : l'énergie achetée est la chaleur divisée par le COP.

    Parameters
    ----------
    case : Case
        Facteurs de pondération, COP via le chiffre c, postes Sveby.
    heat_demand_kwh : float
        Chaleur de chauffage à fournir sur l'année corrigée.
    atemp_m2 : float
        Surface chauffée.

    Returns
    -------
    dict
        Détail du calcul et classe.
    """
    system = HEATING_SYSTEMS[case.heating_code]
    cop = float(system["cop"])
    if system["weight_heat"] == "district":
        weight_heat = case.vf_district_heating
    else:
        weight_heat = case.vf_electricity

    bought_heat = heat_demand_kwh / cop
    # F_geo allège les climats froids. Danderyd vaut 1,0 : le facteur
    # ne change pas le nombre, mais il reste dans la formule.
    weighted_heat = bought_heat * weight_heat / case.f_geo

    dhw_kwh = case.dhw_kwh_per_m2 * atemp_m2
    if system["dhw_on_heating_system"]:
        weighted_dhw = dhw_kwh * weight_heat
        dhw_carrier = str(system["name"])
    else:
        weighted_dhw = dhw_kwh * case.vf_electricity
        dhw_carrier = "direct electric"

    property_kwh = case.property_electricity_kwh_per_m2 * atemp_m2
    weighted_property = property_kwh * case.vf_electricity
    ep = (weighted_heat + weighted_dhw + weighted_property) / atemp_m2
    return {
        "system": str(system["name"]),
        "cop": cop,
        "dhw_carrier": dhw_carrier,
        "bought_heat_kwh": bought_heat,
        "dhw_kwh": dhw_kwh,
        "property_kwh": property_kwh,
        "weighted_heat": weighted_heat,
        "weighted_dhw": weighted_dhw,
        "weighted_property": weighted_property,
        "ep_kwh_m2": ep,
    }
