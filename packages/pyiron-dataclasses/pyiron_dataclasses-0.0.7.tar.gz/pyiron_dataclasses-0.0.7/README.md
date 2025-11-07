# Dataclasses for pyiron
[![Pipeline](https://github.com/pyiron/pyiron_dataclasses/actions/workflows/pipeline.yml/badge.svg)](https://github.com/pyiron/pyiron_dataclasses/actions/workflows/pipeline.yml)
[![codecov](https://codecov.io/gh/pyiron/pyiron_dataclasses/graph/badge.svg?token=83H0OO0AFC)](https://codecov.io/gh/pyiron/pyiron_dataclasses)

The `pyiron_dataclasses` module provides a series of [dataclasses](https://docs.python.org/3/library/dataclasses.html) 
for the `pyiron` workflow framework. It can load HDF5 files created by `pyiron_atomistics` and read the content stored 
in those files, without depending on `pyiron_atomistics`. Furthermore, it is not fixed to a single version of 
`pyiron_atomistics` but rather matches multiple versions of `pyiron_atomistics` to the same API version of 
`pyiron_dataclasses`. 

## Usage 
Using the `get_dataclass()` function of the built-in converter:
```python
from h5io_browser import read_dict_from_hdf
from pyiron_dataclasses import get_dataclass_v1

job_classes = get_dataclass(
    job_dict=read_dict_from_hdf(
        file_name=job.project_hdf5.file_name,
        h5_path="/",
        recursive=True,
        slash='ignore',
    )[job.job_name]
)
job_classes
```

## Supported Versions 
### Version 1 - `v1`
Supported versions of `pyiron_atomistics`:

`pyiron_atomistics` version `0.6.X`:
* `0.6.20` - Jan 8 2025
* `0.6.21` - Jan 9 2025
* `0.6.22` - Jan 13 2025
* `0.6.23` - Feb 6 2025
* `0.6.24` - Feb 17 2025
* `0.6.25` - Feb 21 2025

`pyiron_atomistics` version `0.7.X`:
* `0.7.0` - Feb 28 2025
* `0.7.1` - Mar 5 2025
* `0.7.2` - Mar 12 2025
* `0.7.3` - Apr 3 2025
* `0.7.4` - Apr 14 2025
* `0.7.5` - Apr 17 2025
* `0.7.6` - Apr 30 2025
* `0.7.7` - May 17 2025
* `0.7.8` - Jun 6 2025
* `0.7.9` - Jul 6 2025
* `0.7.10` - Jul 6 2025
* `0.7.11` - Jul 10 2025
* `0.7.12` - Jul 21 2025
* `0.7.13` - Jul 22 2025
* `0.7.14` - Aug 13 2025
* `0.7.15` - Aug 18 2025
* `0.7.16` - Aug 26 2025
* `0.7.17` - Sep 9 2025
* `0.7.18` - Sep 15 2025
* `0.7.19` - Sep 22 2025
* `0.7.20` - Sep 27 2025

`pyiron_atomistics` version `0.8.X`:
* `0.8.0` - Sep 30 2025
* `0.8.1` - Oct 7 2025
* `0.8.2` - Nov 1 2025
* `0.8.3` - Nov 1 2025