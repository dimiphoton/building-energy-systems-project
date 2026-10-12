# Building energy study — Danderyd

**Dimitri Marchand**, birth year 1986.
Course ETA013, Building Energy Systems, University of Gävle.
The birth date is 29 August 1986. Written as year, month, day
(1986, 08, 29) it gives a = 0, b = 8, c = 2, d = 9, ab = 8, cd = 29,
the same split as the example in the brief (1985, 10, 29 → a = 1, b = 0, c = 2, d = 9).

## Answers the brief asks for

| | |
|---|---|
| City | Danderyd (city number 29) |
| DVUT | -10.7 °C (7-day value) |
| Tin | 22.0 °C |
| Average heat transfer coefficient Um | 0.589 W/(m²·K) |
| Balance temperature Tb | 18.21 °C |
| Required heating power, no internal gains | 46.5 kW |
| Same power with appliance gains only | 41.1 kW |
| Heat gain, people | 3.8 kW, 22.2 MWh over the heating season |
| Heat gain, appliances | 5.4 kW, 31.5 MWh over the heating season |
| Solar heat gain | 19.9 MWh over the heating season |
| Heat loss, transmission | 109.0 MWh |
| Heat loss, ventilation | 43.6 MWh |
| Heat deficit, weather year 2017 | 80.2 MWh |
| Heating-season degree hours (base Tin) | 107,242 °C·h |
| Heat deficit after normal-year correction | 81.7 MWh |
| Primary energy number | 108.3 kWh/m²·year |
| Energy class | E |

The duration diagram is `pictures/experiments/duration-temperature.png`.

## What was asked, in plain words

A housing association has one multi-family building that cannot keep
20 °C indoors when the weather is really cold. The brief asks for the
radiator power on a design day, the balance temperature, the average
U-value, the heating season in the city's weather file, and the energy
class once that year has been brought back to a normal climate.

Indoor setpoint Tin = 20 + c = 22.0 °C. The heating system is air-to-air heat pump, COP 3.

## The building

Three storeys (3 + a), plan 10 × 45 m. Heated floor area Atemp = 1,350 m². Storey height 2.5 m, so the heated volume is 3,375 m³. The brief gives the plan as 10 × 45 m² and no internal dimensions, so Atemp is taken as that plan times the number of storeys.

Gross façade 825 m², of which windows 129.0 m² and doors 50.4 m². Opaque wall left: 645.6 m². The enclosing area Aom is 1,725 m² (roof + ground floor + whole façade, windows and doors included).

External corridors run along both long sides, on the intermediate floors. With two intermediate floors and two sides of 45 m, the thermal-bridge length is 180 m at Ψ = 0.6 W/(m·K).

## U-value of the outer wall

The brief asks for the λ-value method. The studs are 45 mm wide at 600 mm
centres, so the wood fraction is 45/600 = 0.075. With mineral wool at
0.037 W/(m·K) and timber at 0.14 W/(m·K):

```text
λ_mix = 0.925 × 0.037 + 0.075 × 0.14
      = 0.0447 W/(m·K)
```

The ventilated cavity and the outer leaf (the brick) are given as one
resistance, 0.20 m²·K/W. Asbestos and the plastic foil are ignored, as
the brief says. Indoor surface resistance is the usual 0.13 m²·K/W
for a wall. Gypsum is 13 mm at 0.25 W/(m·K).

```text
R = 0.13 + 0.013/0.25 + 0.095/λ_mix + 0.20
  = 2.506 m²·K/W
U_wall = 0.399 W/(m²·K)
```

Horizontal noggins are not given, so they are not included. Counting
them would raise U a little.

## Um

Um is the transmission heat loss, bridges included, divided by Aom.
Ventilation is not part of Um.

| Part | UA or ΨL (W/K) |
|---|---:|
| Opaque walls | 257.6 |
| Windows, U = 2.9 | 374.1 |
| Doors, U = 2.0 | 100.8 |
| Roof, U = 0.16 | 72.0 |
| Ground floor, U = 0.23 | 103.5 |
| Balcony slabs | 108.0 |
| **Total H_tr** | **1,016.0** |

Um = H_tr / Aom = 0.589 W/(m²·K). A new multi-family building in BBR is limited to 0.40 W/(m²·K). This envelope is above that limit. The windows alone are a large part of H_tr: double glazing in timber frames, U = 2.9, on a big area.

