from __future__ import annotations

from pathlib import Path

import numpy as np

from .tet4_element import compute_element_strain_stress


def compute_von_mises(stress: np.ndarray) -> float:
    sx, sy, sz, txy, tyz, tzx = stress
    return float(
        np.sqrt(
            0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2)
            + 3.0 * (txy**2 + tyz**2 + tzx**2)
        )
    )


def compute_stress_results(
    nodes: np.ndarray,
    elements: np.ndarray,
    displacements: np.ndarray,
    elasticity_matrix: np.ndarray,
) -> dict[str, np.ndarray | float | int]:
    num_nodes = nodes.shape[0]
    cell_stress = np.zeros((elements.shape[0], 6), dtype=float)
    cell_von_mises = np.zeros(elements.shape[0], dtype=float)
    nodal_von_mises_sum = np.zeros(num_nodes, dtype=float)
    nodal_counts = np.zeros(num_nodes, dtype=int)

    for element_index, element in enumerate(elements):
        coords = nodes[element]
        element_displacements = np.concatenate(
            [displacements[3 * node_id : 3 * node_id + 3] for node_id in element]
        )
        _, stress = compute_element_strain_stress(coords, element_displacements, elasticity_matrix)
        vm = compute_von_mises(stress)
        cell_stress[element_index] = stress
        cell_von_mises[element_index] = vm
        for node_id in element:
            nodal_von_mises_sum[node_id] += vm
            nodal_counts[node_id] += 1

    nodal_von_mises = np.divide(
        nodal_von_mises_sum,
        np.maximum(nodal_counts, 1),
        out=np.zeros_like(nodal_von_mises_sum),
        where=nodal_counts > 0,
    )
    displacement_vectors = displacements.reshape((-1, 3))
    displacement_magnitude = np.linalg.norm(displacement_vectors, axis=1)

    max_disp_index = int(np.argmax(displacement_magnitude))
    max_vm_index = int(np.argmax(cell_von_mises))

    return {
        "cell_stress": cell_stress,
        "cell_von_mises": cell_von_mises,
        "nodal_von_mises": nodal_von_mises,
        "displacement_vectors": displacement_vectors,
        "displacement_magnitude": displacement_magnitude,
        "max_displacement": float(displacement_magnitude[max_disp_index]),
        "max_displacement_node": max_disp_index,
        "max_von_mises": float(cell_von_mises[max_vm_index]),
        "max_von_mises_element": max_vm_index,
        "max_von_mises_location": nodes[elements[max_vm_index]].mean(axis=0),
    }


def compute_theory_values(
    length: float,
    width: float,
    height: float,
    young_modulus: float,
    force_magnitude: float,
) -> dict[str, float]:
    inertia = width * height**3 / 12.0
    tip_displacement = force_magnitude * length**3 / (3.0 * young_modulus * inertia)
    bending_moment = force_magnitude * length
    c = height / 2.0
    max_bending_stress = bending_moment * c / inertia
    return {
        "inertia": inertia,
        "tip_displacement": tip_displacement,
        "max_bending_stress": max_bending_stress,
    }


def percent_difference(fea_value: float, theory_value: float) -> float:
    if abs(theory_value) <= 1e-12:
        return 0.0
    return abs(fea_value - theory_value) / abs(theory_value) * 100.0


def write_summary(
    summary_path: Path,
    *,
    length: float,
    width: float,
    height: float,
    material_name: str,
    young_modulus: float,
    poisson_ratio: float,
    nx: int,
    ny: int,
    nz: int,
    num_nodes: int,
    num_elements: int,
    fixed_nodes_count: int,
    load_nodes_count: int,
    total_force: float,
    max_displacement: float,
    max_von_mises: float,
    max_von_mises_location: np.ndarray,
    theoretical_tip_displacement: float,
    theoretical_max_bending_stress: float,
    displacement_difference_percent: float,
    stress_difference_percent: float,
    result_vtu_path: Path,
    result_png_path: Path,
    result_deformed_png_path: Path,
) -> None:
    lines = [
        "3D Cantilever Static FEA Summary",
        "=" * 40,
        "",
        "Analysis target:",
        "  3D cantilever beam",
        "",
        "Dimensions:",
        f"  L = {length:.3f} mm",
        f"  B = {width:.3f} mm",
        f"  H = {height:.3f} mm",
        "",
        "Material:",
        f"  {material_name}",
        f"  E = {young_modulus:.3f} MPa",
        f"  nu = {poisson_ratio:.6f}",
        "",
        "Mesh:",
        f"  NX = {nx}",
        f"  NY = {ny}",
        f"  NZ = {nz}",
        f"  Nodes = {num_nodes}",
        f"  Elements = {num_elements}",
        "",
        "Boundary condition:",
        "  Fixed face: x = 0",
        f"  Fixed nodes = {fixed_nodes_count}",
        "",
        "Load condition:",
        "  Load face: x = L",
        f"  Total force = {total_force:.3f} N",
        "  Direction = -Z",
        f"  Load nodes = {load_nodes_count}",
        "",
        "Results:",
        f"  Max displacement = {max_displacement:.6f} mm",
        f"  Max von Mises stress = {max_von_mises:.6f} MPa",
        (
            "  Max stress location = "
            f"({max_von_mises_location[0]:.3f}, {max_von_mises_location[1]:.3f}, {max_von_mises_location[2]:.3f}) mm"
        ),
        "",
        "Theory comparison:",
        f"  Theoretical tip displacement = {theoretical_tip_displacement:.6f} mm",
        f"  Theoretical max bending stress = {theoretical_max_bending_stress:.6f} MPa",
        f"  Displacement difference = {displacement_difference_percent:.3f} %",
        f"  Stress difference = {stress_difference_percent:.3f} %",
        "",
        "Result files:",
        f"  {result_png_path}",
        f"  {result_deformed_png_path}",
        f"  {summary_path}",
        f"  {result_vtu_path}",
        "",
        "Note:",
        "  TET4 저차 요소와 비교적 거친 메쉬를 사용하므로 이론값과 차이가 날 수 있습니다.",
    ]
    summary_path.write_text("\n".join(lines), encoding="utf-8")
