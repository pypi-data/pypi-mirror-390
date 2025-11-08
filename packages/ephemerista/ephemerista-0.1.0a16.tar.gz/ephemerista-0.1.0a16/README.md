![Ephemerista Logo](docs/logo.webp)

[![PyPI - Version](https://img.shields.io/pypi/v/ephemerista.svg)](https://pypi.org/project/ephemerista)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ephemerista.svg)](https://pypi.org/project/ephemerista)
[![coverage](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/badges/main/coverage.svg?job=coverage)](https://librespacefoundation.gitlab.io/ephemerista/ephemerista-simulator/coverage)

---

<!-- start introduction -->

Ephemerista is an open source ([AGPLv3]-licensed) Python library for space mission design and analysis with a focus on telecommunications and constellation design.
The development of the first release of Ephemerista was [funded by the European Space Agency (ESA)][esa].

Ephemerista is being maintained by the [Libre Space Foundation][lsf].

[AGPLv3]: https://choosealicense.com/licenses/agpl-3.0/
[lsf]: https://libre.space
[esa]: https://connectivity.esa.int/projects/ossmisi

<!-- end introduction -->

## Features

<!-- start features -->

- Time scale and reference frame transformations
- Semi-analytical and numerical orbit propagation
- Event detection
- Spacecraft and ground asset modelling
- Communication systems modelling and link budgets analyses
- Constellation design and coverage analyses
- Web-based graphical user interface available [at the LSF GitLab](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-web)

<!-- end features -->

## Requirements

### System Requirements

- Python 3.12 or higher
- Java Runtime Environment (JRE) 21 or higher (automatically installed via jdk4py)
- Maven (for building from source)

### Python Dependencies

Core dependencies include:

- numpy ~1.26
- pandas ~2.1
- scipy ~1.14
- matplotlib 3.9.4
- pydantic ~2.8
- lox-space 0.1.0a23
- orekit_jpype ~12.1.1.0
- plotly ~5.22
- geopandas ~1.0.1

For a complete list of dependencies, see [pyproject.toml](pyproject.toml).

## Quickstart

<!-- start quickstart -->

### Installation

Ephemerista is distributed on [PyPI] and can be installed via [uv].

```shell
# Create and activate a new virtual environment (Optional)
uv venv
source .venv/bin/activate # On Linux and macOS
# .\.venv\Scripts\activate.ps1 # On Windows

# Install Ephemerista
uv pip install ephemerista
```

### Obtain Required Data

Ephemerista requires the following data at runtime:

- Earth orientation parameters from the IERS: [finals2000A.all.csv][IERS]
- Planetary ephemerides in SPK format, e.g. [de44s.bsp][NAIF]
- An Orekit data package: [orekit-data-main.zip][orekit-data]
  - Alternatively, the Orekit data can be installed as a Python package via `pip`, see [here][orekit-pip].

### Initialise Ephemerista

Call the `ephemerista.init` function before using any other Ephemerista functionality and provide the paths to the required data files.

```python
import ephemerista

EOP_PATH = ... # e.g. finals2000A.all.csv
SPK_PATH = ... # e.g. de440s.bsp
OREKIT_DATA_PATH = ... # e.g. orekit-data-main.zip

ephemerista.init(eop_path=EOP_PATH, spk_path=SPK_PATH, orekit_data=OREKIT_DATA_PATH)
```

If the Orekit data package was installed via package manager the `orekit_data` parameter can be omitted.

### Use Ephemerista

Propagate the orbit of the ISS with Ephemerista.

```python
import ephemerista
from ephemerista.propagators.sgp4 import SGP4
from ephemerista.time import TimeDelta

# Propgate the trajectory
iss_tle = """ISS (ZARYA)
1 25544U 98067A   24187.33936543 -.00002171  00000+0 -30369-4 0  9995
2 25544  51.6384 225.3932 0010337  32.2603  75.0138 15.49573527461367"""

propagator = SGP4(tle=iss_tle)
start_time = propagator.time
end_time = start_time + TimeDelta.from_hours(6)
times = start_time.trange(end_time, step=float(TimeDelta.from_minutes(1)))
trajectory = propagator.propagate(times)
```

[PyPI]: https://pypi.org/project/ephemerista/
[uv]: https://docs.astral.sh/uv/getting-started/installation/
[IERS]: https://datacenter.iers.org/data/csv/finals2000A.all.csv
[NAIF]: https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de440s.bsp
[orekit-data]: https://gitlab.orekit.org/orekit/orekit-data/-/archive/main/orekit-data-main.zip
[orekit-pip]: https://gitlab.orekit.org/orekit/orekit-data/#notes-for-orekit-python-users

<!-- end quickstart -->

For more information, visit [Ephemerista's documentation][docs].

[docs]: https://docs.ephemerista.space

## Examples

Example Jupyter notebooks and data files are available in the [examples/](examples/) directory. If you installed Ephemerista via pip, you can download the examples from:

- **Browse online**: [GitLab examples directory](https://gitlab.com/librespacefoundation/ephemerista/ephemerista-simulator/-/tree/main/examples)
- **Download all**: See [examples/README.md](examples/README.md) for download instructions

The examples include:
- Interactive Jupyter notebooks demonstrating all major features
- Pre-configured mission scenarios (lunar transfer, navigation, link budgets)
- Sample antenna patterns and geographic areas
- Complete workflows for visibility, coverage, and interference analysis

## Development

Please refer to [CONTRIBUTING.md](https://gitlab.com/librespacefoundation/ossmisi/ossmisi-simulator/-/blob/main/CONTRIBUTING.md).

## License

`ephemerista` is distributed under the terms of the [AGPLv3](https://spdx.org/licenses/AGPL-3.0-or-later.html) license.