## Ventilation

38 people is 30 + ab. Each produces 0.005 L/s of CO₂, outdoor air is 350 ppm, and the indoor limit used for sizing is 1000 ppm.

```text
q = (people × 0.005 L/s) / (1000 − 350) ppm
  = 292 L/s = 0.22 L/(s·m²)
```

Leakage is 0.05 air changes per hour, 47 L/s. The system is mechanical exhaust, so there is no heat recovery. For a design-day calculation the two flows are added: that is the cold-day case, outdoor air coming in both through the vents and through the cracks.

H_vent = 1.2 kg/m³ × 1000 J/(kg·K) × q = 407.0 W/K.

0.22 L/(s·m²) from the CO₂ balance is below the 0.35 L/(s·m²) often used as a hygienic floor for housing. The brief says to size from the CO₂ measurement, so the lower flow is kept. Raising it to 0.35 would increase the ventilation loss, and the heating power with it.

## Time constant and DVUT

DVUT is not the coldest hour of one year. It is the outdoor temperature
of a cold spell whose length matches the building's time constant.
Only the mass on the warm side of the insulation counts, and only the
first 10 cm from each indoor face (ISO 13790). The brick sits outside
the insulation, so it is left out. Using the whole 200 mm ground slab
would pretend that the soil-side concrete follows the room temperature.

C = 822 MJ/K. τ = C / (H_tr + H_vent) = 6.69 days. Rounded to the nearest tabulated duration, that is the 7-day DVUT for Danderyd: **-10.7 °C** (Boverket / SMHI, 1991–2020).

## Balance temperature and design power

Tb is the outdoor temperature at which appliance gains alone cover the
losses. People and sun are left out, as the brief asks for Tb and for
the design power.

```text
Tb = Tin − Q_appliances / (H_tr + H_vent)
   = 22.0 − 5400 / 1423
   = 18.21 °C
```

Above Tb the building does not need the radiators, if the appliances
are running and we still ignore sun and people. Below Tb it does.

The question « power without internal heat generation » is the full loss
at DVUT. The hint then says to keep the appliances. Both numbers are
above. The safe size of the heating system is the larger one: appliances
are not a guarantee at 6 in the morning.

```text
P = (H_tr + H_vent) × (Tin − DVUT)
  = 46.5 kW
P − appliances = 41.1 kW
```

On that design day the loss splits as follows:

- Windows: 12.2 kW
- Ventilation and leaks: 13.3 kW
- Outer walls: 8.4 kW
- Balcony slabs: 3.5 kW
- Ground floor: 3.4 kW
- Doors: 3.3 kW
- Roof: 2.4 kW

## Heating season, 15 September to 15 May

The weather file is Sveby / SMHI for Danderyd, 2017 (2015 + a + a + c). Solar radiation is the monthly curve in Figure 1 of the brief, the Örebro diagram, used for every city as instructed. It was read from the printed figure to about ± 5 W/m². The values are monthly averages, so they are applied to every hour of the month and then multiplied by the hours — the hint in the brief.

People contribute 3.8 kW: 38 people × 100 W. The CO₂ rate in the brief, 0.005 L/s per person, is about one met, which is about 100 W of heat. Presence is taken as continuous. A real schedule, with people out during the day, would lower this gain.

Each hour, heating need = transmission + ventilation − appliances − people − solar,
and never below zero. Surplus in a mild hour is not saved for the next hour.
There is no utilisation factor: gains are fully useful until they match the loss.
That is slightly optimistic.

Degree hours with base Tin over those 5832 hours: 107,242 °C·h. Degree hours with base Tb, used for the climate correction: 85,117 °C·h in 2017, 86,725 °C·h in the typical year.

## Normal year and energy class

The lecture correction scales the climate-dependent heat with the ratio
of degree hours (base Tb) between the typical year and 2017:

```text
E_normal = E_2017 × (degree hours_normal / degree hours_2017)
         = 80.21 MWh × 1.019
         = 81.72 MWh
```

Running the same hourly balance on the Sveby typical year (1991–2020) gives 83.08 MWh directly. The two routes are close. The energy class below uses the scaled 2017 result, which is the correction the brief points to. The direct run is the check.

