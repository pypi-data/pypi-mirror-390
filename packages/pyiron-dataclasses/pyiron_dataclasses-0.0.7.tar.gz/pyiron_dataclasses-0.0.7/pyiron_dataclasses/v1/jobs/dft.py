from dataclasses import dataclass
from typing import List, Optional

import numpy as np


@dataclass
class DensityOfStates:
    energies: str
    int_densities: str
    tot_densities: str


@dataclass
class ElectronicStructure:
    efermi: float
    eig_matrix: np.ndarray
    k_points: np.ndarray
    k_weights: np.ndarray
    occ_matrix: np.ndarray
    dos: DensityOfStates


@dataclass
class OutputGenericDFT:
    energy_free: np.ndarray
    energy_int: np.ndarray
    energy_zero: np.ndarray
    scf_energy_free: np.ndarray
    scf_energy_int: np.ndarray
    scf_energy_zero: np.ndarray
    cbm_list: Optional[np.ndarray]
    e_fermi_list: Optional[np.ndarray]
    final_magmoms: Optional[np.ndarray]
    magnetization: Optional[np.ndarray]
    n_elect: Optional[float]
    n_valence: Optional[dict]
    potentiostat_output: Optional[np.ndarray]
    bands_k_weights: Optional[np.ndarray]
    kpoints_cartesian: Optional[np.ndarray]
    bands_e_fermi: Optional[np.ndarray]
    bands_occ: Optional[np.ndarray]
    bands_eigen_values: Optional[np.ndarray]
    scf_convergence: Optional[List[bool]]
    scf_dipole_mom: Optional[np.ndarray]
    scf_computation_time: Optional[np.ndarray]
    valence_charges: Optional[np.ndarray]
    vbm_list: Optional[np.ndarray]
    bands: Optional[ElectronicStructure]
    scf_energy_band: Optional[np.ndarray]
    scf_electronic_entropy: Optional[np.ndarray]
    scf_residue: Optional[np.ndarray]
    computation_time: Optional[np.ndarray]
    energy_band: Optional[np.ndarray]
    electronic_entropy: Optional[np.ndarray]
    residue: Optional[np.ndarray]


@dataclass
class ChargeDensity:
    total: np.ndarray
