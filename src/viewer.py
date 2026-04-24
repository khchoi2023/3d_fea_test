from __future__ import annotations

from pathlib import Path

import numpy as np

try:
    import pyvista as pv
except ImportError:  # pragma: no cover - import guard
    pv = None


def build_unstructured_grid(
    nodes: np.ndarray,
    elements: np.ndarray,
    nodal_von_mises: np.ndarray,
    cell_von_mises: np.ndarray,
    displacement_vectors: np.ndarray,
) -> "pv.UnstructuredGrid":
    if pv is None:
        raise ImportError(
            "PyVista를 불러올 수 없습니다. 01_install_requirements.bat을 실행하여 패키지를 설치하세요."
        )
    num_cells = elements.shape[0]
    cells = np.hstack(
        [np.full((num_cells, 1), 4, dtype=np.int64), elements.astype(np.int64)]
    ).ravel()
    cell_types = np.full(num_cells, pv.CellType.TETRA, dtype=np.uint8)
    grid = pv.UnstructuredGrid(cells, cell_types, nodes)
    grid.point_data["von_mises"] = nodal_von_mises
    grid.point_data["displacement"] = displacement_vectors
    grid.point_data["displacement_magnitude"] = np.linalg.norm(displacement_vectors, axis=1)
    grid.cell_data["von_mises_cell"] = cell_von_mises
    return grid


def _prepare_plotter(off_screen: bool, title: str) -> "pv.Plotter":
    if pv is None:
        raise ImportError(
            "PyVista를 불러올 수 없습니다. 01_install_requirements.bat을 실행하여 패키지를 설치하세요."
        )
    plotter = pv.Plotter(off_screen=off_screen, title=title, window_size=(1400, 900))
    plotter.set_background("#f5f7fb")
    plotter.add_axes()
    plotter.show_grid(color="gray", location="outer", fmt="%.0f")
    return plotter


def save_and_show_results(
    grid: "pv.UnstructuredGrid",
    result_vtu_path: Path,
    result_png_path: Path,
    result_deformed_png_path: Path,
    max_location: np.ndarray,
    deformation_scale: float,
    show_interactive: bool = True,
) -> None:
    result_vtu_path.parent.mkdir(parents=True, exist_ok=True)
    grid.save(result_vtu_path)

    plotter = _prepare_plotter(off_screen=True, title="3D Cantilever von Mises")
    plotter.add_mesh(
        grid,
        scalars="von_mises",
        cmap="jet",
        show_edges=True,
        edge_color="#555555",
        scalar_bar_args={"title": "von Mises (MPa)"},
    )
    plotter.add_points(
        np.array([max_location]),
        color="red",
        point_size=14,
        render_points_as_spheres=True,
        label="Max von Mises",
    )
    plotter.add_legend()
    plotter.add_text("Original Shape + von Mises", position="upper_left", font_size=12)
    plotter.camera_position = "iso"
    plotter.screenshot(str(result_png_path))
    plotter.close()

    deformed_grid = grid.copy(deep=True)
    deformed_grid.points = grid.points + deformation_scale * grid.point_data["displacement"]
    plotter_def = _prepare_plotter(off_screen=True, title="3D Cantilever Deformed")
    plotter_def.add_mesh(
        grid,
        style="wireframe",
        color="black",
        opacity=0.15,
        line_width=1.0,
    )
    plotter_def.add_mesh(
        deformed_grid,
        scalars="von_mises",
        cmap="jet",
        show_edges=False,
        scalar_bar_args={"title": "von Mises (MPa)"},
    )
    plotter_def.add_points(
        np.array([max_location]),
        color="red",
        point_size=14,
        render_points_as_spheres=True,
        label="Max von Mises",
    )
    plotter_def.add_legend()
    plotter_def.add_text(
        f"Deformed Shape x {deformation_scale:.1f}",
        position="upper_left",
        font_size=12,
    )
    plotter_def.camera_position = "iso"
    plotter_def.screenshot(str(result_deformed_png_path))
    plotter_def.close()

    if show_interactive:
        interactive_plotter = _prepare_plotter(off_screen=False, title="3D Cantilever Viewer")
        interactive_plotter.add_mesh(
            grid,
            style="wireframe",
            color="black",
            opacity=0.10,
            line_width=1.0,
        )
        interactive_plotter.add_mesh(
            deformed_grid,
            scalars="von_mises",
            cmap="jet",
            scalar_bar_args={"title": "von Mises (MPa)"},
        )
        interactive_plotter.add_points(
            np.array([max_location]),
            color="red",
            point_size=16,
            render_points_as_spheres=True,
            label="Max von Mises",
        )
        interactive_plotter.add_legend()
        interactive_plotter.add_text(
            "Rotate: drag mouse | Zoom: mouse wheel",
            position="upper_left",
            font_size=11,
        )
        interactive_plotter.camera_position = "iso"
        interactive_plotter.show()


def open_saved_result(result_vtu_path: Path) -> None:
    if pv is None:
        raise ImportError(
            "PyVista를 불러올 수 없습니다. 01_install_requirements.bat을 실행하여 패키지를 설치하세요."
        )
    if not result_vtu_path.exists():
        raise FileNotFoundError(
            "결과 파일이 없습니다. 먼저 02_run_analysis.bat을 실행하세요."
        )
    grid = pv.read(result_vtu_path)
    plotter = _prepare_plotter(off_screen=False, title="Saved 3D FEA Result Viewer")
    scalars_name = "von_mises"
    if scalars_name not in grid.point_data:
        if "von_mises_cell" in grid.cell_data:
            scalars_name = "von_mises_cell"
        else:
            raise ValueError("결과 파일에 von Mises 응력 데이터가 없습니다.")
    plotter.add_mesh(
        grid,
        scalars=scalars_name,
        cmap="jet",
        show_edges=False,
        scalar_bar_args={"title": "von Mises (MPa)"},
    )
    plotter.add_axes()
    plotter.add_text(
        "Saved result viewer | Rotate: drag mouse | Zoom: mouse wheel",
        position="upper_left",
        font_size=11,
    )
    plotter.camera_position = "iso"
    plotter.show()