The heating system is an air-to-air heat pump with COP = 3. Electricity bought for space heat is the heat divided by 3. An air-to-air unit does not heat domestic hot water, so hot water is counted as direct electric (25 kWh/m², Sveby). Property electricity (fans, common lighting) is 15 kWh/m², also Sveby, also electricity. Household appliances are already inside the heat balance as a gain; their electricity is not part of the building's primary energy number.

Weighting factors are the BBR ones: electricity 1.8, district heating would
have been 0.7. Only space heating is divided by the geographical factor
F_geo. For Danderyd, F_geo = 1.0, so the factor does not move the number.

EP = 108.3 kWh/m²·year. Of that, space heating is 36, domestic hot water is 45, and property electricity is 27. The heat pump divides the space-heat bill by three, so the hot-water cylinder — still a plain electric heater — weighs more in the rating than the heating does.

The new-building limit for a multi-family house is 75 kWh/m²·year (no ventilation supplement: the specific flow is under 0.35 L/(s·m²)). The ratio is 1.44, which is energy class **E**.

Class C means « as good as the requirement for a new building ». Classes
toward A are better. This building does not meet that requirement.
Most of the primary energy is electricity, and electricity is weighted at 1.8.
The same heat on district heating (weight 0.7, no COP) would look different;
the birth date fixes the system, so that comparison is not the result,
only a reminder that the class is about the carrier as well as the heat.

One limit of the COP: it is taken as 3 even on the design day. A real
air-to-air pump loses capacity in a cold spell. The design power above
is the heat the building needs. The pump may need a backup heater to
deliver it at DVUT. That backup is not in the annual COP of 3, so the
annual electricity, and the class, are a little optimistic.

## What would actually cut the heating

Each line below repeats the normal-year correction with the change applied.

| Measure | Corrected heat | Saved | New class |
|---|---:|---:|---|
| Triple glazing, U = 1.0 W/(m²·K) | 56.2 MWh | 25.5 MWh | D |
| Heat recovery of 80 % on the exhaust air | 52.6 MWh | 29.2 MWh | D |
| Balcony thermal break, Ψ = 0.20 W/(m·K) | 74.2 MWh | 7.6 MWh | E |
| All three together | 22.1 MWh | 59.6 MWh | D |

The order of usefulness, on this building:

1. **Heat recovery on the exhaust air.** The ventilation loss is large
   and today it is thrown away. An exhaust-air heat pump or a supply-and-
   exhaust unit with 80 % recovery attacks that term directly.
2. **The windows.** U = 2.9 on more than 100 m² is the biggest single
   transmission term. Triple glazing around U = 1.0 is the obvious replacement.
3. **The balcony slabs.** Ψ = 0.6 W/(m·K) over the long façades is a
   serious bridge, which the brief already flags. A thermal break at the
   slab edge cuts it without touching the apartments much.

Doing all three still leaves domestic hot water and property electricity,
both counted as electricity at factor 1.8. The class moves, but it does
not become a new-building class from the envelope alone, because the
primary-energy number is not only the space heating.

## What this does not claim

- The city list was not inside the PDF. City 29 is Danderyd because the
  SMHI place list, without Abisko, puts Bjurholm at number 14 (a known
  reading of the same brief) and Danderyd at number 29.
- Figure 1 was read by eye. A few watts per square metre either way does
  not change the class; it does move the solar megawatt-hours.
- Internal gains other than the constant 100 W per person and the
  appliance wattage are not modelled. No night setback, no shutters.
- The 10 cm active-depth rule is used only to pick DVUT. The annual
  energy calculation is steady-state hour by hour, not a dynamic simulation.
- Hot water and property electricity are Sveby standard values, not
  measurements from this association.

## Sources

- Assignment brief, course ETA013, University of Gävle, deadline 17 November 2026.
- Boverket / SMHI, DVUT 1991–2020, open data.
- Sveby climate file for 2017, version 2.0, place Danderyd (102646).
- Sveby typical year 1991–2020, same place.
- Figure 1 of the brief: Nevander and Elmarsson, Fukthandboken, 1994.
- BBR weighting factors and energy classes (electricity 1.8, new multi-family
  limit 75 kWh/m²·year, classes A–G). F_geo for Danderyd is 1.0.
- Sveby brukarindata for multi-family buildings: hot water 25 kWh/m²·year,
  property electricity 15 kWh/m²·year.

