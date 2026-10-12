"""Tests du bilan : formules isolées, puis le cas Danderyd."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from building_energy.balance import balance_temperature, design_power_w, hourly_frame
from building_energy.climate import (
    city_row,
    degree_hours,
    dvut_celsius,
    heating_season_mask,
    load_dvut,
    load_temperature,
)
from building_energy.energy_class import energy_class, new_building_limit, primary_energy
from building_energy.envelope import build_envelope, wall_u_value
from building_energy.parameters import load_case, month_day_digits
from building_energy.pipeline import run
from building_energy.ventilation import mechanical_flow_m3_s

ROOT = Path(__file__).resolve().parents[1]


def test_birth_date_digits_match_the_brief_example() -> None:
    assert month_day_digits(10, 29) == (1, 0, 2, 9)
    assert month_day_digits(8, 29) == (0, 8, 2, 9)


def test_case_from_config_is_august_1986() -> None:
    case = load_case(ROOT / "config" / "case.toml")
    assert (case.a, case.b, case.c, case.d) == (0, 8, 2, 9)
    assert case.cd == 29
    assert case.stories == 3
    assert case.tin_c == 22
    assert case.n_people == 38
    assert case.window_area_m2 == 129
    assert case.n_doors == 24
    assert case.weather_year == 2017
    assert case.appliances_w_per_m2 == 4


def test_city_numbers_follow_the_smhi_list() -> None:
    dvut = load_dvut(ROOT / "data" / "reference" / "dvut_1991_2020.csv")
    assert str(city_row(dvut, 14)["Ort"]) == "Bjurholm"
    assert str(city_row(dvut, 29)["Ort"]) == "Danderyd"


def test_wall_u_value_by_hand() -> None:
    case = load_case(ROOT / "config" / "case.toml")
    lambda_mix, resistance, u_value = wall_u_value(case)
    # 0,925 × 0,037 + 0,075 × 0,14, puis les résistances en série.
    expected_lambda = 0.925 * 0.037 + 0.075 * 0.14
    expected_r = 0.13 + 0.013 / 0.25 + 0.095 / expected_lambda + 0.20
    assert lambda_mix == pytest.approx(expected_lambda)
    assert resistance == pytest.approx(expected_r)
    assert u_value == pytest.approx(1 / expected_r)
    assert u_value == pytest.approx(0.399, abs=0.001)


def test_co2_flow_for_38_people() -> None:
    flow = mechanical_flow_m3_s(38, 0.005, 1000, 350)
    assert flow == pytest.approx(0.19e-3 / 650e-6)


def test_um_is_transmission_over_aom() -> None:
    case = load_case(ROOT / "config" / "case.toml")
    envelope = build_envelope(case)
    h_tr = (
        envelope.ua_wall
        + envelope.ua_window
        + envelope.ua_door
        + envelope.ua_roof
        + envelope.ua_foundation
        + envelope.psi_l
    )
    assert envelope.h_tr == pytest.approx(h_tr)
    assert envelope.um == pytest.approx(h_tr / envelope.aom_m2)
    assert envelope.atemp_m2 == 1350
    assert envelope.bridge_length_m == 180


def test_balance_temperature_and_design_power() -> None:
    assert balance_temperature(22, 5400, 1500) == pytest.approx(22 - 5400 / 1500)
    assert design_power_w(1500, 22, -11) == pytest.approx(1500 * 33)


def test_heating_season_is_mid_september_to_mid_may() -> None:
    climate = load_temperature(ROOT / "data" / "processed" / "danderyd_2017_temperature.csv")
    mask = heating_season_mask(climate["month"].to_numpy(), climate["day"].to_numpy())
    assert int(mask.sum()) == 5832


def test_degree_hours_ignore_hours_above_the_base() -> None:
    temperature = np.array([0.0, 10.0, 20.0])
    mask = np.array([True, True, True])
    assert degree_hours(temperature, 15, mask) == pytest.approx(15 + 5 + 0)


def test_one_cold_hour_needs_the_full_loss_minus_gains() -> None:
    case = load_case(ROOT / "config" / "case.toml")
    envelope = build_envelope(case)
    climate = pd.DataFrame(
        {
            "year": [2017],
            "month": [1],
            "day": [15],
            "hour": [0],
            "temperature_c": [0.0],
        }
    )
    frame = hourly_frame(climate, case, envelope, h_tr=100, h_vent=50, appliance_w=10, people_w=5)
    # Pertes 150 × 22, moins 10, moins 5, moins le solaire de janvier.
    assert frame.loc[0, "deficit_w"] == pytest.approx(
        150 * 22 - 10 - 5 - frame.loc[0, "solar_w"]
    )


def test_energy_class_boundaries() -> None:
    assert energy_class(37.5, 75) == "A"
    assert energy_class(37.6, 75) == "B"
    assert energy_class(75, 75) == "C"
    assert energy_class(75.1, 75) == "D"
    assert energy_class(200, 75) == "G"
    assert new_building_limit(75, 0.20) == 75
    assert new_building_limit(75, 0.50) == pytest.approx(75 + 40 * 0.15)


def test_primary_energy_divides_only_the_heat_by_cop_and_fgeo() -> None:
    case = load_case(ROOT / "config" / "case.toml")
    detail = primary_energy(case, heat_demand_kwh=3000, atemp_m2=100)
    # COP 3, F_geo 1, électricité 1,8. Eau chaude et communs en plus.
    assert detail["bought_heat_kwh"] == pytest.approx(1000)
    assert float(detail["weighted_heat"]) == pytest.approx(1800)
    assert float(detail["ep_kwh_m2"]) == pytest.approx(
        (1800 + 25 * 100 * 1.8 + 15 * 100 * 1.8) / 100
    )


def test_full_case_runs_for_danderyd() -> None:
    case = load_case(ROOT / "config" / "case.toml")
    result = run(
        case,
        load_dvut(ROOT / "data" / "reference" / "dvut_1991_2020.csv"),
        load_temperature(ROOT / "data" / "processed" / "danderyd_2017_temperature.csv"),
        load_temperature(ROOT / "data" / "processed" / "danderyd_normal_1991_2020_temperature.csv"),
    )
    assert result["city"] == "Danderyd"
    assert result["weather_year"] == 2017
    assert 0.4 < float(result["um"]) < 1.0
    assert float(result["power_without_gains_w"]) > float(result["power_with_appliances_w"]) > 0
    assert float(result["tb_c"]) < float(result["tin_c"])
    assert float(result["heat_deficit_corrected_kwh"]) > 0
    assert result["energy_class"]["energy_class"] in list("ABCDEFG")
    # Le déficit horaire plafonné est au moins la somme algébrique pertes − apports.
    season = result["season_2017"]
    gross = float(season["transmission_kwh"]) + float(season["ventilation_kwh"])
    gains = (
        float(season["appliances_kwh"])
        + float(season["people_kwh"])
        + float(season["solar_kwh"])
    )
    assert float(season["hours"]) == 5832
    assert float(season["deficit_kwh"]) >= gross - gains - 1.0


def test_nearest_dvut_day_is_capped() -> None:
    dvut = load_dvut(ROOT / "data" / "reference" / "dvut_1991_2020.csv")
    row = city_row(dvut, 29)
    days, temperature = dvut_celsius(row, 0.2)
    assert days == 1
    assert temperature == pytest.approx(float(row["1-dygn"]))
    days_long, temperature_long = dvut_celsius(row, 40)
    assert days_long == 30
    assert temperature_long == pytest.approx(float(row["30-dygn"]))
