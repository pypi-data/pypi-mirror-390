from dataclasses import dataclass

import numpy as np

from pyiron_dataclasses.v1.jobs.atomistic import (
    GenericInput,
    GenericOutput,
    Structure,
)
from pyiron_dataclasses.v1.jobs.dft import (
    ChargeDensity,
    ElectronicStructure,
)
from pyiron_dataclasses.v1.jobs.generic import (
    Executable,
    GenericDict,
    Interactive,
    Server,
)


@dataclass
class PotCar:
    xc: str


@dataclass
class VaspInput:
    generic_dict: GenericDict
    interactive: Interactive
    potential_dict: dict
    generic: GenericInput
    incar: str
    kpoints: str
    potcar: PotCar
    structure: Structure
    vasp_dict: dict


@dataclass
class VaspResources:
    cpu_time: float
    user_time: float
    system_time: float
    elapsed_time: float
    memory_used: float


@dataclass
class OutCar:
    broyden_mixing: int
    irreducible_kpoint_weights: np.ndarray
    irreducible_kpoints: np.ndarray
    kin_energy_error: float
    number_plane_waves: np.ndarray
    resources: VaspResources
    stresses: np.ndarray
    energy_components: dict


@dataclass
class VaspOutput:
    description: str
    charge_density: ChargeDensity
    electronic_structure: ElectronicStructure
    generic: GenericOutput
    outcar: OutCar
    structure: Structure


@dataclass
class VaspJob:
    executable: Executable
    job_id: int
    server: Server
    status: str
    calculation_input: VaspInput
    calculation_output: VaspOutput
