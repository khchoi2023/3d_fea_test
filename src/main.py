from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

from .material import create_steel
from .mesh_generator import generate_cantilever_tet_mesh
from .postprocess import (
    compute_stress_results,
    compute_theory_values,
    percent_difference,
    write_summary,
)
from .solver import assemble_global_stiffness, create_load_vector, solve_linear_system

# Geometry and mesh settings
LENGTH_MM = 1000.0
WIDTH_MM = 80.0
HEIGHT_MM = 120.0
NX = 12
NY = 3
NZ = 4

# Material
YOUNG_MODULUS_MPA = 200000.0
POISSON_RATIO = 0.3

# Load and visualization
TOTAL_FORCE_N = 1000.0
LOAD_DIRECTION_Z_N = -TOTAL_FORCE_N
DEFORMATION_SCALE = 50.0
QUALITY_WARNING_THRESHOLD = 0.02


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    results_dir = project_root / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    result_png_path = results_dir / "3d_cantilever_von_mises.png"
    result_deformed_png_path = results_dir / "3d_cantilever_deformed_von_mises.png"
    result_summary_path = results_dir / "3d_cantilever_summary.txt"
    result_vtu_path = results_dir / "3d_cantilever_result.vtu"

    material = create_steel()

    print("=" * 60)
    print("3D Cantilever Static FEA")
    print("=" * 60)
    print("Model size:")
    print(f"  L = {LENGTH_MM:g} mm")
    print(f"  B = {WIDTH_MM:g} mm")
    print(f"  H = {HEIGHT_MM:g} mm")
    print()
    print("Material:")
    print(f"  {material.name}")
    print(f"  E = {material.young_modulus:g} MPa")
    print(f"  nu = {material.poisson_ratio:g}")
    print()

    try:
        mesh = generate_cantilever_tet_mesh(
            length=LENGTH_MM,
            width=WIDTH_MM,
            height=HEIGHT_MM,
            nx=NX,
            ny=NY,
            nz=NZ,
        )
    except Exception as exc:
        print(f"[ERROR] 메쉬 생성에 실패했습니다: {exc}")
        return 1

    print("Mesh:")
    print(f"  nodes = {mesh.nodes.shape[0]}")
    print(f"  elements = {mesh.elements.shape[0]}")
    print(f"  tet quality min = {mesh.min_quality:.6f}")
    print(f"  tet quality max = {mesh.max_quality:.6f}")
    if mesh.min_quality < QUALITY_WARNING_THRESHOLD:
        print("  [WARNING] 일부 TET4 요소 품질이 낮습니다. 메쉬를 더 촘촘하게 하거나 분할 수를 조정하세요.")
    print()

    print("Boundary condition:")
    print("  fixed face: x = 0")
    print(f"  fixed nodes = {mesh.fixed_nodes.size}")
    print()

    print("Load:")
    print("  load face: x = L")
    print(f"  total force = {TOTAL_FORCE_N:g} N")
    print("  direction = -Z")
    print(f"  load nodes = {mesh.load_nodes.size}")
    print()

    print("Solving K u = F...")
    try:
        stiffness, _ = assemble_global_stiffness(
            mesh.nodes,
            mesh.elements,
            material.elasticity_matrix,
        )
        force_vector = create_load_vector(mesh.nodes.shape[0], mesh.load_nodes, LOAD_DIRECTION_Z_N)
        displacements = solve_linear_system(stiffness, force_vector, mesh.fixed_nodes)
    except ImportError as exc:
        print(exc)
        return 1
    except Exception as exc:
        print(f"[ERROR] 해석 중 문제가 발생했습니다: {exc}")
        return 1

    post = compute_stress_results(
        mesh.nodes,
        mesh.elements,
        displacements,
        material.elasticity_matrix,
    )
    theory = compute_theory_values(
        LENGTH_MM,
        WIDTH_MM,
        HEIGHT_MM,
        material.young_modulus,
        TOTAL_FORCE_N,
    )
    displacement_diff = percent_difference(post["max_displacement"], theory["tip_displacement"])
    stress_diff = percent_difference(post["max_von_mises"], theory["max_bending_stress"])

    max_location = post["max_von_mises_location"]
    print()
    print("Results:")
    print(f"  max displacement = {post['max_displacement']:.6f} mm")
    print(f"  max von Mises stress = {post['max_von_mises']:.6f} MPa")
    print(
        "  max stress location = "
        f"({max_location[0]:.3f}, {max_location[1]:.3f}, {max_location[2]:.3f}) mm"
    )
    print()
    print("Theory comparison:")
    print(f"  theoretical tip displacement = {theory['tip_displacement']:.6f} mm")
    print(f"  theoretical max bending stress = {theory['max_bending_stress']:.6f} MPa")
    print(f"  displacement difference = {displacement_diff:.3f} %")
    print(f"  stress difference = {stress_diff:.3f} %")
    print()

    try:
        from .viewer import build_unstructured_grid, save_and_show_results

        grid = build_unstructured_grid(
            mesh.nodes,
            mesh.elements,
            post["nodal_von_mises"],
            post["cell_von_mises"],
            post["displacement_vectors"],
        )
        write_summary(
        result_summary_path,
        length=LENGTH_MM,
        width=WIDTH_MM,
        height=HEIGHT_MM,
        material_name=material.name,
        young_modulus=material.young_modulus,
        poisson_ratio=material.poisson_ratio,
        nx=NX,
        ny=NY,
        nz=NZ,
        num_nodes=mesh.nodes.shape[0],
        num_elements=mesh.elements.shape[0],
        fixed_nodes_count=mesh.fixed_nodes.size,
        load_nodes_count=mesh.load_nodes.size,
        total_force=TOTAL_FORCE_N,
        max_displacement=post["max_displacement"],
        max_von_mises=post["max_von_mises"],
        max_von_mises_location=post["max_von_mises_location"],
        theoretical_tip_displacement=theory["tip_displacement"],
        theoretical_max_bending_stress=theory["max_bending_stress"],
        displacement_difference_percent=displacement_diff,
        stress_difference_percent=stress_diff,
        result_vtu_path=result_vtu_path,
        result_png_path=result_png_path,
        result_deformed_png_path=result_deformed_png_path,
        )

        print("Saved files:")
        print("  results/3d_cantilever_von_mises.png")
        print("  results/3d_cantilever_deformed_von_mises.png")
        print("  results/3d_cantilever_summary.txt")
        print("  results/3d_cantilever_result.vtu")
        print()
        print("Opening interactive 3D viewer...")
        print("=" * 60)

        save_and_show_results(
            grid,
            result_vtu_path=result_vtu_path,
            result_png_path=result_png_path,
            result_deformed_png_path=result_deformed_png_path,
            max_location=max_location,
            deformation_scale=DEFORMATION_SCALE,
            show_interactive=True,
        )
        return 0
    except ImportError as exc:
        print(exc)
        return 1
    except Exception as exc:
        print(f"[ERROR] 결과 시각화 중 문제가 발생했습니다: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
