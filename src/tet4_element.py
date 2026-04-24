from __future__ import annotations

import numpy as np


def compute_tet_volume(coords: np.ndarray) -> float:
    matrix = np.ones((4, 4), dtype=float)
    matrix[:, 1:] = coords
    volume = np.linalg.det(matrix) / 6.0
    if abs(volume) <= 1e-12:
        raise ValueError("TET4 요소 체적이 0에 가깝습니다. 메쉬 품질을 확인하세요.")
    if volume < 0.0:
        raise ValueError("TET4 요소 체적이 음수입니다. 요소 노드 순서를 확인하세요.")
    return volume


def compute_b_matrix(coords: np.ndarray) -> tuple[np.ndarray, float]:
    matrix = np.ones((4, 4), dtype=float)
    matrix[:, 1:] = coords
    inverse = np.linalg.inv(matrix)
    gradients = inverse[1:, :]
    volume = compute_tet_volume(coords)

    b_matrix = np.zeros((6, 12), dtype=float)
    for i in range(4):
        dndx = gradients[0, i]
        dndy = gradients[1, i]
        dndz = gradients[2, i]
        base = 3 * i
        b_matrix[0, base] = dndx
        b_matrix[1, base + 1] = dndy
        b_matrix[2, base + 2] = dndz
        b_matrix[3, base] = dndy
        b_matrix[3, base + 1] = dndx
        b_matrix[4, base + 1] = dndz
        b_matrix[4, base + 2] = dndy
        b_matrix[5, base] = dndz
        b_matrix[5, base + 2] = dndx
    return b_matrix, volume


def compute_element_stiffness(coords: np.ndarray, elasticity_matrix: np.ndarray) -> tuple[np.ndarray, float]:
    b_matrix, volume = compute_b_matrix(coords)
    stiffness = volume * (b_matrix.T @ elasticity_matrix @ b_matrix)
    return stiffness, volume


def compute_element_strain_stress(
    coords: np.ndarray,
    element_displacements: np.ndarray,
    elasticity_matrix: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    b_matrix, _ = compute_b_matrix(coords)
    strain = b_matrix @ element_displacements
    stress = elasticity_matrix @ strain
    return strain, stress
