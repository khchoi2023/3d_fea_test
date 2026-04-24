from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class CantileverMesh:
    nodes: np.ndarray
    elements: np.ndarray
    fixed_nodes: np.ndarray
    load_nodes: np.ndarray
    min_quality: float
    max_quality: float


def _node_index(ix: int, iy: int, iz: int, ny: int, nz: int) -> int:
    return ix * (ny + 1) * (nz + 1) + iy * (nz + 1) + iz


def _tet_signed_volume(a: np.ndarray, b: np.ndarray, c: np.ndarray, d: np.ndarray) -> float:
    return np.linalg.det(np.column_stack((b - a, c - a, d - a))) / 6.0


def _tet_quality(coords: np.ndarray) -> float:
    edges = [
        np.linalg.norm(coords[i] - coords[j])
        for i, j in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    ]
    avg_edge = sum(edges) / len(edges)
    volume = abs(_tet_signed_volume(coords[0], coords[1], coords[2], coords[3]))
    if avg_edge <= 0.0:
        return 0.0
    return volume / (avg_edge**3)


def generate_cantilever_tet_mesh(
    length: float,
    width: float,
    height: float,
    nx: int,
    ny: int,
    nz: int,
) -> CantileverMesh:
    x_values = np.linspace(0.0, length, nx + 1)
    y_values = np.linspace(-width / 2.0, width / 2.0, ny + 1)
    z_values = np.linspace(-height / 2.0, height / 2.0, nz + 1)

    nodes = np.array(
        [
            [x, y, z]
            for x in x_values
            for y in y_values
            for z in z_values
        ],
        dtype=float,
    )

    tetrahedra: list[list[int]] = []
    qualities: list[float] = []
    base_pattern = np.array(
        [
            [0, 1, 3, 7],
            [0, 1, 5, 7],
            [0, 5, 4, 7],
            [0, 4, 6, 7],
            [0, 2, 6, 7],
            [0, 3, 2, 7],
        ],
        dtype=int,
    )

    for ix in range(nx):
        for iy in range(ny):
            for iz in range(nz):
                cell_nodes = np.array(
                    [
                        _node_index(ix, iy, iz, ny, nz),
                        _node_index(ix + 1, iy, iz, ny, nz),
                        _node_index(ix, iy + 1, iz, ny, nz),
                        _node_index(ix + 1, iy + 1, iz, ny, nz),
                        _node_index(ix, iy, iz + 1, ny, nz),
                        _node_index(ix + 1, iy, iz + 1, ny, nz),
                        _node_index(ix, iy + 1, iz + 1, ny, nz),
                        _node_index(ix + 1, iy + 1, iz + 1, ny, nz),
                    ],
                    dtype=int,
                )
                for tet_local in base_pattern:
                    tet = cell_nodes[tet_local]
                    tet_coords = nodes[tet]
                    signed_volume = _tet_signed_volume(
                        tet_coords[0], tet_coords[1], tet_coords[2], tet_coords[3]
                    )
                    if abs(signed_volume) <= 1e-12:
                        raise ValueError(
                            "메쉬 생성 중 체적이 0에 가까운 TET4 요소가 발견되었습니다. 메쉬 설정을 확인하세요."
                        )
                    if signed_volume < 0.0:
                        tet[[0, 1]] = tet[[1, 0]]
                        tet_coords = nodes[tet]
                        signed_volume = _tet_signed_volume(
                            tet_coords[0], tet_coords[1], tet_coords[2], tet_coords[3]
                        )
                        if signed_volume <= 0.0:
                            raise ValueError(
                                "메쉬 생성 중 음수 체적 TET4 요소를 수정하지 못했습니다. 메쉬 설정을 변경하세요."
                            )
                    tetrahedra.append(tet.tolist())
                    qualities.append(_tet_quality(tet_coords))

    elements = np.array(tetrahedra, dtype=int)
    fixed_nodes = np.flatnonzero(np.isclose(nodes[:, 0], 0.0))
    load_nodes = np.flatnonzero(np.isclose(nodes[:, 0], length))

    return CantileverMesh(
        nodes=nodes,
        elements=elements,
        fixed_nodes=fixed_nodes,
        load_nodes=load_nodes,
        min_quality=float(np.min(qualities)),
        max_quality=float(np.max(qualities)),
    )
