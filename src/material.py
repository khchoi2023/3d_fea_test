from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LinearElasticMaterial:
    name: str
    young_modulus: float
    poisson_ratio: float

    @property
    def elasticity_matrix(self) -> np.ndarray:
        """Return the 3D isotropic constitutive matrix in MPa."""
        e = self.young_modulus
        nu = self.poisson_ratio
        coefficient = e / ((1.0 + nu) * (1.0 - 2.0 * nu))
        lam = nu
        mu = (1.0 - 2.0 * nu) / 2.0
        return coefficient * np.array(
            [
                [1.0 - nu, lam, lam, 0.0, 0.0, 0.0],
                [lam, 1.0 - nu, lam, 0.0, 0.0, 0.0],
                [lam, lam, 1.0 - nu, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, mu, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, mu, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, mu],
            ],
            dtype=float,
        )


def create_steel() -> LinearElasticMaterial:
    return LinearElasticMaterial(
        name="Steel",
        young_modulus=200000.0,
        poisson_ratio=0.3,
    )
