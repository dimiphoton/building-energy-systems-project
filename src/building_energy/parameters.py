"""Lecture du cas : date de naissance et hypothèses du fichier TOML."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path


def month_day_digits(month: int, day: int) -> tuple[int, int, int, int]:
    """Découpe le mois et le jour en chiffres a, b, c, d.

    L'exemple du sujet (octobre = 10, jour = 29) donne a=1, b=0, c=2, d=9.
    Août s'écrit 08 : a=0, b=8.

    Parameters
    ----------
    month : int
        Mois, de 1 à 12.
    day : int
        Jour du mois, de 1 à 31.

    Returns
    -------
    tuple of int
        a, b, c, d.

    Raises
    ------
    ValueError
        Si le mois ou le jour est hors plage.
    """
    if not 1 <= month <= 12:
        raise ValueError(f"mois invalide : {month}")
    if not 1 <= day <= 31:
        raise ValueError(f"jour invalide : {day}")
    a, b = divmod(month, 10)
    c, d = divmod(day, 10)
    return a, b, c, d


@dataclass(frozen=True)
class Case:
    """Toutes les entrées numériques du calcul.

    Les grandeurs fixées par le sujet (plan, U donnés, débits de CO2)
    ont une valeur par défaut. Celles qu'on a dû choisir viennent du TOML.
    """

    name: str
    birth_year: int
    birth_month: int
    birth_day: int
    lambda_insulation: float
    lambda_wood: float
    lambda_gypsum: float
    r_si: float
    person_heat_w: float
    rho_air: float
    cp_air: float
    active_depth_m: float
    f_geo: float
    ep_new_limit: float
    vf_electricity: float
    vf_district_heating: float
    dhw_kwh_per_m2: float
    property_electricity_kwh_per_m2: float
    measure_window_u: float
    measure_heat_recovery: float
    measure_psi: float
    # Données imposées par le sujet.
    floor_length_m: float = 45.0
    floor_width_m: float = 10.0
    story_height_m: float = 2.5
    u_foundation: float = 0.23
    slab_thickness_m: float = 0.20
    intermediate_floor_m: float = 0.16
    u_roof: float = 0.16
    roof_concrete_m: float = 0.12
    u_window: float = 2.9
    g_window: float = 0.7
    krad_window: float = 0.5
    window_south_share: float = 0.10
    window_north_share: float = 0.10
    window_east_share: float = 0.40
    window_west_share: float = 0.40
    u_door: float = 2.0
    door_area_m2: float = 2.1
    psi_balcony: float = 0.6
    air_leakage_ach: float = 0.05
    co2_per_person_l_s: float = 0.005
    co2_indoor_ppm: float = 1000.0
    co2_outdoor_ppm: float = 350.0
    rho_concrete: float = 2300.0
    c_concrete: float = 900.0
    rho_gypsum: float = 650.0
    c_gypsum: float = 720.0
    internal_concrete_wall_m: float = 130.0
    internal_stud_wall_m: float = 120.0
    concrete_wall_thickness_m: float = 0.16
    gypsum_board_m: float = 0.013
    stud_width_m: float = 0.045
    stud_spacing_m: float = 0.60
    insulation_thickness_m: float = 0.095
    r_outdoor: float = 0.20

    @property
    def a(self) -> int:
        """Chiffre des dizaines du mois."""
        return month_day_digits(self.birth_month, self.birth_day)[0]

    @property
    def b(self) -> int:
        """Chiffre des unités du mois."""
        return month_day_digits(self.birth_month, self.birth_day)[1]

    @property
    def c(self) -> int:
        """Chiffre des dizaines du jour."""
        return month_day_digits(self.birth_month, self.birth_day)[2]

    @property
    def d(self) -> int:
        """Chiffre des unités du jour."""
        return month_day_digits(self.birth_month, self.birth_day)[3]

    @property
    def ab(self) -> int:
        """Mois en nombre entier (08 → 8)."""
        return 10 * self.a + self.b

    @property
    def cd(self) -> int:
        """Jour en nombre entier, aussi numéro de ville."""
        return 10 * self.c + self.d

    @property
    def stories(self) -> int:
        """Nombre d'étages : 3 + a."""
        return 3 + self.a

    @property
    def tin_c(self) -> float:
        """Température intérieure de consigne, °C : 20 + c."""
        return 20.0 + self.c

    @property
    def appliances_w_per_m2(self) -> float:
        """Apports des appareils, W/m² Atemp : 2 + c."""
        return 2.0 + self.c

    @property
    def n_people(self) -> int:
        """Nombre d'occupants : 30 + ab."""
        return 30 + self.ab

    @property
    def window_area_m2(self) -> float:
        """Surface vitrée totale : 100 + cd."""
        return 100.0 + self.cd

    @property
    def n_doors(self) -> int:
        """Nombre de portes : 15 + d."""
        return 15 + self.d

    @property
    def weather_year(self) -> int:
        """Année du fichier climatique Sveby : 2015 + a + a + c."""
        return 2015 + self.a + self.a + self.c

    @property
    def heating_code(self) -> int:
        """Type de chauffage, égal au chiffre c."""
        return self.c


def load_case(path: Path) -> Case:
    """Construit un cas à partir du fichier TOML.

    Parameters
    ----------
    path : Path
        Fichier ``case.toml``.

    Returns
    -------
    Case
        Paramètres prêts pour le calcul.
    """
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    person = raw["person"]
    materials = raw["materials"]
    gains = raw["gains"]
    air = raw["air"]
    mass = raw["thermal_mass"]
    energy = raw["energy_class"]
    measures = raw["measures"]
    return Case(
        name=str(person["name"]),
        birth_year=int(person["birth_year"]),
        birth_month=int(person["birth_month"]),
        birth_day=int(person["birth_day"]),
        lambda_insulation=float(materials["lambda_insulation"]),
        lambda_wood=float(materials["lambda_wood"]),
        lambda_gypsum=float(materials["lambda_gypsum"]),
        r_si=float(materials["r_si"]),
        person_heat_w=float(gains["person_heat_w"]),
        rho_air=float(air["rho"]),
        cp_air=float(air["cp"]),
        active_depth_m=float(mass["active_depth_m"]),
        f_geo=float(energy["f_geo"]),
        ep_new_limit=float(energy["ep_new_limit"]),
        vf_electricity=float(energy["vf_electricity"]),
        vf_district_heating=float(energy["vf_district_heating"]),
        dhw_kwh_per_m2=float(energy["dhw_kwh_per_m2"]),
        property_electricity_kwh_per_m2=float(energy["property_electricity_kwh_per_m2"]),
        measure_window_u=float(measures["window_u"]),
        measure_heat_recovery=float(measures["heat_recovery"]),
        measure_psi=float(measures["psi"]),
    )
