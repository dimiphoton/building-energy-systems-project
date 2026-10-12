"""Rapport en anglais, celui qu'on peut rendre pour le cours ETA013."""

from __future__ import annotations


def _n(value: float, digits: int = 1) -> str:
    return f"{value:,.{digits}f}"


def render_report(result: dict[str, object]) -> str:
    """Met les résultats en phrases, avec les cases demandées par le sujet.

    Parameters
    ----------
    result : dict
        Sortie de ``pipeline.run`` (les DataFrame horaires ne sont pas lus).

    Returns
    -------
    str
        Rapport Markdown.
    """
    env = result["envelope"]
    vent = result["ventilation"]
    season = result["season_2017"]
    normal = result["season_normal_direct"]
    energy = result["energy_class"]
    digits = result["digits"]
    shares = result["design_shares_w"]
    gross_kw = float(result["power_without_gains_w"]) / 1000.0
    net_kw = float(result["power_with_appliances_w"]) / 1000.0
    app_kw = float(result["appliance_w"]) / 1000.0
    people_kw = float(result["people_w"]) / 1000.0
    lines: list[str] = []
    add = lines.append

    add(f"# Building energy study — {result['city']}")
    add("")
    add(f"**{result['person']}**, birth year {result['birth_year']}.")
    add("Course ETA013, Building Energy Systems, University of Gävle.")
    add("The birth date is 29 August 1986. Written as year, month, day")
    add("(1986, 08, 29) it gives a = 0, b = 8, c = 2, d = 9, ab = 8, cd = 29,")
    add("the same split as the example in the brief (1985, 10, 29 → a = 1, b = 0, c = 2, d = 9).")
    add("")
    add("## Answers the brief asks for")
    add("")
    add("| | |")
    add("|---|---|")
    add(f"| City | {result['city']} (city number {result['city_number']}) |")
    add(f"| DVUT | {_n(float(result['dvut_c']))} °C ({result['dvut_days']}-day value) |")
    add(f"| Tin | {_n(float(result['tin_c']))} °C |")
    add(f"| Average heat transfer coefficient Um | {_n(float(result['um']), 3)} W/(m²·K) |")
    add(f"| Balance temperature Tb | {_n(float(result['tb_c']), 2)} °C |")
    add(f"| Required heating power, no internal gains | {_n(gross_kw)} kW |")
    add(f"| Same power with appliance gains only | {_n(net_kw)} kW |")
    add(f"| Heat gain, people | {_n(people_kw)} kW, {_n(float(season['people_kwh']) / 1000)} MWh over the heating season |")  # type: ignore[index]
    add(f"| Heat gain, appliances | {_n(app_kw)} kW, {_n(float(season['appliances_kwh']) / 1000)} MWh over the heating season |")  # type: ignore[index]
    add(f"| Solar heat gain | {_n(float(season['solar_kwh']) / 1000)} MWh over the heating season |")  # type: ignore[index]
    add(f"| Heat loss, transmission | {_n(float(season['transmission_kwh']) / 1000)} MWh |")  # type: ignore[index]
    add(f"| Heat loss, ventilation | {_n(float(season['ventilation_kwh']) / 1000)} MWh |")  # type: ignore[index]
    add(f"| Heat deficit, weather year {result['weather_year']} | {_n(float(season['deficit_kwh']) / 1000)} MWh |")  # type: ignore[index]
    add(f"| Heating-season degree hours (base Tin) | {_n(float(season['degree_hours_tin']), 0)} °C·h |")  # type: ignore[index]
    add(
        f"| Heat deficit after normal-year correction | "
        f"{_n(float(result['heat_deficit_corrected_kwh']) / 1000)} MWh |"
    )
    add(
        f"| Primary energy number | {_n(float(energy['ep_kwh_m2']))} kWh/m²·year |"  # type: ignore[index]
    )
    add(f"| Energy class | {energy['energy_class']} |")  # type: ignore[index]
    add("")
    add("The duration diagram is `pictures/experiments/duration-temperature.png`.")
    add("The typeset submission is `docs/report/assignment-report.pdf`,")
    add("compiled from `docs/report/assignment-report.tex`.")
    add("")
    add("## What was asked, in plain words")
    add("")
    add("A housing association has one multi-family building that cannot keep")
    add("20 °C indoors when the weather is really cold. The brief asks for the")
    add("radiator power on a design day, the balance temperature, the average")
    add("U-value, the heating season in the city's weather file, and the energy")
    add("class once that year has been brought back to a normal climate.")
    add("")
    add(
        f"Indoor setpoint Tin = 20 + c = {_n(float(result['tin_c']))} °C. "
        f"The heating system is {energy['system']}."  # type: ignore[index]
    )
    add("")
    add("## The building")
    add("")
    add(
        f"Three storeys (3 + a), plan 10 × 45 m. "
        f"Heated floor area Atemp = {_n(float(env['atemp_m2']), 0)} m². "  # type: ignore[index]
        f"Storey height 2.5 m, so the heated volume is {_n(float(env['volume_m3']), 0)} m³. "  # type: ignore[index]
        "The brief gives the plan as 10 × 45 m² and no internal dimensions, so Atemp"
        " is taken as that plan times the number of storeys."
    )
    add("")
    add(
        f"Gross façade {_n(float(env['facade_gross_m2']), 0)} m², "  # type: ignore[index]
        f"of which windows {_n(float(env['window_m2']), 1)} m² and doors {_n(float(env['door_m2']), 1)} m². "  # type: ignore[index]
        f"Opaque wall left: {_n(float(env['wall_opaque_m2']), 1)} m². "
        f"The enclosing area Aom is {_n(float(env['aom_m2']), 0)} m² "
        "(roof + ground floor + whole façade, windows and doors included)."
    )
    add("")
    add(
        "External corridors run along both long sides, on the intermediate floors. "
        f"With two intermediate floors and two sides of 45 m, the thermal-bridge "
        f"length is {_n(float(env['bridge_length_m']), 0)} m at Ψ = 0.6 W/(m·K)."
    )
    add("")
    add("## U-value of the outer wall")
    add("")
    add("The brief asks for the λ-value method. The studs are 45 mm wide at 600 mm")
    add("centres, so the wood fraction is 45/600 = 0.075. With mineral wool at")
    add("0.037 W/(m·K) and timber at 0.14 W/(m·K):")
    add("")
    add("```text")
    add("λ_mix = 0.925 × 0.037 + 0.075 × 0.14")
    add(f"      = {float(result['lambda_mix']):.4f} W/(m·K)")
    add("```")
    add("")
    add("The ventilated cavity and the outer leaf (the brick) are given as one")
    add("resistance, 0.20 m²·K/W. Asbestos and the plastic foil are ignored, as")
    add("the brief says. Indoor surface resistance is the usual 0.13 m²·K/W")
    add("for a wall. Gypsum is 13 mm at 0.25 W/(m·K).")
    add("")
    add("```text")
    add("R = 0.13 + 0.013/0.25 + 0.095/λ_mix + 0.20")
    add(f"  = {float(result['r_wall']):.3f} m²·K/W")
    add(f"U_wall = {float(result['u_wall']):.3f} W/(m²·K)")
    add("```")
    add("")
    add("Horizontal noggins are not given, so they are not included. Counting")
    add("them would raise U a little.")
    add("")
    add("## Um")
    add("")
    add("Um is the transmission heat loss, bridges included, divided by Aom.")
    add("Ventilation is not part of Um.")
    add("")
    add("| Part | UA or ΨL (W/K) |")
    add("|---|---:|")
    add(f"| Opaque walls | {_n(float(env['ua_wall']), 1)} |")  # type: ignore[index]
    add(f"| Windows, U = 2.9 | {_n(float(env['ua_window']), 1)} |")  # type: ignore[index]
    add(f"| Doors, U = 2.0 | {_n(float(env['ua_door']), 1)} |")  # type: ignore[index]
    add(f"| Roof, U = 0.16 | {_n(float(env['ua_roof']), 1)} |")  # type: ignore[index]
    add(f"| Ground floor, U = 0.23 | {_n(float(env['ua_foundation']), 1)} |")  # type: ignore[index]
    add(f"| Balcony slabs | {_n(float(env['psi_l']), 1)} |")  # type: ignore[index]
    add(f"| **Total H_tr** | **{_n(float(env['h_tr']), 1)}** |")  # type: ignore[index]
    add("")
    add(
        f"Um = H_tr / Aom = {_n(float(result['um']), 3)} W/(m²·K). "
        "A new multi-family building in BBR is limited to 0.40 W/(m²·K). "
        "This envelope is above that limit. The windows alone are a large part of H_tr: "
        "double glazing in timber frames, U = 2.9, on a big area."
    )
    add("")
    add("## Ventilation")
    add("")
    n_people = int(30 + 10 * int(digits["a"]) + int(digits["b"]))  # type: ignore[index]
    add(
        f"{n_people} people is 30 + ab. Each produces 0.005 L/s of CO₂, outdoor air "
        "is 350 ppm, and the indoor limit used for sizing is 1000 ppm."
    )
    add("")
    add("```text")
    add("q = (people × 0.005 L/s) / (1000 − 350) ppm")
    add(
        f"  = {float(vent['q_mech_m3_s']) * 1000:.0f} L/s "  # type: ignore[index]
        f"= {float(vent['specific_flow_l_s_m2']):.2f} L/(s·m²)"
    )
    add("```")
    add("")
    add(
        f"Leakage is 0.05 air changes per hour, "
        f"{float(vent['q_leak_m3_s']) * 1000:.0f} L/s. "  # type: ignore[index]
        "The system is mechanical exhaust, so there is no heat recovery. "
        "For a design-day calculation the two flows are added: that is the "
        "cold-day case, outdoor air coming in both through the vents and through the cracks."
    )
    add("")
    add(
        f"H_vent = 1.2 kg/m³ × 1000 J/(kg·K) × q = {_n(float(vent['h_vent']), 1)} W/K."  # type: ignore[index]
    )
    add("")
    add(
        "0.22 L/(s·m²) from the CO₂ balance is below the 0.35 L/(s·m²) often used "
        "as a hygienic floor for housing. The brief says to size from the CO₂ "
        "measurement, so the lower flow is kept. Raising it to 0.35 would increase "
        "the ventilation loss, and the heating power with it."
    )
    add("")
    add("## Time constant and DVUT")
    add("")
    add("DVUT is not the coldest hour of one year. It is the outdoor temperature")
    add("of a cold spell whose length matches the building's time constant.")
    add("Only the mass on the warm side of the insulation counts, and only the")
    add("first 10 cm from each indoor face (ISO 13790). The brick sits outside")
    add("the insulation, so it is left out. Using the whole 200 mm ground slab")
    add("would pretend that the soil-side concrete follows the room temperature.")
    add("")
    add(
        f"C = {_n(float(env['capacity_j_per_k']) / 1e6, 0)} MJ/K. "  # type: ignore[index]
        f"τ = C / (H_tr + H_vent) = {_n(float(result['time_constant_days']), 2)} days. "
        f"Rounded to the nearest tabulated duration, that is the "
        f"{result['dvut_days']}-day DVUT for {result['city']}: "
        f"**{_n(float(result['dvut_c']))} °C** "
        "(Boverket / SMHI, 1991–2020)."
    )
    add("")
    add("## Balance temperature and design power")
    add("")
    add("Tb is the outdoor temperature at which appliance gains alone cover the")
    add("losses. People and sun are left out, as the brief asks for Tb and for")
    add("the design power.")
    add("")
    add("```text")
    add("Tb = Tin − Q_appliances / (H_tr + H_vent)")
    add(
        f"   = {float(result['tin_c']):.1f} − {app_kw * 1000:.0f} / "
        f"{float(env['h_tr']) + float(vent['h_vent']):.0f}"  # type: ignore[index]
    )
    add(f"   = {float(result['tb_c']):.2f} °C")
    add("```")
    add("")
    add("Above Tb the building does not need the radiators, if the appliances")
    add("are running and we still ignore sun and people. Below Tb it does.")
    add("")
    add("The question « power without internal heat generation » is the full loss")
    add("at DVUT. The hint then says to keep the appliances. Both numbers are")
    add("above. The safe size of the heating system is the larger one: appliances")
    add("are not a guarantee at 6 in the morning.")
    add("")
    add("```text")
    add("P = (H_tr + H_vent) × (Tin − DVUT)")
    add(f"  = {gross_kw:.1f} kW")
    add(f"P − appliances = {net_kw:.1f} kW")
    add("```")
    add("")
    add("On that design day the loss splits as follows:")
    add("")
    for key, label in (
        ("windows", "Windows"),
        ("ventilation", "Ventilation and leaks"),
        ("walls", "Outer walls"),
        ("balconies", "Balcony slabs"),
        ("foundation", "Ground floor"),
        ("doors", "Doors"),
        ("roof", "Roof"),
    ):
        add(f"- {label}: {shares[key] / 1000:.1f} kW")  # type: ignore[index]
    add("")
    add("## Heating season, 15 September to 15 May")
    add("")
    add(
        f"The weather file is Sveby / SMHI for {result['city']}, {result['weather_year']} "
        "(2015 + a + a + c). Solar radiation is the monthly curve in Figure 1 of the "
        "brief, the Örebro diagram, used for every city as instructed. It was read "
        "from the printed figure to about ± 5 W/m². The values are monthly averages, "
        "so they are applied to every hour of the month and then multiplied by the "
        "hours — the hint in the brief."
    )
    add("")
    n_people_heat = case_people(result)
    watts_each = people_kw * 1000.0 / n_people_heat
    add(
        f"People contribute {people_kw:.1f} kW: {n_people_heat} people × {watts_each:.0f} W. "
        "The CO₂ rate in the brief, 0.005 L/s per person, is about one met, "
        "which is about 100 W of heat. Presence is taken as continuous. "
        "A real schedule, with people out during the day, would lower this gain."
    )
    add("")
    add("Each hour, heating need = transmission + ventilation − appliances − people − solar,")
    add("and never below zero. Surplus in a mild hour is not saved for the next hour.")
    add("There is no utilisation factor: gains are fully useful until they match the loss.")
    add("That is slightly optimistic.")
    add("")
    add(
        f"Degree hours with base Tin over those {int(season['hours'])} hours: "  # type: ignore[index]
        f"{float(season['degree_hours_tin']):,.0f} °C·h. "  # type: ignore[index]
        f"Degree hours with base Tb, used for the climate correction: "
        f"{float(season['degree_hours_tb']):,.0f} °C·h in {result['weather_year']}, "  # type: ignore[index]
        f"{float(normal['degree_hours_tb']):,.0f} °C·h in the typical year."  # type: ignore[index]
    )
    add("")
    add("## Normal year and energy class")
    add("")
    add("The lecture correction scales the climate-dependent heat with the ratio")
    add("of degree hours (base Tb) between the typical year and 2017:")
    add("")
    add("```text")
    add("E_normal = E_2017 × (degree hours_normal / degree hours_2017)")
    add(
        f"         = {float(season['deficit_kwh']) / 1000:.2f} MWh × {float(result['correction_factor']):.3f}"  # type: ignore[index]
    )
    add(f"         = {float(result['heat_deficit_corrected_kwh']) / 1000:.2f} MWh")
    add("```")
    add("")
    add(
        f"Running the same hourly balance on the Sveby typical year (1991–2020) "
        f"gives {float(normal['deficit_kwh']) / 1000:.2f} MWh directly. "  # type: ignore[index]
        "The two routes are close. The energy class below uses the scaled 2017 result, "
        "which is the correction the brief points to. The direct run is the check."
    )
    add("")
    add(
        f"The heating system is an air-to-air heat pump with COP = {float(energy['cop']):.0f}. "  # type: ignore[index]
        "Electricity bought for space heat is the heat divided by 3. "
        "An air-to-air unit does not heat domestic hot water, so hot water is counted "
        f"as direct electric ({float(energy['dhw_kwh']) / float(env['atemp_m2']):.0f} kWh/m², Sveby). "  # type: ignore[index]
        f"Property electricity (fans, common lighting) is {float(energy['property_kwh']) / float(env['atemp_m2']):.0f} kWh/m², "
        "also Sveby, also electricity. Household appliances are already inside the "
        "heat balance as a gain; their electricity is not part of the building's "
        "primary energy number."
    )
    add("")
    add("Weighting factors are the BBR ones: electricity 1.8, district heating would")
    add("have been 0.7. Only space heating is divided by the geographical factor")
    add(f"F_geo. For {result['city']}, F_geo = 1.0, so the factor does not move the number.")
    add("")
    atemp = float(env["atemp_m2"])  # type: ignore[index]
    heat_ep = float(energy["weighted_heat"]) / atemp  # type: ignore[index]
    dhw_ep = float(energy["weighted_dhw"]) / atemp  # type: ignore[index]
    property_ep = float(energy["weighted_property"]) / atemp  # type: ignore[index]
    add(
        f"EP = {float(energy['ep_kwh_m2']):.1f} kWh/m²·year. "  # type: ignore[index]
        f"Of that, space heating is {heat_ep:.0f}, domestic hot water is {dhw_ep:.0f}, "
        f"and property electricity is {property_ep:.0f}. "
        "The heat pump divides the space-heat bill by three, so the hot-water "
        "cylinder — still a plain electric heater — weighs more in the rating than the heating does."
    )
    add("")
    add(
        f"The new-building limit for a multi-family house is "
        f"{float(energy['limit_kwh_m2']):.0f} kWh/m²·year "  # type: ignore[index]
        f"(no ventilation supplement: the specific flow is under 0.35 L/(s·m²)). "
        f"The ratio is {float(energy['ratio_to_new_building']):.2f}, "
        f"which is energy class **{energy['energy_class']}**."  # type: ignore[index]
    )
    add("")
    add("Class C means « as good as the requirement for a new building ». Classes")
    add("toward A are better. This building does not meet that requirement.")
    add("Most of the primary energy is electricity, and electricity is weighted at 1.8.")
    add("The same heat on district heating (weight 0.7, no COP) would look different;")
    add("the birth date fixes the system, so that comparison is not the result,")
    add("only a reminder that the class is about the carrier as well as the heat.")
    add("")
    add("One limit of the COP: it is taken as 3 even on the design day. A real")
    add("air-to-air pump loses capacity in a cold spell. The design power above")
    add("is the heat the building needs. The pump may need a backup heater to")
    add("deliver it at DVUT. That backup is not in the annual COP of 3, so the")
    add("annual electricity, and the class, are a little optimistic.")
    add("")
    add("## What would actually cut the heating")
    add("")
    add("Each line below repeats the normal-year correction with the change applied.")
    add("")
    add("| Measure | Corrected heat | Saved | New class |")
    add("|---|---:|---:|---|")
    for row in result["scenarios"]:  # type: ignore[union-attr]
        add(
            f"| {row['name']} | {row['heat_deficit_corrected_kwh'] / 1000:.1f} MWh | "  # type: ignore[index]
            f"{row['saved_kwh'] / 1000:.1f} MWh | {row['energy_class']} |"  # type: ignore[index]
        )
    add("")
    add("The order of usefulness, on this building:")
    add("")
    add("1. **Heat recovery on the exhaust air.** The ventilation loss is large")
    add("   and today it is thrown away. An exhaust-air heat pump or a supply-and-")
    add("   exhaust unit with 80 % recovery attacks that term directly.")
    add("2. **The windows.** U = 2.9 on more than 100 m² is the biggest single")
    add("   transmission term. Triple glazing around U = 1.0 is the obvious replacement.")
    add("3. **The balcony slabs.** Ψ = 0.6 W/(m·K) over the long façades is a")
    add("   serious bridge, which the brief already flags. A thermal break at the")
    add("   slab edge cuts it without touching the apartments much.")
    add("")
    add("Doing all three still leaves domestic hot water and property electricity,")
    add("both counted as electricity at factor 1.8. The class moves, but it does")
    add("not become a new-building class from the envelope alone, because the")
    add("primary-energy number is not only the space heating.")
    add("")
    add("## What this does not claim")
    add("")
    add("- The city list was not inside the PDF. City 29 is Danderyd because the")
    add("  SMHI place list, without Abisko, puts Bjurholm at number 14 (a known")
    add("  reading of the same brief) and Danderyd at number 29.")
    add("- Figure 1 was read by eye. A few watts per square metre either way does")
    add("  not change the class; it does move the solar megawatt-hours.")
    add("- Internal gains other than the constant 100 W per person and the")
    add("  appliance wattage are not modelled. No night setback, no shutters.")
    add("- The 10 cm active-depth rule is used only to pick DVUT. The annual")
    add("  energy calculation is steady-state hour by hour, not a dynamic simulation.")
    add("- Hot water and property electricity are Sveby standard values, not")
    add("  measurements from this association.")
    add("")
    add("## Sources")
    add("")
    add("- Assignment brief, course ETA013, University of Gävle, deadline 17 November 2026.")
    add("- Boverket / SMHI, DVUT 1991–2020, open data.")
    add("- Sveby climate file for 2017, version 2.0, place Danderyd (102646).")
    add("- Sveby typical year 1991–2020, same place.")
    add("- Figure 1 of the brief: Nevander and Elmarsson, Fukthandboken, 1994.")
    add("- BBR weighting factors and energy classes (electricity 1.8, new multi-family")
    add("  limit 75 kWh/m²·year, classes A–G). F_geo for Danderyd is 1.0.")
    add("- Sveby brukarindata for multi-family buildings: hot water 25 kWh/m²·year,")
    add("  property electricity 15 kWh/m²·year.")
    add("")
    return "\n".join(lines) + "\n"


def case_people(result: dict[str, object]) -> int:
    """Nombre d'occupants : 30 + ab, relu depuis les chiffres de la date.

    Parameters
    ----------
    result : dict
        Résultats, avec ``digits``.

    Returns
    -------
    int
        Nombre de personnes.
    """
    digits = result["digits"]
    return 30 + 10 * int(digits["a"]) + int(digits["b"])  # type: ignore[index]
