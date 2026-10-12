"""Point d'entrée : calcule le cas et écrit le rapport et les graphes."""

from __future__ import annotations

import argparse
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from building_energy.climate import load_dvut, load_temperature
from building_energy.parameters import load_case
from building_energy.pipeline import json_ready, run
from building_energy.plots import write_plots
from building_energy.report import render_report

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bilan thermique ETA013 à partir de la date de naissance."
    )
    parser.add_argument("--config", type=Path, default=Path("config/case.toml"))
    parser.add_argument("--dvut", type=Path, default=Path("data/reference/dvut_1991_2020.csv"))
    parser.add_argument(
        "--climate-2017",
        type=Path,
        default=Path("data/processed/danderyd_2017_temperature.csv"),
    )
    parser.add_argument(
        "--climate-normal",
        type=Path,
        default=Path("data/processed/danderyd_normal_1991_2020_temperature.csv"),
    )
    parser.add_argument("--report", type=Path, default=Path("docs/report/assignment-report.md"))
    parser.add_argument("--results", type=Path, default=Path("data/processed/results.json"))
    parser.add_argument("--figures", type=Path, default=Path("pictures/experiments"))
    return parser


def _copy_figures(source: Path) -> None:
    """Recopie les graphes là où le README et les diapositives les attendent."""
    presentations = Path("pictures/presentations")
    readme = Path("pictures/readme")
    presentations.mkdir(parents=True, exist_ok=True)
    readme.mkdir(parents=True, exist_ok=True)
    for name in (
        "duration-temperature.png",
        "monthly-heating.png",
        "design-power-shares.png",
        "energy-class.png",
    ):
        shutil.copy(source / name, presentations / name)
    shutil.copy(source / "design-power-shares.png", readme / "design-power-shares.png")
    shutil.copy(source / "monthly-heating.png", readme / "monthly-heating.png")


def _append_run_log(result: dict[str, object]) -> None:
    path = Path("experiments/runs.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    energy = result["energy_class"]
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "city": result["city"],
        "weather_year": result["weather_year"],
        "um": result["um"],
        "tb_c": result["tb_c"],
        "dvut_c": result["dvut_c"],
        "heat_deficit_corrected_kwh": result["heat_deficit_corrected_kwh"],
        "ep_kwh_m2": energy["ep_kwh_m2"],  # type: ignore[index]
        "energy_class": energy["energy_class"],  # type: ignore[index]
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _print_checklist(result: dict[str, object]) -> None:
    energy = result["energy_class"]
    season = result["season_2017"]
    print(f"City: {result['city']}")
    print(f"DVUT: {float(result['dvut_c']):.1f} °C ({result['dvut_days']}-day)")
    print(f"Tin: {float(result['tin_c']):.1f} °C")
    print(f"Um: {float(result['um']):.3f} W/(m²·K)")
    print(f"Tb: {float(result['tb_c']):.2f} °C")
    print(f"Power without internal gains: {float(result['power_without_gains_w']) / 1000:.1f} kW")
    print(f"Power with appliances: {float(result['power_with_appliances_w']) / 1000:.1f} kW")
    print(f"Heat deficit 2017: {float(season['deficit_kwh']) / 1000:.2f} MWh")  # type: ignore[index]
    print(f"Degree hours (Tin): {float(season['degree_hours_tin']):.0f} °C·h")  # type: ignore[index]
    print(
        "Heat deficit, normal-year corrected: "
        f"{float(result['heat_deficit_corrected_kwh']) / 1000:.2f} MWh"
    )
    print(
        f"Primary energy: {float(energy['ep_kwh_m2']):.1f} kWh/m²·year, "  # type: ignore[index]
        f"class {energy['energy_class']}"  # type: ignore[index]
    )


def main() -> None:
    """Calcule le cas décrit par le fichier de config."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = _build_parser().parse_args()
    for path in (args.config, args.dvut, args.climate_2017, args.climate_normal):
        if not path.is_file():
            raise FileNotFoundError(f"fichier introuvable : {path}")

    case = load_case(args.config)
    result = run(
        case,
        load_dvut(args.dvut),
        load_temperature(args.climate_2017),
        load_temperature(args.climate_normal),
    )
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.results.write_text(
        json.dumps(json_ready(result), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    args.report.write_text(render_report(result), encoding="utf-8")
    write_plots(result, args.figures)
    _copy_figures(args.figures)
    _append_run_log(result)
    _print_checklist(result)
    logger.info("Rapport écrit dans %s", args.report)


if __name__ == "__main__":
    main()
