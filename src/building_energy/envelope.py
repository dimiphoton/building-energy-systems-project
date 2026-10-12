"""Géométrie, U du mur, Um et masse thermique."""

from __future__ import annotations

from dataclasses import dataclass

from building_energy.parameters import Case


@dataclass(frozen=True)
class Envelope:
    """Résultats de l'enveloppe, en unités SI."""

    floor_area_m2: float
    atemp_m2: float
    volume_m3: float
    facade_gross_m2: float
    wall_opaque_m2: float
    window_m2: float
    window_south_m2: float
    window_north_m2: float
    window_east_m2: float
    window_west_m2: float
    door_m2: float
    roof_m2: float
    foundation_m2: float
    aom_m2: float
    bridge_length_m: float
    lambda_mix: float
    r_wall: float
    u_wall: float
    ua_wall: float
    ua_window: float
    ua_door: float
    ua_roof: float
    ua_foundation: float
    psi_l: float
    h_tr: float
    um: float
    capacity_j_per_k: float


def mixed_conductivity(case: Case) -> float:
    """Conductivité du mélange isolant / montants, méthode λ du sujet.

    La fraction de bois est la largeur du montant divisée par l'entraxe.
    Le sujet ne quantifie pas les entretoises horizontales : on n'en met pas.

    Parameters
    ----------
    case : Case
        Conductivités et entraxe.

    Returns
    -------
    float
        λ_mix, en W/(m·K).
    """
    fraction_wood = case.stud_width_m / case.stud_spacing_m
    fraction_insulation = 1.0 - fraction_wood
    return (
        fraction_insulation * case.lambda_insulation
        + fraction_wood * case.lambda_wood
    )


def wall_u_value(case: Case) -> tuple[float, float, float]:
    """U du mur opaque.

    Le sujet donne 0,2 m²·K/W pour la lame d'air ventilée et la couche
    extérieure qui y est accrochée. Cette résistance remplace la brique,
    la lame d'air et Rse. L'amiante et le pare-vapeur sont négligés,
    comme demandé.

    Parameters
    ----------
    case : Case
        Épaisseurs et conductivités.

    Returns
    -------
    tuple of float
        λ_mix, R_tot (m²·K/W), U (W/(m²·K)).
    """
    lambda_mix = mixed_conductivity(case)
    r_gypsum = case.gypsum_board_m / case.lambda_gypsum
    r_mix = case.insulation_thickness_m / lambda_mix
    r_tot = case.r_si + r_gypsum + r_mix + case.r_outdoor
    return lambda_mix, r_tot, 1.0 / r_tot


def _active_thickness(thickness_m: float, sides: int, active_depth_m: float) -> float:
    """Épaisseur qui participe vraiment, depuis chaque face intérieure.

    Au-delà de ``active_depth_m`` par face, le béton ne suit plus les
    variations qui servent à choisir le DVUT (ISO 13790).
    """
    return min(thickness_m, active_depth_m * sides)


def _concrete_capacity(
    area_m2: float,
    thickness_m: float,
    sides: int,
    case: Case,
) -> float:
    active = _active_thickness(thickness_m, sides, case.active_depth_m)
    return area_m2 * active * case.rho_concrete * case.c_concrete


def build_envelope(case: Case) -> Envelope:
    """Assemble les surfaces, les UA et la capacité intérieure.

    Parameters
    ----------
    case : Case
        Cas complet.

    Returns
    -------
    Envelope
        Grandeurs nécessaires au bilan.
    """
    floor = case.floor_length_m * case.floor_width_m
    atemp = floor * case.stories
    volume = atemp * case.story_height_m
    perimeter = 2.0 * (case.floor_length_m + case.floor_width_m)
    facade = perimeter * case.stories * case.story_height_m
    windows = case.window_area_m2
    doors = case.n_doors * case.door_area_m2
    wall = facade - windows - doors
    if wall <= 0:
        raise ValueError("la surface opaque du mur est négative : vérifier le sujet")

    # Coursives sur les deux longs pans, à chaque plancher intermédiaire.
    bridge_length = 2.0 * (case.stories - 1) * case.floor_length_m

    lambda_mix, r_wall, u_wall = wall_u_value(case)
    ua_wall = u_wall * wall
    ua_window = case.u_window * windows
    ua_door = case.u_door * doors
    ua_roof = case.u_roof * floor
    ua_foundation = case.u_foundation * floor
    psi_l = case.psi_balcony * bridge_length
    h_tr = ua_wall + ua_window + ua_door + ua_roof + ua_foundation + psi_l
    # Aom englobe les menuiseries : c'est l'enveloppe chauffée, pas le mur seul.
    aom = floor + floor + facade
    um = h_tr / aom

    cap_slab = _concrete_capacity(floor, case.slab_thickness_m, 1, case)
    cap_mid = _concrete_capacity(floor, case.intermediate_floor_m, 2, case) * (
        case.stories - 1
    )
    cap_roof = _concrete_capacity(floor, case.roof_concrete_m, 1, case)
    concrete_wall_area = case.internal_concrete_wall_m * case.story_height_m * case.stories
    cap_walls = _concrete_capacity(
        concrete_wall_area, case.concrete_wall_thickness_m, 2, case
    )
    # Cloisons : deux plaques, ossature bois négligée comme le dit le sujet.
    partition_faces = 2.0 * case.internal_stud_wall_m * case.story_height_m * case.stories
    cap_partitions = (
        partition_faces * case.gypsum_board_m * case.rho_gypsum * case.c_gypsum
    )
    cap_facade_gypsum = wall * case.gypsum_board_m * case.rho_gypsum * case.c_gypsum
    capacity = cap_slab + cap_mid + cap_roof + cap_walls + cap_partitions + cap_facade_gypsum

    return Envelope(
        floor_area_m2=floor,
        atemp_m2=atemp,
        volume_m3=volume,
        facade_gross_m2=facade,
        wall_opaque_m2=wall,
        window_m2=windows,
        window_south_m2=windows * case.window_south_share,
        window_north_m2=windows * case.window_north_share,
        window_east_m2=windows * case.window_east_share,
        window_west_m2=windows * case.window_west_share,
        door_m2=doors,
        roof_m2=floor,
        foundation_m2=floor,
        aom_m2=aom,
        bridge_length_m=bridge_length,
        lambda_mix=lambda_mix,
        r_wall=r_wall,
        u_wall=u_wall,
        ua_wall=ua_wall,
        ua_window=ua_window,
        ua_door=ua_door,
        ua_roof=ua_roof,
        ua_foundation=ua_foundation,
        psi_l=psi_l,
        h_tr=h_tr,
        um=um,
        capacity_j_per_k=capacity,
    )
