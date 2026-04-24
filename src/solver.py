from __future__ import annotations

import numpy as np

from .tet4_element import compute_element_stiffness

try:
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
except ImportError:  # pragma: no cover - import guard
    coo_matrix = None
    spsolve = None


def assemble_global_stiffness(
    nodes: np.ndarray,
    elements: np.ndarray,
    elasticity_matrix: np.ndarray,
) -> tuple[coo_matrix, np.ndarray]:
    if coo_matrix is None:
        raise ImportError(
            "SciPy를 불러올 수 없습니다. requirements.txt 설치 상태를 확인하세요."
        )
    num_dofs = nodes.shape[0] * 3
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    element_volumes = np.zeros(elements.shape[0], dtype=float)

    for element_index, element in enumerate(elements):
        coords = nodes[element]
        element_stiffness, volume = compute_element_stiffness(coords, elasticity_matrix)
        element_volumes[element_index] = volume
        dof_indices: list[int] = []
        for node_id in element:
            dof_indices.extend([3 * node_id, 3 * node_id + 1, 3 * node_id + 2])
        for local_i, global_i in enumerate(dof_indices):
            for local_j, global_j in enumerate(dof_indices):
                rows.append(global_i)
                cols.append(global_j)
                data.append(element_stiffness[local_i, local_j])

    stiffness = coo_matrix((data, (rows, cols)), shape=(num_dofs, num_dofs)).tocsr()
    return stiffness, element_volumes


def create_load_vector(num_nodes: int, load_nodes: np.ndarray, total_force_z: float) -> np.ndarray:
    force_vector = np.zeros(num_nodes * 3, dtype=float)
    if load_nodes.size == 0:
        raise ValueError("하중을 적용할 노드를 찾지 못했습니다. 메쉬를 확인하세요.")
    nodal_force = total_force_z / float(load_nodes.size)
    for node_id in load_nodes:
        force_vector[3 * node_id + 2] += nodal_force
    return force_vector


def solve_linear_system(
    stiffness: coo_matrix,
    force_vector: np.ndarray,
    fixed_nodes: np.ndarray,
) -> np.ndarray:
    if spsolve is None:
        raise ImportError(
            "SciPy를 불러올 수 없습니다. requirements.txt 설치 상태를 확인하세요."
        )
    num_dofs = force_vector.size
    fixed_dofs = np.array(
        [3 * node + offset for node in fixed_nodes for offset in (0, 1, 2)],
        dtype=int,
    )
    free_mask = np.ones(num_dofs, dtype=bool)
    free_mask[fixed_dofs] = False
    free_dofs = np.flatnonzero(free_mask)

    if free_dofs.size == 0:
        raise ValueError("자유도가 모두 구속되었습니다. 경계조건을 확인하세요.")

    reduced_stiffness = stiffness[free_dofs][:, free_dofs]
    reduced_force = force_vector[free_dofs]

    reduced_displacement = spsolve(reduced_stiffness, reduced_force)
    displacements = np.zeros(num_dofs, dtype=float)
    displacements[free_dofs] = reduced_displacement
    return displacements
