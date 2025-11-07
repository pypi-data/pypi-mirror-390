from dataclasses import dataclass
from typing import Optional

import numpy as np

from pyiron_dataclasses.v1.jobs.atomistic import Structure
from pyiron_dataclasses.v1.jobs.generic import Server


@dataclass
class MurnaghanInput:
    num_points: int
    fit_type: str
    fit_order: Optional[int]
    vol_range: float
    axes: tuple[str]
    strains: Optional[list[float]]
    allow_aborted: bool


@dataclass
class MurnaghanOutput:
    energy: np.ndarray
    equilibrium_b_prime: float
    equilibrium_bulk_modulus: float
    equilibrium_energy: float
    equilibrium_volume: float
    error: np.ndarray
    id: np.ndarray
    volume: np.ndarray
    structure: Structure


@dataclass
class MurnaghanJob:
    job_id: int
    server: Server
    status: str
    calculation_input: MurnaghanInput
    calculation_output: MurnaghanOutput
