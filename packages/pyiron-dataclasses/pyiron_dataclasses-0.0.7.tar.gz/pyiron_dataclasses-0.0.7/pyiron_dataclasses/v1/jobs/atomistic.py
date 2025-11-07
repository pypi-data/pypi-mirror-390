from dataclasses import dataclass
from typing import List, Optional

import numpy as np

from pyiron_dataclasses.v1.jobs.dft import OutputGenericDFT


@dataclass
class GenericOutput:
    cells: np.ndarray  # N_steps * 3 *3  [Angstrom]
    energy_pot: np.ndarray  # N_steps  [eV]
    energy_tot: np.ndarray  # N_steps  [eV]
    forces: np.ndarray  # N_steps * N_atoms * 3  [eV/Angstrom]
    positions: np.ndarray  # N_steps * N_atoms * 3  [Angstrom]
    volume: np.ndarray  # N_steps
    indices: Optional[np.ndarray]  # N_steps * N_atoms
    natoms: Optional[np.ndarray]  # N_steps
    pressures: Optional[np.ndarray]  # N_steps * 3 * 3
    steps: Optional[np.ndarray]  # N_steps
    stresses: Optional[np.ndarray]  # N_steps
    temperature: Optional[np.ndarray]  # N_steps
    unwrapped_positions: Optional[np.ndarray]  # N_steps * N_atoms * 3  [Angstrom]
    velocities: Optional[np.ndarray]  # N_steps * N_atoms * 3  [Angstrom/fs]
    dft: Optional[OutputGenericDFT]
    elastic_constants: Optional[np.ndarray]


@dataclass
class GenericInput:
    calc_mode: str
    structure: str
    fix_symmetry: Optional[bool]
    k_mesh_spacing: Optional[float]
    k_mesh_center_shift: Optional[np.ndarray]
    reduce_kpoint_symmetry: Optional[bool]
    restart_for_band_structure: Optional[bool]
    path_name: Optional[str]
    n_path: Optional[str]
    fix_spin_constraint: Optional[bool]
    max_iter: Optional[int]
    temperature: Optional[float]
    n_ionic_steps: Optional[int]
    n_print: Optional[int]
    temperature_damping_timescale: Optional[float]
    pressure_damping_timescale: Optional[float]
    time_step: Optional[int]


@dataclass
class Units:
    length: str
    mass: str


@dataclass
class Cell:
    cell: np.ndarray  # 3 * 3   [Angstrom]
    pbc: np.ndarray  # 3


@dataclass
class Structure:
    dimension: int
    indices: np.ndarray
    info: dict
    positions: np.ndarray  # N_atoms * 3  [Angstrom]
    species: List[str]
    cell: Cell
    units: Units
