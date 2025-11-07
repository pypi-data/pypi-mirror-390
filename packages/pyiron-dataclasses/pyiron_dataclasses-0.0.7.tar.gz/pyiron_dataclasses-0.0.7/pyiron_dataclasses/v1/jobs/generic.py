from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Executable:
    name: str
    operation_system_nt: bool
    mpi: bool
    accepted_return_codes: List[int]
    version: Optional[str] = None
    executable: Optional[str] = None


@dataclass
class GenericDict:
    restart_file_list: list
    restart_file_dict: dict
    exclude_nodes_hdf: list
    exclude_groups_hdf: list


@dataclass
class Interactive:
    interactive_flush_frequency: int
    interactive_write_frequency: int


@dataclass
class Server:
    user: str
    host: str
    run_mode: str
    cores: int
    threads: Optional[int] = 1
    new_hdf: Optional[bool] = True
    accept_crash: Optional[bool] = False
    additional_arguments: Optional[dict] = None
    gpus: Optional[int] = None
    run_time: Optional[int] = None  # [seconds]
    memory_limit: Optional[str] = None
    queue: Optional[str] = None
    qid: Optional[int] = None
    conda_environment_name: Optional[str] = None
    conda_environment_path: Optional[str] = None
